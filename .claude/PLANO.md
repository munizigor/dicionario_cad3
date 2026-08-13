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
| Navegação | `br-menu push`, aberto por padrão no desktop |
| Alvo de acessibilidade | WCAG 2.2 A+AA (ABNT NBR 17225:2025) |

## Stories

### S0 — Registro do problema e do plano
- [x] `.claude/PROBLEMA.md` no formato A3, com cada necessidade rastreada à fonte
- [x] `.claude/PLANO.md` com as stories
- [x] ADR do conflito `docs/` (site) × documentação do projeto

### S1 — Verificador de conformidade (TDD)
> Como mantenedor, quero um verificador executável para saber se o site está aderente ao padrão sem
> depender de inspeção manual.
- [ ] `tools/verificar_conformidade.py` escrito **antes** da adequação, falhando
- [ ] Saída falhando registrada como evidência
- [ ] Critérios: lang/title/description/viewport · `br-skiplink` com 4 accesskeys · IDs obrigatórios
      (`#main-content`, `#header-navigation`, `#main-searchbox`, `#footer`) · componentes `br-*` ·
      assets locais · ausência de resíduos (`data-tema`, `.pular`, `.veu`) · `alt` em imagem,
      `aria-hidden` em ícone, `aria-label` em botão só-ícone · checklist do Padrão Mínimo

### S2 — Assets vendorizados
> Como órgão, quero os arquivos do DS no próprio repositório para não depender de CDN de terceiros.
- [ ] `tools/baixar_assets_ds.py` idempotente, só stdlib
- [ ] `core.min.css` e `core-init.min.js` do `@govbr-ds/core@3.7.0`
- [ ] Rawline (pesos usados) com os caminhos relativos corrigidos
- [ ] Font Awesome 5.11.2 (CSS + webfonts usados)
- [ ] Nenhuma referência remota no `index.html` além de barra gov.br e VLibras

### S3 — Template base do DS
> Como usuário de serviços gov.br, quero o cabeçalho, o menu e o rodapé que já conheço.
- [ ] `docs/index.html` reescrito em `template-base`
- [ ] `br-skiplink` com accesskeys 1–4 e os IDs de destino existentes
- [ ] `#conteudo` → `#main-content`, com `rotear()` ajustado
- [ ] Constantes do órgão marcadas com `TODO`

### S4 — CSS sobre os tokens do DS
> Como usuário, quero a paleta e a tipografia oficiais, sem perder a legibilidade da grade densa.
- [ ] `styles.css` reduzido a complemento do core
- [ ] Grade, selos PK/FK/NN e diagramas SVG reescritos sobre tokens do DS
- [ ] Tema escuro removido (commit separado)
- [ ] `@media print` e `prefers-reduced-motion` preservados
- [ ] Menu aberto por padrão a partir de 1280px, com o desvio comentado no CSS

### S5 — Componentes no app.js
> Como usuário, quero cards, botões, tags, breadcrumb e mensagens no padrão.
- [ ] `painel()` → `br-card` · `montarLateral()` → `menu-folder`/`menu-item`
- [ ] `paginaInicial()`, `paginaTabela()`, `paginaBusca()`, `paginaMapa()`, `paginaNaoEncontrada()`
- [ ] `tabelaColunas()` com `data-th`, mantendo ordenação e filtro próprios
- [ ] Glifos Unicode → Font Awesome, com `aria-hidden="true"`
- [ ] Toggle manual do menu e do tema removidos
- [ ] Atalho `/`, `Escape`, debounce de 220 ms e roteamento por hash preservados

### S6 — Elementos institucionais
> Como pessoa surda, quero acionar o VLibras; como cidadão, quero a barra do Governo Federal.
- [ ] `<barra-govbr>` isolada em bloco removível, com o risco documentado
- [ ] VLibras com o snippet do manual oficial (1 argumento)
- [ ] `br-footer` com assinatura do órgão, licença e proveniência dos dados

### S7 — Verificação e documentação
- [ ] `verificar_conformidade.py` verde, com saída colada como evidência
- [ ] Roteiro manual completo (rotas, exportações, responsivo, teclado)
- [ ] `README.md` atualizado (tema escuro sai, assets entram)
- [ ] `documentacao/` inicial + `documentacao/CHANGELOG.md`
- [ ] `.claude/CLAUDE.md` do projeto com a stack travada

## Definition of Done

Verificador verde · nenhuma regressão funcional no roteiro manual · `.claude/PLANO.md` e
`documentacao/` atualizados · aceite do Navegador.
