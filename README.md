# Dicionário de Dados — SINESP CAD 3

Versão estática e navegável do dicionário de dados do schema `CAD_OCORRENCIA` do SINESP CAD 3,
gerada a partir do PDF de 87 páginas exportado pelo Oracle SQL Developer Data Modeler.

**71 tabelas · 831 colunas · 206 índices · 60 chaves estrangeiras.**

## O que o site faz

- **Navegação** pelas 71 tabelas, agrupadas por prefixo (`OCORRENCIA_*`, `CHAMADO_*`, `FILA_*`…),
  com filtro incremental na barra lateral.
- **Busca global** por nome de tabela, nome de coluna ou trecho de descrição, sem sensibilidade a
  acentos (`ocorrencia` encontra `Ocorrência`) e com os trechos destacados. Atalho: tecla `/`.
- **Links de chave estrangeira**: cada coluna FK aponta para a coluna referenciada, e cada tabela
  lista o que referencia e por quem é referenciada.
- **Diagramas**: um diagrama de vizinhança por tabela e um mapa geral das 50 tabelas conectadas,
  com zoom, arrasto e destaque de vizinhança — tudo em SVG, sem biblioteca externa.
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

O site é estático e não depende de servidor. Os dados vão embutidos em `docs/dados.js` (e não
carregados via `fetch`), então busca, filtros, diagramas e exportações funcionam mesmo sem rede — só
o VLibras precisa de conexão, por ser um serviço vivo.

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

Quando sair uma nova versão do dicionário, substitua o PDF em `fonte/` e rode o extrator:

```sh
pip install -r tools/requirements.txt
python3 tools/extrair_pdf.py                     # usa fonte/Dicionario_CAD_Ocorrencia.pdf
python3 tools/extrair_pdf.py caminho/outro.pdf   # ou aponte outro arquivo
```

O script reescreve `data/dicionario.json` (indentado, para o diff ficar legível entre versões) e
`docs/dados.js` (compactado, consumido pelo site).

O extrator falha com código de saída 1 se a extração regredir. As assertivas conferem que:

- toda tabela tem o número de colunas que ela mesma declara em `Number Of Columns`;
- nenhuma seção do PDF ficou sem ser reconhecida;
- toda FK aponta para uma tabela existente, com colunas balanceadas;
- as duas visões de cada FK (`referring to` na origem, `referred by` no destino) fecham exatamente.

## Estrutura

```
fonte/Dicionario_CAD_Ocorrencia.pdf   PDF original (87 páginas)
tools/extrair_pdf.py                  extrator PDF → JSON (pdfplumber)
tools/baixar_assets_ds.py             baixa os assets do gov.br DS para docs/assets/
tools/verificar_conformidade.py       checa a aderência ao Padrão Digital
data/dicionario.json                  dados estruturados, versionados
documentacao/                         documentação do projeto (ADRs, arquitetura, changelog)
docs/                                 o site (raiz publicada do GitHub Pages)
  index.html · styles.css · app.js    ~1.400 linhas de JS puro, sem dependências
  dados.js                            gerado pelo extrator
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
- Os campos `Domain Name`, `Security` e `Abbreviation` estão vazios em todas as 831 colunas do
  documento, e a volumetria é idêntica (valores-padrão) nas 71 tabelas; por isso não aparecem na
  interface, embora sigam preservados no JSON.
