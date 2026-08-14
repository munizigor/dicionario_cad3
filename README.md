# Dicionário de Dados — SINESP CAD

Versão estática e navegável dos dicionários de dados do SINESP CAD, gerada a partir dos PDFs
exportados pelo Oracle SQL Developer Data Modeler.

| Schema | Sistema | Tabelas | Colunas | Índices | Chaves estrangeiras |
|---|---|---|---|---|---|
| `CAD_OCORRENCIA` | SINESP CAD 3 | 71 | 831 | 206 | 60 |
| `CAD_RECURSOS` | SINESP CAD 2 | 13 | 76 | 24 | 13 |

Os dois convivem num site só: o seletor no topo do menu lateral troca o schema, e a rota carrega o
slug dele — `#/ocorrencia/tabela/OCORRENCIA`, `#/recursos/tabela/EQUIPE`.

## O que o site faz

- **Navegação** pelas tabelas do schema ativo, agrupadas por prefixo (`OCORRENCIA_*`, `CHAMADO_*`,
  `EQUIPE_*`, `HISTORICO_*`…), com filtro incremental na barra lateral.
- **Busca global** por nome de tabela, nome de coluna ou trecho de descrição, sem sensibilidade a
  acentos (`ocorrencia` encontra `Ocorrência`) e com os trechos destacados. Atalho: tecla `/`.
- **Links de chave estrangeira**: cada coluna FK aponta para a coluna referenciada, e cada tabela
  lista o que referencia e por quem é referenciada.
- **Diagramas**: um diagrama de vizinhança por tabela e um mapa geral das tabelas conectadas do
  schema, com zoom, arrasto e destaque de vizinhança — tudo em SVG, sem biblioteca externa.
- **Exportação**: DDL Oracle aproximado (`.sql`), JSON, CSV das colunas e diagrama Mermaid
  (`.mmd`) por tabela; JSON e DDL completos na página inicial.
- Layout responsivo e folha de estilo de impressão.

## Padrão Digital de Governo

O site segue o [Padrão Digital de Governo](https://www.gov.br/ds/home): cabeçalho e rodapé oficiais,
tipografia Rawline, paleta e componentes do design system, VLibras e skip link com os atalhos de
teclado 1 a 4. Alvo de acessibilidade: **WCAG 2.2 A + AA** (ABNT NBR
17225:2025).

Os arquivos do design system são **vendorizados** em `docs/assets/` — o site não depende de nenhum
CDN. Para verificar a aderência:

```sh
python3 tools/verificar_conformidade.py
```

> **Antes de publicar oficialmente:** falta trocar o favicon do `docs/index.html` pelo do órgão.

## Como usar

O site é estático e não depende de servidor. Os dados vão embutidos em `docs/dados.js` e
`docs/dados-recursos.js` (e não carregados via `fetch`), então busca, filtros, diagramas e
exportações funcionam mesmo sem rede — só o VLibras precisa de conexão, por ser um serviço vivo.

Para publicar no GitHub Pages: **Settings → Pages → Source: Deploy from a branch**, e escolher a
branch com a pasta `/docs`.

Para servir localmente:

```sh
python3 -m http.server -d docs 8000   # http://localhost:8000
```

## Documentação

Em [`documentacao/`](documentacao/) — e não em `docs/`, que é a raiz publicada do site:

- [`processo-negocio.md`](documentacao/processo-negocio.md) — o problema e as pessoas atendidas
- [`arquitetura.md`](documentacao/arquitetura.md) — stack, organização do código e verificação
- [`decisoes.md`](documentacao/decisoes.md) — ADRs curtos
- [`CHANGELOG.md`](documentacao/CHANGELOG.md) — o que mudou em cada release

## Como regenerar a partir de um PDF novo

Quando sair uma nova versão de um dicionário, substitua os PDFs em `fonte/` e rode o extrator
correspondente:

```sh
pip install -r tools/requirements.txt
python3 tools/extrair_pdf.py                     # CAD_OCORRENCIA
python3 tools/extrair_pdf.py caminho/outro.pdf   # ou aponte outro arquivo
python3 tools/extrair_recursos.py                # CAD_RECURSOS (dicionário + diagrama)
```

Cada extrator reescreve o JSON em `data/` (indentado, para o diff ficar legível entre versões) e o
`.js` correspondente em `docs/` (compactado, consumido pelo site).

São duas ferramentas porque os relatórios de origem são diferentes: o do `CAD_RECURSOS` foi gerado
com um perfil enxuto do modelador e **não traz índices nem chaves estrangeiras** — essas vêm do
diagrama relacional, num segundo PDF, que o extrator cruza com o dicionário
([ADR-009](documentacao/decisoes.md)).

Os extratores falham com código de saída 1 se a extração regredir. As assertivas conferem que:

- toda tabela tem o número de colunas que ela mesma declara;
- nenhuma seção do PDF ficou sem ser reconhecida;
- toda FK aponta para uma tabela existente, com colunas balanceadas;
- as duas visões de cada FK (origem e destino) fecham exatamente;
- no `CAD_RECURSOS`, ainda: o destino de toda FK foi resolvido, as marcações de PK/FK do dicionário
  e do diagrama coincidem, e nenhuma descrição presente no PDF ficou de fora do JSON.

## Estrutura

```
fonte/Dicionario_CAD_Ocorrencia.pdf   PDF original do CAD_OCORRENCIA (87 páginas)
fonte/CAD_Recursos_dicionario.pdf     PDF original do CAD_RECURSOS (18 páginas)
fonte/CAD_Recursos_diagrama.pdf       diagrama relacional do CAD_RECURSOS (1 página)
tools/extrair_pdf.py                  extrator do CAD_OCORRENCIA (pdfplumber)
tools/extrair_recursos.py             extrator do CAD_RECURSOS: dicionário + diagrama
tools/baixar_assets_ds.py             baixa os assets do gov.br DS para docs/assets/
tools/verificar_conformidade.py       checa a aderência ao Padrão Digital
data/*.json                           dados estruturados, versionados
documentacao/                         documentação do projeto (ADRs, arquitetura, changelog)
docs/                                 o site (raiz publicada do GitHub Pages)
  index.html · styles.css · app.js    ~1.500 linhas de JS puro, sem dependências
  dados.js · dados-recursos.js        gerados pelos extratores
  assets/                             gov.br DS 3.7.0, Rawline, Font Awesome — gerados por script
```

## Observações sobre os dados

- O conteúdo é reproduzido **como está no documento original**, inclusive imprecisões da fonte
  (por exemplo `Refering To` e `Chamdo`).
- Colunas sem descrição aparecem com `—`: o PDF simplesmente omite a linha de comentário delas.
- O DDL exportado é **aproximado**. Os tipos são traduzidos do modelador para Oracle
  (`VARCHAR (n BYTE)` → `VARCHAR2(n BYTE)`, `NUMERIC (n)` → `NUMBER(n)`, `Raw (n)` → `RAW(n)`,
  `Timestamp (n)` → `TIMESTAMP(n)`), mas defaults e check constraints devem ser conferidos antes
  de qualquer uso real — as check constraints saem apenas como comentário.
- O DDL do `CAD_RECURSOS` é menos aproximado que o do `CAD_OCORRENCIA`: o diagrama traz o tipo
  físico do banco (`NUMBER (10)`, `VARCHAR2 (255 BYTE)`), que é usado direto em vez de deduzido.
- Os campos `Domain Name`, `Security` e `Abbreviation` estão vazios em todo o documento do
  `CAD_OCORRENCIA`, e a volumetria é idêntica (valores-padrão) nas 71 tabelas; por isso não aparecem
  na interface, embora sigam preservados no JSON. O relatório do `CAD_RECURSOS` não traz volumetria
  nenhuma.
- No `CAD_RECURSOS`, `ID_AGENCIA` e `ID_REGIAO` referenciam tabelas de outro sistema: não aparecem
  como chave estrangeira, e a origem de cada uma está na descrição da coluna.
