#!/usr/bin/env python3
"""Extrai o dicionário de dados do schema CAD_RECURSOS para JSON estruturado.

Gera dois arquivos:
  data/dicionario_recursos.json  fonte estruturada versionada (indentada, diff legível)
  docs/dados-recursos.js         mesmo conteúdo, minificado, como
                                 `window.DICIONARIO_RECURSOS = {...}`

Por que este extrator existe em vez de reaproveitar o extrair_pdf.py: o relatório
do Recursos foi gerado com um perfil enxuto do Oracle SQL Developer Data Modeler.
Ele traz apenas Table Name / Description / Notes / Columns / Columns Comments —
**não** traz as seções de índices, de chaves estrangeiras nem a volumetria que o
relatório do CAD_OCORRENCIA traz. Essas informações só existem no diagrama
relacional, num segundo PDF. O extrator lê os dois e cruza as duas fontes:

  fonte/CAD_Recursos_dicionario.pdf  tabelas, colunas, tipos lógicos, descrições
  fonte/CAD_Recursos_diagrama.pdf    PK/FK/índices e os tipos físicos Oracle

O formato de saída é idêntico ao do extrair_pdf.py, de propósito: o docs/app.js
consome os dois datasets sem nenhum ramo por schema. Ver documentacao/decisoes.md,
ADR-008 e ADR-009.

Uso: python3 tools/extrair_recursos.py
"""

import json
import re
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path

import pdfplumber

RAIZ = Path(__file__).resolve().parent.parent
PDF_DICIONARIO = RAIZ / "fonte" / "CAD_Recursos_dicionario.pdf"
PDF_DIAGRAMA = RAIZ / "fonte" / "CAD_Recursos_diagrama.pdf"
SAIDA_JSON = RAIZ / "data" / "dicionario_recursos.json"
SAIDA_JS = RAIZ / "docs" / "dados-recursos.js"

SCHEMA = "CAD_RECURSOS"

# Assinaturas de cabeçalho que identificam cada seção do documento.
CAB_COLUNAS = ("No", "Column Name", "PK", "FK", "M", "Data Type")
CAB_COMENTARIOS = ("No", "Column Name", "Description", "Notes")
# Rótulos do bloco de propriedades da tabela, todos sem conteúdo neste relatório
# exceto Table Name. Ficam registrados em `atributos` quando vêm preenchidos.
ROTULOS_PROPRIEDADES = (
    "Table Name",
    "Functional Name",
    "Abbreviation",
    "Classification Type Name",
    "Object Type Name",
    "MV Prebuilt",
    "MV Query",
)

# Sufixos que qualificam o papel de uma coluna em auto-relacionamentos. Retirá-los
# faz a coluna voltar ao nome da PK que ela referencia — é o que resolve
# HISTORICO_EQUIPE.ID_EQUIPE_RELACIONADA → EQUIPE.ID_EQUIPE.
SUFIXOS_DE_PAPEL = ("_RELACIONADA", "_RELACIONADO", "_ORIGEM", "_DESTINO", "_PAI", "_ANTERIOR")


class ErroExtracao(Exception):
    pass


# --------------------------------------------------------------------------- #
# Utilitários de texto
# --------------------------------------------------------------------------- #


def texto_fluido(valor):
    """Desfaz a quebra de linha que o gerador do PDF aplicou ao parágrafo.

    O relatório foi diagramado pelo Apache FOP, que quebra o texto na largura da
    célula. As quebras são de layout, não de conteúdo, então viram espaço.

    A exceção é a linha terminada em hífen. O FOP roda sem dicionário de
    hifenização, então ele nunca inventa um hífen para quebrar uma palavra: o
    hífen no fim da linha já estava no texto, e é ali que ele preferiu quebrar.
    Emendar sem espaço é o certo — é o que devolve "cad-servico",
    "SINESP-CAD" e "SINESP-Segurança" inteiros.
    """
    valor = (valor or "").strip()
    if not valor:
        return None
    linhas = [re.sub(r"[ \t]+", " ", l).strip() for l in valor.split("\n")]
    linhas = [l for l in linhas if l]
    if not linhas:
        return None
    saida = linhas[0]
    for linha in linhas[1:]:
        if saida.endswith("-"):
            saida += linha
        else:
            saida += " " + linha
    return saida


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


def ou_nulo(valor):
    valor = (valor or "").strip()
    return valor or None


def campo(linha, indice):
    return linha[indice] if indice < len(linha) else ""


# --------------------------------------------------------------------------- #
# PDF do dicionário
# --------------------------------------------------------------------------- #


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
    """Bloco 'Columns'.

    Cabeçalho de 11 células: No | Column Name | PK | FK | M | Data Type |
    DT kind | Domain Name | Formula (Default Value) | Security | Abbreviation.
    O valor padrão da coluna vem na célula 8, a mesma que o relatório do
    CAD_OCORRENCIA usa para a fórmula — é o campo que a grade do app exibe como
    "Padrão".
    """
    for linha in linhas[1:]:
        tabela["colunas"].append(
            OrderedDict(
                no=int(campo(linha, 0)) if campo(linha, 0).isdigit() else None,
                nome=campo(linha, 1),
                pk=campo(linha, 2) == "P",
                fk=campo(linha, 3) == "F",
                obrigatoria=campo(linha, 4) == "Y",
                tipo=ou_nulo(campo(linha, 5)),
                tipo_fisico=None,  # preenchido pelo diagrama
                dt_kind=ou_nulo(campo(linha, 6)),
                dominio=ou_nulo(campo(linha, 7)),
                formula=ou_nulo(campo(linha, 8)),
                seguranca=ou_nulo(campo(linha, 9)),
                abreviacao=ou_nulo(campo(linha, 10)),
                descricao=None,
                notas=None,
            )
        )


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
            anterior["descricao"] = texto_fluido(
                " ".join(filter(None, [anterior["descricao"], campo(linha, 2)]))
            )
            continue
        coluna = por_chave.get((numero, nome)) or por_nome.get(nome)
        if coluna is None:
            raise ErroExtracao(
                f"{tabela['nome']}: comentário sem coluna correspondente ({numero}, {nome})"
            )
        coluna["descricao"] = texto_fluido(campo(linha, 2))
        coluna["notas"] = texto_fluido(campo(linha, 3))
        anterior = coluna


# Altura da faixa do rodapé ("SERPRO … Oracle Data Modeler | Page: n / N"), que
# não faz parte de nenhuma tabela.
ALTURA_RODAPE = 45


def fechar_ultima_linha(pagina):
    """Devolve a linha horizontal que falta para fechar a tabela na quebra de página.

    Quando uma linha de tabela é cortada pelo fim da página, o PDF não desenha a
    borda de baixo dela — e o find_tables(), que trabalha pelas bordas, descarta
    a linha inteira. Foi assim que a descrição de EQUIPAMENTO.ID_AGENCIA sumiu na
    primeira versão deste extrator, e o trecho que continuava na página seguinte
    acabou colado na coluna anterior.

    A correção é oferecer ao find_tables() uma borda logo abaixo do último texto
    da página, fora do rodapé. A coordenada sai do conteúdo, não de um número
    fixo: colada demais no texto ela não fecha a célula, e longe demais o
    pdfplumber deixa de juntá-la à tabela.
    """
    limite = pagina.height - ALTURA_RODAPE
    fundos = [p["bottom"] for p in pagina.extract_words() if p["bottom"] < limite]
    return [max(fundos) + 4] if fundos else []


def extrair_dicionario(caminho_pdf):
    tabelas = []
    metadados = OrderedDict()
    atual = None
    desconhecidos = []
    textos = {}

    with pdfplumber.open(caminho_pdf) as pdf:
        total_paginas = len(pdf.pages)
        for indice, pagina in enumerate(pdf.pages, start=1):
            textos[indice] = pagina.extract_text() or ""
            ajuste = {"explicit_horizontal_lines": fechar_ultima_linha(pagina)}
            for bruta in pagina.find_tables(table_settings=ajuste):
                linhas = normalizar(bruta.extract())
                if not linhas:
                    continue
                cab = assinatura(linhas)

                if cab[0] == "Design Name":
                    metadados.update((l[0], l[1]) for l in linhas if len(l) == 2 and l[1])
                elif cab[0] == "Table Name":
                    atual = nova_tabela(cab[1], indice)
                    tabelas.append(atual)
                    atual["atributos"].update(
                        (l[0], l[1])
                        for l in linhas[1:]
                        if len(l) == 2 and l[1] and l[0] in ROTULOS_PROPRIEDADES
                    )
                elif atual is None:
                    desconhecidos.append((indice, cab))
                elif cab[0] in ("Description", "Notes"):
                    for linha in linhas:
                        if len(linha) == 2 and linha[1]:
                            chave = "descricao" if linha[0] == "Description" else "notas"
                            atual[chave] = texto_fluido(linha[1])
                elif cab[: len(CAB_COLUNAS)] == CAB_COLUNAS:
                    ler_colunas(atual, linhas)
                elif cab[: len(CAB_COMENTARIOS)] == CAB_COMENTARIOS:
                    atual["_comentarios"].extend(linhas[1:])
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
        # O relatório não traz volumetria; o número de colunas é o único valor
        # conhecido e serve à validação cruzada com o diagrama.
        tabela["volumetria"] = OrderedDict(
            numero_colunas=len(tabela["colunas"]),
            linhas_min=None,
            linhas_max=None,
            linhas_esperadas=None,
            crescimento_esperado=None,
            intervalo_crescimento=None,
        )
    return metadados, tabelas, total_paginas, textos


# --------------------------------------------------------------------------- #
# PDF do diagrama
# --------------------------------------------------------------------------- #

# Uma linha de coluna do diagrama começa com os marcadores de papel: P (primary
# key), F (foreign key) e * (obrigatória). O gerador ora os emite grudados
# ("PF*"), ora separados ("P", "*") — daí o casamento por token.
RE_MARCADOR = re.compile(r"^P?F?\*?$")
RE_CONSTRAINT = re.compile(r"^([A-Z][A-Z0-9_]*)\s*\(([^)]*)\)$")


def agrupar_linhas(palavras, tolerancia=4.0):
    """Agrupa palavras em linhas visuais pelo topo, tolerando o ruído do render."""
    linhas = []
    for palavra in sorted(palavras, key=lambda w: (w["top"], w["x0"])):
        if linhas and abs(palavra["top"] - linhas[-1][0]["top"]) <= tolerancia:
            linhas[-1].append(palavra)
        else:
            linhas.append([palavra])
    return [sorted(linha, key=lambda w: w["x0"]) for linha in linhas]


def ler_caixa(linhas):
    """Lê uma caixa de tabela do diagrama: título, colunas e constraints."""
    nome = None
    colunas = []
    constraints = OrderedDict()

    for linha in linhas:
        textos = [w["text"] for w in linha]
        junto = " ".join(textos)

        if nome is None:
            if junto.startswith(SCHEMA + "."):
                nome = junto.split(".", 1)[1]
            continue

        casado = RE_CONSTRAINT.match(junto)
        if casado:
            # A mesma constraint aparece nos dois compartimentos da caixa
            # (chaves e índices); o dicionário ordenado deduplica por nome.
            constraints.setdefault(
                casado.group(1),
                [c.strip() for c in casado.group(2).split(",") if c.strip()],
            )
            continue

        marcadores = ""
        while textos and RE_MARCADOR.match(textos[0]) and textos[0]:
            marcadores += textos.pop(0)
        if not textos:
            continue
        colunas.append(
            OrderedDict(
                nome=textos.pop(0),
                pk="P" in marcadores,
                fk="F" in marcadores,
                obrigatoria="*" in marcadores,
                tipo_fisico=" ".join(textos) or None,
            )
        )

    if nome is None:
        raise ErroExtracao("caixa do diagrama sem título CAD_RECURSOS.<TABELA>")
    return nome, colunas, constraints


def extrair_diagrama(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        if len(pdf.pages) != 1:
            raise ErroExtracao(
                f"diagrama com {len(pdf.pages)} páginas; o leitor pressupõe uma só"
            )
        pagina = pdf.pages[0]
        palavras = pagina.extract_words()
        # Cada tabela é desenhada como um retângulo com traço. O retângulo de
        # fundo da página é descartado pelo limite de largura.
        caixas = [
            r
            for r in pagina.rects
            if r.get("stroke") and 60 < r["width"] < pagina.width * 0.8 and r["height"] > 30
        ]

    diagrama = OrderedDict()
    for caixa in sorted(caixas, key=lambda r: (r["top"], r["x0"])):
        dentro = [
            w
            for w in palavras
            if caixa["x0"] - 2 <= w["x0"]
            and w["x1"] <= caixa["x0"] + caixa["width"] + 2
            and caixa["top"] - 2 <= w["top"]
            and w["bottom"] <= caixa["top"] + caixa["height"] + 2
        ]
        if not dentro:
            continue
        nome, colunas, constraints = ler_caixa(agrupar_linhas(dentro))
        if nome in diagrama:
            raise ErroExtracao(f"tabela {nome} desenhada duas vezes no diagrama")
        diagrama[nome] = OrderedDict(colunas=colunas, constraints=constraints)

    if not diagrama:
        raise ErroExtracao("nenhuma caixa de tabela reconhecida no diagrama")
    return diagrama


# --------------------------------------------------------------------------- #
# Cruzamento das duas fontes
# --------------------------------------------------------------------------- #


def resolver_destino(origem, nome_fk, colunas_fk, pks):
    """Descobre a tabela de destino de uma FK.

    O diagrama nomeia a constraint e lista as colunas de origem, mas não diz para
    onde ela aponta. As três regras abaixo cobrem o modelo inteiro; o que não
    casar por nenhuma delas vira erro de extração, nunca um destino chutado.
    """
    chave = tuple(sorted(colunas_fk))

    # 1. As colunas da FK são exatamente a PK de alguma tabela.
    if chave in pks:
        return pks[chave]

    # 2. Idem, depois de tirar o sufixo que marca o papel da coluna.
    def sem_papel(coluna):
        for sufixo in SUFIXOS_DE_PAPEL:
            if coluna.endswith(sufixo) and len(coluna) > len(sufixo):
                return coluna[: -len(sufixo)]
        return coluna

    chave_papel = tuple(sorted(sem_papel(c) for c in colunas_fk))
    if chave_papel in pks:
        return pks[chave_papel]

    # 3. O resto do nome da constraint, tirados o prefixo FK_ e o nome da origem,
    #    é o nome da tabela de destino.
    resto = nome_fk[3:] if nome_fk.startswith("FK_") else nome_fk
    for prefixo in (origem + "_", ""):
        candidato = resto[len(prefixo):] if resto.startswith(prefixo) else None
        if candidato and candidato in pks.values():
            return candidato

    raise ErroExtracao(
        f"{origem}: não foi possível resolver o destino da FK {nome_fk} "
        f"({', '.join(colunas_fk)})"
    )


def cruzar(tabelas, diagrama):
    """Traz do diagrama o tipo físico, os índices e os relacionamentos."""
    por_nome = {t["nome"]: t for t in tabelas}

    faltando = sorted(set(por_nome) - set(diagrama))
    sobrando = sorted(set(diagrama) - set(por_nome))
    if faltando or sobrando:
        raise ErroExtracao(
            "dicionário e diagrama divergem: só no dicionário "
            f"{faltando or '—'}; só no diagrama {sobrando or '—'}"
        )

    # Tipo físico Oracle, coluna a coluna.
    for nome, caixa in diagrama.items():
        tabela = por_nome[nome]
        tipos = {c["nome"]: c["tipo_fisico"] for c in caixa["colunas"]}
        for coluna in tabela["colunas"]:
            if coluna["nome"] not in tipos:
                raise ErroExtracao(
                    f"{nome}.{coluna['nome']}: coluna do dicionário ausente no diagrama"
                )
            coluna["tipo_fisico"] = tipos[coluna["nome"]]

    # Chaves primárias, para resolver o destino das FKs.
    pks = {}
    for nome, caixa in diagrama.items():
        colunas = [c["nome"] for c in caixa["colunas"] if c["pk"]]
        if not colunas:
            raise ErroExtracao(f"{nome}: sem chave primária no diagrama")
        pks[tuple(sorted(colunas))] = nome
    ordem_pk = {
        nome: [c["nome"] for c in caixa["colunas"] if c["pk"]]
        for nome, caixa in diagrama.items()
    }

    for nome, caixa in diagrama.items():
        tabela = por_nome[nome]
        obrigatorias = {c["nome"] for c in caixa["colunas"] if c["obrigatoria"]}

        for constraint, colunas in caixa["constraints"].items():
            if constraint.startswith("FK_"):
                destino = resolver_destino(nome, constraint, colunas, pks)
                tabela["fks_saida"].append(
                    OrderedDict(
                        nome=constraint,
                        tabela=destino,
                        obrigatoria=all(c in obrigatorias for c in colunas),
                        transferivel=True,
                        em_arco=False,
                        colunas=list(colunas),
                        colunas_referidas=list(ordem_pk[destino]),
                        regra_exclusao=None,
                    )
                )
            else:
                # PK_ e UK_ são índices únicos; IX_ o diagrama não qualifica.
                estado = "PK" if constraint.startswith("PK_") else (
                    "UN" if constraint.startswith("UK_") else None
                )
                tabela["indices"].append(
                    OrderedDict(
                        nome=constraint,
                        estado=estado,
                        funcional=False,
                        espacial=False,
                        expressao=None,
                        colunas=[
                            OrderedDict(nome=coluna, ordem="ASC") for coluna in colunas
                        ],
                    )
                )

    # O lado "referred from" não existe no diagrama: é o espelho do lado de saída.
    for tabela in tabelas:
        for fk in tabela["fks_saida"]:
            espelho = OrderedDict(fk)
            espelho["tabela"] = tabela["nome"]
            por_nome[fk["tabela"]]["fks_entrada"].append(espelho)

    for tabela in tabelas:
        tabela["indices"].sort(key=lambda i: i["nome"])
        tabela["fks_saida"].sort(key=lambda f: f["nome"])
        tabela["fks_entrada"].sort(key=lambda f: (f["tabela"], f["nome"]))


# --------------------------------------------------------------------------- #
# Validação
# --------------------------------------------------------------------------- #


# Começo de uma linha do bloco "Columns", que tem a mesma cara de uma linha do
# bloco "Columns Comments" — "<nº> <COLUNA> …" — e precisa ser distinguida dela.
RE_LINHA_DE_TIPO = re.compile(
    r"^(?:P\s+)?(?:F\s+)?(?:Y\s+)?"
    r"(?:NUMERIC|VARCHAR2?|NUMBER|Date|Timestamp|TIMESTAMP|DATE|CHAR|CLOB|BLOB|RAW)\b"
)


def validar_comentarios(tabelas, textos):
    """Confere as descrições lidas contra o texto cru das páginas.

    O find_tables() lê pelas bordas desenhadas e, por isso, é sensível a linhas
    cortadas pela quebra de página. Esta checagem não depende das bordas: se o
    texto da página traz uma linha de comentário para a coluna, a descrição tem
    que ter chegado ao JSON. É o alarme que faltava quando ID_AGENCIA sumiu.
    """
    erros = []
    for tabela in tabelas:
        cru = "\n".join(textos.get(p, "") for p in tabela["paginas"])
        for coluna in tabela["colunas"]:
            if coluna["descricao"]:
                continue
            padrao = re.compile(
                r"^\s*%d\s+%s\s+(\S.*)$" % (coluna["no"], re.escape(coluna["nome"])),
                re.MULTILINE,
            )
            for casado in padrao.finditer(cru):
                if not RE_LINHA_DE_TIPO.match(casado.group(1)):
                    erros.append(
                        "%s.%s: o PDF descreve a coluna (%r) mas a descrição não "
                        "foi extraída" % (tabela["nome"], coluna["nome"],
                                          casado.group(1)[:60])
                    )
                    break
    return erros


def validar(tabelas, diagrama, textos):
    """Assertivas de integridade: qualquer regressão na extração falha o build."""
    erros = validar_comentarios(tabelas, textos)
    nomes = {t["nome"] for t in tabelas}

    for tabela in tabelas:
        esperado = tabela["volumetria"].get("numero_colunas")
        obtido = len(tabela["colunas"])
        if esperado != obtido:
            erros.append(f"{tabela['nome']}: declara {esperado} colunas, extraídas {obtido}")
        if not tabela["colunas"]:
            erros.append(f"{tabela['nome']}: nenhuma coluna extraída")
        if tabela["schema"] != SCHEMA:
            erros.append(f"{tabela['nome']}: schema inesperado {tabela['schema']}")

        colunas_diagrama = diagrama[tabela["nome"]]["colunas"]
        if len(colunas_diagrama) != obtido:
            erros.append(
                f"{tabela['nome']}: {obtido} colunas no dicionário, "
                f"{len(colunas_diagrama)} no diagrama"
            )
        marcada_pk = {c["nome"] for c in colunas_diagrama if c["pk"]}
        marcada_fk = {c["nome"] for c in colunas_diagrama if c["fk"]}

        for coluna in tabela["colunas"]:
            if not coluna["nome"] or not coluna["tipo"]:
                erros.append(f"{tabela['nome']}: coluna incompleta {coluna}")
            if not coluna["tipo_fisico"]:
                erros.append(f"{tabela['nome']}.{coluna['nome']}: sem tipo físico")
            # As duas fontes marcam PK/FK de forma independente; divergência é
            # sinal de que uma delas foi lida errado.
            if coluna["pk"] != (coluna["nome"] in marcada_pk):
                erros.append(f"{tabela['nome']}.{coluna['nome']}: marcação de PK divergente")
            if coluna["fk"] != (coluna["nome"] in marcada_fk):
                erros.append(f"{tabela['nome']}.{coluna['nome']}: marcação de FK divergente")

        colunas_da_tabela = {c["nome"] for c in tabela["colunas"]}
        for indice in tabela["indices"]:
            for coluna in indice["colunas"]:
                if coluna["nome"] not in colunas_da_tabela:
                    erros.append(
                        f"{tabela['nome']}: índice {indice['nome']} cita coluna "
                        f"inexistente {coluna['nome']}"
                    )
        for fk in tabela["fks_saida"] + tabela["fks_entrada"]:
            if fk["tabela"] not in nomes:
                erros.append(
                    f"{tabela['nome']}: FK {fk['nome']} aponta para tabela "
                    f"desconhecida {fk['tabela']}"
                )
            if len(fk["colunas"]) != len(fk["colunas_referidas"]):
                erros.append(f"{tabela['nome']}: FK {fk['nome']} com colunas desbalanceadas")
        for fk in tabela["fks_saida"]:
            for coluna in fk["colunas"]:
                if coluna not in colunas_da_tabela:
                    erros.append(
                        f"{tabela['nome']}: FK {fk['nome']} cita coluna "
                        f"inexistente {coluna}"
                    )

    # Toda FK tem que aparecer nas duas visões: saída na origem, entrada no destino.
    saida = {(t["nome"], fk["nome"], fk["tabela"]) for t in tabelas for fk in t["fks_saida"]}
    entrada = {(fk["tabela"], fk["nome"], t["nome"]) for t in tabelas for fk in t["fks_entrada"]}
    for origem, nome, destino in sorted(saida ^ entrada):
        erros.append(f"FK {nome} ({origem} → {destino}) declarada só de um lado")

    if erros:
        for erro in erros:
            print(f"  {erro}", file=sys.stderr)
        raise ErroExtracao(f"{len(erros)} inconsistência(s) na extração")


def montar_documento(metadados, tabelas, total_paginas):
    tabelas.sort(key=lambda t: t["nome"])
    return OrderedDict(
        meta=OrderedDict(
            titulo="Dicionário de Dados — SINESP CAD 2",
            subtitulo="Schema CAD_RECURSOS",
            design=metadados.get("Design Name"),
            modelo=metadados.get("Model Name"),
            versao_pdf=metadados.get("Version Date"),
            arquivo_fonte=PDF_DICIONARIO.name,
            arquivo_diagrama=PDF_DIAGRAMA.name,
            paginas_pdf=total_paginas,
            gerado_em=date.today().isoformat(),
            total_tabelas=len(tabelas),
            total_colunas=sum(len(t["colunas"]) for t in tabelas),
            total_relacionamentos=sum(len(t["fks_saida"]) for t in tabelas),
        ),
        tabelas=tabelas,
    )


def main():
    for caminho in (PDF_DICIONARIO, PDF_DIAGRAMA):
        if not caminho.exists():
            sys.exit(f"PDF não encontrado: {caminho}")

    print(f"Lendo {PDF_DICIONARIO.relative_to(RAIZ)} e {PDF_DIAGRAMA.relative_to(RAIZ)}…")
    try:
        metadados, tabelas, total_paginas, textos = extrair_dicionario(PDF_DICIONARIO)
        diagrama = extrair_diagrama(PDF_DIAGRAMA)
        cruzar(tabelas, diagrama)
        validar(tabelas, diagrama, textos)
    except ErroExtracao as erro:
        sys.exit(f"Falha na extração: {erro}")

    documento = montar_documento(metadados, tabelas, total_paginas)

    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JS.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    compacto = json.dumps(documento, ensure_ascii=False, separators=(",", ":"))
    SAIDA_JS.write_text(
        "// Gerado por tools/extrair_recursos.py — não edite à mão.\n"
        f"window.DICIONARIO_RECURSOS = {compacto};\n",
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
