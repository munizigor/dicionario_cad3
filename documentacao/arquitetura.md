# Arquitetura

## Visão geral

Site estático, sem servidor e sem build, servido pelo GitHub Pages a partir de `docs/`. Toda a
aplicação são três arquivos (`index.html`, `styles.css`, `app.js`) mais um arquivo de dados por
schema publicado e os assets do Padrão Digital de Governo em `assets/`.

```
Dicionário PDF                →  tools/extrair_pdf.py       →  data/dicionario.json
(CAD_OCORRENCIA)                                            →  docs/dados.js

Dicionário PDF + diagrama PDF →  tools/extrair_recursos.py  →  data/dicionario_recursos.json
(CAD_RECURSOS)                                              →  docs/dados-recursos.js

docs/index.html   template base do gov.br DS (header, menu, breadcrumb, footer)
docs/app.js       roteador, renderização, busca, diagramas e exportações — ES5, sem dependências
docs/styles.css   complemento ao core.min.css: grade densa, selos de chave, diagramas SVG
docs/assets/      gov.br DS 3.7.0, Rawline, Font Awesome 5.11.2, logo — via baixar_assets_ds.py
```

Os dois extratores emitem o **mesmo formato**, de propósito: o `app.js` consome qualquer dataset sem
ramo por schema. São ferramentas separadas porque os relatórios de origem são diferentes — o do
CAD_RECURSOS não traz índices nem chaves estrangeiras, que vêm de um segundo PDF, o diagrama
(ADR-009).

## Schemas publicados

| Slug | Schema | Sistema | Tabelas | Colunas | FKs | Fonte |
|---|---|---|---|---|---|---|
| `ocorrencia` | `CAD_OCORRENCIA` | SINESP CAD 3 | 71 | 831 | 60 | `Dicionario_CAD_Ocorrencia.pdf` |
| `recursos` | `CAD_RECURSOS` | SINESP CAD 2 | 13 | 76 | 13 | `CAD_Recursos_dicionario.pdf` + `CAD_Recursos_diagrama.pdf` |

O registro fica no topo do `docs/app.js`, no array `SCHEMAS`. Publicar um schema novo é: rodar o
extrator, acrescentar o `<script>` no `index.html`, acrescentar a entrada no array e a dupla
(arquivo, global) em `DATASETS_ESPERADOS` no verificador. Ver ADR-008.

## Stack

| Camada | Escolha | Observação |
|---|---|---|
| Design system | `@govbr-ds/core` **3.7.0** | `core.min.css` + `core-init.min.js`, vendorizados (ADR-002) |
| Tipografia | Rawline (pesos 300–700) | fonte oficial do padrão; Raleway seria fallback e nunca é requisitada |
| Iconografia | Font Awesome **5.11.2** | versão que o DS especifica — o core usa `.fa-w-*`, `.fad` e `.fal`, do FA5 |
| JavaScript | ES5 puro, IIFE | sem framework, sem bundler, sem transpilação |
| Dados | um global por schema (`window.DICIONARIO`, `window.DICIONARIO_RECURSOS`) | embutido em vez de `fetch`, para funcionar por `file://` |
| Extração | Python 3 + `pdfplumber` | só no pipeline de dados, não no site |

**Não usar:** `@govbr-ds/core@4.x` (em `next` há mais de um ano) nem `@govbr-ds/webcomponents`
(major novo em julho/2026, publicando várias vezes por semana).

## Como o app.js se organiza

Uma IIFE em `"use strict"`, dividida em blocos comentados:

1. **Helpers** — `el()` e `svgEl()` constroem todo o DOM via `createElement`; `innerHTML` não aparece
   uma única vez no arquivo. `icone()`, `botao()`, `tag()` e `mensagem()` produzem os componentes do
   DS.
2. **Schema ativo e índices derivados** — `selecionarSchema(slug)` fixa `DADOS`/`TABELAS`/`POR_NOME`
   e recalcula `ARESTAS` (FKs achatadas), `VIZINHOS` (adjacência), `GRUPOS` (por prefixo) e `INDICE`
   (busca), além de zerar o cache do mapa. É chamada pelo roteador a cada navegação, e é idempotente
   quando o schema não muda.
3. **Busca** — `normalizar()` remove diacríticos (NFD); `buscar()` exige todos os termos e pontua por
   tipo de casamento; `destacar()` devolve um fragmento com `<mark>`.
4. **Exportações** — `gerarDDL()`, `gerarCSV()` (com BOM, para o Excel), `gerarMermaid()`.
5. **Diagramas** — SVG à mão: vizinhança por tabela e um mapa global com layout de forças
   Fruchterman-Reingold determinístico, memoizado, com zoom e pan por Pointer Events.
6. **Páginas e roteamento** — hash-based, com o slug do schema no primeiro segmento:
   `#/<slug>`, `#/<slug>/tabela/X`, `#/<slug>/tabela/X?col=Y`, `#/<slug>/busca?q=`, `#/<slug>/mapa`.
   Cada rota ajusta `document.title` e o breadcrumb. Hashes sem slug (`#/tabela/X`, `#/busca`,
   `#/mapa`) são servidos pelo schema padrão, sem redirecionar, para não invalidar links antigos.

## Integração com o design system

O `core-init.min.js` roda por último e instancia sozinho todos os componentes `.br-*` presentes no
DOM. Por isso a ordem dos scripts importa: `dados.js` e `dados-recursos.js` → `app.js` (monta menu e
trilha) → `core-init.min.js`. O verificador cobra essa ordem.

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
python tools/verificar_conformidade.py     # 84 checagens; sai 1 se alguma falhar
python -m http.server -d docs 8000         # http://localhost:8000
```

Os extratores também validam a si mesmos e saem 1 em qualquer inconsistência — contagem de colunas,
FK sem destino resolvido, marcação de PK/FK divergente entre dicionário e diagrama, descrição que o
PDF tem e o JSON não.

O verificador cobre o que dá para checar estaticamente: metadados do documento, skip link com os
quatro `accesskey`, âncoras obrigatórias do template, presença dos componentes, assets todos locais,
ausência de resíduos da versão anterior, acessibilidade estrutural (`alt`, `aria-hidden` em ícone,
rótulo em botão só-ícone, `label` em campo), ganchos entre `app.js` e `index.html`, presença e ordem
dos datasets de cada schema, e as oito funcionalidades que não podem se perder.

O que ele **não** cobre e continua sendo manual: contraste renderizado, ordem de foco, leitura por
leitor de tela e o comportamento real dos componentes do DS.

Não existe ferramenta federal automatizável para isso. Para acessibilidade, a escolha defensável é
**axe DevTools** ou **Pa11y** contra WCAG 2.2 AA; depois do deploy, AMAWeb, Access Monitor Plus ou
WAVE. O ASES continua no ar, mas avalia pelo eMAG 3.1 (WCAG 2.0, de 2014), exige reCAPTCHA e saiu da
lista oficial de ferramentas do Governo Digital.

Para validar a sintaxe do `app.js`:

```sh
node --check docs/app.js                             # onde houver Node
cscript //Nologo //E:JScript docs\app.js             # no Windows, sem Node
```

No `cscript`, um erro de *compilação* indica sintaxe inválida; o erro de *runtime*
`'window' não está definido` é o resultado esperado — significa que o arquivo inteiro compilou.

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
filtros, ordenação, diagramas e exportações — porque os arquivos de dados são embutidos e não há
`fetch` em lugar nenhum.

A barra do Governo Federal chegou a ser adotada e foi removida (ADR-007): sem documentação, sem
licença pública e com um botão de login que trava em carregamento permanente num site sem
autenticação.
