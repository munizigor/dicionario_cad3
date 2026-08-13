# A3 — Adequação ao Padrão Digital de Governo

## Contexto

O Dicionário de Dados do SINESP CAD 3 é um site estático (GitHub Pages, pasta `docs/`) que torna
navegável o dicionário do schema `CAD_OCORRENCIA`: 71 tabelas, 831 colunas, 206 índices, 60 chaves
estrangeiras, extraídos de um PDF de 87 páginas do Oracle SQL Developer Data Modeler.

Tecnicamente é sólido: HTML/CSS/JS puro, sem build, sem dependência de rede, com busca sem
sensibilidade a acentos, diagramas SVG próprios e exportações (DDL, JSON, CSV, Mermaid). A
acessibilidade já foi cuidada de forma artesanal — skip link, `aria-*`, `prefers-reduced-motion`.

O que não existe é vínculo com o **Padrão Digital de Governo (gov.br DS)**. A identidade visual é
inteiramente autoral: paleta própria, fontes de sistema, glifos Unicode no lugar de iconografia,
markup próprio no lugar dos componentes do design system.

## Problema e causa-raiz

**Problema.** O site é uma ferramenta institucional que não se parece com uma solução de governo.
Quem abre não tem sinal visual de que é um sistema oficial, e quem já usa outros serviços gov.br não
encontra os padrões de interação que conhece — cabeçalho, menu, busca, rodapé, barra do Governo
Federal, VLibras.

**Causa-raiz.** O site nasceu como saída de um pipeline de extração de PDF, com foco em resolver o
problema de dados. A camada de apresentação foi construída do zero, otimizada para densidade de
informação, sem que o Padrão Digital fosse considerado como requisito — porque na origem ele não
era um requisito, era um dicionário técnico de uso interno.

**Não é** um problema de processo que se resolva sem tecnologia: a adequação a um design system é,
por definição, mudança de código. Mas também não é um problema de reescrita: o que existe funciona,
e a estrutura do código (um único helper `el()` construindo todo o DOM) torna a troca de camada
visual uma cirurgia localizada, não um recomeço.

## Necessidades de negócio

| # | Necessidade | Fonte |
|---|---|---|
| 1 | O site deve ser reconhecível como solução de governo — cabeçalho, logo, rodapé, tipografia e paleta oficiais | Portaria MCom nº 540/2020 (adoção obrigatória do DS); Portaria SECOM-MCOM nº 7.508/2022 |
| 2 | Deve atender ao **Padrão Mínimo** de aderência (8 itens) | https://www.gov.br/ds/introducao/padrao-minimo |
| 3 | Deve ser acessível a pessoas com deficiência, inclusive surdas (VLibras) | Lei 13.146/2015 art. 63; ABNT NBR 17225:2025; eMAG 3.1 |
| 4 | Deve continuar estático, servido pelo GitHub Pages, sem servidor e sem build | Restrição de infraestrutura — conversa com o Navegador, 13/08/2026 |
| 5 | Não pode perder funcionalidade: busca, filtros, ordenação, diagramas e exportações | Estado atual do sistema; `README.md` |
| 6 | Não pode depender de CDN de terceiros | Recomendação da doc do DS ("evite o CDN, baixe os arquivos localmente"); decisão do Navegador |

## Restrições

- **Estático.** Sem servidor, sem bundler, sem etapa de build. ES5 no `app.js`, sem transpilação.
- **Densidade de dados.** `CHAMADO` tem 92 colunas e `OCORRENCIA` tem 74. A `br-table` do DS empilha
  cada linha em bloco no responsivo — inviável nessa escala. A grade densa precisa continuar própria.
- **Versões.** `@govbr-ds/core@3.7.0` (estável desde nov/2025). A v4 está em `next` há mais de um ano
  e os web components tiveram major novo há duas semanas — ambos instáveis demais para este site.
- **Barra gov.br e VLibras são serviços vivos**, não vendorizáveis. O site perde o funcionamento
  100% offline via `file://`, com degradação graciosa.
- **`docs/` é a raiz publicada do GitHub Pages**, não pode receber documentação de projeto.

## Critérios de sucesso (outcome)

1. Um servidor que abre o site identifica em menos de 5 segundos que é um sistema institucional de
   governo — sem precisar ler o conteúdo.
2. Quem já usa outros serviços gov.br navega sem reaprender: encontra a busca onde espera, o menu
   onde espera, os atalhos de teclado 1–4 funcionando como em qualquer site do padrão.
3. Uma pessoa surda consegue acionar o VLibras; uma pessoa que navega só por teclado percorre o site
   inteiro; uma pessoa com baixa visão tem contraste conforme WCAG 2.2 AA.
4. Nenhuma das capacidades atuais se perde: busca sem acento, filtro incremental, ordenação da
   grade, deep link para coluna, mapa com zoom, e as seis exportações continuam funcionando.
5. `tools/verificar_conformidade.py` sai com código 0 e imprime os 8 itens do Padrão Mínimo
   atendidos.

## Fora de escopo

- Mudar o pipeline de extração do PDF (`tools/extrair_pdf.py`, `data/`, `fonte/`).
- Alterar o conteúdo ou a modelagem dos dados.
- Autenticação / Sign-In gov.br (o site é público e somente leitura).
