#!/usr/bin/env python3
"""Baixa os arquivos do Padrão Digital de Governo para docs/assets/.

O site não usa CDN: a própria documentação do DS recomenda baixar os arquivos
localmente, e vendorizar mantém o site imune a indisponibilidade de terceiros
(ver documentacao/decisoes.md, ADR-003).

A estrutura de pastas replica a das origens de propósito. O `rawline.css` aponta
para `../font/` e o `all.min.css` do Font Awesome aponta para `../webfonts/`;
mantendo o CSS dentro de um subdiretório `css/`, esses caminhos relativos
resolvem sem precisar reescrever nada.

Da Rawline são gerados apenas os @font-face dos pesos em uso, com `src` reduzido
a woff2 — o arquivo oficial declara 18 variantes em cinco formatos cada, o que
traria ~2 MB de eot/ttf/svg que nenhum navegador suportado chega a requisitar.

Uso: python tools/baixar_assets_ds.py
"""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "docs" / "assets"

# Versões travadas. Ao atualizar, mexa só aqui e rode o script de novo.
VERSAO_CORE = "3.7.0"          # última estável; a v4 segue em `next` desde 2024
VERSAO_FONTAWESOME = "5.11.2"  # versão que o DS especifica; o core usa .fa-w-*, .fad e .fal, do FA5

BASE_CORE = "https://cdn.jsdelivr.net/npm/@govbr-ds/core@%s/dist" % VERSAO_CORE
BASE_RAWLINE = "https://cdngovbr-ds.estaleiro.serpro.gov.br/design-system/fonts/rawline"
BASE_FA = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/%s" % VERSAO_FONTAWESOME

# Pesos da Rawline efetivamente usados pelo site e pelos componentes do core.
# Cada variante custa ~80 KB, então os extremos (100/200/800/900) ficam de fora:
# só aparecem em classes utilitárias que este site não usa, e na falta delas o
# navegador sintetiza. O itálico também sai — o core tem uma única regra
# font-style:italic e o conteúdo do dicionário não usa itálico.
PESOS_RAWLINE = ["300", "400", "500", "600", "700"]

# Famílias do Font Awesome. `brands` entra porque componentes do DS usam `fab`.
FAMILIAS_FA = ["fa-solid-900", "fa-regular-400", "fa-brands-400"]

CABECALHO_RAWLINE = """/* Fonte Rawline — tipografia oficial do Padrão Digital de Governo.
 *
 * Derivado de %s/css/rawline.css,
 * restrito aos pesos em uso e ao formato woff2. Gerado por
 * tools/baixar_assets_ds.py — não edite à mão.
 */
""" % BASE_RAWLINE

MOLDE_FONT_FACE = """
@font-face {
  font-family: "rawline";
  src: url("../font/rawline-%(variante)s.woff2") format("woff2");
  font-weight: %(peso)s;
  font-style: %(estilo)s;
  font-display: swap;
}
"""


class ErroDownload(Exception):
    pass


def baixar(url):
    requisicao = urllib.request.Request(url, headers={"User-Agent": "dicionario-cad3/1.0"})
    try:
        with urllib.request.urlopen(requisicao, timeout=60) as resposta:
            return resposta.read()
    except urllib.error.HTTPError as erro:
        raise ErroDownload("%s -> HTTP %s" % (url, erro.code))
    except urllib.error.URLError as erro:
        raise ErroDownload("%s -> %s" % (url, erro.reason))


def gravar(destino, conteudo):
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(conteudo)
    relativo = destino.relative_to(RAIZ).as_posix()
    print("  %-52s %7.1f KB" % (relativo, len(conteudo) / 1024))
    return len(conteudo)


def filtrar_rawline(css_original):
    """Reduz o CSS oficial aos pesos em uso, só com woff2.

    Cada @font-face do arquivo original declara a variante no nome do arquivo
    (`rawline-400i.woff2`), que é o que identifica peso e estilo de forma
    confiável — o campo font-weight sozinho não distingue normal de itálico.
    """
    blocos = re.findall(r"@font-face\s*\{.*?\}", css_original, re.DOTALL)
    if not blocos:
        raise ErroDownload("nenhum @font-face encontrado no rawline.css de origem")

    partes = [CABECALHO_RAWLINE]
    vistos = set()
    for bloco in blocos:
        achado = re.search(r'url\("\.\./font/rawline-(\d{3}i?)\.woff2"\)', bloco)
        if not achado:
            continue
        variante = achado.group(1)
        if variante not in PESOS_RAWLINE or variante in vistos:
            continue
        vistos.add(variante)
        partes.append(MOLDE_FONT_FACE % {
            "variante": variante,
            "peso": variante.rstrip("i"),
            "estilo": "italic" if variante.endswith("i") else "normal",
        })

    faltando = [p for p in PESOS_RAWLINE if p not in vistos]
    if faltando:
        raise ErroDownload("pesos ausentes no rawline.css de origem: %s" % ", ".join(faltando))

    return "".join(partes).encode("utf-8")


def baixar_core():
    print("\ngov.br DS core %s" % VERSAO_CORE)
    total = 0
    for nome in ("core.min.css", "core-init.min.js"):
        total += gravar(ASSETS / "govbr" / nome, baixar("%s/%s" % (BASE_CORE, nome)))
    return total


def baixar_rawline():
    print("\nFonte Rawline (pesos %s)" % ", ".join(PESOS_RAWLINE))
    original = baixar("%s/css/rawline.css" % BASE_RAWLINE).decode("utf-8", "replace")
    total = gravar(ASSETS / "fonts" / "rawline" / "css" / "rawline.css", filtrar_rawline(original))
    for variante in PESOS_RAWLINE:
        nome = "rawline-%s.woff2" % variante
        total += gravar(ASSETS / "fonts" / "rawline" / "font" / nome,
                        baixar("%s/font/%s" % (BASE_RAWLINE, nome)))
    return total


def baixar_fontawesome():
    print("\nFont Awesome %s" % VERSAO_FONTAWESOME)
    total = gravar(ASSETS / "fontawesome" / "css" / "all.min.css",
                   baixar("%s/css/all.min.css" % BASE_FA))
    for familia in FAMILIAS_FA:
        nome = "%s.woff2" % familia
        total += gravar(ASSETS / "fontawesome" / "webfonts" / nome,
                        baixar("%s/webfonts/%s" % (BASE_FA, nome)))
    return total


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    print("Baixando os assets do Padrão Digital de Governo para docs/assets/")
    try:
        total = baixar_core() + baixar_rawline() + baixar_fontawesome()
    except ErroDownload as erro:
        print("\nFalhou: %s" % erro)
        return 1

    print("\nTotal vendorizado: %.1f KB" % (total / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
