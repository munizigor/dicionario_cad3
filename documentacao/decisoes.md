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

## ADR-003 — Assets vendorizados; o VLibras permanece remoto

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

A barra do Governo Federal acabou removida — ver ADR-007. O VLibras permanece como única dependência
remota.

---

## ADR-004 — A grade de colunas não recebe a classe `br-table`

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O DS oferece `br-table` com busca (`data-search`), seleção, colapso e paginação.

**Decisão.** A grade de colunas não recebe a classe `.br-table`. Mantém a implementação própria:
ordenação clicável com `aria-sort`, filtro incremental e cabeçalho sticky. A moldura visual vem do
`br-card` que a envolve.

**Justificativa.** Duas razões, uma de layout e outra de comportamento.

Layout: `CHAMADO` tem 92 colunas e `OCORRENCIA` tem 74. O modo responsivo da `br-table` empilha cada
linha em um bloco rotulado por `data-th` — legível numa tabela de 5 colunas, inutilizável nessa
escala.

Comportamento: o `core-init.min.js` instancia `BRTable` em **todo** elemento com a classe
`.br-table`, e o componente injeta header e footer próprios. Usar a classe apenas como moldura
visual, como se pretendia no plano original, não é possível — a instanciação vem junto e brigaria
com a ordenação e o filtro que já existem.

**Consequências.** Desvio consciente do padrão, restrito a um componente. Os `<td>` recebem `data-th`
mesmo assim, para que o rótulo da coluna esteja disponível a leitores de tela, e cada tabela tem um
`<caption class="sr-only">`.

---

## ADR-005 — O menu lateral fica aberto por padrão no desktop

**Data:** 2026-08-13 · **Status:** aceita

**Contexto.** O `br-menu` do DS nasce fechado e abre pelo botão do cabeçalho, em qualquer largura.

**Decisão.** Usar o `br-menu` no modo offcanvas padrão, **sem** o modificador `push`, e mantê-lo
aberto a partir de **992px** (`md`) por media query própria, escondendo o gatilho nessa faixa.

**Justificativa.** O menu é a navegação primária entre 71 tabelas. Com o comportamento nativo, cada
troca de tabela custaria dois cliques e uma reabertura — o uso principal do site ficaria penalizado.

O `push`, que seria o candidato natural, foi descartado: ele aplica `display:none` tanto ao
`menu-scrim` quanto ao `menu-header`, e essas regras não dependem de `.active`. No mobile isso
deixaria o menu aberto sem véu e sem botão de fechar — o usuário ficaria preso. Sem o `push`, o
mobile recebe o comportamento completo do DS (véu, fechar, controle de foco) e o desvio fica contido
numa media query de desktop.

O corte é 992px e não 1280px (`lg`) por causa da escala de tela do Windows, comum em notebooks: um
monitor de 1366px a 125% reporta 1092px CSS, e um de 1600px a 150% reporta 1067px. Com o corte em
1280 essas pessoas cairiam no offcanvas — exatamente o público que esta decisão quer atender.

**Consequências.**

As regras do desvio usam o `#main-navigation` como seletor, para vencer
`.br-menu.active .menu-container{position:fixed}` do core — que voltaria a valer se o usuário
abrisse o menu no mobile e depois alargasse a janela.

**O core não define largura alguma** para `.br-menu`, `.menu-container` ou `.menu-panel`. O painel só
ganha `flex:1` na regra `.br-menu.active .menu-panel`, e aqui o menu nunca fica `active` — quem o
abre é o CSS. Sem `flex:1` explícito, o painel vira `flex:0 1 auto` e encolhe até o conteúdo mínimo,
que foi o defeito observado na primeira abertura em navegador. Qualquer largura de menu no gov.br
3.7.0 tem que vir do CSS do projeto.

Entre 992 e 1279px o DS ainda mantém a busca do cabeçalho como overlay e os links de acesso rápido
como dropdown. Menu fixo com busca em overlay é uma inconsistência menor, aceita em troca do ganho de
navegação.

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

---

## ADR-007 — A barra do Governo Federal não é usada

**Data:** 2026-08-13 · **Status:** aceita · **Substitui** parte do ADR-003

**Contexto.** A barra do Governo Federal foi incluída na adequação inicial como elemento de
identidade institucional. Na primeira abertura em navegador ela apresentou um botão "Entrar" com
spinner girando indefinidamente, o que levou a uma análise do bundle — o componente não tem
documentação pública.

**Decisão.** Remover a `<barra-govbr>` do site.

**Justificativa.** O que a análise revelou pesa contra mantê-la num site institucional que precisa
ficar estável por anos:

- **Sem documentação, sem licença, sem versionamento declarado.** O componente não consta no
  gov.br/ds, na wiki do DS nem no npm. Todo o conhecimento sobre ele veio de engenharia reversa do
  bundle e do HTML do portal gov.br em produção. Não há contrato de estabilidade.
- **Comportamento-armadilha.** Sem a flag `no-login`, o botão de entrar trava em carregamento
  permanente: o estado de sessão nasce `undefined`, a flag de carregamento é literalmente
  `typeof sessão === "undefined"`, e não há timeout nem fallback. Um site público sem autenticação
  cai nesse estado por padrão.
- **API enganosa.** O atributo `class` não é estilo, é um saco de feature flags lido por
  `includes()`. E o `linksdosistema`, que aparece no HTML do portal gov.br em produção, **não
  existe** no componente — é ignorado em silêncio; o nome real é `menulinks`. Copiar o markup do
  portal, que é a única fonte disponível, produz configuração que não funciona.
- **Ela não é exigida.** A barra não está entre os oito itens do Padrão Mínimo. Cabeçalho com logo
  gov.br, rodapé, tipografia, paleta, botões, formulários, iconografia e responsividade continuam
  atendidos.

**Consequências.** O site perde os links institucionais do governo, o seletor de idioma e o toggle de
alto contraste que a barra oferecia. A acessibilidade não fica desamparada: o VLibras permanece, e o
alvo de WCAG 2.2 AA é atendido pelo próprio design system.

O VLibras passa a ser a **única** dependência remota do site.

Se a barra ganhar documentação e licença públicas, reverter é barato — o
`tools/verificar_conformidade.py` tem duas checagens que hoje garantem a ausência dela, e são o ponto
exato onde a decisão se inverte.
