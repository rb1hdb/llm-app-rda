# AGENTS.md — LLM App RDA

Regras únicas do projeto para qualquer harness. `CLAUDE.md` contém apenas `@AGENTS.md`: **toda regra mora aqui**, nunca em `CLAUDE.md`.

Runbook interativo de pentest para aplicações LLM (Recon → Defesas → Ataques).
Pipeline: **Sinal → Defesa@locus → Técnica/Evasão**. Guia de decisão (aba Triagem) na entrada.

## Estado do projeto
- Versão atual: **v0.3** (base), em **depuração e refinamento**. Tags: `v0.1-snapshot`, `v0.2-estavel`.
- A v0.3 acrescentou a Triagem: `data/triagem.json`, `data/clusters.json`, `data/sinais_estruturais.json`, com validação própria em `build.py`.
- Trabalho atual: corrigir e refinar o conteúdo e a interface existentes, sem expandir o escopo sem pedido.

## O que vai ao git (regra de exposição)
- **Só o produto é versionado e espelhado no remoto** (`origin`, GitHub Pages): `data/`, `labels/`, `translations/`, `build-page/`, `index.html`, `README*.md`, `LICENSE`, `.nojekyll`, `Bandeira-*.svg`, `.gitignore`, `AGENTS.md`, `CLAUDE.md`.
- **Evidências, logs, rascunhos e histórico não são expostos**: `arquivados/`, `evidencias/`, `prompts-and-logs/`, `tmp/`, `ROADMAP.md`, `.obsidian/`, `.claude/` ficam só locais e no `.gitignore`.
- Nenhum arquivo versionado (README, labels, dados) pode apontar para caminho ignorado.
- Antes de qualquer commit, conferir `git status` para garantir que nada fora do produto entrou.

## Restrições
- `data/` é a fonte da verdade (PT). `index.html` é **gerado** por `build-page/build.py`; nunca editar à mão.
- Mudar esquema (`data/schema.json`, campos dos JSON), `build.py`, `template.html`, `style.css` ou `labels/` é permitido na depuração, mas só quando o problema exigir. Descrever a mudança e rodar a validação em seguida.
- Alterou dado com tradução: atualizar `translations/{en,es}/` e `labels/` no mesmo ciclo, para manter PT/EN/ES coerentes.
- IDs (R## D## S## RECON- T## E## P## W##) não são renumerados. Remoção ou fusão deve ser registrada.
- Sem cruzamento com catálogos externos (ex.: Arcanum) como fonte; ele aparece só nos créditos do README.

## Regras de conteúdo
- Toda ficha tem fonte rastreada (primária, survey, operacional ou inferência documentada). Técnica/evasão sem fonte é reprovada.
- Só vale a fonte lida na hora; conhecimento do modelo não é evidência.
- Vínculo técnica/evasão→defesa (`bypass[]`) declara a base: `testado`, `alegado`, `inferencia` (exigem `fonte` da técnica e `nota`) ou `nao_auditado` (pendente de auditoria).
- Taxonomia: o ramo de técnicas é gerado de `tecnicas.json` (grupo → técnica → `variantes`); `translations/*/{tecnicas,evasoes,produtos,defesas,sinais,recon,wiki,triagem,clusters}.json` são overlays só com texto traduzido (cada item leva `pt_hash`; se o PT mudar, `--validate` reprova até retraduzir e rodar `python build-page/build.py --stamp-translations`). Estrutura vive só em `data/`.
- Fraquezas de defesa específicas (nomear a limitação), nunca genéricas.
- Recon é passivo; nenhum probe de recon é ataque.
- Idioma: PT (fonte); EN/ES por tradução. Prompts de recon e exemplos de ataque em EN.

## Estrutura
```
AGENTS.md  CLAUDE.md  README*.md  LICENSE  index.html
data/          catálogo (fonte da verdade, PT)
labels/        textos de UI pt/en/es
translations/  tradução dos dados en/es
build-page/    build.py, template.html, style.css
(local, ignorado) arquivados/ evidencias/ prompts-and-logs/ tmp/ ROADMAP.md
```

## Arquivados (fonte do passado)
`arquivados/` guarda `old/`, `old2/`, `_snapshot-v0.2/`, `SPEC.md`, `SPEC-v2.md` e `ETAPAS.md`. **Não são fonte da verdade** e não descrevem a v0.3. Consultar só quando o autor mencionar versões anteriores ou quando um ajuste exigir saber o que havia antes; nunca copiar dali sem reverificar contra `data/`.

## Roadmap
`ROADMAP.md` (local, ignorado) lista os próximos passos, inclusive os que citam arquivos internos. O Roadmap dos README é público: sem referências a arquivos internos. Ao mudar um, avaliar o outro.

## Comandos
```bash
python build-page/build.py --validate   # só valida
python build-page/build.py              # valida e gera index.html
python -m http.server 8080              # servir localmente (.claude/launch.json)
```
Avisos de "Orphan references" são esperados (referências sem ficha que as cite) e entram na depuração, não bloqueiam o build.

## Limites de autonomia
- Commits locais são autorizados direto na `main`, um por tarefa do backlog, sem pedir confirmação; o `index.html` é regenerado a cada tarefa para o autor testar. `push`, tags, apagar arquivos e reescrever histórico só por pedido explícito do autor, que roda o push.
- Nunca fazer `push` (nem sugerir como rotina). Ao concluir uma tarefa, apresentar ao autor o(s) comando(s) `git commit` já com a mensagem completa (`-m` e corpo), para ele conferir ou refazer o commit. Cada commit leva o comentário junto com o comando, não só o hash.
- Rodar `build.py --validate` após qualquer mudança em `data/`, `labels/`, `translations/` ou `build-page/`; regenerar `index.html` ao concluir.
- Dúvida de critério ou escopo: perguntar ao autor.
