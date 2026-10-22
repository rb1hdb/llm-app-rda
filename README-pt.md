# LLM App RDA — Recon, Defesas e Ataques

<p align="center">
  <a href="https://rb1hdb.github.io/llm-app-rda/"><img src="https://img.shields.io/badge/Site%20ao%20vivo-llm--app--rda-9966CC?style=for-the-badge&logo=lightning&logoColor=white" alt="Site"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licen%C3%A7a-CC%20BY%204.0-2ea44f?style=for-the-badge&logo=creative-commons&logoColor=white" alt="Licença"></a>
  <img src="https://img.shields.io/badge/vers%C3%A3o-0.2-1f6feb?style=for-the-badge&logo=git&logoColor=white" alt="Versão">
  <img src="https://img.shields.io/badge/uso-educacional%20%26%20autorizado-d73a4a?style=for-the-badge&logo=law&logoColor=white" alt="Uso">
</p>

<p align="center">
  <b>Idioma:</b> <a href="README.md">English</a> · <b>Português</b> · <a href="README-es.md">Español</a>
</p>

---

## O que é isto

Runbook interativo de pentest para aplicações baseadas em LLM. Metodologia estruturada para identificar, fingerprint e explorar defesas — organizado em três fases:

| Fase | Conteúdo |
|------|----------|
| **R — Recon** | 36 prompts black-box + 66 sinais observáveis |
| **D — Defesas** | 52 defesas catalogadas em 6 loci |
| **A — Ataques** | 50 técnicas de prompt injection + 12 evasões |

**Pipeline:** Sinal → Defesa@locus → Técnica/Evasão

Diferente de coleções de jailbreaks avulsos, cada entrada tem fontes rastreadas (primária, survey ou operacional) e um pipeline reproduzível.

---

## Catálogos

| Catálogo | Qtd | Descrição |
|----------|-----|-----------|
| **Recon** | 36 | Prompts black-box para identificar defesas sem conhecimento prévio |
| **Sinais** | 66 | Heurísticas observáveis indicando defesas ativas |
| **Defesas** | 52 | Fichas com definição, locus, fortalezas, fraquezas, aplicabilidade |
| **Técnicas** | 50 | Técnicas de ataque organizadas por turno e grupo |
| **Evasões** | 12 | Transformações para escapar detecção |
| **Produtos** | 14 | Ferramentas comerciais mapeadas para defesas que implementam |
| **Referências** | 231 | Fontes (224 primárias + 4 surveys + 3 operacionais) |
| **Wiki** | 7 | Artigos conceituais sobre metodologia e decisões de schema |
| **Taxonomia** | 1 | Árvore hierárquica de ataques |

---

## Como usar

### Via GitHub Pages (recomendado)

Abra **[rb1hdb.github.io/llm-app-rda/](https://rb1hdb.github.io/llm-app-rda/)** — página interativa single-file, sem servidor.

### Localmente

```bash
git clone https://github.com/rb1hdb/llm-app-rda.git
cd llm-app-rda
# abrir index.html no navegador
```

### Rebuild após editar dados

```bash
python build-page/build.py            # gerar index.html
python build-page/build.py --validate # validar integridade apenas
```

---

## Idiomas

PT, EN, ES — alternável no header. Todos os textos de UI vêm de `labels/{pt,en,es}.json`. Traduções de dados das entidades ficam em `translations/{en,es}/`.

---

## Estrutura do repositório

```
llm-app-rda/
├── index.html              <- Página interativa gerada
├── .nojekyll               <- Config GitHub Pages
├── LICENSE                 <- CC BY 4.0
├── README.md               <- README (EN)
├── README-pt.md            <- Este arquivo (PT)
├── README-es.md            <- README (ES)
├── data/                   <- Fonte da verdade (PT)
│   ├── defesas.json        <- 52 defesas
│   ├── sinais.json         <- 66 sinais
│   ├── tecnicas.json       <- 50 técnicas
│   ├── evasoes.json        <- 12 evasões
│   ├── recon.json          <- 36 prompts de recon
│   ├── produtos.json       <- 14 produtos
│   ├── referencias.json    <- 231 referências
│   ├── wiki.json           <- 7 artigos
│   ├── taxonomia.json      <- Árvore taxonômica
│   └── schema.json         <- Schema de validação
├── labels/                 <- Strings de UI (i18n)
│   ├── pt.json
│   ├── en.json
│   └── es.json
├── translations/           <- Traduções de dados
│   ├── en/                 <- Arquivos traduzidos
│   └── es/                 <- Arquivos traduzidos
└── build-page/
    ├── template.html       <- Template HTML/JS
    ├── style.css           <- Estilos
    └── build.py            <- Validador + gerador
```

---

## Loci de defesa

Defesas são classificadas por onde atuam no pipeline LLM:

| Locus | Qtd | Descrição |
|-------|-----|-----------|
| input | 9 | Filtros na entrada do usuário |
| output | 6 | Filtros na saída do modelo |
| prompt | 7 | Design do system prompt |
| modelo | 6 | Controles no nível do modelo |
| ação | 20 | Gating de ações/ferramentas |
| processo | 4 | Controles de processo |

---

## Metodologia

Este runbook interativo (pipeline R-D-A) foi construído a partir de fontes âncora em segurança de LLM (listadas em `data/referencias.json`).

**Hierarquia de fontes:** cada entrada carrega o tipo da fonte — *primária* (evidência textual direta), *survey* (revisão sistemática), *operacional* (documentação de ferramenta) ou *inferência* (inferência lógica, sempre documentada com racional).

### Sobre relações N:N

As relações ligando sinais → defesas → técnicas/evasões foram geradas por **varredura automatizada por LLM** (não curadas manualmente uma a uma). Uma auditoria subsequente corrigiu conexões defesa-evasão com base em análise de mecanismo de detecção (regex/lexical, classificador treinado, LLM judge, semântico/embedding, estrutural, processo). **Fora do escopo de auditoria**: sinais e mecanismos em isolamento, recon, referências, wiki, taxonomia.

### Motor de seleção

Marque sinais/defesas para filtrar técnicas/evasões candidatas. A lista resultante é uma **shortlist para refinar**, não um veredito — combine com o passo de teste discriminatório (aba Método) antes de atribuir um bypass.

---

## Inspiração

A estrutura taxonômica de prompt injection é inspirada na [Arcanum Prompt Injection Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) de Jason Haddix (Arcanum Information Security).

O **workflow R-D-A** (pipeline Recon → Defesas → Ataques), as fichas com fontes rastreadas, o método de descoberta por sinais e a ligação defesa-locus-ataque são **trabalho original**.

---

## Roadmap

- **Evidence JSONL por produto** — registros estruturados de engajamentos reais (mantidos separados deste repo; evidências pertencem a cada engajamento, não ao runbook público)
- **Auditoria de cobertura sinal-defesa** — revisão sistemática da matriz 66×52 com o mesmo rigor de mecanismo aplicado às conexões evasão-defesa
- **Auditoria de conexões técnica-defesa** — validar a matriz 50×52 contra mecanismos de detecção
- **Expansão de catálogos** — novas defesas, técnicas e evasões conforme o campo evolui; novos mapeamentos de produtos conforme vendors lançam guardrails
- **Regressão automatizada** — pipeline CI para rodar `build.py --validate` em cada commit

---

## Aviso

Para **fins educacionais e testes de segurança autorizados apenas**. Sempre obtenha autorização adequada antes de testar qualquer sistema.

---

## Créditos

Criado por **[Renato Braga](https://www.linkedin.com/in/renato-braga/)** — Material base para o curso *"LLM Application Security - Pentest Edition (LLMAS-P)"*

Taxonomia de prompt injection inspirada na [Arcanum PI Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy/) (Jason Haddix, CC BY 4.0).
