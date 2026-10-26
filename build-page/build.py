"""Build index.html from data JSONs, labels and template.

Usage:
  python build-page/build.py            # validate + generate index.html
  python build-page/build.py --check    # exit 1 if outdated
  python build-page/build.py --validate # validate only, no generation
"""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "data"
LABELS = BASE / "labels"
TEMPLATE = BASE / "build-page" / "template.html"
STYLE = BASE / "build-page" / "style.css"
SAIDA = BASE / "index.html"

FONTES = [
    DADOS / "referencias.json",
    DADOS / "defesas.json",
    DADOS / "sinais.json",
    DADOS / "recon.json",
    DADOS / "tecnicas.json",
    DADOS / "evasoes.json",
    DADOS / "produtos.json",
    DADOS / "wiki.json",
    DADOS / "taxonomia.json",
    DADOS / "clusters.json",
    DADOS / "triagem.json",
    DADOS / "sinais_estruturais.json",
    DADOS / "schema.json",
    LABELS / "pt.json",
    TEMPLATE,
    STYLE,
    Path(__file__).resolve(),
]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def schema_enums(data):
    return data.get("schema", {}).get("enums", {})


def validar_bypass(nome_ent, it, defs, bases, errs):
    """Each link carries its evidence base; returns the number of 'nao_auditado' links."""
    n_na = 0
    fontes_it = {f["r"] for f in it.get("fontes", [])}
    vistos = set()
    for b in it.get("bypass", []):
        if b["defesa"] not in defs:
            errs.append(f"{nome_ent} {it['id']}: bypass references nonexistent defesa '{b['defesa']}'")
        if b["defesa"] in vistos:
            errs.append(f"{nome_ent} {it['id']}: bypass duplicates defesa '{b['defesa']}'")
        vistos.add(b["defesa"])
        if b.get("base") not in bases:
            errs.append(f"{nome_ent} {it['id']}: bypass[{b['defesa']}].base invalid '{b.get('base')}'")
        elif b["base"] == "nao_auditado":
            n_na += 1
        else:
            fontes_def = {f["r"] for f in defs.get(b["defesa"], {}).get("fontes", [])} if b.get("base") == "inferencia" else set()
            if b.get("fonte") not in fontes_it and b.get("fonte") not in fontes_def:
                errs.append(f"{nome_ent} {it['id']}: bypass[{b['defesa']}].fonte '{b.get('fonte')}' not in its fontes" + (" nor in the defesa's fontes" if b.get("base") == "inferencia" else ""))
            if not b.get("nota"):
                errs.append(f"{nome_ent} {it['id']}: bypass[{b['defesa']}] needs a nota (base != nao_auditado)")
    return n_na


OVERLAYS = ("tecnicas", "evasoes", "produtos")


def validate_translations(data):
    """Translations of tecnicas/evasoes/produtos are overlays (only translatable fields); taxonomia keeps parity."""
    errs = []
    allowed = {"id", "nome", "descricao", "variantes", "bypass", "rotulos"}
    errs += validate_generic(data)
    for lang in ("en", "es"):
        for chave in OVERLAYS:
            pt = {t["id"]: t for t in data[chave][chave]}
            tf = BASE / "translations" / lang / f"{chave}.json"
            ov = load(tf)[chave]
            ids = [o["id"] for o in ov]
            if sorted(ids) != sorted(pt):
                errs.append(f"translations/{lang}/{chave}: ids differ from data/{chave}: {sorted(set(ids) ^ set(pt))}")
                continue
            for o in ov:
                t = pt[o["id"]]
                ref = f"translations/{lang}/{chave} {o['id']}"
                extra = set(o) - allowed
                if extra:
                    errs.append(f"{ref}: non-translatable fields {sorted(extra)}")
                if "descricao" not in o:
                    errs.append(f"{ref}: missing descricao")
                if len(o.get("variantes", [])) != len(t.get("variantes", [])):
                    errs.append(f"{ref}: variantes count differs")
                if "rotulos" in o and len(o["rotulos"]) != len(t.get("exemplos", [])):
                    errs.append(f"{ref}: rotulos count differs from exemplos")
                notas_pt = {b["defesa"] for b in t.get("bypass", []) if b.get("nota")}
                notas_tr = {b["defesa"] for b in o.get("bypass", [])}
                if notas_pt != notas_tr:
                    errs.append(f"{ref}: bypass notas differ from PT: {sorted(notas_pt ^ notas_tr)}")
        tx = load(BASE / "translations" / lang / "taxonomia.json")
        if tx.get("grupo_ordem") != data["taxonomia"]["grupo_ordem"]:
            errs.append(f"translations/{lang}/taxonomia: grupo_ordem differs from PT")
        if set(tx.get("grupo_descricoes", {})) != set(data["taxonomia"]["grupo_descricoes"]):
            errs.append(f"translations/{lang}/taxonomia: grupo_descricoes keys differ from PT")
        marcas = [(i, r["gerado"]) for i, r in enumerate(tx["ramos"]) if r.get("gerado")]
        marcas_pt = [(i, r["gerado"]) for i, r in enumerate(data["taxonomia"]["ramos"]) if r.get("gerado")]
        if marcas != marcas_pt or len(tx["ramos"]) != len(data["taxonomia"]["ramos"]):
            errs.append(f"translations/{lang}/taxonomia: ramos structure differs from PT")
    return errs


# Generic overlays: translation files hold only translated text (+ id and pt_hash); PT is the single source.
# (list_path inside the PT file, translated text keys, structural keys that must match PT)
GENERIC = {
    "defesas":  (("defesas",),  {"nome", "descricao", "fortalezas", "fraquezas", "categoria"}, False),
    "sinais":   (("sinais",),   {"texto"}, False),
    "recon":    (("prompts",),  {"titulo", "quando", "objetivo", "interpretacao", "rotulo"}, False),
    "wiki":     (("artigos",),  {"titulo", "texto", "linhas", "itens"}, True),
    "triagem":  (("perguntas",), {"pergunta", "rotulo", "nota"}, False),
    "clusters": (("_meta", "clusters"), {"nome", "descricao"}, False),
}
STRUCT_KEYS = {"id", "tipo", "pt_hash"}


def _lista(d, caminho):
    for k in caminho:
        d = d[k]
    return d


def _extrair(no, texto, tipo=False):
    """Shape-preserving projection of a PT node onto its translatable keys (lists keep their length)."""
    if isinstance(no, dict):
        out = {}
        for k, v in no.items():
            if k in texto:
                out[k] = v
            elif k == "tipo" and tipo:
                out[k] = v
            elif isinstance(v, (dict, list)):
                sub = _extrair(v, texto, tipo)
                if sub not in ({}, []):
                    out[k] = sub
        return out
    if isinstance(no, list):
        sub = [_extrair(x, texto, tipo) for x in no if isinstance(x, (dict, list))]
        if len(sub) != len(no) or all(x in ({}, []) for x in sub):
            return []
        return sub
    return no


def pt_hash(item, texto, tipo=False):
    proj = _extrair({k: v for k, v in item.items() if k != "id"}, texto, tipo)
    return hashlib.sha1(json.dumps(proj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:10]


def _comparar(pt, ov, texto, ref, errs):
    if isinstance(ov, dict):
        if not isinstance(pt, dict):
            errs.append(f"{ref}: shape differs from PT")
            return
        for k, v in ov.items():
            if k in ("pt_hash",):
                continue
            if k not in pt:
                errs.append(f"{ref}: field '{k}' does not exist in PT")
            elif k == "tipo" or k == "id":
                if v != pt[k]:
                    errs.append(f"{ref}: '{k}' differs from PT")
            elif k in texto:
                if type(v) is not type(pt[k]) or (isinstance(v, list) and len(v) != len(pt[k])):
                    errs.append(f"{ref}.{k}: shape/length differs from PT")
            else:
                _comparar(pt[k], v, texto, f"{ref}.{k}", errs)
    elif isinstance(ov, list):
        if not isinstance(pt, list) or len(pt) != len(ov):
            errs.append(f"{ref}: list length differs from PT")
            return
        for i, (a, b) in enumerate(zip(pt, ov)):
            _comparar(a, b, texto, f"{ref}[{i}]", errs)
    else:
        errs.append(f"{ref}: non-translatable value in overlay")


def validate_generic(data):
    errs = []
    for chave, (caminho, texto, tipo) in GENERIC.items():
        pt = {t["id"]: t for t in _lista(data[chave], caminho)}
        for lang in ("en", "es"):
            f = BASE / "translations" / lang / f"{chave}.json"
            ov = _lista(load(f), caminho)
            ids = [o["id"] for o in ov]
            if sorted(ids) != sorted(pt):
                errs.append(f"translations/{lang}/{chave}: ids differ from data/{chave}: {sorted(set(ids) ^ set(pt))}")
                continue
            for o in ov:
                ref = f"translations/{lang}/{chave} {o['id']}"
                _comparar(pt[o["id"]], o, texto, ref, errs)
                if o.get("pt_hash") != pt_hash(pt[o["id"]], texto, tipo):
                    errs.append(f"{ref}: PT changed since translation (pt_hash); retranslate, then run --stamp-translations")
    return errs


def merge_generic(pt, ov, chave):
    caminho, texto, _ = GENERIC[chave]
    out = copy.deepcopy(pt)
    mapa = {o["id"]: o for o in _lista(ov, caminho)}

    def aplicar(no, o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in STRUCT_KEYS:
                    continue
                if k in texto:
                    no[k] = v
                else:
                    aplicar(no[k], v)
        elif isinstance(o, list):
            for a, b in zip(no, o):
                aplicar(a, b)

    for it in _lista(out, caminho):
        aplicar(it, mapa[it["id"]])
    return out


def stamp_translations(data):
    """Create/refresh translations as overlays: keep translated text, drop everything else, stamp pt_hash."""
    for chave, (caminho, texto, tipo) in GENERIC.items():
        pt = {t["id"]: t for t in _lista(data[chave], caminho)}
        for lang in ("en", "es"):
            f = BASE / "translations" / lang / f"{chave}.json"
            ov = load(f)
            lista = _lista(ov, caminho)
            novos = []
            for o in lista:
                proj = _extrair({k: v for k, v in o.items() if k not in ("id", "pt_hash")}, texto, tipo)
                item = {"id": o["id"], "pt_hash": pt_hash(pt[o["id"]], texto, tipo)}
                item.update(proj)
                novos.append(item)
            saida = {caminho[-1]: novos} if len(caminho) == 1 else {caminho[0]: {caminho[1]: novos}}
            f.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK: translations stamped")


def merge_overlay(pt, overlay, chave, variacao):
    """PT is the source of truth; overlay only supplies translated text."""
    ov = {o["id"]: o for o in overlay[chave]}
    out = copy.deepcopy(pt)
    for t in out[chave]:
        o = ov[t["id"]]
        for k in ("nome", "descricao"):
            if k in o:
                t[k] = o[k]
        for v, ovv in zip(t.get("variantes", []), o.get("variantes", [])):
            v["descricao"] = ovv["descricao"]
        notas = {b["defesa"]: b["nota"] for b in o.get("bypass", [])}
        for b in t.get("bypass", []):
            if b["defesa"] in notas:
                b["nota"] = notas[b["defesa"]]
        for ex, rot in zip(t.get("exemplos", []), o.get("rotulos", [None] * len(t.get("exemplos", [])))):
            if rot:
                ex["rotulo"] = rot
            ex["rotulo"] = ex["rotulo"].replace("Variação", variacao, 1)
    return out


def gerar_taxonomia(tax, tecs, evas):
    """Branches derived from the catalogs: techniques (group → technique → variants) and evasions (flat list)."""
    tax = copy.deepcopy(tax)
    filhos = []
    for g in tax["grupo_ordem"]:
        nos = []
        for t in tecs:
            if t["grupo"] != g:
                continue
            no = {"t": f"{t['id']} — {t['nome']}", "ref": t["id"]}
            if t.get("variantes"):
                no["filhos"] = [{"t": v["nome"], "desc": v["descricao"]} for v in t["variantes"]]
            nos.append(no)
        if nos:
            filhos.append({"t": g, "desc": tax["grupo_descricoes"][g], "filhos": nos})
    folhas = [{"t": f"{e['id']} — {e['nome']}", "ref": e["id"]} for e in evas]
    geradas = {"tecnicas": (filhos, len(tecs)), "evasoes": (folhas, len(evas))}
    for r in tax["ramos"]:
        if r.get("gerado") in geradas:
            lista, n = geradas[r["gerado"]]
            r["t"] = f"{r['t']} ({n})"
            r["filhos"] = lista
            del r["gerado"]
    return tax


def finalizar_idioma(d):
    for chave in ("tecnicas", "evasoes"):
        for it in d[chave][chave]:
            it["defesas_bypassadas"] = [b["defesa"] for b in it["bypass"]]  # derived, never stored
    d["taxonomia"] = gerar_taxonomia(d["taxonomia"], d["tecnicas"]["tecnicas"], d["evasoes"]["evasoes"])


def validate(data):
    errs = []
    warns = []

    refs = {r["id"]: r for r in data["referencias"]["referencias"]}
    defs = {d["id"]: d for d in data["defesas"]["defesas"]}
    sigs = {s["id"]: s for s in data["sinais"]["sinais"]}

    def check_fk(entity_name, items, field, valid_ids, label):
        for item in items:
            for fk in item.get(field, []):
                if fk not in valid_ids:
                    errs.append(f"{entity_name} {item['id']}: {field} references nonexistent {label} '{fk}'")

    def check_fontes(entity_name, items):
        for item in items:
            for f in item.get("fontes", []):
                rid = f["r"]
                if rid not in refs:
                    errs.append(f"{entity_name} {item['id']}: fontes references nonexistent ref '{rid}'")
                elif f["tipo"] != refs[rid]["tipo"]:
                    errs.append(f"{entity_name} {item['id']}: fontes[{rid}].tipo='{f['tipo']}' != refs tipo='{refs[rid]['tipo']}'")
                if "verificacao" in f and f["verificacao"] not in ("confirmado", "parcial", "nao_verificado"):
                    errs.append(f"{entity_name} {item['id']}: fontes[{rid}].verificacao invalid '{f['verificacao']}'")
                if "url" in f and not str(f["url"]).startswith("https://"):
                    errs.append(f"{entity_name} {item['id']}: fontes[{rid}].url must start with https://")

    # FK: sinais → defesas
    check_fk("sinal", data["sinais"]["sinais"], "defesas", defs, "defesa")

    # FK: recon → sinais (sinal_alvo)
    for p in data["recon"]["prompts"]:
        for sa in p.get("sinal_alvo", []):
            if sa not in sigs:
                errs.append(f"recon {p['id']}: sinal_alvo references nonexistent sinal '{sa}'")
            elif sigs[sa]["tipo"] != "passivo":
                errs.append(f"recon {p['id']}: sinal_alvo '{sa}' is tipo='{sigs[sa]['tipo']}', must be passivo")

    # FK: produtos → defesas
    check_fk("produto", data["produtos"]["produtos"], "defesas", defs, "defesa")

    # técnicas: bypass com base de evidência, grupo e variantes
    ordem = data["taxonomia"]["grupo_ordem"]
    gdesc = data["taxonomia"]["grupo_descricoes"]
    bases = schema_enums(data).get("bypass.base", [])
    n_nao_auditado = 0
    for nome_ent, itens in (("tecnica", data["tecnicas"]["tecnicas"]), ("evasao", data["evasoes"]["evasoes"])):
        for it in itens:
            n_nao_auditado += validar_bypass(nome_ent, it, defs, bases, errs)
    for t in data["tecnicas"]["tecnicas"]:
        tid = t["id"]
        if t["grupo"] not in ordem:
            errs.append(f"tecnica {tid}: grupo '{t['grupo']}' not in taxonomia.grupo_ordem")
        nomes = [v.get("nome") for v in t.get("variantes", [])]
        if len(nomes) != len(set(nomes)) or not all(nomes) or not all(v.get("descricao") for v in t.get("variantes", [])):
            errs.append(f"tecnica {tid}: variantes need unique nome and a descricao")
    n_vazios = sum(1 for _, itens in (("t", data["tecnicas"]["tecnicas"]), ("e", data["evasoes"]["evasoes"])) for it in itens if not it.get("bypass"))
    if n_vazios:
        warns.append(f"{n_vazios} technique/evasion items with no defense link (no evidence read)")
    if n_nao_auditado:
        warns.append(f"{n_nao_auditado} technique/evasion→defense links with base 'nao_auditado' (audit pending)")
    if len(ordem) != len(set(ordem)):
        errs.append("taxonomia.grupo_ordem has duplicates")
    if set(gdesc) != set(ordem):
        errs.append(f"taxonomia: grupo_descricoes keys differ from grupo_ordem: {sorted(set(gdesc) ^ set(ordem))}")
    usados = {t["grupo"] for t in data["tecnicas"]["tecnicas"]}
    if set(ordem) - usados:
        warns.append(f"taxonomia: grupos sem técnica: {sorted(set(ordem) - usados)}")
    if sum(1 for r in data["taxonomia"]["ramos"] if r.get("gerado") == "tecnicas") != 1:
        errs.append("taxonomia: exactly one ramo with gerado='tecnicas' is required")
    errs.extend(validate_translations(data))

    # fontes consistency
    check_fontes("defesa", data["defesas"]["defesas"])
    check_fontes("tecnica", data["tecnicas"]["tecnicas"])
    check_fontes("evasao", data["evasoes"]["evasoes"])
    check_fontes("recon", data["recon"]["prompts"])
    check_fontes("produto", data["produtos"]["produtos"])

    # Unique IDs
    for name, key, items in [
        ("referencias", "referencias", data["referencias"]["referencias"]),
        ("defesas", "defesas", data["defesas"]["defesas"]),
        ("sinais", "sinais", data["sinais"]["sinais"]),
        ("recon", "prompts", data["recon"]["prompts"]),
        ("tecnicas", "tecnicas", data["tecnicas"]["tecnicas"]),
        ("evasoes", "evasoes", data["evasoes"]["evasoes"]),
        ("produtos", "produtos", data["produtos"]["produtos"]),
        ("wiki", "artigos", data["wiki"]["artigos"]),
    ]:
        ids = [item["id"] for item in items]
        dupes = [x for x in ids if ids.count(x) > 1]
        if dupes:
            errs.append(f"{name}: duplicate IDs: {set(dupes)}")

    # Enum validation
    schema = data.get("schema", {})
    enums = schema.get("enums", {})
    for d in data["defesas"]["defesas"]:
        if d["locus"] not in enums.get("defesas.locus", []):
            errs.append(f"defesa {d['id']}: invalid locus '{d['locus']}'")
        if d.get("aplicabilidade"):
            for a in d["aplicabilidade"]:
                if a not in enums.get("defesas.aplicabilidade", []):
                    errs.append(f"defesa {d['id']}: invalid aplicabilidade '{a}'")

    for s in data["sinais"]["sinais"]:
        if s["tipo"] not in enums.get("sinais.tipo", []):
            errs.append(f"sinal {s['id']}: invalid tipo '{s['tipo']}'")

    for t in data["tecnicas"]["tecnicas"]:
        if t["turno"] not in enums.get("tecnicas.turno", []):
            errs.append(f"tecnica {t['id']}: invalid turno '{t['turno']}'")

    for p in data["recon"]["prompts"]:
        if p["grupo"] not in enums.get("recon.grupo", []):
            errs.append(f"recon {p['id']}: invalid grupo '{p['grupo']}'")
        comp = p.get("componente")
        if p["grupo"] == "arquitetura":
            if comp not in enums.get("recon.componente", []):
                errs.append(f"recon {p['id']}: grupo arquitetura needs a valid componente (got '{comp}')")
        elif comp is not None:
            errs.append(f"recon {p['id']}: componente only applies to grupo arquitetura")

    # Coverage: passive signals → recon
    passive = {s["id"] for s in data["sinais"]["sinais"] if s["tipo"] == "passivo"}
    covered = set()
    for p in data["recon"]["prompts"]:
        covered.update(p.get("sinal_alvo", []))
    uncovered = passive - covered
    if uncovered:
        warns.append(f"Passive signals without recon probe: {sorted(uncovered)}")

    # Coverage: defesas with at least one fraqueza
    for d in data["defesas"]["defesas"]:
        if not d.get("fraquezas"):
            warns.append(f"defesa {d['id']}: no fraquezas listed")

    # Orphan references
    cited = set()
    for name, items in [
        ("defesas", data["defesas"]["defesas"]),
        ("tecnicas", data["tecnicas"]["tecnicas"]),
        ("evasoes", data["evasoes"]["evasoes"]),
        ("recon", data["recon"]["prompts"]),
        ("produtos", data["produtos"]["produtos"]),
        ("sinais", data["sinais"]["sinais"]),
    ]:
        for item in items:
            for f in item.get("fontes", []):
                cited.add(f["r"])
    # citações em texto livre (ex.: "(R251 §3)") também contam como citadas
    _txt = json.dumps({k: v for k, v in data.items() if k != "referencias"}, ensure_ascii=False)
    cited |= set(re.findall(r"\bR\d{2,3}\b", _txt))
    orphans = set(refs.keys()) - cited
    if orphans:
        warns.append(f"Orphan references (not cited): {sorted(orphans)}")

    # --- Validação da triagem (clusters, árvore, sinais_estruturais) ---
    tecs = {t["id"] for t in data["tecnicas"]["tecnicas"]}
    cluster_ids = {c["id"] for c in data["clusters"]["_meta"]["clusters"]}
    defesa_para_cluster = data["clusters"]["defesa_para_cluster"]

    # cobertura: toda defesa aparece exatamente 1 vez em defesa_para_cluster
    missing_cluster = set(defs.keys()) - set(defesa_para_cluster.keys())
    if missing_cluster:
        errs.append(f"clusters: defesas sem cluster: {sorted(missing_cluster)}")
    extra_cluster = set(defesa_para_cluster.keys()) - set(defs.keys())
    if extra_cluster:
        errs.append(f"clusters: defesa_para_cluster referencia defesa inexistente: {sorted(extra_cluster)}")
    bad_cluster_vals = {v for v in defesa_para_cluster.values() if v not in cluster_ids}
    if bad_cluster_vals:
        errs.append(f"clusters: valores de cluster inválidos: {sorted(bad_cluster_vals)}")

    # triagem: sinais_ref e opcoes A/B
    pergunta_ids = {p["id"] for p in data["triagem"]["perguntas"]}
    for p in data["triagem"]["perguntas"]:
        for sr in p.get("sinais_ref", []):
            if sr not in sigs:
                errs.append(f"triagem {p['id']}: sinais_ref referencia sinal inexistente '{sr}'")
        ops = p.get("opcoes", [])
        if len(ops) != 2:
            errs.append(f"triagem {p['id']}: opcoes deve ter exatamente 2 itens (A e B)")
        for i, op in enumerate(ops):
            ref = f"triagem {p['id']} opcoes[{i}]"
            if not op.get("rotulo"):
                errs.append(f"{ref}: rotulo ausente")
            v = op.get("destino")
            if isinstance(v, str):
                if v not in pergunta_ids:
                    errs.append(f"{ref}: destino referencia pergunta inexistente '{v}'")
            elif isinstance(v, dict):
                if not v.get("familia"):
                    errs.append(f"{ref}: destino sem familia")
                for c in v.get("clusters", []):
                    if c not in cluster_ids:
                        errs.append(f"{ref}: destino.clusters referencia cluster inexistente '{c}'")
            else:
                errs.append(f"{ref}: destino deve ser string ou objeto")

    # sinais_estruturais: toda técnica citada existe
    for chave, ids in data["sinais_estruturais"].items():
        if chave == "_meta":
            continue
        for tid in ids:
            if tid not in tecs:
                errs.append(f"sinais_estruturais.{chave}: referencia técnica inexistente '{tid}'")

    return errs, warns


def load_all():
    data = {
        "referencias": load(DADOS / "referencias.json"),
        "defesas": load(DADOS / "defesas.json"),
        "sinais": load(DADOS / "sinais.json"),
        "recon": load(DADOS / "recon.json"),
        "tecnicas": load(DADOS / "tecnicas.json"),
        "evasoes": load(DADOS / "evasoes.json"),
        "produtos": load(DADOS / "produtos.json"),
        "wiki": load(DADOS / "wiki.json"),
        "taxonomia": load(DADOS / "taxonomia.json"),
        "clusters": load(DADOS / "clusters.json"),
        "triagem": load(DADOS / "triagem.json"),
        "sinais_estruturais": load(DADOS / "sinais_estruturais.json"),
        "schema": load(DADOS / "schema.json"),
    }
    return data


def check_outdated():
    if not SAIDA.exists():
        return True
    t = SAIDA.stat().st_mtime
    return any(f.stat().st_mtime > t for f in FONTES if f.exists())


def load_translations(data_pt):
    """Load EN/ES translations and build multi-lang DATA and LABELS."""
    TRANS = BASE / "translations"
    all_data = {"pt": data_pt}
    all_labels = {"pt": load(LABELS / "pt.json")}

    translatable = ["defesas", "sinais", "tecnicas", "evasoes",
                    "recon", "produtos", "wiki", "taxonomia"]

    for lang_code in ["en", "es"]:
        lang_dir = TRANS / lang_code
        labels_file = LABELS / f"{lang_code}.json"
        if labels_file.exists():
            all_labels[lang_code] = load(labels_file)
        lang_data = {}
        for key in data_pt:
            tf = lang_dir / f"{key}.json"
            if key in OVERLAYS:
                lang_data[key] = merge_overlay(
                    data_pt[key], load(tf), key, all_labels[lang_code]["campos"]["rotulo_variacao"])
            elif key in GENERIC:
                lang_data[key] = merge_generic(data_pt[key], load(tf), key)
            elif key in translatable and tf.exists():
                lang_data[key] = load(tf)
            else:
                lang_data[key] = data_pt[key]
        all_data[lang_code] = lang_data

    for d in all_data.values():
        finalizar_idioma(d)
    return all_data, all_labels


def build():
    data = load_all()

    errs, warns = validate(data)
    for w in warns:
        print(f"  WARN: {w}")
    if errs:
        print(f"\nVALIDATION ERRORS ({len(errs)}):")
        for e in errs:
            print(f"  {e}")
        sys.exit(1)

    all_data, all_labels = load_translations(data)

    template = TEMPLATE.read_text(encoding="utf-8")
    style_css = STYLE.read_text(encoding="utf-8")

    html = template.replace("__CSS__", style_css)
    html = html.replace("/*__DATA__*/", json.dumps(all_data, ensure_ascii=False))
    html = html.replace("/*__LABELS__*/", json.dumps(all_labels, ensure_ascii=False))

    SAIDA.write_text(html, encoding="utf-8")

    n = lambda k, d: len(d[k][k] if k != "recon" else d["recon"]["prompts"])
    print(f"OK: {SAIDA} ({SAIDA.stat().st_size:,} bytes)")
    print(f"  refs={n('referencias', data)} defs={n('defesas', data)} sinais={n('sinais', data)} "
          f"recon={len(data['recon']['prompts'])} tecs={n('tecnicas', data)} evas={n('evasoes', data)} "
          f"prods={n('produtos', data)} wiki={len(data['wiki']['artigos'])}")
    print(f"  langs: {sorted(all_labels.keys())}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        if check_outdated():
            print("OUTDATED: index.html does not reflect latest sources.")
            sys.exit(1)
        print("OK: index.html is up to date.")
        sys.exit(0)
    if "--stamp-translations" in sys.argv:
        stamp_translations(load_all())
        sys.exit(0)
    if "--validate" in sys.argv:
        data = load_all()
        errs, warns = validate(data)
        for w in warns:
            print(f"  WARN: {w}")
        if errs:
            print(f"\nVALIDATION ERRORS ({len(errs)}):")
            for e in errs:
                print(f"  {e}")
            sys.exit(1)
        print("OK: all validations passed.")
        sys.exit(0)
    build()
