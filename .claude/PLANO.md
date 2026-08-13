# Plano — Adequação ao Padrão Digital de Governo

Épico único. Iteração 1 entrega a fatia vertical completa: o site inteiro no padrão gov.br.

Referência: `.claude/PROBLEMA.md` · plano de execução detalhado em
`~/.claude/plans/preciso-colocar-o-sistema-binary-river.md`.

## Decisões travadas com o Navegador (13/08/2026)

| Decisão | Escolha |
|---|---|
| Nível | Padrão Mínimo + componentes `br-*`; CSS próprio só na grade densa e nos diagramas |
| Identidade | Institucional — logo gov.br, barra do Governo Federal, VLibras, assinatura do órgão |
| Órgão | Placeholder `TODO`, preenchido antes da publicação |
| Assets | Vendorizados em `docs/assets/` |
| Tema escuro | Removido |
| Navegação | `br-menu` offcanvas, fixado aberto por CSS a partir de 992px (ver ADR-005) |
| Alvo de acessibilidade | WCAG 2.2 A+AA (ABNT NBR 17225:2025) |

## Stories

### S0 — Registro do problema e do plano
- [x] `.claude/PROBLEMA.md` no formato A3, com cada necessidade rastreada à fonte
- [x] `.claude/PLANO.md` com as stories
- [x] ADR do conflito `docs/` (site) × documentação do projeto

### S1 — Verificador de conformidade (TDD)
> Como mantenedor, quero um verificador executável para saber se o site está aderente ao padrão sem
> depender de inspeção manual.
- [x] `tools/verificar_conformidade.py` escrito **antes** da adequação, falhando
- [x] Saída falhando registrada como evidência
- [x] Critérios: lang/title/description/viewport · `br-skiplink` com 4 accesskeys · IDs obrigatórios
      (`#main-content`, `#header-navigation`, `#main-searchbox`, `#footer`) · componentes `br-*` ·
      assets locais · ausência de resíduos (`data-tema`, `.pular`, `.veu`) · `alt` em imagem,
      `aria-hidden` em ícone, `aria-label` em botão só-ícone · checklist do Padrão Mínimo

### S2 — Assets vendorizados
> Como órgão, quero os arquivos do DS no próprio repositório para não depender de CDN de terceiros.
- [x] `tools/baixar_assets_ds.py` idempotente, só stdlib
- [x] `core.min.css` e `core-init.min.js` do `@govbr-ds/core@3.7.0`
- [x] Rawline (pesos usados) com os caminhos relativos corrigidos
- [x] Font Awesome 5.11.2 (CSS + webfonts usados)
- [x] Nenhuma referência remota no `index.html` além de barra gov.br e VLibras

### S3 — Template base do DS
> Como usuário de serviços gov.br, quero o cabeçalho, o menu e o rodapé que já conheço.
- [x] `docs/index.html` reescrito em `template-base`
- [x] `br-skiplink` com accesskeys 1–4 e os IDs de destino existentes
- [x] `#conteudo` → `#main-content`, com `rotear()` ajustado
- [x] Constantes do órgão marcadas com `TODO`

### S4 — CSS sobre os tokens do DS
> Como usuário, quero a paleta e a tipografia oficiais, sem perder a legibilidade da grade densa.
- [x] `styles.css` reduzido a complemento do core
- [x] Grade, selos PK/FK/NN e diagramas SVG reescritos sobre tokens do DS
- [x] Tema escuro removido (commit separado)
- [x] `@media print` e `prefers-reduced-motion` preservados
- [x] Menu aberto por padrão a partir de 992px, com o desvio comentado no CSS

### S5 — Componentes no app.js
> Como usuário, quero cards, botões, tags, breadcrumb e mensagens no padrão.
- [x] `painel()` → `br-card` · `montarLateral()` → `menu-folder`/`menu-item`
- [x] `paginaInicial()`, `paginaTabela()`, `paginaBusca()`, `paginaMapa()`, `paginaNaoEncontrada()`
- [x] `tabelaColunas()` com `data-th`, mantendo ordenação e filtro próprios
- [x] Glifos Unicode → Font Awesome, com `aria-hidden="true"`
- [x] Toggle manual do menu e do tema removidos
- [x] Atalho `/`, `Escape`, debounce de 220 ms e roteamento por hash preservados

### S6 — Elementos institucionais
> Como pessoa surda, quero acionar o VLibras; como cidadão, quero a barra do Governo Federal.
- [x] `<barra-govbr>` isolada em bloco removível, com o risco documentado
- [x] VLibras com o snippet do manual oficial (1 argumento)
- [x] `br-footer` com assinatura do órgão, licença e proveniência dos dados

### S7 — Verificação e documentação
- [x] `verificar_conformidade.py` verde (73/73), com saída colada como evidência
- [x] Sintaxe do `app.js` validada (compila; erro apenas de runtime por falta de `window`)
- [x] `README.md` atualizado (tema escuro sai, assets e conformidade entram)
- [x] `documentacao/` inicial + `documentacao/CHANGELOG.md`
- [x] `.claude/CLAUDE.md` do projeto com a stack travada
- [ ] **Roteiro manual em navegador — pendente com o Navegador** (ver abaixo)

## Pendente: verificação visual

Não há navegador disponível no ambiente onde a implementação foi feita, então tudo que depende de
renderização continua por conferir. Roteiro proposto, com `python -m http.server -d docs 8000`:

1. **Rotas:** home · `ACOES_ATENDENTE` (tabela pequena) · `CHAMADO` (92 colunas) · busca com e sem
   acento (`ocorrencia` deve achar `Ocorrência`) · deep link
   `#/tabela/OCORRENCIA?col=ID_OCORRENCIA` · `#/mapa` com zoom, arrasto e destaque de vizinhança ·
   rota inválida.
2. **Menu:** aberto e fixo acima de 992px; offcanvas com véu e botão de fechar abaixo disso;
   filtro incremental atualizando o contador; item da tabela atual destacado.
3. **Exportações:** DDL, JSON, CSV (abrir no Excel para conferir o BOM) e Mermaid de uma tabela;
   DDL e JSON completos na home.
4. **Responsivo:** 360 · 991 · 992 · 1279 · 1280 · 1600px.
5. **Teclado:** Tab desde o topo, os quatro `accesskey`, `/` para focar a busca, `Escape`,
   ordenação da grade anunciando `aria-sort`.
6. **Institucional:** barra do Governo Federal carregando e botão do VLibras aparecendo.
7. **Sem rede:** DevTools em offline — só a barra e o VLibras devem sumir.
8. **Acessibilidade:** axe DevTools ou Pa11y contra WCAG 2.2 AA.

## Definition of Done

Verificador verde · roteiro manual sem regressão · `.claude/PLANO.md` e `documentacao/` atualizados ·
aceite do Navegador.
