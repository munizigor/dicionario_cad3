/* Dicionário de Dados SINESP CAD 3 — aplicação estática, sem dependências.
 * Os dados vêm de dados.js (window.DICIONARIO), gerado por tools/extrair_pdf.py.
 */
(function () {
  "use strict";

  var DADOS = window.DICIONARIO;
  var TABELAS = DADOS.tabelas;
  var POR_NOME = Object.create(null);
  TABELAS.forEach(function (t) { POR_NOME[t.nome] = t; });

  /* ------------------------------------------------------------------ *
   * Utilitários
   * ------------------------------------------------------------------ */

  function $(sel) { return document.querySelector(sel); }

  /** Cria um elemento. `props` aceita atributos, `dataset`, `on*` e `texto`. */
  function el(tag, props, filhos) {
    var node = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (chave) {
        var valor = props[chave];
        if (valor === null || valor === undefined || valor === false) return;
        if (chave === "texto") node.textContent = valor;
        else if (chave === "classe") node.className = valor;
        else if (chave.slice(0, 2) === "on") node.addEventListener(chave.slice(2), valor);
        else node.setAttribute(chave, valor === true ? "" : valor);
      });
    }
    (filhos || []).forEach(function (filho) {
      if (filho === null || filho === undefined || filho === false) return;
      node.appendChild(typeof filho === "string" ? document.createTextNode(filho) : filho);
    });
    return node;
  }

  function svgEl(tag, props, filhos) {
    var node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.keys(props || {}).forEach(function (chave) {
      var valor = props[chave];
      if (valor === null || valor === undefined || valor === false) return;
      if (chave === "texto") node.textContent = valor;
      else if (chave === "classe") node.setAttribute("class", valor);
      else if (chave.slice(0, 2) === "on") node.addEventListener(chave.slice(2), valor);
      else node.setAttribute(chave, valor);
    });
    (filhos || []).forEach(function (filho) { if (filho) node.appendChild(filho); });
    return node;
  }

  function limpar(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  /** Minúsculas sem acento, para busca e filtros tolerantes. */
  function normalizar(texto) {
    return (texto || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  function plural(n, singular, pluralForma) {
    return n + " " + (n === 1 ? singular : pluralForma);
  }

  function baixar(nomeArquivo, conteudo, tipo) {
    var blob = new Blob([conteudo], { type: (tipo || "text/plain") + ";charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = el("a", { href: url, download: nomeArquivo });
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
  }

  /* ------------------------------------------------------------------ *
   * Grafo de relacionamentos
   * ------------------------------------------------------------------ */

  var ARESTAS = [];
  TABELAS.forEach(function (t) {
    t.fks_saida.forEach(function (fk) {
      ARESTAS.push({
        origem: t.nome,
        destino: fk.tabela,
        nome: fk.nome,
        colunas: fk.colunas,
        colunas_referidas: fk.colunas_referidas,
        obrigatoria: fk.obrigatoria
      });
    });
  });

  var VIZINHOS = Object.create(null);
  TABELAS.forEach(function (t) { VIZINHOS[t.nome] = { entrada: [], saida: [] }; });
  ARESTAS.forEach(function (a) {
    VIZINHOS[a.origem].saida.push(a);
    if (VIZINHOS[a.destino]) VIZINHOS[a.destino].entrada.push(a);
  });

  /** Colunas de uma tabela que participam de alguma FK de saída. */
  function fkDaColuna(tabela, nomeColuna) {
    var achado = null;
    VIZINHOS[tabela.nome].saida.forEach(function (a) {
      var i = a.colunas.indexOf(nomeColuna);
      if (i >= 0 && !achado) {
        achado = { tabela: a.destino, coluna: a.colunas_referidas[i] || nomeColuna, nome: a.nome };
      }
    });
    return achado;
  }

  /* ------------------------------------------------------------------ *
   * Agrupamento por prefixo (usado na lateral e na home)
   * ------------------------------------------------------------------ */

  var GRUPOS = (function () {
    var porPrefixo = Object.create(null);
    TABELAS.forEach(function (t) {
      var prefixo = t.nome.split("_")[0];
      (porPrefixo[prefixo] = porPrefixo[prefixo] || []).push(t);
    });
    var grupos = [];
    var soltas = [];
    Object.keys(porPrefixo).sort().forEach(function (prefixo) {
      if (porPrefixo[prefixo].length >= 2) grupos.push({ nome: prefixo, tabelas: porPrefixo[prefixo] });
      else soltas = soltas.concat(porPrefixo[prefixo]);
    });
    grupos.sort(function (a, b) { return b.tabelas.length - a.tabelas.length || a.nome.localeCompare(b.nome); });
    if (soltas.length) {
      soltas.sort(function (a, b) { return a.nome.localeCompare(b.nome); });
      grupos.push({ nome: "Outras", tabelas: soltas });
    }
    return grupos;
  })();

  /* ------------------------------------------------------------------ *
   * Índice de busca
   * ------------------------------------------------------------------ */

  var INDICE = [];
  TABELAS.forEach(function (t) {
    INDICE.push({
      tipo: "tabela",
      tabela: t,
      nomeNorm: normalizar(t.nome),
      descNorm: normalizar(t.descricao)
    });
    t.colunas.forEach(function (c) {
      INDICE.push({
        tipo: "coluna",
        tabela: t,
        coluna: c,
        nomeNorm: normalizar(c.nome),
        descNorm: normalizar(c.descricao)
      });
    });
  });

  function buscar(consulta) {
    var termos = normalizar(consulta).split(/\s+/).filter(Boolean);
    if (!termos.length) return [];
    var achados = [];

    INDICE.forEach(function (item) {
      var pontos = 0;
      for (var i = 0; i < termos.length; i++) {
        var termo = termos[i];
        var emNome = item.nomeNorm.indexOf(termo);
        var emDesc = item.descNorm.indexOf(termo);
        if (emNome < 0 && emDesc < 0) return;
        if (item.nomeNorm === termo) pontos += 100;
        else if (emNome === 0) pontos += 50;
        else if (emNome > 0) pontos += 25;
        if (emDesc >= 0) pontos += 5;
      }
      if (item.tipo === "tabela") pontos += 10;
      achados.push({ item: item, pontos: pontos });
    });

    // Agrupa por tabela, mantendo a melhor pontuação de cada grupo.
    var porTabela = Object.create(null);
    achados.forEach(function (a) {
      var nome = a.item.tabela.nome;
      var grupo = porTabela[nome];
      if (!grupo) grupo = porTabela[nome] = { tabela: a.item.tabela, pontos: 0, tabelaBateu: false, colunas: [] };
      grupo.pontos = Math.max(grupo.pontos, a.pontos);
      if (a.item.tipo === "tabela") grupo.tabelaBateu = true;
      else grupo.colunas.push(a.item.coluna);
    });

    return Object.keys(porTabela)
      .map(function (nome) { return porTabela[nome]; })
      .sort(function (a, b) { return b.pontos - a.pontos || a.tabela.nome.localeCompare(b.tabela.nome); });
  }

  /** Devolve um fragmento com os trechos da consulta destacados. */
  function destacar(texto, consulta, limite) {
    var frag = document.createDocumentFragment();
    if (!texto) return frag;
    var termos = normalizar(consulta).split(/\s+/).filter(Boolean);
    var alvo = normalizar(texto);
    var recorte = 0;

    if (limite && texto.length > limite) {
      var primeiro = -1;
      termos.forEach(function (t) {
        var p = alvo.indexOf(t);
        if (p >= 0 && (primeiro < 0 || p < primeiro)) primeiro = p;
      });
      if (primeiro > limite / 2) recorte = primeiro - Math.floor(limite / 3);
      texto = (recorte ? "… " : "") + texto.slice(recorte, recorte + limite) +
        (recorte + limite < alvo.length ? " …" : "");
      alvo = normalizar(texto);
    }

    // Marca todas as ocorrências de todos os termos.
    var marcas = [];
    termos.forEach(function (termo) {
      var pos = alvo.indexOf(termo);
      while (pos >= 0) {
        marcas.push([pos, pos + termo.length]);
        pos = alvo.indexOf(termo, pos + termo.length);
      }
    });
    marcas.sort(function (a, b) { return a[0] - b[0]; });

    var cursor = 0;
    marcas.forEach(function (m) {
      if (m[0] < cursor) return;
      if (m[0] > cursor) frag.appendChild(document.createTextNode(texto.slice(cursor, m[0])));
      frag.appendChild(el("mark", { texto: texto.slice(m[0], m[1]) }));
      cursor = m[1];
    });
    frag.appendChild(document.createTextNode(texto.slice(cursor)));
    return frag;
  }

  /* ------------------------------------------------------------------ *
   * Exportações
   * ------------------------------------------------------------------ */

  /** Traduz o tipo do modelador para o tipo Oracle correspondente. */
  function tipoOracle(tipo) {
    if (!tipo) return "VARCHAR2(1 BYTE)";
    var m = tipo.match(/^([A-Za-z_]+)\s*(?:\(([^)]*)\))?$/);
    if (!m) return tipo.toUpperCase();
    var base = m[1].toUpperCase();
    var arg = (m[2] || "").trim();
    switch (base) {
      case "VARCHAR": return "VARCHAR2(" + arg + ")";
      case "NUMERIC": return arg ? "NUMBER(" + arg.replace(/\s/g, "") + ")" : "NUMBER";
      case "RAW": return "RAW(" + arg + ")";
      case "TIMESTAMP": return arg ? "TIMESTAMP(" + arg + ")" : "TIMESTAMP";
      case "CLOB": return "CLOB";
      case "BLOB": return "BLOB";
      case "DATE": return "DATE";
      case "CHAR": return "CHAR(" + arg + ")";
      default: return arg ? base + "(" + arg + ")" : base;
    }
  }

  function aspas(texto) { return "'" + String(texto).replace(/'/g, "''") + "'"; }

  function gerarDDL(tabela) {
    var qualificado = (tabela.schema ? tabela.schema + "." : "") + tabela.nome;
    var linhas = [
      "-- " + qualificado,
      "-- DDL aproximado, derivado do dicionário de dados (" + DADOS.meta.arquivo_fonte + ").",
      "-- Conferir tipos, defaults e constraints antes de usar em produção.",
      "",
      "CREATE TABLE " + qualificado + " ("
    ];

    var partes = tabela.colunas.map(function (c) {
      return "  " + c.nome + " " + tipoOracle(c.tipo) +
        (c.formula ? " DEFAULT " + c.formula : "") +
        (c.obrigatoria ? " NOT NULL" : "");
    });

    // O documento lista o índice de suporte da PK/UK também como índice único.
    // Aqui ele vira constraint, e o índice homônimo é omitido (o Oracle o cria).
    var comoConstraint = Object.create(null);
    tabela.indices.forEach(function (idx) {
      if (idx.estado !== "PK" && idx.estado !== "UK") return;
      comoConstraint[idx.nome] = true;
      var colunas = idx.colunas.map(function (c) { return c.nome; }).join(", ");
      partes.push("  CONSTRAINT " + idx.nome + " " +
        (idx.estado === "PK" ? "PRIMARY KEY" : "UNIQUE") + " (" + colunas + ")");
    });

    linhas.push(partes.join(",\n"), ");", "");

    var criados = 0;
    tabela.indices.forEach(function (idx) {
      if (comoConstraint[idx.nome]) return;
      var alvo = idx.expressao || idx.colunas.map(function (c) {
        return c.nome + (c.ordem && c.ordem !== "ASC" ? " " + c.ordem : "");
      }).join(", ");
      linhas.push("CREATE " + (idx.estado === "UN" ? "UNIQUE " : "") + "INDEX " + idx.nome +
        " ON " + qualificado + " (" + alvo + ");");
      criados++;
    });
    if (criados) linhas.push("");

    (tabela.fks_saida || []).forEach(function (fk) {
      var destino = POR_NOME[fk.tabela];
      var destinoQualificado = (destino && destino.schema ? destino.schema + "." : "") + fk.tabela;
      linhas.push("ALTER TABLE " + qualificado + " ADD CONSTRAINT " + fk.nome +
        " FOREIGN KEY (" + fk.colunas.join(", ") + ") REFERENCES " +
        destinoQualificado + " (" + fk.colunas_referidas.join(", ") + ");");
    });
    if (tabela.fks_saida.length) linhas.push("");

    if (tabela.descricao) {
      linhas.push("COMMENT ON TABLE " + qualificado + " IS " + aspas(tabela.descricao) + ";");
    }
    tabela.colunas.forEach(function (c) {
      if (c.descricao) {
        linhas.push("COMMENT ON COLUMN " + qualificado + "." + c.nome + " IS " + aspas(c.descricao) + ";");
      }
    });

    if (tabela.constraints.length) {
      linhas.push("", "-- Check constraints declaradas no modelo (texto do documento original):");
      tabela.constraints.forEach(function (ct) {
        linhas.push("--   " + [ct.tipo, ct.alvo].filter(Boolean).join(" · ").replace(/\n/g, " "));
        ct.detalhes.forEach(function (d) { linhas.push("--     " + d); });
      });
    }

    return linhas.join("\n") + "\n";
  }

  function gerarCSV(tabela) {
    var cabecalho = ["No", "Coluna", "Tipo", "PK", "FK", "Obrigatoria", "Padrao", "Descricao"];
    var celula = function (v) {
      var texto = v === null || v === undefined ? "" : String(v);
      return /[",\n;]/.test(texto) ? '"' + texto.replace(/"/g, '""') + '"' : texto;
    };
    var linhas = [cabecalho.join(";")];
    tabela.colunas.forEach(function (c) {
      linhas.push([
        c.no, c.nome, c.tipo, c.pk ? "S" : "", c.fk ? "S" : "",
        c.obrigatoria ? "S" : "", c.formula, c.descricao
      ].map(celula).join(";"));
    });
    return "﻿" + linhas.join("\r\n") + "\r\n";
  }

  function gerarMermaid(tabela) {
    var linhas = ["erDiagram"];
    var incluidas = Object.create(null);
    incluidas[tabela.nome] = true;

    VIZINHOS[tabela.nome].saida.forEach(function (a) {
      incluidas[a.destino] = true;
      linhas.push("  " + a.destino + " ||--o{ " + a.origem + " : " + JSON.stringify(a.nome));
    });
    VIZINHOS[tabela.nome].entrada.forEach(function (a) {
      incluidas[a.origem] = true;
      linhas.push("  " + a.destino + " ||--o{ " + a.origem + " : " + JSON.stringify(a.nome));
    });

    // Atributos apenas da tabela central, para o diagrama não explodir.
    var atributos = tabela.colunas.map(function (c) {
      var chave = c.pk ? " PK" : (c.fk ? " FK" : "");
      return "    " + tipoOracle(c.tipo).replace(/[^A-Za-z0-9_]/g, "_") + " " + c.nome + chave;
    });
    linhas.push("  " + tabela.nome + " {", atributos.join("\n"), "  }");

    if (Object.keys(incluidas).length === 1) {
      linhas.push("  %% Esta tabela não possui relacionamentos declarados.");
    }
    return linhas.join("\n") + "\n";
  }

  /* ------------------------------------------------------------------ *
   * Diagrama de vizinhança (página da tabela)
   * ------------------------------------------------------------------ */

  function medirLargura(texto) { return Math.max(90, texto.length * 6.6 + 22); }

  function caixaNo(nome, x, y, largura, altura, ehCentro) {
    return svgEl("g", {
      classe: "no-grupo",
      onclick: function () { irPara("#/tabela/" + nome); },
      role: "link",
      tabindex: "0",
      onkeydown: function (ev) { if (ev.key === "Enter") irPara("#/tabela/" + nome); }
    }, [
      svgEl("title", { texto: nome }),
      svgEl("rect", { classe: "no-caixa" + (ehCentro ? " centro" : ""), x: x, y: y, width: largura, height: altura, rx: 5 }),
      svgEl("text", { classe: "no-texto", x: x + largura / 2, y: y + altura / 2, "text-anchor": "middle", texto: nome })
    ]);
  }

  /** Junta arestas paralelas: uma caixa por tabela vizinha, colunas somadas. */
  function agruparPorVizinha(arestas, chave) {
    var lista = [], indice = Object.create(null);
    arestas.forEach(function (a) {
      var nome = a[chave];
      if (indice[nome] === undefined) {
        indice[nome] = lista.length;
        lista.push({ nome: nome, colunas: [] });
      }
      var item = lista[indice[nome]];
      a.colunas.forEach(function (coluna) {
        if (item.colunas.indexOf(coluna) < 0) item.colunas.push(coluna);
      });
    });
    return lista;
  }

  function diagramaVizinhanca(tabela) {
    var entrada = agruparPorVizinha(VIZINHOS[tabela.nome].entrada, "origem");
    var saida = agruparPorVizinha(VIZINHOS[tabela.nome].saida, "destino");
    if (!entrada.length && !saida.length) return null;

    var ALTURA_NO = 26, ESPACO = 14, MARGEM = 16;
    var larguraCentro = medirLargura(tabela.nome);
    var larguraEsq = Math.max.apply(null, [120].concat(entrada.map(function (a) { return medirLargura(a.nome); })));
    var larguraDir = Math.max.apply(null, [120].concat(saida.map(function (a) { return medirLargura(a.nome); })));

    // O vão entre as colunas acomoda o rótulo com os nomes das colunas da FK.
    function vao(lista) {
      return Math.max.apply(null, [130].concat(lista.map(function (a) {
        return a.colunas.join(", ").length * 5.4 + 24;
      })));
    }
    var colunaEsqX = MARGEM;
    var colunaCentroX = colunaEsqX + (entrada.length ? larguraEsq + vao(entrada) : 0);
    var colunaDirX = colunaCentroX + larguraCentro + (saida.length ? vao(saida) : 0);
    var largura = colunaDirX + (saida.length ? larguraDir : 0) + MARGEM;

    var alturaEsq = entrada.length * ALTURA_NO + Math.max(0, entrada.length - 1) * ESPACO;
    var alturaDir = saida.length * ALTURA_NO + Math.max(0, saida.length - 1) * ESPACO;
    var alturaConteudo = Math.max(alturaEsq, alturaDir, ALTURA_NO);
    var altura = alturaConteudo + MARGEM * 2;

    var centroY = altura / 2 - ALTURA_NO / 2;
    var filhos = [];

    function posicoes(lista, alturaLista) {
      var inicio = (altura - alturaLista) / 2;
      return lista.map(function (_, i) { return inicio + i * (ALTURA_NO + ESPACO); });
    }

    var ysEsq = posicoes(entrada, alturaEsq);
    var ysDir = posicoes(saida, alturaDir);

    entrada.forEach(function (a, i) {
      var y = ysEsq[i] + ALTURA_NO / 2;
      var x1 = colunaEsqX + larguraEsq, x2 = colunaCentroX;
      var meio = (x1 + x2) / 2;
      filhos.push(svgEl("path", {
        classe: "aresta entrada",
        "marker-end": "url(#seta-entrada)",
        d: "M" + x1 + "," + y + " C" + meio + "," + y + " " + meio + "," + (centroY + ALTURA_NO / 2) +
           " " + (x2 - 8) + "," + (centroY + ALTURA_NO / 2)
      }));
      filhos.push(svgEl("text", {
        classe: "rotulo-aresta", x: (x1 + x2) / 2, y: y - 5, "text-anchor": "middle",
        texto: a.colunas.join(", ")
      }));
    });

    saida.forEach(function (a, i) {
      var y = ysDir[i] + ALTURA_NO / 2;
      var x1 = colunaCentroX + larguraCentro, x2 = colunaDirX;
      var meio = (x1 + x2) / 2;
      filhos.push(svgEl("path", {
        classe: "aresta saida",
        "marker-end": "url(#seta-saida)",
        d: "M" + x1 + "," + (centroY + ALTURA_NO / 2) + " C" + meio + "," + (centroY + ALTURA_NO / 2) +
           " " + meio + "," + y + " " + (x2 - 8) + "," + y
      }));
      filhos.push(svgEl("text", {
        classe: "rotulo-aresta", x: (x1 + x2) / 2, y: y - 5, "text-anchor": "middle",
        texto: a.colunas.join(", ")
      }));
    });

    entrada.forEach(function (a, i) { filhos.push(caixaNo(a.nome, colunaEsqX, ysEsq[i], larguraEsq, ALTURA_NO, false)); });
    saida.forEach(function (a, i) { filhos.push(caixaNo(a.nome, colunaDirX, ysDir[i], larguraDir, ALTURA_NO, false)); });
    filhos.push(caixaNo(tabela.nome, colunaCentroX, centroY, larguraCentro, ALTURA_NO, true));

    var svg = svgEl("svg", {
      classe: "diagrama-vizinhanca",
      viewBox: "0 0 " + largura + " " + altura,
      width: largura, height: altura,
      role: "img",
      "aria-label": "Diagrama de relacionamentos de " + tabela.nome
    }, [marcadores()].concat(filhos));

    return el("div", { classe: "moldura-svg" }, [
      svg,
      el("p", {
        classe: "legenda-diagrama",
        texto: "À esquerda, tabelas que referenciam " + tabela.nome +
          "; à direita, tabelas referenciadas por ela. Clique para navegar."
      })
    ]);
  }

  function marcadores() {
    function seta(id, classe) {
      return svgEl("marker", {
        id: id, viewBox: "0 0 10 10", refX: "9", refY: "5",
        markerWidth: "6", markerHeight: "6", orient: "auto-start-reverse"
      }, [svgEl("path", { d: "M0,0 L10,5 L0,10 z", classe: "preenchimento-" + classe })]);
    }
    var defs = svgEl("defs", {}, [seta("seta-entrada", "entrada"), seta("seta-saida", "saida"), seta("seta-mapa", "mapa")]);
    // As setas herdam a cor via CSS variável aplicada inline (markers não herdam contexto).
    defs.querySelectorAll("path").forEach(function (p) {
      var classe = p.getAttribute("class");
      p.setAttribute("fill", classe === "preenchimento-entrada" ? "var(--fk)"
        : classe === "preenchimento-saida" ? "var(--interactive)" : "var(--gray-30)");
    });
    return defs;
  }

  /* ------------------------------------------------------------------ *
   * Mapa global (layout de forças determinístico)
   * ------------------------------------------------------------------ */

  var mapaCache = null;

  function calcularMapa() {
    if (mapaCache) return mapaCache;

    // Só as tabelas conectadas entram no grafo; as isoladas viram uma lista
    // à parte, para não desperdiçar área do diagrama com nós soltos.
    var nos = TABELAS.filter(function (t) {
      return VIZINHOS[t.nome].entrada.length || VIZINHOS[t.nome].saida.length;
    }).map(function (t, i) {
      return {
        nome: t.nome, indice: i,
        largura: medirLargura(t.nome), altura: 26,
        x: 0, y: 0, grau: VIZINHOS[t.nome].entrada.length + VIZINHOS[t.nome].saida.length
      };
    });
    var porNome = Object.create(null);
    nos.forEach(function (n) { porNome[n.nome] = n; });

    // Componentes conexas.
    var visitado = Object.create(null);
    var componentes = [];
    nos.forEach(function (no) {
      if (visitado[no.nome]) return;
      var fila = [no], comp = [];
      visitado[no.nome] = true;
      while (fila.length) {
        var atual = fila.shift();
        comp.push(atual);
        VIZINHOS[atual.nome].saida.concat(VIZINHOS[atual.nome].entrada).forEach(function (a) {
          [a.origem, a.destino].forEach(function (nome) {
            if (!visitado[nome] && porNome[nome]) { visitado[nome] = true; fila.push(porNome[nome]); }
          });
        });
      }
      componentes.push(comp);
    });

    // Fruchterman-Reingold por componente, com posições iniciais determinísticas.
    componentes.forEach(function (comp) {
      var n = comp.length;
      if (n === 1) { comp[0].x = 0; comp[0].y = 0; return; }
      var raio = 40 * Math.sqrt(n);
      comp.forEach(function (no, i) {
        var angulo = i * 2.399963;               // ângulo áureo: distribuição estável
        no.x = raio * Math.cos(angulo);
        no.y = raio * Math.sin(angulo);
      });

      var nomes = Object.create(null);
      comp.forEach(function (no) { nomes[no.nome] = no; });
      var arestas = ARESTAS.filter(function (a) { return nomes[a.origem] && nomes[a.destino]; });

      // Distância-alvo entre nós: compacta o suficiente para os rótulos
      // continuarem legíveis quando o grafo inteiro cabe na tela.
      var k = 30;
      var temperatura = raio;
      var ITERACOES = 400;
      for (var passo = 0; passo < ITERACOES; passo++) {
        comp.forEach(function (a) { a.dx = 0; a.dy = 0; });
        for (var i = 0; i < n; i++) {
          for (var j = i + 1; j < n; j++) {
            var a = comp[i], b = comp[j];
            var dx = a.x - b.x, dy = a.y - b.y;
            var dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
            var forca = (k * k) / dist;
            var ux = dx / dist, uy = dy / dist;
            a.dx += ux * forca; a.dy += uy * forca;
            b.dx -= ux * forca; b.dy -= uy * forca;
          }
        }
        arestas.forEach(function (aresta) {
          var a = nomes[aresta.origem], b = nomes[aresta.destino];
          var dx = a.x - b.x, dy = a.y - b.y;
          var dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
          var forca = (dist * dist) / k;
          var ux = dx / dist, uy = dy / dist;
          a.dx -= ux * forca; a.dy -= uy * forca;
          b.dx += ux * forca; b.dy += uy * forca;
        });
        comp.forEach(function (no) {
          var desloc = Math.sqrt(no.dx * no.dx + no.dy * no.dy) || 0.01;
          var limite = Math.min(desloc, temperatura);
          no.x += (no.dx / desloc) * limite;
          no.y += (no.dy / desloc) * limite;
        });
        temperatura *= 0.975;
      }

      // Separa caixas que ainda se sobrepõem.
      for (var repeticao = 0; repeticao < 60; repeticao++) {
        var moveu = false;
        for (var p = 0; p < n; p++) {
          for (var q = p + 1; q < n; q++) {
            var u = comp[p], v = comp[q];
            var folgaX = (u.largura + v.largura) / 2 + 16;
            var folgaY = (u.altura + v.altura) / 2 + 12;
            var difX = v.x - u.x, difY = v.y - u.y;
            if (Math.abs(difX) < folgaX && Math.abs(difY) < folgaY) {
              var empurraX = folgaX - Math.abs(difX);
              var empurraY = folgaY - Math.abs(difY);
              if (empurraX / folgaX < empurraY / folgaY) {
                var sx = (difX >= 0 ? 1 : -1) * empurraX / 2;
                u.x -= sx; v.x += sx;
              } else {
                var sy = (difY >= 0 ? 1 : -1) * empurraY / 2;
                u.y -= sy; v.y += sy;
              }
              moveu = true;
            }
          }
        }
        if (!moveu) break;
      }
    });

    // Empacota as componentes em prateleiras horizontais.
    componentes.sort(function (a, b) { return b.length - a.length; });
    var ESPACO_COMP = 46;
    var LARGURA_MAX = 1000;
    var cursorX = 0, cursorY = 0, alturaLinha = 0, larguraTotal = 0;

    componentes.forEach(function (comp) {
      var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      comp.forEach(function (no) {
        minX = Math.min(minX, no.x - no.largura / 2);
        maxX = Math.max(maxX, no.x + no.largura / 2);
        minY = Math.min(minY, no.y - no.altura / 2);
        maxY = Math.max(maxY, no.y + no.altura / 2);
      });
      var largura = maxX - minX, altura = maxY - minY;
      if (cursorX > 0 && cursorX + largura > LARGURA_MAX) {
        cursorX = 0; cursorY += alturaLinha + ESPACO_COMP; alturaLinha = 0;
      }
      comp.forEach(function (no) {
        no.x = no.x - minX + cursorX;
        no.y = no.y - minY + cursorY;
      });
      cursorX += largura + ESPACO_COMP;
      larguraTotal = Math.max(larguraTotal, cursorX);
      alturaLinha = Math.max(alturaLinha, altura);
    });

    mapaCache = {
      nos: nos,
      porNome: porNome,
      largura: larguraTotal + ESPACO_COMP,
      altura: cursorY + alturaLinha + ESPACO_COMP,
      componentes: componentes.length
    };
    return mapaCache;
  }

  /** Ponto onde a reta entre dois nós cruza a borda da caixa de destino. */
  function pontoBorda(de, para) {
    var dx = para.x - de.x, dy = para.y - de.y;
    if (!dx && !dy) return { x: para.x, y: para.y };
    var metadeL = para.largura / 2 + 3, metadeA = para.altura / 2 + 3;
    var escala = Math.min(
      Math.abs(dx) > 0.001 ? metadeL / Math.abs(dx) : Infinity,
      Math.abs(dy) > 0.001 ? metadeA / Math.abs(dy) : Infinity
    );
    return { x: para.x - dx * escala, y: para.y - dy * escala };
  }

  function montarMapa() {
    var mapa = calcularMapa();
    var grupoArestas = svgEl("g", {});
    var grupoNos = svgEl("g", {});
    var elementosPorNome = Object.create(null);
    var arestasPorNome = Object.create(null);

    ARESTAS.forEach(function (a) {
      var origem = mapa.porNome[a.origem], destino = mapa.porNome[a.destino];
      if (!origem || !destino) return;
      var fim = pontoBorda(origem, destino);
      var inicio = pontoBorda(destino, origem);
      var linha = svgEl("line", {
        classe: "aresta", "marker-end": "url(#seta-mapa)",
        x1: inicio.x, y1: inicio.y, x2: fim.x, y2: fim.y
      }, [svgEl("title", { texto: a.origem + " → " + a.destino + " (" + a.nome + ")" })]);
      grupoArestas.appendChild(linha);
      (arestasPorNome[a.origem] = arestasPorNome[a.origem] || []).push(linha);
      (arestasPorNome[a.destino] = arestasPorNome[a.destino] || []).push(linha);
    });

    mapa.nos.forEach(function (no) {
      var grupo = caixaNo(no.nome, no.x - no.largura / 2, no.y - no.altura / 2, no.largura, no.altura, false);
      grupo.addEventListener("mouseenter", function () { realcar(no.nome); });
      grupo.addEventListener("mouseleave", function () { realcar(null); });
      grupo.addEventListener("focus", function () { realcar(no.nome); });
      grupo.addEventListener("blur", function () { realcar(null); });
      elementosPorNome[no.nome] = grupo;
      grupoNos.appendChild(grupo);
    });

    function realcar(nome) {
      var relacionados = Object.create(null);
      if (nome) {
        relacionados[nome] = true;
        VIZINHOS[nome].saida.forEach(function (a) { relacionados[a.destino] = true; });
        VIZINHOS[nome].entrada.forEach(function (a) { relacionados[a.origem] = true; });
      }
      Object.keys(elementosPorNome).forEach(function (chave) {
        elementosPorNome[chave].classList.toggle("apagado", !!nome && !relacionados[chave]);
      });
      var destacadas = nome ? (arestasPorNome[nome] || []) : [];
      grupoArestas.querySelectorAll("line").forEach(function (linha) {
        linha.classList.toggle("apagada", !!nome && destacadas.indexOf(linha) < 0);
      });
    }

    var svg = svgEl("svg", {
      id: "svg-mapa",
      viewBox: "-20 -20 " + (mapa.largura + 40) + " " + (mapa.altura + 40),
      role: "img", "aria-label": "Mapa de relacionamentos entre as tabelas"
    }, [marcadores(), grupoArestas, grupoNos]);

    habilitarZoom(svg, mapa);
    return svg;
  }

  function habilitarZoom(svg, mapa) {
    var vista = { x: -20, y: -20, largura: mapa.largura + 40, altura: mapa.altura + 40 };
    var inicial = Object.assign({}, vista);

    function aplicar() {
      svg.setAttribute("viewBox", vista.x + " " + vista.y + " " + vista.largura + " " + vista.altura);
    }

    svg.addEventListener("wheel", function (ev) {
      ev.preventDefault();
      var caixa = svg.getBoundingClientRect();
      var fracaoX = (ev.clientX - caixa.left) / caixa.width;
      var fracaoY = (ev.clientY - caixa.top) / caixa.height;
      var fator = ev.deltaY > 0 ? 1.12 : 1 / 1.12;
      var novaLargura = Math.min(inicial.largura * 3, Math.max(240, vista.largura * fator));
      var novaAltura = novaLargura * (vista.altura / vista.largura);
      vista.x += (vista.largura - novaLargura) * fracaoX;
      vista.y += (vista.altura - novaAltura) * fracaoY;
      vista.largura = novaLargura;
      vista.altura = novaAltura;
      aplicar();
    }, { passive: false });

    var arrastando = false, ultimoX = 0, ultimoY = 0;
    svg.addEventListener("pointerdown", function (ev) {
      if (ev.target.closest(".no-grupo")) return;
      arrastando = true; ultimoX = ev.clientX; ultimoY = ev.clientY;
      svg.classList.add("arrastando");
      svg.setPointerCapture(ev.pointerId);
    });
    svg.addEventListener("pointermove", function (ev) {
      if (!arrastando) return;
      var caixa = svg.getBoundingClientRect();
      vista.x -= (ev.clientX - ultimoX) * (vista.largura / caixa.width);
      vista.y -= (ev.clientY - ultimoY) * (vista.altura / caixa.height);
      ultimoX = ev.clientX; ultimoY = ev.clientY;
      aplicar();
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach(function (evento) {
      svg.addEventListener(evento, function () { arrastando = false; svg.classList.remove("arrastando"); });
    });

    svg.reiniciarVista = function () { vista = Object.assign({}, inicial); aplicar(); };
  }

  /* ------------------------------------------------------------------ *
   * Componentes de página
   * ------------------------------------------------------------------ */

  /* Um painel é um br-card do design system: o <h2> vira card-header, com o
     selo alinhado à direita, e o conteúdo vira card-content. */
  function painel(titulo, selo, conteudo, semPadding) {
    return el("section", { classe: "br-card mb-4" }, [
      el("h2", { classe: "card-header" }, [
        document.createTextNode(titulo),
        selo ? el("span", { classe: "selo", texto: selo }) : null
      ]),
      el("div", { classe: semPadding ? "card-content p-0" : "card-content" }, [conteudo])
    ]);
  }

  function linkTabela(nome, rotulo) {
    if (!POR_NOME[nome]) return el("span", { texto: nome });
    return el("a", { href: "#/tabela/" + nome, texto: rotulo || nome });
  }

  /* Ícone Font Awesome. Sempre aria-hidden: o rótulo acessível vem do texto ao
     lado ou do aria-label de quem o contém. */
  function icone(nome) {
    return el("i", { classe: "fas fa-" + nome, "aria-hidden": "true" });
  }

  /* Botão do DS. `enfase` é "primary", "secondary" ou vazio (terciário). */
  function botao(rotulo, nomeIcone, aoClicar, enfase) {
    return el("button", {
      classe: "br-button" + (enfase ? " " + enfase : ""),
      type: "button",
      onclick: aoClicar
    }, [nomeIcone ? icone(nomeIcone) : null, document.createTextNode(rotulo)]);
  }

  function tag(texto, classeExtra) {
    return el("span", { classe: "br-tag" + (classeExtra ? " " + classeExtra : "") }, [
      el("span", { texto: texto })
    ]);
  }

  /* br-message do DS. `tipo` é "info", "success", "warning" ou "danger" — o
     ícone de cada um é convencionado pelo padrão. */
  var ICONE_MENSAGEM = {
    info: "info-circle", success: "check-circle",
    warning: "exclamation-triangle", danger: "times-circle"
  };

  function mensagem(tipo, titulo, corpo) {
    return el("div", { classe: "br-message " + tipo }, [
      el("div", { classe: "icon" }, [
        el("i", { classe: "fas fa-" + ICONE_MENSAGEM[tipo] + " fa-lg", "aria-hidden": "true" })
      ]),
      el("div", { classe: "content", role: "alert", "aria-label": titulo + " " + corpo }, [
        el("span", { classe: "message-title", texto: titulo }),
        el("span", { classe: "message-body", texto: " " + corpo })
      ])
    ]);
  }

  function tabelaColunas(tabela) {
    var estado = { chave: "no", ordem: 1, filtro: "" };
    var corpo = el("tbody", {});

    var colunasVisiveis = [
      { chave: "no", rotulo: "Nº", classe: "col-num" },
      { chave: "nome", rotulo: "Coluna", classe: "col-nome" },
      { chave: "marcas", rotulo: "Chaves", classe: "col-marcas", semOrdenacao: true },
      { chave: "tipo", rotulo: "Tipo", classe: "col-tipo" },
      { chave: "descricao", rotulo: "Descrição", classe: "col-desc" }
    ];
    var temPadrao = tabela.colunas.some(function (c) { return c.formula; });
    if (temPadrao) {
      colunasVisiveis.splice(4, 0, { chave: "formula", rotulo: "Padrão", classe: "col-tipo" });
    }

    var cabecalhos = colunasVisiveis.map(function (def) {
      if (def.semOrdenacao) {
        return el("th", { classe: def.classe, texto: def.rotulo, scope: "col" });
      }

      var seta = el("i", { classe: "fas fa-sort ordenacao", "aria-hidden": "true" });
      var th = el("th", {
        classe: def.classe, scope: "col",
        "aria-sort": def.chave === estado.chave ? "ascending" : "none"
      }, [document.createTextNode(def.rotulo), seta]);

      th.addEventListener("click", function () {
        if (estado.chave === def.chave) estado.ordem = -estado.ordem;
        else { estado.chave = def.chave; estado.ordem = 1; }
        cabecalhos.forEach(function (outro, i) {
          var ativo = colunasVisiveis[i].chave === estado.chave;
          var ordem = ativo ? (estado.ordem === 1 ? "ascending" : "descending") : "none";
          if (outro.hasAttribute("aria-sort")) outro.setAttribute("aria-sort", ordem);
          var glifo = outro.querySelector(".ordenacao");
          if (glifo) {
            glifo.className = "fas ordenacao " + (!ativo ? "fa-sort"
              : ordem === "ascending" ? "fa-sort-up" : "fa-sort-down");
          }
        });
        desenhar();
      });
      return th;
    });

    function desenhar() {
      limpar(corpo);
      var filtro = normalizar(estado.filtro);
      var linhas = tabela.colunas.filter(function (c) {
        if (!filtro) return true;
        return normalizar(c.nome + " " + c.tipo + " " + (c.descricao || "")).indexOf(filtro) >= 0;
      });

      linhas.sort(function (a, b) {
        var va = a[estado.chave], vb = b[estado.chave];
        if (va === null || va === undefined) va = "";
        if (vb === null || vb === undefined) vb = "";
        if (typeof va === "number" && typeof vb === "number") return (va - vb) * estado.ordem;
        return String(va).localeCompare(String(vb), "pt-BR") * estado.ordem;
      });

      linhas.forEach(function (c) {
        var alvoFk = c.fk ? fkDaColuna(tabela, c.nome) : null;
        // `data-th` é o rótulo que o DS expõe no layout responsivo da tabela.
        var marcas = el("td", { classe: "col-marcas", "data-th": "Chaves" }, [
          c.pk ? tag("PK", "selo-chave selo-pk") : null,
          c.fk ? tag("FK", "selo-chave selo-fk") : null,
          c.obrigatoria ? tag("NN", "selo-chave selo-nn") : null
        ]);

        var celulas = [
          el("td", { classe: "col-num", texto: c.no, "data-th": "Nº" }),
          el("td", { classe: "col-nome", "data-th": "Coluna" }, [
            el("a", {
              href: "#/tabela/" + tabela.nome + "?col=" + encodeURIComponent(c.nome),
              texto: c.nome
            })
          ]),
          marcas,
          el("td", { classe: "col-tipo", texto: c.tipo, "data-th": "Tipo" })
        ];
        if (temPadrao) celulas.push(el("td", { classe: "col-tipo", texto: c.formula || "", "data-th": "Padrão" }));
        celulas.push(el("td", { classe: "col-desc", "data-th": "Descrição" }, [
          c.descricao ? document.createTextNode(c.descricao) : el("span", { classe: "col-vazio", texto: "—" }),
          alvoFk ? el("div", { classe: "col-referencia" }, [
            icone("long-arrow-alt-right"),
            document.createTextNode(" "),
            el("a", {
              href: "#/tabela/" + alvoFk.tabela + "?col=" + encodeURIComponent(alvoFk.coluna),
              texto: alvoFk.tabela + "." + alvoFk.coluna
            })
          ]) : null
        ]));

        corpo.appendChild(el("tr", { id: "col-" + c.nome }, celulas));
      });

      if (!linhas.length) {
        corpo.appendChild(el("tr", {}, [
          el("td", { colspan: colunasVisiveis.length, classe: "col-vazio", texto: "Nenhuma coluna corresponde ao filtro." })
        ]));
      }
    }

    desenhar();

    var campo = el("input", {
      type: "search", id: "filtro-colunas", placeholder: "Filtrar colunas desta tabela…",
      autocomplete: "off",
      oninput: function (ev) { estado.filtro = ev.target.value; desenhar(); }
    });
    // Sem `.input-icon`: ele é position:absolute sem `top` e ancora no topo do
    // .br-input, caindo sobre o label em vez de ficar sobre o campo.
    var filtro = el("div", { classe: "br-input filtro-colunas" }, [
      el("label", { classe: "sr-only", "for": "filtro-colunas", texto: "Filtrar colunas desta tabela" }),
      campo
    ]);

    return {
      filtro: filtro,
      // Sem a classe .br-table de propósito: o core-init instancia BRTable em
      // todo .br-table e injeta header/footer próprios, que brigariam com a
      // ordenação e o filtro daqui. A moldura visual vem do br-card (ADR-004).
      grade: el("div", { classe: "rolagem grade-rolante" }, [
        el("table", { classe: "grade grade-longa" }, [
          el("caption", { classe: "sr-only", texto: "Colunas da tabela " + tabela.nome }),
          el("thead", {}, [el("tr", {}, cabecalhos)]),
          corpo
        ])
      ])
    };
  }

  /* ------------------------------------------------------------------ *
   * Páginas
   * ------------------------------------------------------------------ */

  function paginaInicial() {
    var meta = DADOS.meta;
    var frag = document.createDocumentFragment();

    frag.appendChild(el("div", { classe: "cabecalho-pagina" }, [
      el("h1", { texto: meta.titulo }),
      el("p", { classe: "descricao-tabela", texto:
        "Versão navegável do dicionário de dados do SINESP CAD 3" })
    ]));

    var cartoes = [
      [meta.total_tabelas, "tabelas"],
      [meta.total_colunas, "colunas"],
      [meta.total_relacionamentos, "chaves estrangeiras"],
      [TABELAS.reduce(function (s, t) { return s + t.indices.length; }, 0), "índices"]
    ];
    frag.appendChild(el("div", { classe: "cartoes" }, cartoes.map(function (c) {
      return el("div", { classe: "br-card" }, [
        el("div", { classe: "card-content" }, [
          el("div", { classe: "numero", texto: String(c[0]) }),
          el("div", { classe: "rotulo", texto: c[1] })
        ])
      ]);
    })));

    frag.appendChild(el("div", { classe: "barra-ferramentas" }, [
      el("a", { classe: "br-button primary", href: "#/mapa" }, [
        icone("project-diagram"), document.createTextNode("Ver mapa de relacionamentos")
      ]),
      // botao("Baixar dicionário completo (JSON)", "file-code", function () {
      //   baixar("dicionario-cad3.json", JSON.stringify(DADOS, null, 2), "application/json");
      // }, "secondary"),
      // botao("Baixar DDL de todas as tabelas", "database", function () {
      //   baixar("cad3-ddl-completo.sql", TABELAS.map(gerarDDL).join("\n"), "text/plain");
      // }, "secondary")
    ]));

    var grupos = el("div", { classe: "grade-grupos" }, GRUPOS.map(function (grupo) {
      return el("div", { classe: "br-card" }, [
        el("h3", { classe: "card-header", texto: grupo.nome + " · " + grupo.tabelas.length }),
        el("div", { classe: "card-content" }, [
          el("ul", {}, grupo.tabelas.slice().sort(function (a, b) {
            return a.nome.localeCompare(b.nome);
          }).map(function (t) {
            return el("li", {}, [
              linkTabela(t.nome),
              el("span", { classe: "col-vazio", texto: " " + t.colunas.length + " col." })
            ]);
          }))
        ])
      ]);
    }));
    frag.appendChild(painel("Tabelas por grupo", meta.total_tabelas + " tabelas", grupos));

    return frag;
  }

  function paginaTabela(nome, colunaAlvo) {
    var tabela = POR_NOME[nome];
    if (!tabela) return paginaNaoEncontrada(nome);

    var frag = document.createDocumentFragment();
    var pks = tabela.colunas.filter(function (c) { return c.pk; });

    frag.appendChild(el("div", { classe: "cabecalho-pagina cabecalho-tabela" }, [
      el("h1", {}, [
        tabela.schema ? el("span", { classe: "schema", texto: tabela.schema + "." }) : null,
        document.createTextNode(tabela.nome)
      ]),
      tabela.descricao ? el("p", { classe: "descricao-tabela", texto: tabela.descricao }) : null,
      el("div", { classe: "pilulas" }, [
        tag(plural(tabela.colunas.length, "coluna", "colunas")),
        pks.length ? tag("PK: " + pks.map(function (c) { return c.nome; }).join(", ")) : null,
        tag(plural(tabela.indices.length, "índice", "índices")),
        el("span", { classe: "br-tag" }, [
          icone("arrow-up"), el("span", { texto: tabela.fks_saida.length + " referencia" })
        ]),
        el("span", { classe: "br-tag" }, [
          icone("arrow-down"), el("span", { texto: tabela.fks_entrada.length + " referenciada" })
        ])
      ])
    ]));

    var grade = tabelaColunas(tabela);

    frag.appendChild(el("div", { classe: "barra-ferramentas" }, [
      // botao("DDL (.sql)", "database", function () {
      //   baixar(tabela.nome + ".sql", gerarDDL(tabela), "text/plain");
      // }, "secondary"),
      // botao("JSON", "file-code", function () {
      //   baixar(tabela.nome + ".json", JSON.stringify(tabela, null, 2), "application/json");
      // }, "secondary"),
      botao("CSV das colunas", "file-csv", function () {
        baixar(tabela.nome + "-colunas.csv", gerarCSV(tabela), "text/csv");
      }, "secondary"),
      botao("Mermaid (.mmd)", "project-diagram", function () {
        baixar(tabela.nome + ".mmd", gerarMermaid(tabela), "text/plain");
      }, "secondary"),
      grade.filtro
    ]));

    frag.appendChild(painel("Colunas", tabela.colunas.length + " colunas", grade.grade, true));

    if (tabela.indices.length) {
      var linhasIndice = tabela.indices.map(function (idx) {
        return el("tr", {}, [
          el("td", { classe: "col-nome", texto: idx.nome, "data-th": "Nome" }),
          el("td", { classe: "col-tipo", texto: idx.estado || "—", title: rotuloEstado(idx.estado), "data-th": "Tipo" }),
          el("td", { classe: "col-tipo", "data-th": "Colunas / expressão", texto: idx.expressao || idx.colunas.map(function (c) {
            return c.nome + (c.ordem && c.ordem !== "ASC" ? " " + c.ordem : "");
          }).join(", ") })
        ]);
      });
      frag.appendChild(painel("Índices", null, el("div", { classe: "rolagem" }, [
        el("table", { classe: "grade" }, [
          el("caption", { classe: "sr-only", texto: "Índices da tabela " + tabela.nome }),
          el("thead", {}, [el("tr", {}, [
            el("th", { texto: "Nome", scope: "col" }),
            el("th", { texto: "Tipo", scope: "col" }),
            el("th", { texto: "Colunas / expressão", scope: "col" })
          ])]),
          el("tbody", {}, linhasIndice)
        ])
      ]), true));
    }

    if (tabela.constraints.length) {
      frag.appendChild(painel("Constraints", null, el("div", {}, tabela.constraints.map(function (ct) {
        return el("div", { classe: "mb-3" }, [
          el("div", { classe: "col-nome", texto: [ct.tipo, ct.alvo].filter(Boolean).join(" · ").replace(/\n/g, " ") }),
          el("pre", { classe: "codigo", texto: ct.detalhes.join("\n") })
        ]);
      }))));
    }

    if (tabela.fks_saida.length || tabela.fks_entrada.length) {
      var conteudoRel = el("div", {});

      if (tabela.fks_saida.length) {
        conteudoRel.appendChild(el("h3", { classe: "text-up-01 mb-1", texto: "Referencia (chaves estrangeiras desta tabela)" }));
        conteudoRel.appendChild(listaFks(tabela.fks_saida, tabela, "saida"));
      }
      if (tabela.fks_entrada.length) {
        conteudoRel.appendChild(el("h3", { classe: "text-up-01 mt-4 mb-1", texto: "É referenciada por" }));
        conteudoRel.appendChild(listaFks(tabela.fks_entrada, tabela, "entrada"));
      }
      frag.appendChild(painel("Relacionamentos",
        tabela.fks_saida.length + " ↗ · " + tabela.fks_entrada.length + " ↘", conteudoRel));

      var diagrama = diagramaVizinhanca(tabela);
      if (diagrama) frag.appendChild(painel("Diagrama de vizinhança", null, diagrama, true));
    }

    frag.appendChild(el("p", { classe: "proveniencia",
      texto: "Origem: " + DADOS.meta.arquivo_fonte + ", página " + tabela.paginas.join(", ") + "." }));

    if (colunaAlvo) {
      setTimeout(function () {
        var alvo = document.getElementById("col-" + colunaAlvo);
        if (alvo) {
          alvo.classList.add("realce");
          alvo.scrollIntoView({ block: "center", behavior: "smooth" });
        }
      }, 30);
    }

    return frag;
  }

  function rotuloEstado(estado) {
    return { PK: "Chave primária", UK: "Chave única", UN: "Índice único" }[estado] || "Índice";
  }

  function listaFks(lista, tabela, direcao) {
    var rotuloTabela = direcao === "saida" ? "Tabela referenciada" : "Tabela de origem";
    return el("div", { classe: "rolagem" }, [
      el("table", { classe: "grade" }, [
        el("caption", { classe: "sr-only", texto:
          (direcao === "saida" ? "Tabelas referenciadas por " : "Tabelas que referenciam ") + tabela.nome }),
        el("thead", {}, [el("tr", {}, [
          el("th", { texto: "Constraint", scope: "col" }),
          el("th", { texto: rotuloTabela, scope: "col" }),
          el("th", { texto: "Colunas", scope: "col" }),
          el("th", { texto: "Obrigatória", scope: "col" })
        ])]),
        el("tbody", {}, lista.map(function (fk) {
          // fk.colunas pertencem sempre à tabela de origem do relacionamento;
          // o lado desta tabela aparece sem prefixo, o outro lado qualificado.
          var origem = direcao === "saida"
            ? fk.colunas.join(", ")
            : fk.tabela + "." + fk.colunas.join(", ");
          var destino = direcao === "saida"
            ? fk.tabela + "." + fk.colunas_referidas.join(", ")
            : fk.colunas_referidas.join(", ");
          return el("tr", {}, [
            el("td", { classe: "col-tipo", texto: fk.nome, "data-th": "Constraint" }),
            el("td", { classe: "col-nome", "data-th": rotuloTabela }, [linkTabela(fk.tabela)]),
            el("td", { classe: "col-tipo", texto: origem + " → " + destino, "data-th": "Colunas" }),
            el("td", { classe: "col-tipo", texto: fk.obrigatoria ? "Sim" : "Não", "data-th": "Obrigatória" })
          ]);
        }))
      ])
    ]);
  }

  function paginaBusca(consulta) {
    var frag = document.createDocumentFragment();
    var resultados = buscar(consulta);

    frag.appendChild(el("div", { classe: "cabecalho-pagina" }, [
      el("h1", { classe: "text-up-03" }, [
        document.createTextNode("Busca por "),
        el("span", { classe: "col-nome", texto: "“" + consulta + "”" })
      ]),
      el("p", { classe: "descricao-tabela", texto:
        resultados.length ? plural(resultados.length, "tabela encontrada", "tabelas encontradas")
          : "Nenhum resultado." })
    ]));

    if (!resultados.length) {
      frag.appendChild(mensagem("info", "Nenhum resultado.",
        "Nenhuma tabela ou coluna corresponde a “" + consulta + "”."));
      return frag;
    }

    resultados.slice(0, 60).forEach(function (grupo) {
      var colunas = grupo.colunas.slice(0, 12);
      frag.appendChild(el("article", { classe: "br-card resultado mb-3" }, [
        el("div", { classe: "card-content" }, [
          el("h3", {}, [
            el("a", { href: "#/tabela/" + grupo.tabela.nome }, [destacar(grupo.tabela.nome, consulta)]),
            el("span", { classe: "contagem", texto: grupo.tabela.colunas.length + " colunas" })
          ]),
          grupo.tabela.descricao
            ? el("p", { classe: "contexto" }, [destacar(grupo.tabela.descricao, consulta, 220)])
            : null,
          colunas.length ? el("ul", {}, colunas.map(function (c) {
            return el("li", {}, [
              el("a", {
                href: "#/tabela/" + grupo.tabela.nome + "?col=" + encodeURIComponent(c.nome),
                classe: "nome-col"
              }, [destacar(c.nome, consulta)]),
              el("span", { classe: "tipo-col", texto: c.tipo }),
              c.descricao ? el("div", { classe: "contexto" }, [destacar(c.descricao, consulta, 200)]) : null
            ]);
          })) : null,
          grupo.colunas.length > colunas.length
            ? el("p", { classe: "contexto", texto: "+ " + (grupo.colunas.length - colunas.length) + " outras colunas nesta tabela." })
            : null
        ])
      ]));
    });

    if (resultados.length > 60) {
      frag.appendChild(mensagem("info", "Resultados parciais.",
        "Exibindo as 60 tabelas mais relevantes de " + resultados.length + ". Refine a busca para ver o restante."));
    }

    return frag;
  }

  function paginaMapa() {
    var frag = document.createDocumentFragment();
    var mapa = calcularMapa();
    var isoladas = TABELAS.filter(function (t) {
      return !VIZINHOS[t.nome].saida.length && !VIZINHOS[t.nome].entrada.length;
    });

    frag.appendChild(el("div", { classe: "cabecalho-pagina" }, [
      el("h1", { texto: "Mapa de relacionamentos" }),
      el("p", { classe: "descricao-tabela", texto: "Passe o mouse para isolar a vizinhança, use a roda para dar zoom, arraste para mover e clique para abrir a tabela." })
    ]));

    var svg = montarMapa();
    frag.appendChild(el("div", { classe: "barra-ferramentas" }, [
      botao("Reiniciar visualização", "compress-arrows-alt", function () { svg.reiniciarVista(); }, "secondary"),
      botao("Baixar Mermaid do modelo", "project-diagram", function () {
        var linhas = ["erDiagram"];
        ARESTAS.forEach(function (a) {
          linhas.push("  " + a.destino + " ||--o{ " + a.origem + " : " + JSON.stringify(a.nome));
        });
        baixar("cad3-relacionamentos.mmd", linhas.join("\n") + "\n", "text/plain");
      }, "secondary")
    ]));

    frag.appendChild(el("div", { classe: "moldura-svg" }, [svg]));

    if (isoladas.length) {
      frag.appendChild(painel("Tabelas sem relacionamentos declarados", isoladas.length + " tabelas",
        el("div", { classe: "pilulas" }, isoladas.map(function (t) {
          return el("a", { classe: "br-tag interaction-select", href: "#/tabela/" + t.nome }, [
            el("span", { texto: t.nome })
          ]);
        }))));
    }

    return frag;
  }

  function paginaNaoEncontrada(nome) {
    var frag = document.createDocumentFragment();
    frag.appendChild(el("div", { classe: "cabecalho-pagina" }, [
      el("h1", { texto: "Tabela não encontrada" })
    ]));
    frag.appendChild(mensagem("danger", "Tabela não encontrada.",
      "Não existe nenhuma tabela chamada “" + nome + "” neste dicionário."));
    frag.appendChild(el("div", { classe: "barra-ferramentas" }, [
      el("a", { classe: "br-button primary", href: "#/" }, [
        icone("home"), document.createTextNode("Voltar ao início")
      ])
    ]));
    return frag;
  }

  /* ------------------------------------------------------------------ *
   * Lateral e roteamento
   * ------------------------------------------------------------------ */

  var listaLateral = $("#lista-tabelas");
  var contador = $("#contador-tabelas");
  var itensLaterais = Object.create(null);

  function montarLateral(filtro) {
    limpar(listaLateral);
    itensLaterais = Object.create(null);
    var alvo = normalizar(filtro);
    var total = 0;

    GRUPOS.forEach(function (grupo) {
      var tabelas = grupo.tabelas.filter(function (t) {
        return !alvo || normalizar(t.nome).indexOf(alvo) >= 0 || normalizar(t.descricao).indexOf(alvo) >= 0;
      }).sort(function (a, b) { return a.nome.localeCompare(b.nome); });
      if (!tabelas.length) return;

      listaLateral.appendChild(el("div", { classe: "grupo-titulo", texto: grupo.nome }));
      tabelas.forEach(function (t) {
        var item = el("a", {
          classe: "menu-item", role: "treeitem",
          href: "#/tabela/" + t.nome, title: t.descricao || t.nome
        }, [
          el("span", { classe: "content", texto: t.nome }),
          el("span", { classe: "qtd", texto: t.colunas.length })
        ]);
        itensLaterais[t.nome] = item;
        listaLateral.appendChild(item);
        total++;
      });
    });

    if (!total) listaLateral.appendChild(el("p", { classe: "vazio-lista", texto: "Nenhuma tabela encontrada." }));
    contador.textContent = total + "/" + TABELAS.length;
  }

  function marcarAtual(nome) {
    Object.keys(itensLaterais).forEach(function (chave) {
      if (chave === nome) itensLaterais[chave].setAttribute("aria-current", "page");
      else itensLaterais[chave].removeAttribute("aria-current");
    });
    if (nome && itensLaterais[nome] && itensLaterais[nome].scrollIntoView) {
      var caixa = itensLaterais[nome].getBoundingClientRect();
      var pai = listaLateral.getBoundingClientRect();
      if (caixa.top < pai.top || caixa.bottom > pai.bottom) {
        itensLaterais[nome].scrollIntoView({ block: "center" });
      }
    }
  }

  function irPara(hash) {
    if (location.hash === hash) rotear();
    else location.hash = hash;
  }

  /* Trilha no formato br-breadcrumb: o item "Início" é o botão de casa, e a
     página corrente é um <span aria-current="page">, não um link. */
  function montarTrilha(atual) {
    var lista = $("#lista-trilha");
    limpar(lista);

    lista.appendChild(el("li", { classe: "crumb home" }, [
      el("a", { classe: "br-button circle", href: "#/" }, [
        el("span", { classe: "sr-only", texto: "Página inicial" }),
        icone("home")
      ])
    ]));

    if (!atual) return;
    lista.appendChild(el("li", { classe: "crumb", "data-active": "active" }, [
      el("i", { classe: "icon fas fa-chevron-right", "aria-hidden": "true" }),
      el("span", { tabindex: "0", "aria-current": "page", texto: atual })
    ]));
  }

  function rotear() {
    var bruto = location.hash.replace(/^#/, "") || "/";
    var partes = bruto.split("?");
    var caminho = partes[0].split("/").filter(Boolean);
    var parametros = new URLSearchParams(partes[1] || "");
    var conteudo = $("#main-content");

    limpar(conteudo);
    document.title = "Dicionário de Dados — SINESP CAD 3";

    if (!caminho.length) {
      conteudo.appendChild(paginaInicial());
      montarTrilha(null);
      marcarAtual(null);
    } else if (caminho[0] === "tabela" && caminho[1]) {
      var nome = decodeURIComponent(caminho[1]);
      conteudo.appendChild(paginaTabela(nome, parametros.get("col")));
      montarTrilha(nome);
      marcarAtual(nome);
      if (POR_NOME[nome]) document.title = nome + " — Dicionário CAD 3";
    } else if (caminho[0] === "busca") {
      var consulta = parametros.get("q") || "";
      $("#busca-global").value = consulta;
      conteudo.appendChild(paginaBusca(consulta));
      montarTrilha("Busca");
      marcarAtual(null);
      document.title = "Busca: " + consulta + " — Dicionário CAD 3";
    } else if (caminho[0] === "mapa") {
      conteudo.appendChild(paginaMapa());
      montarTrilha("Mapa de relacionamentos");
      marcarAtual(null);
      document.title = "Mapa de relacionamentos — Dicionário CAD 3";
    } else {
      conteudo.appendChild(paginaNaoEncontrada(bruto));
      montarTrilha("Não encontrada");
      marcarAtual(null);
    }

    if (!parametros.get("col")) window.scrollTo(0, 0);
    fecharMenu();
  }

  /* ------------------------------------------------------------------ *
   * Interações globais
   * ------------------------------------------------------------------ */

  /* Fecha o br-menu depois de navegar. Quem controla o estado é o BRMenu do
     core, que alterna a classe `active`; no desktop o menu fica aberto por CSS
     e essa classe nem entra em jogo. */
  function fecharMenu() {
    var menu = $("#main-navigation");
    if (menu) menu.classList.remove("active");
  }

  function iniciar() {
    montarLateral("");

    $("#filtro-tabelas").addEventListener("input", function (ev) {
      montarLateral(ev.target.value);
      var atual = location.hash.match(/^#\/tabela\/([^?]+)/);
      if (atual) marcarAtual(decodeURIComponent(atual[1]));
    });

    var temporizador = null;
    var campoBusca = $("#busca-global");
    campoBusca.addEventListener("input", function () {
      clearTimeout(temporizador);
      temporizador = setTimeout(function () {
        var valor = campoBusca.value.trim();
        if (valor.length >= 2) irPara("#/busca?q=" + encodeURIComponent(valor));
        else if (!valor && location.hash.indexOf("#/busca") === 0) irPara("#/");
      }, 220);
    });

    $("#form-busca").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var valor = campoBusca.value.trim();
      if (valor) irPara("#/busca?q=" + encodeURIComponent(valor));
    });

    document.addEventListener("keydown", function (ev) {
      var digitando = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
      if (ev.key === "/" && !digitando) { ev.preventDefault(); campoBusca.focus(); campoBusca.select(); }
      if (ev.key === "Escape") {
        if (document.activeElement === campoBusca) campoBusca.blur();
        fecharMenu();
      }
    });

    // A proveniência dos dados fica no fim de cada página de tabela ("Origem:
    // <arquivo>, página N"), não no rodapé institucional.

    window.addEventListener("hashchange", rotear);
    rotear();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
