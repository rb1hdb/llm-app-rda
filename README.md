# LLM App RDA — Recon, Defenses and Attacks

<p align="center">
  <a href="https://rb1hdb.github.io/llm-app-rda/"><img src="https://img.shields.io/badge/Live%20site-llm--app--rda-9966CC?style=for-the-badge&logo=lightning&logoColor=white" alt="Live site"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-CC%20BY%204.0-2ea44f?style=for-the-badge&logo=creative-commons&logoColor=white" alt="License"></a>
  <img src="https://img.shields.io/badge/version-0.3-1f6feb?style=for-the-badge&logo=git&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/use-educational%20%26%20authorized-d73a4a?style=for-the-badge&logo=law&logoColor=white" alt="Use">
</p>

<p align="center">
  <b>Language:</b> <b>English</b> · <a href="README-pt.md">Português</a> · <a href="README-es.md">Español</a>
</p>

---

## What is this

Interactive pentest runbook for LLM-based applications. Structured methodology to identify, fingerprint, and exploit defenses — organized in three phases:

| Phase | Content |
|-------|---------|
| **R — Recon** | 37 black-box prompts + 66 observable signals |
| **D — Defenses** | 52 cataloged defenses across 6 loci |
| **A — Attacks** | 50 prompt injection techniques + 12 evasion transforms |

**Pipeline:** Signal → Defense@locus → Technique/Evasion

The **Triage** tab opens the page with a decision guide: a few observable questions narrow the likely defense clusters before the full Recon → Signals → Defenses flow.

Unlike collections of loose jailbreaks, every entry has traced sources (primary, survey, or operational) and a reproducible pipeline.

---

## Catalogs

| Catalog | Count | Description |
|---------|-------|-------------|
| **Recon** | 37 | Black-box prompts to identify defenses without prior knowledge |
| **Signals** | 66 | Observable heuristics indicating active defenses |
| **Defenses** | 52 | Cards with definition, locus, strengths, weaknesses, applicability |
| **Techniques** | 52 | Attack techniques organized by turn and group |
| **Evasions** | 12 | Transformations to escape detection |
| **Products** | 14 | Commercial tools mapped to defenses they implement |
| **References** | 136 | Sources (128 primary + 5 surveys + 3 operational) |
| **Wiki** | 8 | Conceptual articles on methodology and schema decisions |
| **Taxonomy** | 1 | Hierarchical attack tree |
| **Triage** | 6 questions | Decision guide mapping observations to defense clusters |

---

## How to use

### Via GitHub Pages (recommended)

Open **[rb1hdb.github.io/llm-app-rda/](https://rb1hdb.github.io/llm-app-rda/)** — interactive single-file page, no server needed.

### Locally

```bash
git clone https://github.com/rb1hdb/llm-app-rda.git
cd llm-app-rda
# open index.html in your browser
```

### Rebuild after editing data

```bash
python build-page/build.py            # generate index.html
python build-page/build.py --validate # validate integrity only
```

---

## Languages

PT, EN, ES — toggle in the header. All UI text comes from `labels/{pt,en,es}.json`. Entity data translations live in `translations/{en,es}/`.

---

## Repository structure

```
llm-app-rda/
├── index.html              <- Generated interactive page
├── .nojekyll               <- GitHub Pages config
├── LICENSE                 <- CC BY 4.0
├── README.md               <- This file (EN)
├── README-pt.md            <- README (PT)
├── README-es.md            <- README (ES)
├── data/                   <- Source of truth (PT)
│   ├── defesas.json        <- 52 defenses
│   ├── sinais.json         <- 66 signals
│   ├── tecnicas.json       <- 52 techniques
│   ├── evasoes.json        <- 12 evasions
│   ├── recon.json          <- 37 recon prompts
│   ├── produtos.json       <- 14 products
│   ├── referencias.json    <- 136 references
│   ├── wiki.json           <- 8 articles
│   ├── taxonomia.json      <- Taxonomy tree
│   ├── triagem.json        <- Decision-triage tree (questions → clusters)
│   ├── clusters.json       <- Defense → cluster map
│   ├── sinais_estruturais.json <- Structural signals → techniques
│   └── schema.json         <- Validation schema
├── labels/                 <- UI strings (i18n)
│   ├── pt.json
│   ├── en.json
│   └── es.json
├── translations/           <- Entity data translations
│   ├── en/                 <- Translated data files
│   └── es/                 <- Translated data files
└── build-page/
    ├── template.html       <- HTML/JS template
    ├── style.css           <- Styles
    └── build.py            <- Validator + generator
```

---

## Defense locus

Defenses are classified by where they act in the LLM pipeline:

| Locus | Count | Description |
|-------|-------|-------------|
| input | 9 | Filters on user input |
| output | 6 | Filters on model output |
| prompt | 7 | System prompt design |
| modelo | 6 | Model-level controls |
| acao | 20 | Action/tool gating |
| processo | 4 | Process-level controls |

---

## Methodology

This interactive runbook (R-D-A pipeline) was built from anchor sources in LLM security (listed in `data/referencias.json`).

**Source hierarchy:** each entry's source carries a type — *primary* (direct textual evidence), *survey* (systematic review), *operational* (tool documentation), or *inference* (logical inference, always documented with rationale).

### About N:N relations

The relations linking signals → defenses → techniques/evasions were generated by **LLM-automated sweep** (not human-curated one by one). A subsequent audit corrected defense-evasion connections based on detection mechanism analysis (regex/lexical, trained classifier, LLM judge, semantic/embedding, structural, process). Technique/evasion → defense links were then audited against the sources: each link keeps only a basis that was read (tested, alleged by the source, or documented inference); links with no evidence were removed, so some techniques show no defense link yet. Technique sources also carry a verification status and deep links to the exact page or payload. **Out of audit scope**: signals and mechanisms in isolation, recon, wiki, taxonomy.

### Selection engine

Mark signals/defenses to filter candidate techniques/evasions. The resulting list is a **shortlist to refine**, not a verdict — combine it with the discriminative-test step (Method tab) before attributing a bypass.

---

## Inspiration

The prompt injection taxonomy structure is inspired by the [Arcanum Prompt Injection Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) by Jason Haddix (Arcanum Information Security).

The **R-D-A workflow** (Recon → Defenses → Attacks pipeline), the source-traced cards, the signal-based discovery method, and the defense-locus-attack linkage are **original work**.

---

## Roadmap

- **Evidence JSONL per product** — structured records from real engagements (kept separate from this repo; evidence belongs to each engagement, not the public runbook)
- **Signal-defense coverage audit** — systematic review of the 66×52 signal-defense matrix with the same mechanism-based rigor applied to evasion-defense connections
- **Link coverage** — find sources that support defense links for techniques and evasions that still have none
- **Catalog expansion** — new defenses, techniques, and evasions as the field evolves; new product mappings as vendors ship guardrails
- **Automated regression** — CI pipeline to run `build.py --validate` on every commit
- **Blind validation of the decision-triage guide** — test each branch of the triage tree with independent public cases (CTF/red-team write-ups, authorized engagements) and report coverage per branch

---

## Disclaimer

For **educational and authorized security testing only**. Always obtain proper authorization before testing any system.

---

## Credits

Created by **[Renato Braga](https://www.linkedin.com/in/renato-braga/)** — Base material for the course *"LLM Application Security - Pentest Edition (LLMAS-P)"*

Prompt injection taxonomy inspired by [Arcanum PI Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) (Jason Haddix, CC BY 4.0).
