# LLM App RDA — Recon, Defensas y Ataques

<p align="center">
  <a href="https://rb1hdb.github.io/llm-app-rda/"><img src="https://img.shields.io/badge/Sitio%20en%20vivo-llm--app--rda-9966CC?style=for-the-badge&logo=lightning&logoColor=white" alt="Sitio"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licencia-CC%20BY%204.0-2ea44f?style=for-the-badge&logo=creative-commons&logoColor=white" alt="Licencia"></a>
  <img src="https://img.shields.io/badge/versi%C3%B3n-0.1-1f6feb?style=for-the-badge&logo=git&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/uso-educativo%20%26%20autorizado-d73a4a?style=for-the-badge&logo=law&logoColor=white" alt="Uso">
</p>

<p align="center">
  <b>Idioma:</b> <a href="README.md">English</a> · <a href="README-pt.md">Portugues</a> · <b>Espanol</b>
</p>

---

## Que es esto

Runbook interactivo de pentest para aplicaciones basadas en LLM. Metodologia estructurada para identificar, fingerprint y explotar defensas — organizado en tres fases:

| Fase | Contenido |
|------|-----------|
| **R — Recon** | 35 prompts black-box + 56 senales observables |
| **D — Defensas** | 42 defensas catalogadas en 6 locales |
| **A — Ataques** | 50 tecnicas de prompt injection + 12 evasiones |

**Pipeline:** Senal → Defensa@locus → Tecnica/Evasion

A diferencia de colecciones de jailbreaks sueltos, cada entrada tiene fuentes rastreadas (primaria o survey) y un pipeline reproducible.

---

## Catalogos

| Catalogo | Cant | Descripcion |
|----------|------|-------------|
| **Recon** | 35 | Prompts black-box para identificar defensas sin conocimiento previo |
| **Senales** | 56 | Heuristicas observables indicando defensas activas |
| **Defensas** | 42 | Fichas con definicion, locus, fortalezas, debilidades, aplicabilidad |
| **Tecnicas** | 50 | Tecnicas de ataque organizadas por turno y grupo |
| **Evasiones** | 12 | Transformaciones para escapar deteccion |
| **Productos** | 14 | Herramientas comerciales mapeadas a defensas que implementan |
| **Referencias** | 100 | Fuentes (92 primarias + 8 surveys) |
| **Wiki** | 7 | Articulos conceptuales sobre metodologia y decisiones de schema |
| **Taxonomia** | 1 | Arbol jerarquico de ataques |

---

## Inspiracion

La estructura taxonomica de prompt injection esta inspirada en la [Arcanum Prompt Injection Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) de Jason Haddix (Arcanum Information Security).

El **workflow R-D-A** (pipeline Recon → Defensas → Ataques), las fichas con fuentes rastreadas, el metodo de descubrimiento por senales y el enlace defensa-locus-ataque son **trabajo original**.

---

## Como usar

### Via GitHub Pages (recomendado)

Abra **[rb1hdb.github.io/llm-app-rda/](https://rb1hdb.github.io/llm-app-rda/)** — pagina interactiva single-file, sin servidor.

### Localmente

```bash
git clone https://github.com/rb1hdb/llm-app-rda.git
cd llm-app-rda
# abrir index.html en el navegador
```

### Rebuild despues de editar datos

```bash
python build-page/build.py
```

---

## Idiomas

PT, EN, ES — alternables en el header. Todos los textos de UI vienen de `labels/{pt,en,es}.json`. Traducciones de datos de entidades en `translations/{en,es}/`.

---

## Estructura del repositorio

```
llm-app-rda/
├── index.html              <- Pagina interactiva generada
├── .nojekyll               <- Config GitHub Pages
├── LICENSE                 <- CC BY 4.0
├── README.md               <- Version EN
├── README-es.md            <- Este archivo
├── data/                   <- Fuente de verdad (PT)
│   ├── defesas.json        <- 42 defensas
│   ├── sinais.json         <- 56 senales
│   ├── tecnicas.json       <- 50 tecnicas
│   ├── evasoes.json        <- 12 evasiones
│   ├── recon.json          <- 35 prompts de recon
│   ├── produtos.json       <- 14 productos
│   ├── referencias.json    <- 100 referencias
│   ├── wiki.json           <- 7 articulos
│   ├── taxonomia.json      <- Arbol taxonomico
│   └── schema.json         <- Schema de validacion
├── labels/                 <- Strings de UI (i18n)
│   ├── pt.json
│   ├── en.json
│   └── es.json
├── translations/           <- Traducciones de datos
│   ├── en/                 <- 8 archivos traducidos
│   └── es/                 <- 8 archivos traducidos
└── build-page/
    ├── template.html       <- Template HTML/JS
    ├── style.css           <- Estilos
    └── build.py            <- Validador + generador
```

---

## Loci de defensa

Las defensas se clasifican por donde actuan en el pipeline LLM:

| Locus | Cant | Descripcion |
|-------|------|-------------|
| input | 8 | Filtros en la entrada del usuario |
| output | 6 | Filtros en la salida del modelo |
| prompt | 5 | Diseno del system prompt |
| modelo | 5 | Controles a nivel de modelo |
| acao | 14 | Gating de acciones/herramientas |
| processo | 4 | Controles de proceso |

---

## Estado metodologico

Este runbook interactivo (pipeline R-D-A) fue construido a partir de fuentes ancla en seguridad de LLM (listadas en `data/referencias.json`). Cada entrada contiene la fuente que soporta su contenido.

### Sobre relaciones N:N

Las relaciones vinculando senales → defensas → tecnicas/evasiones fueron generadas por **barrido automatizado por LLM** (no humano). **Fuera del alcance de auditoria**: senales y mecanismos en aislamiento, recon, referencias, wiki, taxonomia.

### Motor de seleccion

Marque senales/defensas para filtrar tecnicas/evasiones candidatas. La lista resultante es una **shortlist para refinar**, no un veredicto — combinela con el paso de prueba discriminatoria (pestana Metodo) antes de atribuir un bypass.

---

## Aviso

Para **fines educativos y pruebas de seguridad autorizadas solamente**. Siempre obtenga autorizacion adecuada antes de probar cualquier sistema.

---

## Creditos

Creado por **[Renato Braga](https://www.linkedin.com/in/renato-braga/)** — Material base para el curso *"LLM Application Security - Pentest Edition (LLMAS-P)"*

Taxonomía de prompt injection inspirada en [Arcanum PI Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) (Jason Haddix, CC BY 4.0).
