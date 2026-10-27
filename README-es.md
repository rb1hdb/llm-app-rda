# LLM App RDA — Recon, Defensas y Ataques

<p align="center">
  <a href="https://rb1hdb.github.io/llm-app-rda/"><img src="https://img.shields.io/badge/Sitio%20en%20vivo-llm--app--rda-9966CC?style=for-the-badge&logo=lightning&logoColor=white" alt="Sitio"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licencia-CC%20BY%204.0-2ea44f?style=for-the-badge&logo=creative-commons&logoColor=white" alt="Licencia"></a>
  <img src="https://img.shields.io/badge/versi%C3%B3n-0.3-1f6feb?style=for-the-badge&logo=git&logoColor=white" alt="Versión">
  <img src="https://img.shields.io/badge/uso-educativo%20%26%20autorizado-d73a4a?style=for-the-badge&logo=law&logoColor=white" alt="Uso">
</p>

<p align="center">
  <b>Idioma:</b> <a href="README.md">English</a> · <a href="README-pt.md">Português</a> · <b>Español</b>
</p>

---

## Qué es esto

Runbook interactivo de pentest para aplicaciones basadas en LLM. Metodología estructurada para identificar, fingerprint y explotar defensas — organizado en tres fases:

| Fase | Contenido |
|------|-----------|
| **R — Recon** | 37 prompts black-box + 66 señales observables |
| **D — Defensas** | 52 defensas catalogadas en 6 loci |
| **A — Ataques** | 52 técnicas de prompt injection + 12 evasiones |

**Pipeline:** Señal → Defensa@locus → Técnica/Evasión

La pestaña **Triaje** abre la página con una guía de decisión: pocas preguntas observables acotan los clusters de defensa probables antes del flujo completo Recon → Señales → Defensas.

A diferencia de colecciones de jailbreaks sueltos, cada entrada tiene fuentes rastreadas (primaria, survey u operacional) y un pipeline reproducible.

---

## Catálogos

| Catálogo | Cant | Descripción |
|----------|------|-------------|
| **Recon** | 37 | Prompts black-box para identificar defensas sin conocimiento previo |
| **Señales** | 66 | Heurísticas observables indicando defensas activas |
| **Defensas** | 52 | Fichas con definición, locus, fortalezas, debilidades, aplicabilidad |
| **Técnicas** | 52 | Técnicas de ataque organizadas por turno y grupo |
| **Evasiones** | 12 | Transformaciones para escapar detección |
| **Productos** | 14 | Herramientas comerciales mapeadas a defensas que implementan |
| **Referencias** | 143 | Fuentes (134 primarias + 6 surveys + 3 operacionales) |
| **Wiki** | 8 | Artículos conceptuales sobre metodología y decisiones de schema |
| **Taxonomía** | 1 | Árbol jerárquico de ataques |
| **Triaje** | 6 | Guía de decisión que mapea observaciones a clusters de defensa |

---

## Cómo usar

### Vía GitHub Pages (recomendado)

Abra **[rb1hdb.github.io/llm-app-rda/](https://rb1hdb.github.io/llm-app-rda/)** — página interactiva single-file, sin servidor.

### Localmente

```bash
git clone https://github.com/rb1hdb/llm-app-rda.git
cd llm-app-rda
# abrir index.html en el navegador
```

### Rebuild después de editar datos

```bash
python build-page/build.py            # generar index.html
python build-page/build.py --validate # validar integridad solamente
```

---

## Idiomas

PT, EN, ES — alternables en el header. Todos los textos de UI vienen de `labels/{pt,en,es}.json`. Traducciones de datos de entidades en `translations/{en,es}/`.

---

## Estructura del repositorio

```
llm-app-rda/
├── index.html              <- Página interactiva generada
├── .nojekyll               <- Config GitHub Pages
├── LICENSE                 <- CC BY 4.0
├── README.md               <- README (EN)
├── README-pt.md            <- README (PT)
├── README-es.md            <- Este archivo (ES)
├── data/                   <- Fuente de verdad (PT)
│   ├── defesas.json        <- 52 defensas
│   ├── sinais.json         <- 66 señales
│   ├── tecnicas.json       <- 52 técnicas
│   ├── evasoes.json        <- 12 evasiones
│   ├── recon.json          <- 37 prompts de recon
│   ├── produtos.json       <- 14 productos
│   ├── referencias.json    <- 143 referencias
│   ├── wiki.json           <- 8 artículos
│   ├── taxonomia.json      <- Árbol taxonómico
│   ├── triagem.json        <- Árbol de triaje (preguntas → clusters)
│   ├── clusters.json       <- Mapa defensa → cluster
│   ├── sinais_estruturais.json <- Señales estructurales → técnicas
│   └── schema.json         <- Schema de validación
├── labels/                 <- Strings de UI (i18n)
│   ├── pt.json
│   ├── en.json
│   └── es.json
├── translations/           <- Traducciones de datos
│   ├── en/                 <- Archivos traducidos
│   └── es/                 <- Archivos traducidos
└── build-page/
    ├── template.html       <- Template HTML/JS
    ├── style.css           <- Estilos
    └── build.py            <- Validador + generador
```

---

## Locus de defensa

Las defensas se clasifican por dónde actúan en el pipeline LLM:

| Locus | Cant | Descripción |
|-------|------|-------------|
| input | 9 | Filtros en la entrada del usuario |
| output | 6 | Filtros en la salida del modelo |
| prompt | 7 | Diseño del system prompt |
| modelo | 6 | Controles a nivel de modelo |
| acción | 20 | Gating de acciones/herramientas |
| proceso | 4 | Controles de proceso |

---

## Metodología

Este runbook interactivo (pipeline R-D-A) fue construido a partir de fuentes ancla en seguridad de LLM (listadas en `data/referencias.json`).

**Jerarquía de fuentes:** cada entrada porta el tipo de fuente — *primaria* (evidencia textual directa), *survey* (revisión sistemática), *operacional* (documentación de herramienta) o *inferencia* (inferencia lógica, siempre documentada con racional).

### Sobre relaciones N:N

Las relaciones vinculando señales → defensas → técnicas/evasiones fueron generadas por **barrido automatizado por LLM** (no curadas manualmente una a una). Una auditoría subsecuente corrigió conexiones defensa-evasión basándose en análisis de mecanismo de detección (regex/lexical, clasificador entrenado, LLM judge, semántico/embedding, estructural, proceso). Los vínculos técnica/evasión → defensa fueron luego auditados contra las fuentes: cada vínculo conserva solo una base leída (probado, alegado por la fuente o inferencia documentada); los vínculos sin evidencia se eliminaron, por lo que algunas técnicas aún aparecen sin vínculo con una defensa. Las fuentes de las técnicas también traen estado de verificación y enlace directo a la página o al payload exacto. **Fuera del alcance de auditoría**: señales y mecanismos en aislamiento, recon, wiki, taxonomía.

### Motor de selección

Marque señales/defensas para filtrar técnicas/evasiones candidatas. La lista resultante es una **shortlist para refinar**, no un veredicto — combínela con el paso de prueba discriminatoria (pestaña Método) antes de atribuir un bypass.

---

## Inspiración

La estructura taxonómica de prompt injection está inspirada en la [Arcanum Prompt Injection Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) de Jason Haddix (Arcanum Information Security).

El **workflow R-D-A** (pipeline Recon → Defensas → Ataques), las fichas con fuentes rastreadas, el método de descubrimiento por señales y el enlace defensa-locus-ataque son **trabajo original**.

---

## Roadmap

- **Evidence JSONL por producto** — registros estructurados de engagements reales (mantenidos separados de este repo; evidencias pertenecen a cada engagement, no al runbook público)
- **Auditoría de cobertura señal-defensa** — revisión sistemática de la matriz 66×52 con el mismo rigor de mecanismo aplicado a las conexiones evasión-defensa
- **Cobertura de vínculos** — encontrar fuentes que respalden vínculos con defensas para técnicas y evasiones que aún no tienen ninguno
- **Expansión de catálogos** — nuevas defensas, técnicas y evasiones conforme el campo evoluciona; nuevos mapeos de productos conforme vendors lanzan guardrails
- **Regresión automatizada** — pipeline CI para ejecutar `build.py --validate` en cada commit
- **Validación ciega de la guía de decisión (triaje)** — probar cada rama del árbol de triaje con casos públicos independientes (write-ups de CTF/red team, engagements autorizados) y reportar la cobertura por rama

---

## Aviso

Para **fines educativos y pruebas de seguridad autorizadas solamente**. Siempre obtenga autorización adecuada antes de probar cualquier sistema.

---

## Créditos

Creado por **[Renato Braga](https://www.linkedin.com/in/renato-braga/)** — Material base para el curso *"LLM Application Security - Pentest Edition (LLMAS-P)"*

Taxonomía de prompt injection inspirada en [Arcanum PI Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) (Jason Haddix, CC BY 4.0).
