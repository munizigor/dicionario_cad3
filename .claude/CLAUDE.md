# CLAUDE.md — Dicionário de Dados SINESP CAD

Especializa o CLAUDE.md global. Site estático de dicionário de dados, aderente ao Padrão Digital de
Governo, servido pelo GitHub Pages a partir de `docs/`. Publica dois schemas: `CAD_OCORRENCIA`
(SINESP CAD 3) e `CAD_RECURSOS` (SINESP CAD 2).

## Stack travada

Sem alternativas. Desvios exigem justificativa técnica e decisão do Navegador.

- **Design system:** `@govbr-ds/core` **3.7.0** (`core.min.css` + `core-init.min.js`), vendorizado.
  **Não** usar core 4.x nem `@govbr-ds/webcomponents`.
- **Tipografia:** Rawline, pesos 300–700. **Iconografia:** Font Awesome **5.11.2** (não 6).
- **JavaScript:** ES5 puro, IIFE, sem framework, sem bundler, sem transpilação.
- **Python:** 3, stdlib; `pdfplumber` só no extrator.
- **Sem build.** Sem `package.json`, sem npm, sem node_modules.

## Comandos

```sh
python tools/verificar_conformidade.py          # testes — 84 checagens, sai 1 se falhar
python -m http.server -d docs 8000              # rodar — http://localhost:8000
python tools/baixar_assets_ds.py                # atualizar assets do DS
python tools/extrair_pdf.py                     # regerar o CAD_OCORRENCIA a partir do PDF
python tools/extrair_recursos.py                # regerar o CAD_RECURSOS (dicionário + diagrama)
node --check docs/app.js                        # validar sintaxe do JS
cscript //Nologo //E:JScript docs\app.js        # idem, no Windows sem Node (erro de runtime = ok)
```

Os extratores precisam de `pdfplumber` (`pip install -r tools/requirements.txt`); o site e o
verificador não precisam de nada além da stdlib.

## Estrutura

```
docs/            o site (raiz publicada do GitHub Pages — NÃO colocar documentação aqui)
  index.html     template base do DS
  app.js         aplicação inteira, ES5
  styles.css     complemento ao core.min.css
  dados.js            CAD_OCORRENCIA — gerado pelo extrator, não editar à mão
  dados-recursos.js   CAD_RECURSOS   — idem
  assets/        gov.br DS, Rawline, Font Awesome, logo — gerados por script
data/            os mesmos dados, versionados e indentados (diff legível)
fonte/           PDFs originais
tools/           extrair_pdf.py, extrair_recursos.py, baixar_assets_ds.py, verificar_conformidade.py
documentacao/    docs do projeto: processo-negocio, arquitetura, decisoes (ADRs), CHANGELOG
.claude/         PROBLEMA.md, PLANO.md, este arquivo
```

## Regras do domínio

- **`docs/` é o site publicado.** Documentação do projeto vai em `documentacao/` (ADR-001). O
  `.nojekyll` precisa continuar existindo.
- **Nenhuma cor literal no CSS.** Toda cor sai de um token do DS. Há verificação por script.
- **Nunca `innerHTML`.** Todo DOM se constrói via `el()` / `svgEl()`, que usam `createElement`.
- **Não aplicar `.br-table` na grade de colunas.** O `core-init` instancia `BRTable` em toda
  `.br-table` e injeta header/footer que brigam com a ordenação e o filtro (ADR-004).
- **Ordem dos scripts importa:** `dados.js` → `app.js` → `core-init.min.js`. O core-init instancia
  os componentes sobre o DOM já montado pelo app.
- **Os `dados*.js` e os `data/*.json` são gerados.** Mudanças de dados se fazem no extrator.
- **Schema novo entra pelo registro `SCHEMAS`, no topo do `app.js`** (ADR-008), nunca por uma segunda
  página HTML. São quatro passos: rodar o extrator, acrescentar o `<script>` no `index.html` antes do
  `app.js`, acrescentar a entrada no array e a dupla (arquivo, global) em `DATASETS_ESPERADOS`, no
  verificador.
- **Rota é prefixada pelo slug do schema** (`#/recursos/tabela/EQUIPE`). Nunca escreva `"#/tabela/"`
  à mão no `app.js`: use `rota("tabela/" + nome)`. Hashes sem slug caem no schema padrão e existem só
  para não invalidar links antigos.
- **O `CAD_RECURSOS` sai de dois PDFs.** O dicionário não tem índices nem FKs; eles vêm do diagrama
  (ADR-009). O extrator aborta se não conseguir resolver o destino de uma FK — não invente um mapa
  de exceções sem antes ler a regra de três passos que já está lá.
- **`find_tables()` do pdfplumber perde a linha cortada pela quebra de página**, porque ela fica sem
  borda de baixo. O `extrair_recursos.py` fecha essa borda e tem uma checagem
  (`validar_comentarios`) que confere as descrições contra o texto cru. Se mexer nessa área, rode o
  extrator e confira `EQUIPAMENTO.ID_AGENCIA`.
- **Ícone sempre com `aria-hidden="true"`**; botão só-ícone sempre com `aria-label`.
- **Chaves de objeto que sejam palavras reservadas vão entre aspas** (`"for"`), por segurança de
  parser.
- **Ao editar `styles.css` ou `app.js`, incremente o `?v=` no `index.html`.** Sem isso o navegador
  serve a versão em cache e a mudança some — foi o que aconteceu na primeira rodada de correções
  visuais. O verificador cobra a presença do `?v=`, mas não sabe se o número foi incrementado.

## Armadilhas dos tokens do DS

- `.p-3` = **16px**, não 24px. A escala numérica é 0/4/8/16/24/32/40 e **para em 6**.
- Breakpoint `md` = **992px**, não 768. Os breakpoints são 576 / 992 / 1280 / 1600.
- **Não existem** no core 3.7.0: `.w-100`, `.h-100`, `.gap-*`, `.rounded`, `--surface-base-*`.
  Arredondamento é `--surface-rounder-*`.
- O DS **não tem dark mode global** — só modificadores por componente (`.dark-mode`, `.inverted`).
- **O `br-menu` não tem largura nenhuma no core.** O painel só ganha `flex:1` quando o menu está
  `.active`. Menu aberto por CSS precisa de `flex:1` explícito no `.menu-panel`, senão ele encolhe
  até o conteúdo mínimo. O menu deste site fica permanente a partir de **992px** (ADR-005).
- **`.input-icon` é `position:absolute` sem `top`** — ancora no topo do `.br-input`, que inclui o
  `<label>`. Com label visível, o ícone cai sobre o label. Só use onde o label está oculto.
- **`has-icon` não posiciona ícone à esquerda**, apesar do nome: ela só abre `padding-right` no
  campo, para botão à direita.
- `.text-up-*` usam `!important` e congelam o `font-size`, matando o crescimento responsivo do `h1`
  (29px → 41,8px acima de 576px). Não existem variantes por breakpoint.

## Acessibilidade

Alvo: **WCAG 2.2 A + AA**, via ABNT NBR 17225:2025. O eMAG 3.1 (WCAG 2.0, de 2014) segue sendo o
único padrão juridicamente obrigatório para órgãos do SISP; mirar 2.2 AA cobre os dois.

Não há ferramenta federal automatizável. Use axe DevTools ou Pa11y; depois do deploy, AMAWeb, Access
Monitor Plus ou WAVE.

## Pendências de publicação

Falta trocar o favicon do `index.html` pelo do órgão. A barra do Governo Federal **não** deve ser
reintroduzida sem revisar o ADR-007 — o verificador falha se ela voltar.
