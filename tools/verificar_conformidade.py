#!/usr/bin/env python3
"""Verifica a aderência do site ao Padrão Digital de Governo (gov.br DS).

Não existe ferramenta oficial de avaliação de conformidade: não há selo federal,
checklist pontuado nem API automatizável. A página "Padrão Mínimo" do gov.br/ds é
orientação narrativa, e os checklists da wiki do DS são de governança interna de
quem contribui com o design system, não de sites que o consomem. Este script é a
nossa verificação, escrita a partir daquela orientação e do template base oficial.

Cobre o que é verificável estaticamente. O que depende de renderização (contraste
real, ordem de foco, leitura por leitor de tela) continua sendo trabalho manual —
ver a seção de verificação em documentacao/arquitetura.md.

Uso: python tools/verificar_conformidade.py
Sai com código 1 se qualquer verificação falhar.
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "docs"
INDEX = SITE / "index.html"
APP = SITE / "app.js"
ESTILOS = SITE / "styles.css"

# Destinos do br-skiplink, na ordem dos accesskeys 1..4 do template base do DS.
ANCORAS_SKIPLINK = [
    ("1", "main-content", "Ir para o conteúdo"),
    ("2", "header-navigation", "Ir para o menu"),
    ("3", "main-searchbox", "Ir para a busca"),
    ("4", "footer", "Ir para o rodapé"),
]

# Únicos hosts remotos aceitos: são serviços vivos, não vendorizáveis (ADR-003).
HOSTS_PERMITIDOS = ("barra.sistema.gov.br", "vlibras.gov.br")

# Arquivos que precisam existir vendorizados em docs/assets/. Os CSS de fonte
# ficam sob `css/` porque referenciam `../font/` e `../webfonts/` — a estrutura
# replica a das origens para que os caminhos relativos resolvam sem reescrita.
ASSETS_ESPERADOS = [
    "assets/govbr/core.min.css",
    "assets/govbr/core-init.min.js",
    "assets/fonts/rawline/css/rawline.css",
    "assets/fontawesome/css/all.min.css",
]

# Marcas do tema escuro e do menu artesanal, removidos na adequação.
RESIDUOS = [
    (r"data-tema", "tema escuro (atributo data-tema)"),
    (r"alternar-tema", "botão de alternar tema"),
    (r"tema-cad3", "chave de localStorage do tema"),
    (r'classe:\s*"pular"|class="pular"', "skip link artesanal (.pular)"),
    (r'id="veu"|\$\("#veu"\)', "véu do drawer artesanal (#veu)"),
    (r"alternar-menu", "botão de menu artesanal"),
]

PADRAO_MINIMO = [
    "Cabeçalho com logo gov.br",
    "Rodapé institucional",
    "Tipografia Rawline",
    "Paleta de cores oficial aplicada por função",
    "Botões padronizados, com hierarquia",
    "Formulários com semântica correta",
    "Iconografia seguindo as orientações de uso",
    "Web responsivo",
]

# Elementos que, se contiverem apenas ícone, precisam de rótulo acessível.
INTERATIVOS = ("button", "a")


class Documento(HTMLParser):
    """Coleta a árvore do HTML de forma rasa: elementos, ids, classes e o texto
    acumulado dentro de cada elemento interativo.

    Não valida o HTML — só o suficiente para as verificações abaixo. Elementos
    interativos guardam `texto` e `icones` para distinguir "botão com rótulo" de
    "botão só de ícone", que é o caso que exige aria-label.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elementos = []
        self.pilha = []

    def handle_starttag(self, tag, atributos):
        item = {
            "tag": tag,
            "attrs": dict(atributos),
            "texto": "",
            "icones": 0,
            "filhos": [],
        }
        self.elementos.append(item)
        if self.pilha:
            self.pilha[-1]["filhos"].append(item)
            if tag == "i" or tag == "svg":
                self.pilha[-1]["icones"] += 1
        if tag not in ("br", "hr", "img", "input", "meta", "link", "source"):
            self.pilha.append(item)

    def handle_startendtag(self, tag, atributos):
        self.handle_starttag(tag, atributos)

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i]["tag"] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, dados):
        texto = dados.strip()
        if texto:
            for item in self.pilha:
                item["texto"] += " " + texto

    # -- consultas -----------------------------------------------------------

    def por_tag(self, tag):
        return [e for e in self.elementos if e["tag"] == tag]

    def por_classe(self, classe):
        return [e for e in self.elementos if classe in classes(e)]

    def por_id(self, ident):
        return [e for e in self.elementos if e["attrs"].get("id") == ident]

    def ids(self):
        return {e["attrs"]["id"] for e in self.elementos if e["attrs"].get("id")}


def classes(elemento):
    return elemento["attrs"].get("class", "").split()


def rotulo_acessivel(elemento):
    """Um elemento tem rótulo se traz texto visível, aria-label, aria-labelledby,
    title, ou um filho .sr-only (que é texto visível só para leitor de tela)."""
    atributos = elemento["attrs"]
    if elemento["texto"].strip():
        return True
    for chave in ("aria-label", "aria-labelledby", "title"):
        if atributos.get(chave, "").strip():
            return True
    return any("sr-only" in classes(f) for f in elemento["filhos"])


class Relatorio:
    def __init__(self):
        self.grupos = []
        self.falhas = 0

    def grupo(self, titulo):
        atual = {"titulo": titulo, "itens": []}
        self.grupos.append(atual)
        return atual

    def checar(self, grupo, condicao, descricao, detalhe=""):
        grupo["itens"].append((bool(condicao), descricao, detalhe))
        if not condicao:
            self.falhas += 1

    def imprimir(self):
        for grupo in self.grupos:
            print("\n" + grupo["titulo"])
            print("-" * len(grupo["titulo"]))
            for ok, descricao, detalhe in grupo["itens"]:
                marca = "[ok]  " if ok else "[FALHA]"
                print("%s %s" % (marca, descricao))
                if not ok and detalhe:
                    for linha in str(detalhe).splitlines():
                        print("        %s" % linha)


# -- verificações ------------------------------------------------------------


def verificar_documento(rel, doc):
    g = rel.grupo("Documento")

    html = doc.por_tag("html")
    rel.checar(g, html and html[0]["attrs"].get("lang") == "pt-BR",
               'idioma declarado como lang="pt-BR"',
               "encontrado: %s" % (html[0]["attrs"].get("lang") if html else "sem <html>"))

    titulo = doc.por_tag("title")
    rel.checar(g, titulo and titulo[0]["texto"].strip(), "<title> presente e não vazio")

    metas = {m["attrs"].get("name", ""): m["attrs"].get("content", "")
             for m in doc.por_tag("meta")}
    rel.checar(g, metas.get("description", "").strip(), '<meta name="description"> preenchida')
    rel.checar(g, "width=device-width" in metas.get("viewport", ""),
               "<meta viewport> com width=device-width (Padrão Mínimo: web responsivo)")
    rel.checar(g, any(m["attrs"].get("charset") for m in doc.por_tag("meta")),
               "<meta charset> declarado")


def verificar_skiplink(rel, doc):
    g = rel.grupo("Skip link e atalhos de teclado")

    skiplinks = doc.por_classe("br-skiplink")
    rel.checar(g, skiplinks, "nav.br-skiplink presente")
    if not skiplinks:
        return

    itens = [e for e in skiplinks[0]["filhos"] if e["tag"] == "a"]
    rel.checar(g, len(itens) == 4,
               "skip link com exatamente 4 itens", "encontrados: %d" % len(itens))

    encontrados = {e["attrs"].get("accesskey"): e["attrs"].get("href", "") for e in itens}
    for tecla, ancora, descricao in ANCORAS_SKIPLINK:
        href = encontrados.get(tecla, "")
        rel.checar(g, href == "#" + ancora,
                   'accesskey="%s" aponta para #%s (%s)' % (tecla, ancora, descricao),
                   "encontrado: %s" % (href or "ausente"))


def verificar_ancoras(rel, doc):
    g = rel.grupo("Âncoras obrigatórias do template base")
    ids = doc.ids()
    for _, ancora, descricao in ANCORAS_SKIPLINK:
        rel.checar(g, ancora in ids, 'id="%s" existe no documento (%s)' % (ancora, descricao))


def verificar_componentes(rel, doc, fonte_app):
    g = rel.grupo("Componentes do design system")

    for classe, descricao in [
        ("template-base", "template base"),
        ("br-header", "cabeçalho"),
        ("br-menu", "menu"),
        ("br-footer", "rodapé"),
    ]:
        rel.checar(g, doc.por_classe(classe), ".%s presente no index.html (%s)" % (classe, descricao))

    # O breadcrumb, os cards e as mensagens são construídos em tempo de execução
    # pelo app.js, então aqui a verificação é textual sobre o código-fonte.
    for classe, descricao in [
        ("br-breadcrumb", "trilha de navegação"),
        ("br-card", "cards"),
        ("br-button", "botões padronizados"),
        ("br-tag", "tags"),
        ("br-message", "mensagens de feedback"),
    ]:
        rel.checar(g, classe in fonte_app, "%s usado em app.js (%s)" % (classe, descricao))

    rel.checar(g, "menu-item" in fonte_app,
               "lista de tabelas montada como menu-item do br-menu")


def verificar_assets(rel, doc):
    g = rel.grupo("Assets vendorizados")

    referencias = []
    for elemento in doc.elementos:
        for chave in ("href", "src"):
            valor = elemento["attrs"].get(chave)
            if valor:
                referencias.append((elemento["tag"], valor))

    remotas = [(tag, url) for tag, url in referencias
               if url.startswith(("http://", "https://", "//"))
               and not any(host in url for host in HOSTS_PERMITIDOS)]
    rel.checar(g, not remotas,
               "nenhuma referência remota além de barra gov.br e VLibras",
               "\n".join("%s -> %s" % (t, u) for t, u in remotas))

    urls = " ".join(url for _, url in referencias)
    for caminho in ASSETS_ESPERADOS:
        nome = caminho.split("/")[-1]
        rel.checar(g, nome in urls, "%s referenciado no index.html" % nome)
        rel.checar(g, (SITE / caminho).exists(), "docs/%s existe no disco" % caminho)

    fontes = list((SITE / "assets" / "fonts").rglob("*.woff2")) if (SITE / "assets" / "fonts").exists() else []
    rel.checar(g, fontes, "fontes Rawline (.woff2) baixadas", "nenhum .woff2 em docs/assets/fonts/")

    webfonts = list((SITE / "assets" / "fontawesome").rglob("*.woff2")) if (SITE / "assets" / "fontawesome").exists() else []
    rel.checar(g, webfonts, "webfonts do Font Awesome baixados")


def verificar_institucional(rel, doc, fonte_index):
    g = rel.grupo("Elementos institucionais")

    rel.checar(g, doc.por_tag("barra-govbr"), "<barra-govbr> presente (barra do Governo Federal)")
    rel.checar(g, "barra.sistema.gov.br" in fonte_index,
               "barra carregada de barra.sistema.gov.br (a legada foi descontinuada)")
    rel.checar(g, "barra.brasil.gov.br" not in fonte_index,
               "barra legada barra.brasil.gov.br ausente")

    rel.checar(g, "vlibras-plugin.js" in fonte_index, "VLibras presente")
    rel.checar(g, "vw-access-button" in fonte_index, "botão de acesso do VLibras presente")

    logos = [e for e in doc.elementos
             if e["tag"] == "img" and "gov" in e["attrs"].get("src", "").lower()]
    rel.checar(g, logos, "logo gov.br no cabeçalho (Padrão Mínimo)")


def verificar_acessibilidade(rel, doc):
    g = rel.grupo("Acessibilidade (WCAG 2.2 AA — verificável estaticamente)")

    sem_alt = [e["attrs"].get("src", "?") for e in doc.por_tag("img")
               if "alt" not in e["attrs"]]
    rel.checar(g, not sem_alt, "toda <img> tem atributo alt", "\n".join(sem_alt))

    icones_expostos = [
        " ".join(classes(e)) for e in doc.elementos
        if e["tag"] == "i" and any(c.startswith("fa") for c in classes(e))
        and e["attrs"].get("aria-hidden") != "true"
    ]
    rel.checar(g, not icones_expostos,
               'todo ícone Font Awesome tem aria-hidden="true"', "\n".join(icones_expostos))

    sem_rotulo = []
    for elemento in doc.elementos:
        if elemento["tag"] not in INTERATIVOS:
            continue
        if elemento["icones"] and not rotulo_acessivel(elemento):
            sem_rotulo.append("<%s> com ícone e sem rótulo acessível" % elemento["tag"])
    rel.checar(g, not sem_rotulo,
               "todo elemento interativo só-ícone tem rótulo acessível", "\n".join(sem_rotulo))

    sem_label = []
    labels = {e["attrs"].get("for") for e in doc.por_tag("label")}
    for campo in doc.por_tag("input"):
        if campo["attrs"].get("type") in ("hidden", "submit", "button"):
            continue
        ident = campo["attrs"].get("id")
        if ident in labels:
            continue
        if campo["attrs"].get("aria-label") or campo["attrs"].get("aria-labelledby"):
            continue
        sem_label.append(ident or campo["attrs"].get("name") or "<input sem id>")
    rel.checar(g, not sem_label,
               "todo campo de formulário tem rótulo associado", "\n".join(sem_label))

    main = doc.por_tag("main")
    rel.checar(g, main, "landmark <main> presente")
    rel.checar(g, doc.por_tag("header"), "landmark <header> presente")
    rel.checar(g, doc.por_tag("footer"), "landmark <footer> presente")


def verificar_residuos(rel, fontes):
    g = rel.grupo("Resíduos da versão anterior")
    for padrao, descricao in RESIDUOS:
        encontrados = [nome for nome, conteudo in fontes.items()
                       if re.search(padrao, conteudo)]
        rel.checar(g, not encontrados, "sem resíduo de %s" % descricao,
                   "encontrado em: %s" % ", ".join(encontrados))


def verificar_funcionalidades(rel, fonte_app):
    """A adequação não pode custar funcionalidade. Estas são as capacidades que
    precisam sobreviver à troca da camada visual."""
    g = rel.grupo("Funcionalidades preservadas")
    for padrao, descricao in [
        (r"normalizar", "busca sem sensibilidade a acentos"),
        (r"aria-sort", "ordenação da grade anunciada por aria-sort"),
        (r"gerarDDL", "exportação de DDL"),
        (r"gerarCSV", "exportação de CSV"),
        (r"gerarMermaid", "exportação de Mermaid"),
        (r"hashchange", "roteamento por hash"),
        (r'ev\.key === "/"', "atalho / para focar a busca"),
        (r"calcularMapa", "mapa de relacionamentos"),
    ]:
        rel.checar(g, re.search(padrao, fonte_app), descricao)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    if not INDEX.exists():
        print("Não encontrei %s" % INDEX)
        return 1

    fonte_index = INDEX.read_text(encoding="utf-8")
    fonte_app = APP.read_text(encoding="utf-8") if APP.exists() else ""
    fonte_css = ESTILOS.read_text(encoding="utf-8") if ESTILOS.exists() else ""

    doc = Documento()
    doc.feed(fonte_index)

    rel = Relatorio()
    verificar_documento(rel, doc)
    verificar_skiplink(rel, doc)
    verificar_ancoras(rel, doc)
    verificar_componentes(rel, doc, fonte_app)
    verificar_assets(rel, doc)
    verificar_institucional(rel, doc, fonte_index)
    verificar_acessibilidade(rel, doc)
    verificar_residuos(rel, {
        "index.html": fonte_index,
        "app.js": fonte_app,
        "styles.css": fonte_css,
    })
    verificar_funcionalidades(rel, fonte_app)

    rel.imprimir()

    print("\nPadrão Mínimo — itens a confirmar visualmente")
    print("---------------------------------------------")
    for item in PADRAO_MINIMO:
        print("  - %s" % item)

    total = sum(len(g["itens"]) for g in rel.grupos)
    print("\n%d de %d verificações passaram." % (total - rel.falhas, total))
    if rel.falhas:
        print("%d falha(s). O site ainda não está aderente ao Padrão Digital." % rel.falhas)
        return 1
    print("Site aderente ao Padrão Digital de Governo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
