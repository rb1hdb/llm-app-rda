"""Build index.html from data JSONs, labels and template.

Usage:
  python build-page/build.py            # validate + generate index.html
  python build-page/build.py --check    # exit 1 if outdated
  python build-page/build.py --validate # validate only, no generation
"""
import json
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
    DADOS / "schema.json",
    LABELS / "pt.json",
    TEMPLATE,
    STYLE,
    Path(__file__).resolve(),
]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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

    # FK: sinais → defesas
    check_fk("sinal", data["sinais"]["sinais"], "defesas", defs, "defesa")

    # FK: recon → sinais (sinal_alvo)
    for p in data["recon"]["prompts"]:
        for sa in p.get("sinal_alvo", []):
            if sa not in sigs:
                errs.append(f"recon {p['id']}: sinal_alvo references nonexistent sinal '{sa}'")
            elif sigs[sa]["tipo"] != "passivo":
                errs.append(f"recon {p['id']}: sinal_alvo '{sa}' is tipo='{sigs[sa]['tipo']}', must be passivo")

    # FK: tecnicas → defesas
    check_fk("tecnica", data["tecnicas"]["tecnicas"], "defesas_bypassadas", defs, "defesa")
    for t in data["tecnicas"]["tecnicas"]:
        if not t.get("defesas_bypassadas"):
            errs.append(f"tecnica {t['id']}: defesas_bypassadas is empty")

    # FK: evasoes → defesas
    check_fk("evasao", data["evasoes"]["evasoes"], "defesas_bypassadas", defs, "defesa")
    for e in data["evasoes"]["evasoes"]:
        if not e.get("defesas_bypassadas"):
            errs.append(f"evasao {e['id']}: defesas_bypassadas is empty")

    # FK: produtos → defesas
    check_fk("produto", data["produtos"]["produtos"], "defesas", defs, "defesa")

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
    ]:
        for item in items:
            for f in item.get("fontes", []):
                cited.add(f["r"])
    orphans = set(refs.keys()) - cited
    if orphans:
        warns.append(f"Orphan references (not cited): {sorted(orphans)}")

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
            if key in translatable and tf.exists():
                lang_data[key] = load(tf)
            else:
                lang_data[key] = data_pt[key]
        all_data[lang_code] = lang_data

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
