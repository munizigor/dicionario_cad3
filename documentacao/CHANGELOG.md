# Changelog

## 2026-08-13 — Adequação ao Padrão Digital de Governo

Primeira release com identidade visual de governo. O conteúdo e as funcionalidades são os mesmos; o
que muda é a camada de apresentação e a acessibilidade.

### Adicionado
- Design system gov.br (`@govbr-ds/core` 3.7.0) vendorizado em `docs/assets/`, sem CDN.
- Template base do DS: `br-skiplink` com `accesskey` 1–4, `br-header` com logo gov.br e busca,
  `br-menu`, `br-breadcrumb` e `br-footer`.
- Tipografia Rawline e iconografia Font Awesome 5.11.2.
- Barra do Governo Federal (`barra.sistema.gov.br`) e VLibras.
- Rodapé institucional com proveniência dos dados e licença de uso.
- `tools/baixar_assets_ds.py` — baixa e atualiza os assets do DS com as versões fixadas.
- `tools/verificar_conformidade.py` — 73 checagens estáticas de aderência ao padrão.
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
Quatro `TODO` marcados no `index.html`: nome do órgão no cabeçalho, no rodapé e no atributo `titulo`
da `<barra-govbr>`, e o favicon institucional.

### Nota
O site deixou de funcionar 100% offline por `file://`: a barra do Governo Federal e o VLibras são
serviços vivos e não vendorizáveis. Sem rede os dois somem e todo o resto continua funcionando.
