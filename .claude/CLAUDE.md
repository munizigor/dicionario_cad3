# CLAUDE.md — Dicionário de Dados SINESP CAD 3

Especializa o CLAUDE.md global. Site estático de dicionário de dados, aderente ao Padrão Digital de
Governo, servido pelo GitHub Pages a partir de `docs/`.

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
python tools/verificar_conformidade.py          # testes — 73 checagens, sai 1 se falhar
python -m http.server -d docs 8000              # rodar — http://localhost:8000
python tools/baixar_assets_ds.py                # atualizar assets do DS
python tools/extrair_pdf.py                     # regerar dados a partir do PDF
cscript //Nologo //E:JScript docs\app.js        # validar sintaxe do JS (erro de runtime = ok)
```

## Estrutura

```
docs/            o site (raiz publicada do GitHub Pages — NÃO colocar documentação aqui)
  index.html     template base do DS
  app.js         aplicação inteira, ES5
  styles.css     complemento ao core.min.css
  dados.js       gerado pelo extrator — não editar à mão
  assets/        gov.br DS, Rawline, Font Awesome, logo — gerados por script
data/            dicionario.json versionado (diff legível)
fonte/           PDF original
tools/           extrair_pdf.py, baixar_assets_ds.py, verificar_conformidade.py
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
- **`dados.js` e `data/dicionario.json` são gerados.** Mudanças de dados se fazem no extrator.
- **Ícone sempre com `aria-hidden="true"`**; botão só-ícone sempre com `aria-label`.
- **Chaves de objeto que sejam palavras reservadas vão entre aspas** (`"for"`), por segurança de
  parser.

## Armadilhas dos tokens do DS

- `.p-3` = **16px**, não 24px. A escala numérica é 0/4/8/16/24/32/40 e **para em 6**.
- Breakpoint `md` = **992px**, não 768. Os breakpoints são 576 / 992 / 1280 / 1600.
- **Não existem** no core 3.7.0: `.w-100`, `.h-100`, `.gap-*`, `.rounded`, `--surface-base-*`.
  Arredondamento é `--surface-rounder-*`.
- O DS **não tem dark mode global** — só modificadores por componente (`.dark-mode`, `.inverted`).

## Acessibilidade

Alvo: **WCAG 2.2 A + AA**, via ABNT NBR 17225:2025. O eMAG 3.1 (WCAG 2.0, de 2014) segue sendo o
único padrão juridicamente obrigatório para órgãos do SISP; mirar 2.2 AA cobre os dois.

Não há ferramenta federal automatizável. Use axe DevTools ou Pa11y; depois do deploy, AMAWeb, Access
Monitor Plus ou WAVE.

## Pendências de publicação

Quatro `TODO` no `index.html`: nome do órgão (cabeçalho, rodapé, `titulo` da `<barra-govbr>`) e o
favicon institucional.
