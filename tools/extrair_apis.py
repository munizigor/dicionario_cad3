#!/usr/bin/env python3
"""Extrai a documentação das APIs do CAD para JSON estruturado.

Gera dois arquivos:
  data/apis.json        fonte estruturada versionada (indentada, diff legível)
  docs/dados-apis.js    mesmo conteúdo, minificado, como `window.APIS = {...}`

Lê duas fontes, que descrevem APIs diferentes e complementares, sem nenhum
endpoint em comum (ADR-011):

  fonte/api_agente_operacional.json  OpenAPI 3 do serviço consumido pelo
                                     aplicativo do agente operacional
  fonte/api_sistemas_externos.md     documentação em Markdown das APIs para
                                     sistemas externos integrados

As duas saem no mesmo formato: cada endpoint vira uma lista de blocos (os mesmos
que docs/guias.js usa: p, subtitulo, tabela, codigo, lista, nota), e o
docs/app.js os desenha sem saber de qual fonte vieram. Nos textos, `trecho`
vira código, **trecho** vira negrito e [rótulo](api:destino) vira link interno.

Os avisos de revisão (divergências e lacunas das fontes) ficam neste arquivo, em
AVISOS_API e AVISOS_ENDPOINT. Os que dependem só da fonte, como a contagem de
campos sem descrição, são calculados a cada execução, para continuarem
verdadeiros quando a fonte for atualizada.

Uso: python3 tools/extrair_apis.py
"""

import json
import re
import sys
import unicodedata
from collections import Counter, OrderedDict
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE_OPENAPI = RAIZ / "fonte" / "api_agente_operacional.json"
FONTE_MARKDOWN = RAIZ / "fonte" / "api_sistemas_externos.md"
SAIDA_JSON = RAIZ / "data" / "apis.json"
SAIDA_JS = RAIZ / "docs" / "dados-apis.js"

ORDEM_METODOS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

# Entidades tratadas pelas duas APIs. Cada página de endpoint de uma delas
# remete aos endpoints da outra que tratam da mesma entidade.
ENTIDADES = OrderedDict([
    ("unidades-servico", {
        "nome": "Unidades de Serviço e equipes",
        "descricao": "O Agente Operacional consulta o cabeçalho da Unidade de Serviço e opera as "
                     "equipes (status, detalhe, listagens); a API de Sistemas Externos cobre o "
                     "ciclo de vida completo da Unidade de Serviço e das suas equipes."
    }),
    ("pessoas", {
        "nome": "Pessoas",
        "descricao": "O Agente Operacional pesquisa pessoas e consulta perfis; a API de Sistemas "
                     "Externos também cria, altera e exclui pessoas e consulta cargos."
    }),
    ("equipamentos", {
        "nome": "Equipamentos",
        "descricao": "O Agente Operacional pesquisa equipamentos por placa e prefixo; a API de "
                     "Sistemas Externos também cria, altera e exclui equipamentos."
    }),
    ("posicoes", {
        "nome": "Posições geográficas",
        "descricao": "O Agente Operacional recebe a localização das equipes; a API de Sistemas "
                     "Externos consulta as últimas posições e o histórico."
    }),
])

# Tag do OpenAPI → entidade. As duas operações de localização das equipes são
# exceção: ficam com as posições, não com as equipes.
ENTIDADE_POR_TAG = {
    "Unidades de Serviço": "unidades-servico",
    "Equipes": "unidades-servico",
    "Pessoas": "pessoas",
    "Equipamentos": "equipamentos",
}
ENTIDADE_POR_OPERACAO = {
    ("PUT", "/equipes/{uuid}/localizacao"): "posicoes",
    ("POST", "/equipes/localizacoes"): "posicoes",
}
# Seção "## API de X" do Markdown → entidade.
ENTIDADE_POR_SECAO = {
    "API de Unidade de Serviço": "unidades-servico",
    "API de Pessoa": "pessoas",
    "API de Equipamento": "equipamentos",
    "API de Posições": "posicoes",
}

# Avisos de revisão escritos à mão, por API. Os calculados se somam a estes.
AVISOS_API = {
    "sistemas-externos": [
        "A paginação segue três convenções: `pagina` começando em 1 (Unidades de Serviço), "
        "`numeroPagina` começando em 0 (Equipamentos e Pessoas) e `numeroPagina` começando em 1 "
        "(Posições), com padrões e máximos diferentes em cada uma.",
        "Datas aparecem em dois formatos (`YYYY-MM-DD` na listagem de Unidades de Serviço, "
        "`dd/MM/yyyy` nas Posições) e as datas e horas não informam fuso.",
        "A situação aparece em quatro estilos: siglas (`AT`, `ES`), `ATIVO`, `EM_SERVICO` e `Ativa`.",
        "O documento não explica como o sistema integrado é identificado, embora exista o erro "
        "“Sistema integrado não encontrado”, e não documenta respostas 401, 403 nem 500.",
        "O documento não tem data nem versão próprias, e o histórico de alterações não é datado.",
    ],
}

# Avisos de revisão escritos à mão, por endpoint: (método, caminho completo).
AVISOS_ENDPOINT = {
    ("POST", "/agente-campo/v3/cad-posicoes-api/pesquisar-posicoes-historico"):
        "O filtro `uuidPessoa` é descrito de forma contraditória: a tabela de parâmetros diz que "
        "ele filtra as posições da pessoa, e a tabela de comportamentos diz que vêm as posições de "
        "todas as equipes acessíveis.",
    ("PUT", "/agente-campo/v3/cad-pessoa-api/alterar-pessoa/{uuid}"):
        "O endpoint permite trocar o `cpf` e o `registroFuncional`, mas não documenta os erros de "
        "duplicidade que o Criar Pessoa documenta.",
    ("POST", "/agente-campo/v3/cad-unidade-servico-api/{uuidUnidadeServico}/criar-equipe"):
        "Aqui as pessoas são identificadas por CPF; no Vincular Pessoa à Equipe, por UUID.",
    ("POST", "/agente-campo/v3/cad-unidade-servico-api/criar-unidade-servico"):
        "Só a modalidade 1 (Outros) é explicada; o documento não lista as demais, e o exemplo "
        "usa a 2.",
    ("POST", "/equipes/{uuid}/indicador-agente"):
        "O resumo no Swagger é só “Indicador Agente”; o identificador da operação é "
        "`iniciarServicoOperador`.",
}


def falhar(mensagem):
    print("ERRO: " + mensagem, file=sys.stderr)
    sys.exit(1)


def slug(texto):
    """Minúsculas, sem acento, palavras separadas por hífen."""
    texto = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", texto)  # camelCase → camel-Case
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def ancora_github(titulo):
    """Âncora no estilo do GitHub, que é a usada nos links internos do Markdown."""
    texto = titulo.strip().lower()
    texto = re.sub(r"[^\w\- ]", "", texto)
    return texto.replace(" ", "-")


def ordenar_endpoints(lista):
    return sorted(lista, key=lambda e: (e["caminho"], ORDEM_METODOS.index(e["metodo"])))


# ---------------------------------------------------------------------------
# OpenAPI (Agente Operacional)
# ---------------------------------------------------------------------------

def rotulo_tipo(esquema, componentes):
    """Tipo legível de um esquema OpenAPI, sem expandir objetos."""
    if "$ref" in esquema:
        return "Objeto " + esquema["$ref"].rsplit("/", 1)[-1]
    tipo = esquema.get("type")
    formato = esquema.get("format")
    if tipo == "array":
        return "Lista de " + rotulo_tipo(esquema.get("items", {}), componentes)
    if tipo == "string":
        return {"uuid": "UUID", "date-time": "Data/hora", "date": "Data"}.get(formato, "Texto")
    if tipo == "integer":
        return "Inteiro"
    if tipo == "number":
        return "Número"
    if tipo == "boolean":
        return "Booleano"
    if tipo == "object":
        return "Objeto"
    return tipo or "Não declarado"


def resolver(esquema, componentes):
    if "$ref" in esquema:
        nome = esquema["$ref"].rsplit("/", 1)[-1]
        return nome, componentes[nome]
    return None, esquema


def linhas_campos(esquema, componentes, prefixo="", visitados=(), profundidade=0):
    """Achata um esquema em linhas [campo, tipo, obrigatório, descrição]."""
    nome, esquema = resolver(esquema, componentes)
    if esquema.get("type") == "array" and not esquema.get("properties"):
        return linhas_campos(esquema.get("items", {}), componentes, prefixo + "[]",
                             visitados, profundidade)
    if nome in visitados or profundidade > 5:
        return []
    visitados = visitados + ((nome,) if nome else ())
    obrigatorios = set(esquema.get("required", []))
    linhas = []
    for campo, sub in esquema.get("properties", {}).items():
        caminho = (prefixo + "." if prefixo else "") + campo
        descricao = sub.get("description", "")
        valores = sub.get("enum") or sub.get("items", {}).get("enum")
        if valores:
            descricao = (descricao + " " if descricao else "") + \
                "Valores: " + ", ".join("`%s`" % v for v in valores) + "."
        linhas.append([caminho, rotulo_tipo(sub, componentes),
                       "Sim" if campo in obrigatorios else "", descricao])
        alvo_nome, alvo = resolver(sub, componentes)
        if sub.get("type") == "array":
            alvo_nome, alvo = resolver(sub.get("items", {}), componentes)
            caminho += "[]"
        if alvo.get("properties"):
            linhas.extend(linhas_campos(alvo, componentes, caminho, visitados,
                                        profundidade + 1) if not alvo_nome else
                          linhas_campos({"$ref": "#/components/schemas/" + alvo_nome},
                                        componentes, caminho, visitados, profundidade + 1))
    return linhas


def tabela_campos(linhas):
    return {"tipo": "tabela", "colunas": ["Campo", "Tipo", "Obrigatório", "Descrição"],
            "codigo": [0], "linhas": linhas}


def extrair_openapi(caminho):
    doc = json.loads(caminho.read_text(encoding="utf-8"))
    info = doc["info"]
    componentes = doc.get("components", {}).get("schemas", {})
    servidor = (doc.get("servers") or [{}])[0].get("url", "")

    operacoes = [(m.upper(), p, o) for p, x in doc["paths"].items() for m, o in x.items()
                 if m.upper() in ORDEM_METODOS]

    endpoints = []
    for metodo, rota, op in operacoes:
        tag = (op.get("tags") or ["Sem grupo"])[0]
        op_id = op.get("operationId", "")
        ident = slug(op_id) if op_id and not re.search(r"_\d+$", op_id) else slug(metodo + " " + rota)

        blocos = []
        if op.get("description"):
            blocos.append({"tipo": "p", "texto": op["description"]})

        parametros = op.get("parameters", [])
        headers = [q["name"] for q in parametros if q.get("in") == "header"]
        blocos.append({"tipo": "subtitulo", "texto": "Parâmetros"})
        if parametros:
            onde = {"header": "Header", "path": "Caminho", "query": "Query"}
            blocos.append({"tipo": "tabela", "codigo": [0],
                           "colunas": ["Nome", "Onde", "Obrigatório", "Tipo", "Descrição"],
                           "linhas": [[q["name"], onde.get(q.get("in"), q.get("in")),
                                       "Sim" if q.get("required") else "Não",
                                       rotulo_tipo(q.get("schema", {}), componentes),
                                       q.get("description", "")] for q in parametros]})
        else:
            blocos.append({"tipo": "p", "texto": "Nenhum parâmetro declarado."})
        if not headers:
            blocos.append({"tipo": "p", "texto":
                           "Nenhum header de identificação (`cpf`, `nome`, `sinesp-username`) "
                           "é declarado para esta operação."})

        corpo = op.get("requestBody", {}).get("content", {})
        if corpo:
            tipo_conteudo, conteudo = next(iter(corpo.items()))
            esquema = conteudo.get("schema", {})
            blocos.append({"tipo": "subtitulo", "texto": "Corpo da requisição"})
            blocos.append({"tipo": "p", "texto": "`%s`, esquema `%s`." % (
                tipo_conteudo, rotulo_tipo(esquema, componentes).replace("Objeto ", ""))})
            linhas = linhas_campos(esquema, componentes)
            blocos.append(tabela_campos(linhas) if linhas else
                          {"tipo": "p", "texto": "O esquema não declara campos."})

        blocos.append({"tipo": "subtitulo", "texto": "Respostas"})
        for codigo, resposta in op.get("responses", {}).items():
            conteudo = resposta.get("content", {})
            if not conteudo:
                blocos.append({"tipo": "p", "texto": "**%s**: sem corpo declarado." % codigo})
                continue
            tipo_conteudo, c = next(iter(conteudo.items()))
            esquema = c.get("schema", {})
            blocos.append({"tipo": "p", "texto": "**%s**: `%s`, %s." % (
                codigo, tipo_conteudo, rotulo_tipo(esquema, componentes))})
            linhas = linhas_campos(esquema, componentes)
            if linhas:
                blocos.append(tabela_campos(linhas))

        avisos = []
        if metodo == "DELETE" and corpo:
            avisos.append("Este DELETE exige corpo na requisição. A semântica de corpo em DELETE "
                          "não é definida pelo HTTP, e proxies e clientes costumam descartá-lo.")
        if (metodo, rota) in AVISOS_ENDPOINT:
            avisos.append(AVISOS_ENDPOINT[(metodo, rota)])

        endpoints.append({
            "slug": ident, "metodo": metodo, "caminho": rota,
            "titulo": op.get("summary") or op_id, "grupo": tag,
            "entidade": ENTIDADE_POR_OPERACAO.get((metodo, rota), ENTIDADE_POR_TAG.get(tag)),
            "operation_id": op_id, "avisos": avisos, "blocos": blocos,
        })

    # Avisos calculados sobre a especificação inteira.
    props = [(n, p, v) for n, s in componentes.items() for p, v in s.get("properties", {}).items()]
    descritos = sum(1 for *_, v in props if v.get("description"))
    com_obrigatorios = sum(1 for s in componentes.values() if s.get("required"))
    codigos = Counter(c for *_, o in operacoes for c in o.get("responses", {}))
    sem_header = sum(1 for *_, o in operacoes
                     if not any(q.get("in") == "header" for q in o.get("parameters", [])))
    avisos_api = []
    if set(codigos) <= {"200"}:
        avisos_api.append("Todas as %d operações declaram só a resposta 200, sem nenhum formato de "
                          "erro." % len(operacoes))
    avisos_api.append("Só %d dos %d campos dos esquemas %s descrição, e só %d dos %d esquemas "
                      "declaram campos obrigatórios. Nas tabelas, a coluna Obrigatório vazia quer "
                      "dizer não declarado, não opcional." % (
                          descritos, len(props), "tem" if descritos == 1 else "têm",
                          com_obrigatorios, len(componentes)))
    if not doc.get("components", {}).get("securitySchemes"):
        avisos_api.append("Nenhum mecanismo de autenticação é declarado, e %d operações não "
                          "declaram header de identificação. A autenticação pode ficar num "
                          "gateway, mas isso não está escrito." % sem_header)
    genericos = [o.get("operationId") for *_, o in operacoes
                 if re.search(r"_\d+$", o.get("operationId", ""))]
    if genericos:
        avisos_api.append("%d operações têm identificador genérico gerado automaticamente "
                          "(%s)." % (len(genericos), ", ".join("`%s`" % g for g in genericos)))
    if "Generated server url" in json.dumps(doc.get("servers", [])):
        avisos_api.append("O servidor declarado (`%s`) é o gerado automaticamente pelo framework, "
                          "apontando para homologação." % servidor)

    combinacoes = Counter(tuple(q["name"] for q in o.get("parameters", []) if q.get("in") == "header")
                          for *_, o in operacoes)
    visao = [
        {"tipo": "p", "texto": info.get("description", "")},
        {"tipo": "subtitulo", "texto": "Servidor"},
        {"tipo": "codigo", "texto": servidor},
        {"tipo": "subtitulo", "texto": "Headers de identificação"},
        {"tipo": "p", "texto": "O Swagger declara os headers operação por operação, e eles não "
                               "são os mesmos em todas:"},
        {"tipo": "tabela", "colunas": ["Headers declarados", "Operações"],
         "linhas": [[", ".join("`%s`" % h for h in hs) or "Nenhum", str(n)]
                    for hs, n in combinacoes.most_common()]},
    ]

    contagem = Counter(e["grupo"] for e in endpoints)
    grupos = [{"nome": g, "endpoints": [e["slug"] for e in ordenar_endpoints(
        [e for e in endpoints if e["grupo"] == g])]}
        for g in sorted(contagem, key=lambda g: (-contagem[g], g))]

    return {
        "slug": "agente-operacional",
        "titulo": "Agente Operacional",
        "subtitulo": info["title"],
        "descricao": "Serviços consumidos pelo aplicativo do agente operacional: chamados, "
                     "ocorrências, empenhos, equipes e consultas de apoio.",
        "versao": info.get("version"),
        "formato": "OpenAPI " + doc.get("openapi", ""),
        "base": servidor,
        "fonte": FONTE_OPENAPI.name,
        "avisos": avisos_api,
        "visao": visao,
        "grupos": grupos,
        "endpoints": endpoints,
    }


# ---------------------------------------------------------------------------
# Markdown (Sistemas Externos)
# ---------------------------------------------------------------------------

RE_ENDPOINT = re.compile(r"^\*\*Endpoint:\*\*\s*`(GET|POST|PUT|PATCH|DELETE)\s+([^`]+)`")
RE_LINK = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")


def blocos_markdown(linhas, resolver_link):
    """Converte linhas de Markdown nos blocos do site. Cobre o que a fonte usa:
    parágrafos, títulos, tabelas, blocos de código, citações e listas."""
    blocos = []
    i = 0

    def inline(texto):
        return RE_LINK.sub(lambda m: "[%s](%s)" % (m.group(1), resolver_link(m.group(2))), texto)

    while i < len(linhas):
        linha = linhas[i]
        if not linha.strip() or linha.strip() == "---":
            i += 1
            continue
        if linha.startswith("```"):
            fim = i + 1
            while fim < len(linhas) and not linhas[fim].startswith("```"):
                fim += 1
            blocos.append({"tipo": "codigo", "texto": "\n".join(linhas[i + 1:fim])})
            i = fim + 1
            continue
        if re.match(r"^#{1,2}\s", linha):
            # Títulos de documento e de seção já viraram estrutura (API, grupo).
            i += 1
            continue
        titulo = re.match(r"^(#{3,6})\s+(.*)", linha)
        if titulo:
            nivel = 3 if len(titulo.group(1)) <= 4 else 4
            blocos.append({"tipo": "subtitulo", "nivel": nivel, "texto": inline(titulo.group(2))})
            i += 1
            continue
        if linha.startswith("|"):
            tabela = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tabela.append(linhas[i])
                i += 1
            celulas = [[inline(c.strip()) for c in t.strip().strip("|").split("|")] for t in tabela]
            corpo = [c for c in celulas[1:] if not all(re.fullmatch(r":?-+:?", x) for x in c)]
            blocos.append({"tipo": "tabela", "colunas": celulas[0], "linhas": corpo})
            continue
        if linha.startswith(">"):
            trecho = []
            while i < len(linhas) and linhas[i].startswith(">"):
                trecho.append(linhas[i][1:].strip())
                i += 1
            # Itens de lista dentro da citação viram lista de verdade na nota.
            itens = [inline(re.sub(r"^[-*]\s+", "", t)) for t in trecho if re.match(r"^[-*]\s+", t)]
            texto = "\n".join(t for t in trecho if t and not re.match(r"^[-*]\s+", t))
            m = re.match(r"^\*\*([^*]+?):?\*\*:?\s*(.*)", texto, re.S)
            titulo_nota, corpo_nota = (m.group(1).rstrip(":") + ".", m.group(2)) if m else ("Nota.", texto)
            nota = {"tipo": "nota", "nivel": "info", "titulo": inline(titulo_nota),
                    "texto": inline(corpo_nota.strip())}
            if itens:
                nota["itens"] = itens
            blocos.append(nota)
            continue
        if re.match(r"^\s*[-*]\s+", linha):
            itens = []
            while i < len(linhas) and re.match(r"^\s*[-*]\s+", linhas[i]):
                itens.append(inline(re.sub(r"^\s*[-*]\s+", "", linhas[i])))
                i += 1
            blocos.append({"tipo": "lista", "itens": itens})
            continue
        paragrafo = []
        while (i < len(linhas) and linhas[i].strip() and not linhas[i].startswith(("```", "|", ">", "#"))
               and not re.match(r"^\s*[-*]\s+", linhas[i])):
            paragrafo.append(linhas[i].strip())
            i += 1
        if not paragrafo:
            falhar("linha de Markdown não reconhecida: %r" % linha)
        blocos.append({"tipo": "p", "texto": inline(" ".join(paragrafo))})
    return blocos


def secoes(linhas, nivel):
    """Divide em seções pelo título do nível dado: [(título, linhas)]."""
    prefixo = "#" * nivel + " "
    resultado, atual, corpo = [], None, []
    for linha in linhas:
        if linha.startswith(prefixo):
            if atual is not None or corpo:
                resultado.append((atual, corpo))
            atual, corpo = linha[len(prefixo):].strip(), []
        else:
            corpo.append(linha)
    resultado.append((atual, corpo))
    return resultado


def extrair_markdown(caminho, endpoints_openapi):
    texto = caminho.read_text(encoding="utf-8")
    linhas = texto.splitlines()

    # Primeira passada: endpoints e suas âncoras, para resolver os links.
    ancoras = {}
    titulo_atual = None
    for linha in linhas:
        if linha.startswith("### "):
            titulo_atual = linha[4:].strip()
        m = RE_ENDPOINT.match(linha)
        if m and titulo_atual:
            ancoras[ancora_github(titulo_atual)] = "sistemas-externos/" + slug(titulo_atual)

    def resolver_link(ancora):
        return "api:" + ancoras.get(ancora, "sistemas-externos")

    titulo_doc = linhas[0].lstrip("# ").strip()
    visao, grupos, endpoints = [], [], []
    for titulo, corpo in secoes(linhas, 2):
        if titulo is None:
            # Cabeçalho do documento: a descrição e a citação de referência.
            visao.extend(b for b in blocos_markdown(corpo, resolver_link))
            continue
        if titulo == "Índice":
            continue
        if not titulo.startswith("API de "):
            visao.append({"tipo": "subtitulo", "nivel": 2, "texto": titulo})
            visao.extend(blocos_markdown(corpo, resolver_link))
            continue

        entidade = ENTIDADE_POR_SECAO.get(titulo)
        if not entidade:
            falhar("seção %r sem entidade em ENTIDADE_POR_SECAO" % titulo)
        grupo = {"nome": titulo.replace("API de ", ""), "endpoints": []}
        atual = None
        for sub_titulo, sub_corpo in secoes(corpo, 3):
            alvo = next((RE_ENDPOINT.match(l) for l in sub_corpo if RE_ENDPOINT.match(l)), None)
            if alvo:
                metodo, rota = alvo.group(1), alvo.group(2).strip()
                sem_endpoint = [l for l in sub_corpo if not RE_ENDPOINT.match(l)]
                atual = {
                    "slug": slug(sub_titulo), "metodo": metodo, "caminho": rota,
                    "titulo": sub_titulo, "grupo": grupo["nome"], "entidade": entidade,
                    "avisos": [], "blocos": blocos_markdown(sem_endpoint, resolver_link),
                }
                endpoints.append(atual)
                grupo["endpoints"].append(atual["slug"])
            elif sub_titulo in ("Base URL", "Endpoints") or sub_titulo is None:
                base = re.search(r"```\s*\n(.*?)\n```", "\n".join(sub_corpo), re.S)
                if base:
                    grupo["base"] = base.group(1).strip()
            elif atual:
                # Subseção que pertence ao endpoint anterior (ex.: a tabela de
                # situações dentro da listagem de Unidades de Serviço).
                atual["blocos"].append({"tipo": "subtitulo", "nivel": 3, "texto": sub_titulo})
                atual["blocos"].extend(blocos_markdown(sub_corpo, resolver_link))
        grupos.append(grupo)

    slugs = Counter(e["slug"] for e in endpoints)
    repetidos = [s for s, n in slugs.items() if n > 1]
    if repetidos:
        falhar("endpoints com o mesmo título no Markdown: %s" % ", ".join(repetidos))

    for e in endpoints:
        texto_ep = json.dumps(e["blocos"], ensure_ascii=False)
        if "{0}" in texto_ep:
            e["avisos"].append("A mensagem de erro documentada traz `{0}` literal, sem o valor "
                               "preenchido: ou o servidor não substitui o parâmetro, ou o "
                               "documento copiou o modelo da mensagem.")
        if (e["metodo"], e["caminho"]) in AVISOS_ENDPOINT:
            e["avisos"].append(AVISOS_ENDPOINT[(e["metodo"], e["caminho"])])

    avisos = []
    referencia = re.search(r"especificação OpenAPI \*([^*]+)\* \S+ versão \*\*([^*]+)\*\*", texto)
    comuns = {(e["metodo"], e["caminho"]) for e in endpoints} & \
             {(e["metodo"], e["caminho"]) for e in endpoints_openapi}
    if referencia and not comuns:
        avisos.append("O documento diz estar alinhado à especificação OpenAPI “%s” %s, mas não "
                      "tem nenhum endpoint em comum com ela: aquela especificação descreve a API "
                      "do Agente Operacional. Esta API não tem contrato OpenAPI publicado aqui, e "
                      "o conteúdo não pôde ser conferido contra um." % referencia.groups())
    avisos.extend(AVISOS_API.get("sistemas-externos", []))

    return {
        "slug": "sistemas-externos",
        "titulo": "Sistemas Externos",
        "subtitulo": titulo_doc,
        "descricao": "APIs para sistemas externos integrados: Unidades de Serviço e equipes, "
                     "equipamentos, pessoas e posições geográficas, sujeitas ao compartilhamento "
                     "de dados por agência.",
        "versao": None,
        "formato": "Markdown",
        "base": "/agente-campo/v3",
        "fonte": FONTE_MARKDOWN.name,
        "avisos": avisos,
        "visao": visao,
        "grupos": grupos,
        "endpoints": endpoints,
    }


def validar(apis):
    usados = {(e["metodo"], e["caminho"]) for a in apis for e in a["endpoints"]}
    soltos = [k for k in AVISOS_ENDPOINT if k not in usados]
    if soltos:
        falhar("AVISOS_ENDPOINT cita endpoints que não existem nas fontes: %s" % soltos)
    for api in apis:
        slugs = [e["slug"] for e in api["endpoints"]]
        if len(slugs) != len(set(slugs)):
            falhar("slugs repetidos na API %s" % api["slug"])
        for e in api["endpoints"]:
            if e["entidade"] and e["entidade"] not in ENTIDADES:
                falhar("entidade desconhecida %r em %s" % (e["entidade"], e["slug"]))
    # Toda entidade precisa aparecer nas duas APIs, senão a remissão não faz sentido.
    for chave in ENTIDADES:
        presentes = [a["slug"] for a in apis if any(e["entidade"] == chave for e in a["endpoints"])]
        if len(presentes) != len(apis):
            falhar("a entidade %r só aparece em %s" % (chave, presentes))


def main():
    for fonte in (FONTE_OPENAPI, FONTE_MARKDOWN):
        if not fonte.exists():
            falhar("fonte não encontrada: %s" % fonte)
    openapi = extrair_openapi(FONTE_OPENAPI)
    markdown = extrair_markdown(FONTE_MARKDOWN, openapi["endpoints"])
    apis = [openapi, markdown]
    validar(apis)

    documento = OrderedDict([
        ("meta", OrderedDict([
            ("titulo", "APIs do CAD"),
            ("gerado_em", date.today().isoformat()),
            ("total_apis", len(apis)),
            ("total_endpoints", sum(len(a["endpoints"]) for a in apis)),
        ])),
        ("entidades", [dict(slug=k, **v) for k, v in ENTIDADES.items()]),
        ("apis", apis),
    ])

    SAIDA_JSON.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compacto = json.dumps(documento, ensure_ascii=False, separators=(",", ":"))
    SAIDA_JS.write_text(
        "/* Gerado por tools/extrair_apis.py. Não editar à mão. */\n"
        "window.APIS = %s;\n" % compacto, encoding="utf-8")

    for api in apis:
        print("%-20s %3d endpoints em %d grupos, %d avisos gerais, %d endpoints com aviso" % (
            api["slug"], len(api["endpoints"]), len(api["grupos"]), len(api["avisos"]),
            sum(1 for e in api["endpoints"] if e["avisos"])))
    print("Gravados %s e %s" % (SAIDA_JSON.relative_to(RAIZ), SAIDA_JS.relative_to(RAIZ)))


if __name__ == "__main__":
    main()
