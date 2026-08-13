#!/usr/bin/env python3
"""Extrai o dicionário de dados do CAD 3 (schema CAD_OCORRENCIA) do PDF do
Oracle SQL Developer Data Modeler para JSON estruturado.

Gera dois arquivos:
  data/dicionario.json  fonte estruturada versionada (indentada, diff legível)
  docs/dados.js         mesmo conteúdo, minificado, como `window.DICIONARIO = {...}`

O PDF desenha as seções como tabelas com bordas reais, então cada bloco é lido
via pdfplumber.find_tables() e classificado pela assinatura do cabeçalho. Uma
tabela do dicionário pode atravessar várias páginas: o cabeçalho da seção é
repetido em cada página, e as linhas são acumuladas na tabela corrente.

Uso: python3 tools/extrair_pdf.py [caminho-do-pdf]
"""

import json
import re
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path

import pdfplumber

RAIZ = Path(__file__).resolve().parent.parent
PDF_PADRAO = RAIZ / "fonte" / "Dicionario_CAD_Ocorrencia.pdf"
SAIDA_JSON = RAIZ / "data" / "dicionario.json"
SAIDA_JS = RAIZ / "docs" / "dados.js"

# Assinaturas de cabeçalho que identificam cada seção do documento.
CAB_COLUNAS = ("No", "Column Name", "PK", "FK", "M", "Data Type")
CAB_COMENTARIOS = ("No", "Column Name", "Description", "Notes")
CAB_INDICES = ("Index Name", "State")
CAB_FK_SAIDA = ("Name", "Refering To")  # grafia do documento original
CAB_FK_ENTRADA = ("Name", "Referred From")
CAB_CONSTRAINTS = ("Type", "Column / Constraint Name", "Details")

CHAVES_VOLUMETRIA = {
    "Number Of Columns": "numero_colunas",
    "Number Of Rows Min.": "linhas_min",
    "Number Of Rows Max.": "linhas_max",
    "Expected Number Of Rows": "linhas_esperadas",
    "Expected Growth": "crescimento_esperado",
    "Growth Interval": "intervalo_crescimento",
}


class ErroExtracao(Exception):
    pass


def normalizar(linhas):
    """Remove colunas totalmente vazias e limpa espaços das células.

    Algumas tabelas do PDF vêm com colunas-fantasma nas bordas (células None em
    todas as linhas), o que deslocaria a classificação pelo cabeçalho.
    """
    if not linhas:
        return []
    largura = max(len(l) for l in linhas)
    linhas = [list(l) + [None] * (largura - len(l)) for l in linhas]
    manter = [i for i in range(largura) if any((l[i] or "").strip() for l in linhas)]
    return [[re.sub(r"[ \t]+", " ", (l[i] or "")).strip() for i in manter] for l in linhas]


def assinatura(linhas):
    return tuple(c.replace("\n", " ") for c in linhas[0])


def partes(celula):
    """Célula multi-linha vira lista de valores não vazios."""
    return [p.strip() for p in (celula or "").split("\n") if p.strip()]


def ou_nulo(valor):
    valor = (valor or "").strip()
    return valor or None


def campo(linha, indice):
    return linha[indice] if indice < len(linha) else ""


def nova_tabela(nome_completo, pagina):
    schema, _, nome = nome_completo.rpartition(".")
    return OrderedDict(
        nome=nome or nome_completo,
        schema=schema or None,
        nome_completo=nome_completo,
        descricao=None,
        notas=None,
        atributos=OrderedDict(),
        volumetria=OrderedDict(),
        colunas=[],
        _comentarios=[],
        indices=[],
        fks_saida=[],
        fks_entrada=[],
        constraints=[],
        paginas=[pagina],
    )


def ler_colunas(tabela, linhas):
    for linha in linhas[1:]:
        tabela["colunas"].append(
            OrderedDict(
                no=int(campo(linha, 0)) if campo(linha, 0).isdigit() else None,
                nome=campo(linha, 1),
                pk=campo(linha, 2) == "P",
                fk=campo(linha, 3) == "F",
                obrigatoria=campo(linha, 4) == "Y",
                tipo=ou_nulo(campo(linha, 5)),
                dt_kind=ou_nulo(campo(linha, 6)),
                dominio=ou_nulo(campo(linha, 7)),
                formula=ou_nulo(campo(linha, 8)),
                seguranca=ou_nulo(campo(linha, 9)),
                abreviacao=ou_nulo(campo(linha, 10)),
                descricao=None,
                notas=None,
            )
        )


def ler_indices(tabela, linhas):
    for linha in linhas[1:]:
        colunas = [
            OrderedDict(nome=nome, ordem=ordem)
            for nome, ordem in zip(
                partes(campo(linha, 5)),
                partes(campo(linha, 6)) or [""] * len(partes(campo(linha, 5))),
            )
        ]
        if not campo(linha, 0) and tabela["indices"]:
            # Continuação de um índice composto: só traz mais colunas.
            tabela["indices"][-1]["colunas"].extend(colunas)
            continue
        tabela["indices"].append(
            OrderedDict(
                nome=campo(linha, 0),
                estado=ou_nulo(campo(linha, 1)),
                funcional=campo(linha, 2) == "Y",
                espacial=campo(linha, 3) == "Y",
                expressao=ou_nulo(campo(linha, 4)),
                colunas=colunas,
            )
        )


def ler_fks(tabela, linhas, chave):
    for linha in linhas[1:]:
        if not campo(linha, 0) and tabela[chave]:
            tabela[chave][-1]["colunas"].extend(partes(campo(linha, 5)))
            tabela[chave][-1]["colunas_referidas"].extend(partes(campo(linha, 6)))
            continue
        tabela[chave].append(
            OrderedDict(
                nome=campo(linha, 0),
                tabela=campo(linha, 1),
                obrigatoria=campo(linha, 2) == "Y",
                transferivel=campo(linha, 3) == "Y",
                em_arco=campo(linha, 4) == "Y",
                colunas=partes(campo(linha, 5)),
                colunas_referidas=partes(campo(linha, 6)),
                regra_exclusao=ou_nulo(campo(linha, 7)),
            )
        )


def ler_constraints(tabela, linhas):
    """Bloco de check constraints: o texto vem espalhado entre linhas/células.

    Uma linha com o tipo preenchido abre um bloco; as seguintes complementam o
    nome do alvo (célula 1) ou acrescentam detalhes (célula 2).
    """
    for linha in linhas[1:]:
        tipo, alvo, detalhe = campo(linha, 0), campo(linha, 1), campo(linha, 2)
        if tipo or not tabela["constraints"]:
            tabela["constraints"].append(
                OrderedDict(tipo=tipo or None, alvo=alvo, detalhes=[])
            )
        elif alvo:
            atual = tabela["constraints"][-1]
            atual["alvo"] = (atual["alvo"] + " " + alvo).strip()
        atual = tabela["constraints"][-1]
        for parte in partes(detalhe):
            if parte not in atual["detalhes"]:
                atual["detalhes"].append(parte)


def extrair(caminho_pdf):
    tabelas = []
    metadados = OrderedDict()
    atual = None
    desconhecidos = []

    with pdfplumber.open(caminho_pdf) as pdf:
        total_paginas = len(pdf.pages)
        for indice, pagina in enumerate(pdf.pages, start=1):
            for bruta in pagina.find_tables():
                linhas = normalizar(bruta.extract())
                if not linhas:
                    continue
                cab = assinatura(linhas)

                if cab[0] == "Design Name":
                    metadados.update(
                        (l[0], l[1]) for l in linhas if len(l) == 2 and l[1]
                    )
                elif cab[0] == "Table Name":
                    atual = nova_tabela(cab[1], indice)
                    tabelas.append(atual)
                    atual["atributos"].update(
                        (l[0], l[1]) for l in linhas[1:] if len(l) == 2 and l[1]
                    )
                elif atual is None:
                    desconhecidos.append((indice, cab))
                elif cab[0] in ("Description", "Notes"):
                    for linha in linhas:
                        if len(linha) == 2 and linha[1]:
                            chave = "descricao" if linha[0] == "Description" else "notas"
                            atual[chave] = linha[1]
                elif cab[0] in CHAVES_VOLUMETRIA:
                    for linha in linhas:
                        if len(linha) == 2 and linha[0] in CHAVES_VOLUMETRIA:
                            valor = linha[1]
                            atual["volumetria"][CHAVES_VOLUMETRIA[linha[0]]] = (
                                int(valor) if valor.lstrip("-").isdigit() else valor
                            )
                elif cab[: len(CAB_COLUNAS)] == CAB_COLUNAS:
                    ler_colunas(atual, linhas)
                elif cab[: len(CAB_COMENTARIOS)] == CAB_COMENTARIOS:
                    atual["_comentarios"].extend(linhas[1:])
                elif cab[: len(CAB_INDICES)] == CAB_INDICES:
                    ler_indices(atual, linhas)
                elif cab[: len(CAB_FK_SAIDA)] == CAB_FK_SAIDA:
                    ler_fks(atual, linhas, "fks_saida")
                elif cab[: len(CAB_FK_ENTRADA)] == CAB_FK_ENTRADA:
                    ler_fks(atual, linhas, "fks_entrada")
                elif cab[: len(CAB_CONSTRAINTS)] == CAB_CONSTRAINTS:
                    ler_constraints(atual, linhas)
                else:
                    desconhecidos.append((indice, cab))

                if atual is not None and indice not in atual["paginas"]:
                    atual["paginas"].append(indice)

    if desconhecidos:
        for pagina, cab in desconhecidos:
            print(f"  seção não reconhecida na página {pagina}: {cab}", file=sys.stderr)
        raise ErroExtracao(f"{len(desconhecidos)} seção(ões) não reconhecida(s)")

    for tabela in tabelas:
        aplicar_comentarios(tabela)
    return metadados, tabelas, total_paginas


def aplicar_comentarios(tabela):
    """Casa o bloco 'Columns Comments' com as colunas.

    O PDF omite a linha de comentário das colunas sem descrição, então o
    casamento é feito por (nº, nome) e não por posição.
    """
    por_chave = {(c["no"], c["nome"]): c for c in tabela["colunas"]}
    por_nome = {c["nome"]: c for c in tabela["colunas"]}
    anterior = None
    for linha in tabela.pop("_comentarios"):
        numero = int(campo(linha, 0)) if campo(linha, 0).isdigit() else None
        nome = campo(linha, 1)
        if numero is None and not nome:
            # Descrição que transbordou a quebra de página: continua a anterior.
            if anterior is None or not campo(linha, 2):
                continue
            anterior["descricao"] = "\n".join(
                filter(None, [anterior["descricao"], campo(linha, 2)])
            )
            continue
        coluna = por_chave.get((numero, nome)) or por_nome.get(nome)
        if coluna is None:
            raise ErroExtracao(
                f"{tabela['nome']}: comentário sem coluna correspondente ({numero}, {nome})"
            )
        coluna["descricao"] = ou_nulo(campo(linha, 2))
        coluna["notas"] = ou_nulo(campo(linha, 3))
        anterior = coluna


def validar(tabelas):
    """Assertivas de integridade: qualquer regressão na extração falha o build."""
    erros = []
    nomes = {t["nome"] for t in tabelas}

    for tabela in tabelas:
        esperado = tabela["volumetria"].get("numero_colunas")
        obtido = len(tabela["colunas"])
        if esperado is None:
            erros.append(f"{tabela['nome']}: sem 'Number Of Columns'")
        elif esperado != obtido:
            erros.append(
                f"{tabela['nome']}: declara {esperado} colunas, extraídas {obtido}"
            )
        if not tabela["colunas"]:
            erros.append(f"{tabela['nome']}: nenhuma coluna extraída")
        for coluna in tabela["colunas"]:
            if not coluna["nome"] or not coluna["tipo"]:
                erros.append(f"{tabela['nome']}: coluna incompleta {coluna}")
        for fk in tabela["fks_saida"] + tabela["fks_entrada"]:
            if fk["tabela"] not in nomes:
                erros.append(
                    f"{tabela['nome']}: FK {fk['nome']} aponta para tabela desconhecida {fk['tabela']}"
                )
            if len(fk["colunas"]) != len(fk["colunas_referidas"]):
                erros.append(
                    f"{tabela['nome']}: FK {fk['nome']} com colunas desbalanceadas"
                )

    # Cada FK é declarada dos dois lados no documento ("referring to" na origem,
    # "referred by" no destino). As duas visões têm que fechar exatamente.
    saida = {(t["nome"], fk["nome"], fk["tabela"]) for t in tabelas for fk in t["fks_saida"]}
    entrada = {(fk["tabela"], fk["nome"], t["nome"]) for t in tabelas for fk in t["fks_entrada"]}
    for origem, nome, destino in sorted(saida ^ entrada):
        erros.append(f"FK {nome} ({origem} → {destino}) declarada só de um lado")

    if erros:
        for erro in erros:
            print(f"  {erro}", file=sys.stderr)
        raise ErroExtracao(f"{len(erros)} inconsistência(s) na extração")


def montar_documento(metadados, tabelas, caminho_pdf, total_paginas):
    tabelas.sort(key=lambda t: t["nome"])
    return OrderedDict(
        meta=OrderedDict(
            titulo="Dicionário de Dados — SINESP CAD 3",
            subtitulo="Schema CAD_OCORRENCIA",
            design=metadados.get("Design Name"),
            modelo=metadados.get("Model Name"),
            versao_pdf=metadados.get("Version Date"),
            arquivo_fonte=caminho_pdf.name,
            paginas_pdf=total_paginas,
            gerado_em=date.today().isoformat(),
            total_tabelas=len(tabelas),
            total_colunas=sum(len(t["colunas"]) for t in tabelas),
            total_relacionamentos=sum(len(t["fks_saida"]) for t in tabelas),
        ),
        tabelas=tabelas,
    )


def main():
    caminho_pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else PDF_PADRAO
    if not caminho_pdf.exists():
        sys.exit(f"PDF não encontrado: {caminho_pdf}")

    print(f"Lendo {caminho_pdf}…")
    try:
        metadados, tabelas, total_paginas = extrair(caminho_pdf)
        validar(tabelas)
    except ErroExtracao as erro:
        sys.exit(f"Falha na extração: {erro}")

    documento = montar_documento(metadados, tabelas, caminho_pdf, total_paginas)

    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JS.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    compacto = json.dumps(documento, ensure_ascii=False, separators=(",", ":"))
    SAIDA_JS.write_text(
        "// Gerado por tools/extrair_pdf.py — não edite à mão.\n"
        f"window.DICIONARIO = {compacto};\n",
        encoding="utf-8",
    )

    meta = documento["meta"]
    print(
        f"{meta['total_tabelas']} tabelas / {meta['total_colunas']} colunas / "
        f"{meta['total_relacionamentos']} relacionamentos"
    )
    print(f"  {SAIDA_JSON.relative_to(RAIZ)} ({SAIDA_JSON.stat().st_size // 1024} KB)")
    print(f"  {SAIDA_JS.relative_to(RAIZ)} ({SAIDA_JS.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
