# Changelog

## 2026-08-14 — Schema CAD_RECURSOS e navegação multi-schema

O site passa a servir dois dicionários. O do `CAD_OCORRENCIA` continua igual; ao lado dele entra o
`CAD_RECURSOS` do SINESP CAD 2 — 13 tabelas, 76 colunas, 13 chaves estrangeiras e 24 índices.

### Adicionado
- `fonte/CAD_Recursos_dicionario.pdf` e `fonte/CAD_Recursos_diagrama.pdf`.
- `tools/extrair_recursos.py` — extrator do CAD_RECURSOS. Cruza os dois PDFs: o dicionário dá
  tabelas, colunas, tipos lógicos e descrições; o diagrama dá PK, FK, índices e os tipos físicos do
  banco, que o dicionário não traz (ADR-009). Gera `data/dicionario_recursos.json` e
  `docs/dados-recursos.js`.
- Seletor de schema no topo do menu lateral, com a rota prefixada pelo slug —
  `#/recursos/tabela/EQUIPE` (ADR-008).
- Campo `tipo_fisico` nas colunas, usado nos exports de DDL e Mermaid quando disponível.
- ADR-008 (navegação multi-schema) e ADR-009 (relacionamentos vindos do diagrama).
- Grupo de checagens "Datasets dos schemas" no `tools/verificar_conformidade.py`: 84 checagens.

### Alterado
- `docs/app.js`: o estado derivado do dataset — grafo, grupos, índice de busca, mapa — passou a ser
  recalculado por `selecionarSchema()` em vez de ser fixado na carga.
- `docs/index.html`: `<title>` e descrição deixaram de citar um schema só; o subtítulo do cabeçalho e
  os atalhos do "Acesso Rápido" passaram a acompanhar o schema ativo.
- `?v=` de `styles.css` e `app.js` incrementado para 4.

### Compatibilidade
Links sem slug (`#/tabela/X`, `#/busca`, `#/mapa`) continuam funcionando e abrem no `CAD_OCORRENCIA`.

## 2026-08-13 — Adequação ao Padrão Digital de Governo

Primeira release com identidade visual de governo. O conteúdo e as funcionalidades são os mesmos; o
que muda é a camada de apresentação e a acessibilidade.

### Adicionado
- Design system gov.br (`@govbr-ds/core` 3.7.0) vendorizado em `docs/assets/`, sem CDN.
- Template base do DS: `br-skiplink` com `accesskey` 1–4, `br-header` com logo gov.br e busca,
  `br-menu`, `br-breadcrumb` e `br-footer`.
- Tipografia Rawline e iconografia Font Awesome 5.11.2.
- VLibras.
- Rodapé institucional com proveniência dos dados e licença de uso.
- `tools/baixar_assets_ds.py` — baixa e atualiza os assets do DS com as versões fixadas.
- `tools/verificar_conformidade.py` — checagens estáticas de aderência ao padrão (73 na época).
- `documentacao/` com processo de negócio, arquitetura e seis ADRs.

### Alterado
- `index.html`, `styles.css` e `app.js` reescritos sobre os componentes e tokens do DS.
- `styles.css` encolheu de 377 para 250 linhas e deixou de usar cores literais.
- Grade de colunas, selos PK/FK/NN e diagramas SVG permanecem próprios, agora sobre tokens do DS.
- O menu lateral passou a ser `br-menu`: offcanvas no mobile, permanente a partir de 992px.

### Removido
- **Tema escuro.** O DS 3.7.0 não tem dark mode global e mantê-lo exigiria uma paleta paralela não
  oficial (ADR-006).
- Skip link, drawer e véu artesanais, substituídos pelos componentes do padrão.

### Pendências antes da publicação oficial
Falta trocar o favicon do `index.html` pelo do órgão.

### Nota
O site deixou de funcionar 100% offline por `file://`: o VLibras é serviço vivo e não vendorizável.
Sem rede ele some e todo o resto continua funcionando.
