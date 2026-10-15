# LLM App RDA — Recon, Defesas e Ataques

<p align="center">
  <a href="https://rb1hdb.github.io/llm-app-rda/"><img src="https://img.shields.io/badge/Site%20ao%20vivo-llm--app--rda-9966CC?style=for-the-badge&logo=lightning&logoColor=white" alt="Site"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licen%C3%A7a-CC%20BY%204.0-2ea44f?style=for-the-badge&logo=creative-commons&logoColor=white" alt="Licenca"></a>
  <img src="https://img.shields.io/badge/vers%C3%A3o-0.1-1f6feb?style=for-the-badge&logo=git&logoColor=white" alt="Versao">
  <img src="https://img.shields.io/badge/uso-educacional%20%26%20autorizado-d73a4a?style=for-the-badge&logo=law&logoColor=white" alt="Uso">
</p>

<p align="center">
  <b>Idioma:</b> <a href="README.md">English</a> · <b>Portugues</b> · <a href="README-es.md">Espanol</a>
</p>

---

## O que e isto

Runbook interativo de pentest para aplicacoes baseadas em LLM. Metodologia estruturada para identificar, fingerprint e explorar defesas — organizado em tres fases:

| Fase | Conteudo |
|------|----------|
| **R — Recon** | 35 prompts black-box + 56 sinais observaveis |
| **D — Defesas** | 42 defesas catalogadas em 6 locais |
| **A — Ataques** | 50 tecnicas de prompt injection + 12 evasoes |

**Pipeline:** Sinal → Defesa@locus → Tecnica/Evasao

Diferente de colecoes de jailbreaks avulsos, cada entrada tem fontes rastreadas (primaria ou survey) e um pipeline reproduzivel.

---

## Catalogos

| Catalogo | Qtd | Descricao |
|----------|-----|-----------|
| **Recon** | 35 | Prompts black-box para identificar defesas sem conhecimento previo |
| **Sinais** | 56 | Heuristicas observaveis indicando defesas ativas |
| **Defesas** | 42 | Fichas com definicao, locus, fortalezas, fraquezas, aplicabilidade |
| **Tecnicas** | 50 | Tecnicas de ataque organizadas por turno e grupo |
| **Evasoes** | 12 | Transformacoes para escapar deteccao |
| **Produtos** | 14 | Ferramentas comerciais mapeadas para defesas que implementam |
| **Referencias** | 100 | Fontes (92 primarias + 8 surveys) |
| **Wiki** | 7 | Artigos conceituais sobre metodologia e decisoes de schema |
| **Taxonomia** | 1 | Arvore hierarquica de ataques |

---

## Inspiracao

A estrutura taxonomica de prompt injection e inspirada na [Arcanum Prompt Injection Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) de Jason Haddix (Arcanum Information Security).

O **workflow R-D-A** (pipeline Recon → Defesas → Ataques), as fichas com fontes rastreadas, o metodo de descoberta por sinais e a ligacao defesa-locus-ataque sao **trabalho original**.

---

## Como usar

### Via GitHub Pages (recomendado)

Abra **[rb1hdb.github.io/llm-app-rda/](https://rb1hdb.github.io/llm-app-rda/)** — pagina interativa single-file, sem servidor.

### Localmente

```bash
git clone https://github.com/rb1hdb/llm-app-rda.git
cd llm-app-rda
# abrir index.html no navegador
```

### Rebuild apos editar dados

```bash
python build-page/build.py
```

---

## Idiomas

PT, EN, ES — alternavel no header. Todos os textos de UI vem de `labels/{pt,en,es}.json`. Traducoes de dados das entidades ficam em `translations/{en,es}/`.

---

## Estrutura do repositorio

```
llm-app-rda/
├── index.html              <- Pagina interativa gerada
├── .nojekyll               <- Config GitHub Pages
├── LICENSE                 <- CC BY 4.0
├── README.md               <- Versao EN
├── README-pt.md            <- Este arquivo
├── data/                   <- Fonte da verdade (PT)
│   ├── defesas.json        <- 42 defesas
│   ├── sinais.json         <- 56 sinais
│   ├── tecnicas.json       <- 50 tecnicas
│   ├── evasoes.json        <- 12 evasoes
│   ├── recon.json          <- 35 prompts de recon
│   ├── produtos.json       <- 14 produtos
│   ├── referencias.json    <- 100 referencias
│   ├── wiki.json           <- 7 artigos
│   ├── taxonomia.json      <- Arvore taxonomica
│   └── schema.json         <- Schema de validacao
├── labels/                 <- Strings de UI (i18n)
│   ├── pt.json
│   ├── en.json
│   └── es.json
├── translations/           <- Traducoes de dados
│   ├── en/                 <- 8 arquivos traduzidos
│   └── es/                 <- 8 arquivos traduzidos
└── build-page/
    ├── template.html       <- Template HTML/JS
    ├── style.css           <- Estilos
    └── build.py            <- Validador + gerador
```

---

## Loci de defesa

Defesas sao classificadas por onde atuam no pipeline LLM:

| Locus | Qtd | Descricao |
|-------|-----|-----------|
| input | 8 | Filtros na entrada do usuario |
| output | 6 | Filtros na saida do modelo |
| prompt | 5 | Design do system prompt |
| modelo | 5 | Controles no nivel do modelo |
| acao | 14 | Gating de acoes/ferramentas |
| processo | 4 | Controles de processo |

---

## Status metodologico

Este runbook interativo (pipeline R-D-A) foi construido a partir de fontes ancora em seguranca de LLM (listadas em `data/referencias.json`). Cada entrada contem a fonte que suporta seu conteudo.

### Sobre relacoes N:N

As relacoes ligando sinais → defesas → tecnicas/evasoes foram geradas por **varredura automatizada por LLM** (nao humana). **Fora do escopo de auditoria**: sinais e mecanismos em isolamento, recon, referencias, wiki, taxonomia.

### Motor de selecao

Marque sinais/defesas para filtrar tecnicas/evasoes candidatas. A lista resultante e uma **shortlist para refinar**, nao um veredito — combine com o passo de teste discriminatorio (aba Metodo) antes de atribuir um bypass.

---

## Aviso

Para **fins educacionais e testes de seguranca autorizados apenas**. Sempre obtenha autorizacao adequada antes de testar qualquer sistema.

---

## Creditos

Criado por **[Renato Braga](https://www.linkedin.com/in/renato-braga/)** — Material base para o curso *"LLM Application Security - Pentest Edition (LLMAS-P)"*

Taxonomia de prompt injection inspirada na [Arcanum PI Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) (Jason Haddix, CC BY 4.0).
