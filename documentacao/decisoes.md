# Decisões técnicas (ADRs)

Registros curtos das decisões que não são óbvias a partir do código.

---

## ADR-001 — A documentação do projeto vive em `documentacao/`, não em `docs/`

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O ciclo de trabalho adotado pede a documentação do sistema em `./docs/` como markdown.
Neste repositório, porém, `docs/` **é a raiz publicada do GitHub Pages** (Settings → Pages → Deploy
from a branch → `/docs`). Qualquer `.md` colocado lá vira conteúdo servido do site, misturando
documentação interna com a aplicação pública.

**Decisão.** `docs/` permanece exclusivamente o site. A documentação do projeto fica em
`documentacao/` na raiz: `processo-negocio.md`, `arquitetura.md`, `decisoes.md` (este arquivo) e
`CHANGELOG.md`.

**Consequências.** Divergência deliberada da convenção do ciclo, restrita a este repositório. Quem
procurar documentação em `docs/` não vai achar — daí o apontamento no `README.md`.

---

## ADR-002 — Design system consumido via `core` + `core-init`, não via web components

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O gov.br DS oferece dois caminhos: o CSS/JS do `@govbr-ds/core` com classes `.br-*`, ou
a biblioteca `@govbr-ds/webcomponents` com custom elements. A documentação oficial recomenda os web
components para "projetos modernos".

**Decisão.** Usar `@govbr-ds/core@3.7.0` (`core.min.css` + `core-init.min.js`).

**Justificativa.** (a) O `core.min.css` é necessário nos dois cenários — os web components trazem só
os componentes, não o grid, o espaçamento nem as cores. (b) Os web components tiveram major novo em
23/07/2026 e publicaram três vezes em agosto; superfície de API instável para um site que deve ficar
estável por anos. (c) Sem Shadow DOM, o CSS próprio da grade densa e dos diagramas SVG customiza
livremente. (d) `core-init.min.js` instancia todos os componentes sozinho, eliminando o boilerplate
que era o principal atrito dessa rota.

**Consequências.** O core 3.7.0 está congelado desde nov/2025 (a v4 segue em `next`). Para um
dicionário de dados estático isso é estabilidade, não estagnação. Se um dia a v4 sair, a migração é
um trabalho de CSS, não de arquitetura.

---

## ADR-003 — Assets vendorizados; barra gov.br e VLibras permanecem remotos

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O site funcionava 100% offline, inclusive por `file://`, porque os dados são embutidos
em `docs/dados.js` e não havia nenhuma requisição de rede.

**Decisão.** CSS, JS, fontes Rawline e Font Awesome são baixados para `docs/assets/` por
`tools/baixar_assets_ds.py`. A barra do Governo Federal e o VLibras continuam sendo carregados dos
serviços oficiais.

**Justificativa.** Vendorizar é o que a própria documentação do DS recomenda ("evite o CDN, baixe os
arquivos localmente") e imuniza o site contra indisponibilidade de terceiros. Barra e VLibras, por
outro lado, são **serviços vivos**: têm backend, avatares, tradução e atualização contínua — copiar
um snapshot seria congelar um serviço que deve evoluir.

**Consequências.** O repositório cresce ~1,3 MB. O site deixa de funcionar 100% offline: sem rede,
some a barra e some o widget do VLibras. Todo o resto — dados, busca, filtros, diagramas,
exportações — continua funcionando, porque não há `fetch` em lugar nenhum.

---

## ADR-004 — A grade de colunas não usa `br-table` como componente funcional

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O DS oferece `br-table` com busca (`data-search`), seleção, colapso e paginação.

**Decisão.** Usar `.br-table` apenas como moldura visual. A grade de colunas mantém a implementação
própria: ordenação clicável com `aria-sort`, filtro incremental e cabeçalho sticky.

**Justificativa.** `CHAMADO` tem 92 colunas e `OCORRENCIA` tem 74. O layout responsivo da `br-table`
empilha cada linha em um bloco rotulado por `data-th` — legível para uma tabela de 5 colunas,
inutilizável nessa escala. Além disso, `data-search` e `br-pagination` colidiriam com o filtro e a
ordenação que já existem e funcionam.

**Consequências.** Desvio consciente do padrão, restrito a um componente. Os `<td>` recebem `data-th`
mesmo assim, para que o rótulo esteja disponível a leitores de tela.

---

## ADR-005 — O menu lateral fica aberto por padrão no desktop

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O `br-menu` do DS nasce fechado e abre pelo botão do cabeçalho, em qualquer largura.

**Decisão.** Usar o markup `br-menu push` do padrão, com uma media query própria que o mantém aberto
a partir de 1280px (`lg`), escondendo o gatilho nessa faixa.

**Justificativa.** O menu é a navegação primária entre 71 tabelas. Com o comportamento nativo, cada
troca de tabela custaria dois cliques e uma reabertura — o uso principal do site ficaria penalizado.

**Consequências.** Desvio documentado do comportamento nativo, só em CSS. No mobile o comportamento é
o padrão do DS (offcanvas com scrim).

---

## ADR-006 — Tema escuro removido

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O site tinha alternância claro/escuro com preferência salva em `localStorage` e
fallback para `prefers-color-scheme`.

**Decisão.** Remover.

**Justificativa.** O gov.br DS 3.7.0 não tem dark mode global — não há `prefers-color-scheme` nem
`[data-theme]` no core, apenas modificadores por componente (`.dark-mode`, `.inverted`). Manter o
tema exigiria sobrescrever centenas de tokens do DS, criando uma paleta paralela não oficial. O
Padrão Mínimo pede paleta oficial aplicada por função.

**Consequências.** Perda de funcionalidade existente, decidida pelo Navegador. Se o DS v4 trouxer
dark mode nativo, reintroduzir passa a ser trivial.
