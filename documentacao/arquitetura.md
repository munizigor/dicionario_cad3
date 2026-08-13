# Arquitetura

## Visão geral

Site estático, sem servidor e sem build, servido pelo GitHub Pages a partir de `docs/`. Toda a
aplicação são três arquivos (`index.html`, `styles.css`, `app.js`) mais os dados embutidos em
`dados.js` e os assets do Padrão Digital de Governo em `assets/`.

```
PDF (Data Modeler)  →  tools/extrair_pdf.py  →  data/dicionario.json   (versionado, legível)
                                              →  docs/dados.js          (minificado, consumido)

docs/index.html   template base do gov.br DS (header, menu, breadcrumb, footer)
docs/app.js       roteador, renderização, busca, diagramas e exportações — ES5, sem dependências
docs/styles.css   complemento ao core.min.css: grade densa, selos de chave, diagramas SVG
docs/assets/      gov.br DS 3.7.0, Rawline, Font Awesome 5.11.2, logo — via baixar_assets_ds.py
```

## Stack

| Camada | Escolha | Observação |
|---|---|---|
| Design system | `@govbr-ds/core` **3.7.0** | `core.min.css` + `core-init.min.js`, vendorizados (ADR-002) |
| Tipografia | Rawline (pesos 300–700) | fonte oficial do padrão; Raleway seria fallback e nunca é requisitada |
| Iconografia | Font Awesome **5.11.2** | versão que o DS especifica — o core usa `.fa-w-*`, `.fad` e `.fal`, do FA5 |
| JavaScript | ES5 puro, IIFE | sem framework, sem bundler, sem transpilação |
| Dados | `window.DICIONARIO` em `dados.js` | embutido em vez de `fetch`, para funcionar por `file://` |
| Extração | Python 3 + `pdfplumber` | só no pipeline de dados, não no site |

**Não usar:** `@govbr-ds/core@4.x` (em `next` há mais de um ano) nem `@govbr-ds/webcomponents`
(major novo em julho/2026, publicando várias vezes por semana).

## Como o app.js se organiza

Uma IIFE em `"use strict"`, dividida em blocos comentados:

1. **Helpers** — `el()` e `svgEl()` constroem todo o DOM via `createElement`; `innerHTML` não aparece
   uma única vez no arquivo. `icone()`, `botao()`, `tag()` e `mensagem()` produzem os componentes do
   DS.
2. **Índices derivados** — no boot são calculados `ARESTAS` (60 FKs achatadas), `VIZINHOS`
   (adjacência), `GRUPOS` (por prefixo) e `INDICE` (busca).
3. **Busca** — `normalizar()` remove diacríticos (NFD); `buscar()` exige todos os termos e pontua por
   tipo de casamento; `destacar()` devolve um fragmento com `<mark>`.
4. **Exportações** — `gerarDDL()`, `gerarCSV()` (com BOM, para o Excel), `gerarMermaid()`.
5. **Diagramas** — SVG à mão: vizinhança por tabela e um mapa global com layout de forças
   Fruchterman-Reingold determinístico, memoizado, com zoom e pan por Pointer Events.
6. **Páginas e roteamento** — hash-based (`#/`, `#/tabela/X`, `#/tabela/X?col=Y`, `#/busca?q=`,
   `#/mapa`), cada rota ajustando `document.title` e o breadcrumb.

## Integração com o design system

O `core-init.min.js` roda por último e instancia sozinho todos os componentes `.br-*` presentes no
DOM. Por isso a ordem dos scripts importa: `dados.js` → `app.js` (monta menu e trilha) →
`core-init.min.js`.

Essa instanciação automática é também o motivo de a grade de colunas **não** levar a classe
`.br-table` (ADR-004).

O que continua sendo CSS próprio, porque o DS não cobre:

- **Grade densa de colunas** — cabeçalho sticky dentro do card, ordenação clicável, filtro.
- **Selos PK / FK / NN** — `br-tag` com três cores semânticas derivadas de tokens do DS.
- **Diagramas SVG** — nós, arestas, marcadores e zoom.
- **Menu permanente no desktop** — media query a partir de 992px (ADR-005). O core não dá largura
  nenhuma ao `br-menu`; o painel precisa de `flex:1` explícito.

Regra ao editar `styles.css`: **nenhuma cor literal**. Toda cor sai de um token do DS. Há um
verificador para isso na seção seguinte.

## Verificação

```sh
python tools/verificar_conformidade.py     # 71 checagens; sai 1 se alguma falhar
python -m http.server -d docs 8000         # http://localhost:8000
```

O verificador cobre o que dá para checar estaticamente: metadados do documento, skip link com os
quatro `accesskey`, âncoras obrigatórias do template, presença dos componentes, assets todos locais,
ausência de resíduos da versão anterior, acessibilidade estrutural (`alt`, `aria-hidden` em ícone,
rótulo em botão só-ícone, `label` em campo), ganchos entre `app.js` e `index.html`, e as oito
funcionalidades que não podem se perder.

O que ele **não** cobre e continua sendo manual: contraste renderizado, ordem de foco, leitura por
leitor de tela e o comportamento real dos componentes do DS.

Não existe ferramenta federal automatizável para isso. Para acessibilidade, a escolha defensável é
**axe DevTools** ou **Pa11y** contra WCAG 2.2 AA; depois do deploy, AMAWeb, Access Monitor Plus ou
WAVE. O ASES continua no ar, mas avalia pelo eMAG 3.1 (WCAG 2.0, de 2014), exige reCAPTCHA e saiu da
lista oficial de ferramentas do Governo Digital.

Para validar a sintaxe do `app.js` sem instalar Node:

```sh
cscript //Nologo //E:JScript docs\app.js
```

Um erro de *compilação* indica sintaxe inválida. O erro de *runtime* `'window' não está definido` é o
resultado esperado — significa que o arquivo inteiro compilou.

## Atualizar os assets do design system

As versões estão fixadas no topo de `tools/baixar_assets_ds.py`. Para atualizar, mude as constantes
e rode:

```sh
python tools/baixar_assets_ds.py
python tools/verificar_conformidade.py
```

## Dependências de rede em produção

O site funciona sem rede, com uma exceção declarada: o VLibras (`vlibras.gov.br`) é serviço vivo e
não vendorizável (ADR-003). Sem rede ele some e todo o resto continua funcionando — dados, busca,
filtros, ordenação, diagramas e exportações — porque `dados.js` é embutido e não há `fetch` em lugar
nenhum.

A barra do Governo Federal chegou a ser adotada e foi removida (ADR-007): sem documentação, sem
licença pública e com um botão de login que trava em carregamento permanente num site sem
autenticação.
