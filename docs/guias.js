/* Guias de colunas: páginas explicativas para colunas cujo conteúdo não cabe
 * numa descrição de dicionário (JSONs, códigos compostos, formatos próprios).
 *
 * Ao contrário de dados.js e dados-recursos.js, este arquivo é escrito à mão:
 * o conteúdo vem de documentos de negócio, não do extrator. Cada guia se
 * associa a uma ou mais colunas pela chave "TABELA.COLUNA", dentro de um
 * schema, e o app.js troca o link da coluna na grade pelo link do guia
 * (ADR-010).
 *
 * Blocos aceitos em `blocos`:
 *   { tipo: "p", texto }                       parágrafo; `trecho` vira <code>
 *   { tipo: "lista", itens: [texto] }          lista com marcadores
 *   { tipo: "checklist", itens: [texto] }      lista de conferência
 *   { tipo: "tabela", colunas, linhas }        tabela simples, células em texto
 *   { tipo: "codigo", texto }                  bloco de código
 *   { tipo: "nota", nivel, titulo, texto }     br-message (info/warning/...)
 */
window.GUIAS_COLUNAS = [
  {
    slug: "grupos-adicionais",
    schema: "ocorrencia",
    colunas: ["OCORRENCIA.DS_GRUPOS_ADICIONAIS"],
    titulo: "Grupos de dados adicionais",
    resumo: "Como funcionam os grupos de dados adicionais do CAD e como montar o arquivo JSON " +
      "que define os campos extras gravados em OCORRENCIA.DS_GRUPOS_ADICIONAIS.",
    fonte: "Guia_do_Grupos_de_Dados_Adicionais.pdf",
    secoes: [
      {
        titulo: "A coluna no banco",
        blocos: [
          { tipo: "p", texto:
            "A coluna `DS_GRUPOS_ADICIONAIS`, da tabela `OCORRENCIA`, é um `CLOB` que guarda em " +
            "formato JSON os grupos de campos adicionais da ocorrência. A constraint " +
            "`CT_RESPOSTAS_GRUPOS_ADICIONAIS_JSON` garante que o conteúdo seja sempre um JSON " +
            "válido (`DS_GRUPOS_ADICIONAIS IS JSON`)." },
          { tipo: "p", texto:
            "Quais grupos e campos existem, e como cada um é exibido e validado, não está no " +
            "banco: vem do arquivo JSON de configuração cadastrado para cada grupo de dados " +
            "adicionais, descrito nas seções a seguir." },
          { tipo: "nota", nivel: "info", titulo: "O que este guia cobre.", texto:
            "O guia de origem documenta o arquivo de configuração dos grupos. O leiaute exato " +
            "das respostas gravadas na ocorrência não é descrito nele." }
        ]
      },
      {
        titulo: "Para que serve",
        blocos: [
          { tipo: "p", texto:
            "O grupo de dados adicionais acrescenta campos extras ao registro de uma ocorrência, " +
            "exibidos conforme a natureza e a agência envolvidas. Esses campos são definidos em " +
            "um arquivo JSON de configuração, enviado no cadastro do grupo." },
          { tipo: "p", texto:
            "O arquivo modelo (`modeloJSONGrupoAdicional.json`), disponível para download na " +
            "própria tela de cadastro, é o ponto de partida recomendado." }
        ]
      },
      {
        titulo: "Campos do formulário de cadastro",
        blocos: [
          { tipo: "p", texto: "Todos os quatro campos do formulário são obrigatórios e editáveis." },
          { tipo: "tabela",
            colunas: ["Campo", "Formato", "O que informar", "Mensagem se houver erro"],
            linhas: [
              ["Nome do Grupo de Dados Adicionais", "Alfanumérico, até 100 caracteres",
               "Um nome que ainda não esteja em uso por outro grupo ativo", "MSG-ER0057 (nome já utilizado)"],
              ["Arquivo JSON de Configuração", "Arquivo .json",
               "O arquivo com os grupos e campos. Após o envio, o arquivo pode ser baixado novamente",
               "MSG-ER0058 (arquivo não está em formato JSON)"],
              ["Naturezas", "Seleção múltipla", "Pelo menos uma natureza à qual o grupo se aplica",
               "MSG-ER0061 (nenhuma natureza informada)"],
              ["Agências", "Seleção múltipla", "Pelo menos uma agência que usará o grupo",
               "MSG-ER0061 (nenhuma agência informada)"]
            ] },
          { tipo: "p", texto:
            "Naturezas: quem tem acesso a “Manter Natureza” vê todas as naturezas ativas, em ordem " +
            "alfabética. As escolhidas aparecem como cards com ícone, nome, prioridade, tipos de " +
            "agência e grupos de dados já associados." },
          { tipo: "p", texto:
            "Agências: quem tem acesso a “Manter Agência” vê todas as agências ativas. Os demais " +
            "usuários veem apenas as agências da mesma EO ou de EOs subordinadas à sua. Os cards " +
            "mostram nome, EO, tipo e esfera. Itens inativos aparecem nos cards em tom esmaecido." }
        ]
      },
      {
        titulo: "Estrutura do arquivo JSON",
        blocos: [
          { tipo: "p", texto:
            "O arquivo tem três níveis: a raiz, que contém uma lista de grupos; cada grupo contém " +
            "uma lista de campos; e os campos de escolha contêm uma lista de opções. Só os " +
            "atributos abaixo são aceitos, e qualquer atributo fora do modelo é rejeitado." },
          { tipo: "codigo", texto:
            "raiz\n" +
            "└── grupos[]\n" +
            "    └── campos[]\n" +
            "        └── opcoes[]   (só em selecao, selecaoMultipla e opcao)" },
          { tipo: "subtitulo", texto: "Raiz" },
          { tipo: "tabela", colunas: ["Atributo", "Obrigatório", "Descrição"], codigo: [0],
            linhas: [
              ["id", "Sim", "Identificador da configuração"],
              ["grupos", "Sim", "Lista com pelo menos um grupo"]
            ] },
          { tipo: "subtitulo", texto: "Grupo (cada item de grupos)" },
          { tipo: "tabela", colunas: ["Atributo", "Obrigatório", "Descrição"], codigo: [0],
            linhas: [
              ["id", "Sim", "Identificador do grupo. Não pode se repetir no arquivo"],
              ["nome", "Sim", "Título exibido para o grupo"],
              ["descricao", "Sim", "Texto explicativo do grupo"],
              ["permiteLista", "Não", "true ou false (padrão do modelo: false)"],
              ["idsAgenciasObrigatorias", "Não",
               "Lista de identificadores (UUID) de agências para as quais os campos marcados como " +
               "obrigatórios serão exigidos. Cada UUID deve ser de agência cadastrada e ativa no CAD Configurações"],
              ["campos", "Sim", "Lista com pelo menos um campo"]
            ] },
          { tipo: "subtitulo", texto: "Campo (cada item de campos)" },
          { tipo: "tabela", colunas: ["Atributo", "Obrigatório", "Descrição"], codigo: [0],
            linhas: [
              ["id", "Sim", "Identificador do campo. Não pode se repetir dentro do mesmo grupo"],
              ["nome", "Sim", "Rótulo exibido no formulário"],
              ["tipo", "Sim", "Um dos nove tipos listados em “Tipos de campo”"],
              ["instrucao", "Sim", "Orientação de preenchimento exibida ao usuário"],
              ["obrigatorio", "Não", "true torna o campo de preenchimento obrigatório"],
              ["tamanhoColuna", "Não", "Largura do campo no formulário (ex.: 2)"],
              ["opcoes", "Sim, para selecao, selecaoMultipla e opcao", "Lista de opções de escolha"]
            ] },
          { tipo: "subtitulo", texto: "Opção (cada item de opcoes)" },
          { tipo: "tabela", colunas: ["Atributo", "Obrigatório", "Descrição"], codigo: [0],
            linhas: [
              ["valor", "Sim", "Código gravado. Sem espaços e sem caracteres especiais (ex.: opcao_1)"],
              ["rotulo", "Sim", "Texto exibido ao usuário (ex.: Opção 1)"]
            ] },
          { tipo: "p", texto:
            "Atributos opcionais podem ser omitidos ou informados como `null`. Os textos do " +
            "arquivo aceitam formatação em Markdown (por exemplo, `**negrito**`)." }
        ]
      },
      {
        titulo: "Tipos de campo",
        blocos: [
          { tipo: "p", texto:
            "O atributo `tipo` aceita apenas os nove valores abaixo, escritos exatamente assim " +
            "(maiúsculas e minúsculas importam)." },
          { tipo: "tabela", colunas: ["tipo", "Exibição", "Quando usar", "Exige opcoes?"], codigo: [0],
            linhas: [
              ["texto", "Caixa de texto de uma linha", "Nomes, códigos, textos curtos", "Não"],
              ["areaTexto", "Caixa de texto de várias linhas", "Descrições longas", "Não"],
              ["numero", "Campo numérico", "Quantidades e valores", "Não"],
              ["data", "Calendário", "Uma data", "Não"],
              ["dataHora", "Calendário com hora", "Data e horário", "Não"],
              ["caixaSelecao", "Checkbox", "Confirmação sim/não", "Não"],
              ["selecao", "Lista suspensa (dropdown)", "Uma opção entre muitas", "Sim"],
              ["opcao", "Botões de rádio", "Uma opção entre poucas, todas visíveis", "Sim"],
              ["selecaoMultipla", "Lista de seleção múltipla", "Uma ou mais opções", "Sim"]
            ] },
          { tipo: "subtitulo", texto: "Exemplo de campo simples" },
          { tipo: "codigo", texto:
            "{\n" +
            "  \"id\": \"placa_veiculo\",\n" +
            "  \"nome\": \"Placa do veículo\",\n" +
            "  \"tipo\": \"texto\",\n" +
            "  \"instrucao\": \"Informe a placa no formato AAA0A00.\",\n" +
            "  \"obrigatorio\": true\n" +
            "}" },
          { tipo: "subtitulo", texto: "Exemplo de campo com opções" },
          { tipo: "codigo", texto:
            "{\n" +
            "  \"id\": \"cor_veiculo\",\n" +
            "  \"nome\": \"Cor do veículo\",\n" +
            "  \"tipo\": \"selecao\",\n" +
            "  \"instrucao\": \"Selecione a cor predominante.\",\n" +
            "  \"opcoes\": [\n" +
            "    { \"valor\": \"branco\", \"rotulo\": \"Branco\" },\n" +
            "    { \"valor\": \"preto\",  \"rotulo\": \"Preto\" },\n" +
            "    { \"valor\": \"prata\",  \"rotulo\": \"Prata\" }\n" +
            "  ]\n" +
            "}" }
        ]
      },
      {
        titulo: "Regras de validação",
        blocos: [
          { tipo: "p", texto:
            "Ao enviar o arquivo, o sistema confere todas as regras abaixo de uma vez. Se alguma " +
            "falhar, o cadastro não é concluído e é exibida a lista completa de problemas." },
          { tipo: "tabela", colunas: ["#", "Regra", "Aplica-se a"],
            linhas: [
              ["1", "O arquivo deve ser um JSON válido (caso contrário: MSG-ER0058)", "Arquivo"],
              ["2", "Somente atributos existentes no arquivo modelo são aceitos", "Arquivo inteiro"],
              ["3", "Deve haver pelo menos um grupo com pelo menos um campo", "Arquivo"],
              ["4", "id é obrigatório", "Cada grupo e cada campo"],
              ["5", "O id de um grupo não pode se repetir no arquivo", "Grupos"],
              ["6", "O id de um campo não pode se repetir dentro do mesmo grupo (pode repetir em grupos diferentes)", "Campos"],
              ["7", "nome e descricao são obrigatórios", "Cada grupo"],
              ["8", "idsAgenciasObrigatorias, se informado, só pode conter agências cadastradas e ativas no CAD Configurações", "Grupos"],
              ["9", "tipo é obrigatório e deve ser um dos nove tipos válidos", "Cada campo"],
              ["10", "nome e instrucao são obrigatórios", "Cada campo"],
              ["11", "valor e rotulo são obrigatórios nas opções", "Campos selecao, selecaoMultipla e opcao"],
              ["12", "valor não pode ter espaços nem caracteres especiais", "Opções"]
            ] },
          { tipo: "nota", nivel: "warning", titulo: "Dica para a regra 12.", texto:
            "Use letras sem acento, números e sublinhado. via_publica é aceito; via pública e " +
            "via-pública! não são." }
        ]
      },
      {
        titulo: "Como ler o relatório de erros",
        blocos: [
          { tipo: "p", texto:
            "Cada problema encontrado aparece em uma linha do relatório com cinco informações: " +
            "categoria do erro, item validado (o grupo ou campo), campo com erro (o atributo), " +
            "valor informado e descrição do erro. Corrija todos os itens listados e envie o " +
            "arquivo novamente." },
          { tipo: "subtitulo", texto: "Erros mais comuns" },
          { tipo: "tabela", colunas: ["Problema", "Causa provável", "Como corrigir"],
            linhas: [
              ["Arquivo não é JSON", "Vírgula sobrando no último item, aspas simples, chave não fechada",
               "Valide o arquivo em um editor ou validador de JSON antes de enviar"],
              ["Atributo não permitido", "Nome digitado errado (ex.: instrução, descrição, Tipo)",
               "Use os nomes exatamente como no modelo, sem acento"],
              ["Tipo inválido", "Texto, checkbox, dropdown", "Use um dos nove tipos, com a grafia exata"],
              ["id repetido", "Grupo ou campo copiado sem trocar o id",
               "Dê um id único a cada grupo, e a cada campo dentro do grupo"],
              ["Opções ausentes", "Campo selecao, opcao ou selecaoMultipla sem opcoes, ou opção sem valor/rotulo",
               "Inclua a lista de opções, cada uma com valor e rotulo"],
              ["valor inválido", "Espaço, acento ou símbolo no valor", "Troque por letras sem acento, números e _"],
              ["Agência inexistente", "UUID errado ou de agência inativa em idsAgenciasObrigatorias",
               "Confira o UUID no CAD Configurações"]
            ] }
        ]
      },
      {
        titulo: "Exemplo completo",
        blocos: [
          { tipo: "p", texto:
            "O arquivo abaixo está em uso em produção e passa em todas as regras. Ele mostra três " +
            "práticas úteis:" },
          { tipo: "lista", itens: [
            "`permiteLista: true` permite registrar vários objetos na mesma ocorrência.",
            "A opção “Outros” acompanhada de um campo de texto opcional: `desc_objeto_outros` " +
              "complementa a opção `outros`. O sistema não condiciona um campo ao outro; a " +
              "orientação fica na `instrucao`.",
            "Atributos opcionais com `null`: `tamanhoColuna` e `opcoes` podem ser informados como " +
              "`null` quando não se aplicam."
          ] },
          { tipo: "nota", nivel: "warning", titulo: "Troque o UUID ao reaproveitar.", texto:
            "O UUID em idsAgenciasObrigatorias é o de uma agência específica. Ao reaproveitar o " +
            "arquivo, substitua-o pelo da sua agência." },
          { tipo: "codigo", texto:
            "{\n" +
            "  \"id\": \"objetos_apreendidos\",\n" +
            "  \"grupos\": [\n" +
            "    {\n" +
            "      \"id\": \"objetos_apreendidos_detalhes\",\n" +
            "      \"nome\": \"Objetos Apreendidos\",\n" +
            "      \"descricao\": \"Informações sobre objetos apreendidos na ocorrência.\",\n" +
            "      \"permiteLista\": true,\n" +
            "      \"idsAgenciasObrigatorias\": [\n" +
            "        \"abbf7b19-cc3d-47fc-bb9f-f6c0c7b2cb8b\"\n" +
            "      ],\n" +
            "      \"campos\": [\n" +
            "        {\n" +
            "          \"id\": \"tipo_objeto\",\n" +
            "          \"tipo\": \"selecao\",\n" +
            "          \"nome\": \"Tipo de Objeto\",\n" +
            "          \"instrucao\": \"Selecione o tipo de objeto apreendido\",\n" +
            "          \"obrigatorio\": true,\n" +
            "          \"tamanhoColuna\": null,\n" +
            "          \"opcoes\": [\n" +
            "            { \"valor\": \"balanca_medidor_precisao\", \"rotulo\": \"Balança/Medidores de Precisão\" },\n" +
            "            { \"valor\": \"cabos_e_fios\", \"rotulo\": \"Cabos e Fios\" },\n" +
            "            { \"valor\": \"carretel_de_linha\", \"rotulo\": \"Carretel de Linha\" },\n" +
            "            { \"valor\": \"carretinha_som_automotivo\", \"rotulo\": \"Carretinha - som automotivo\" },\n" +
            "            { \"valor\": \"celular\", \"rotulo\": \"Celular\" },\n" +
            "            { \"valor\": \"eppendorf_vazio\", \"rotulo\": \"Eppendorf vazio (embalagem)\" },\n" +
            "            { \"valor\": \"estojo_municao\", \"rotulo\": \"Estojo de munição\" },\n" +
            "            { \"valor\": \"linha_chilena\", \"rotulo\": \"Linha Chilena\" },\n" +
            "            { \"valor\": \"linha_cortante\", \"rotulo\": \"Linha Cortante\" },\n" +
            "            { \"valor\": \"maquina_caca_niquel\", \"rotulo\": \"Maquina Caça Níquel\" },\n" +
            "            { \"valor\": \"municao\", \"rotulo\": \"Munição\" },\n" +
            "            { \"valor\": \"valor_moeda\", \"rotulo\": \"Valor / Moeda\" },\n" +
            "            { \"valor\": \"outros\", \"rotulo\": \"Outros\" }\n" +
            "          ]\n" +
            "        },\n" +
            "        {\n" +
            "          \"id\": \"desc_objeto_outros\",\n" +
            "          \"tipo\": \"texto\",\n" +
            "          \"nome\": \"Descrição do Objeto\",\n" +
            "          \"instrucao\": \"Descreva o objeto quando selecionar a opção Outros\",\n" +
            "          \"obrigatorio\": false,\n" +
            "          \"tamanhoColuna\": null,\n" +
            "          \"opcoes\": null\n" +
            "        },\n" +
            "        {\n" +
            "          \"id\": \"qtd_objeto\",\n" +
            "          \"tipo\": \"numero\",\n" +
            "          \"nome\": \"Quantidade\",\n" +
            "          \"instrucao\": \"Informe a quantidade do objeto apreendido\",\n" +
            "          \"obrigatorio\": true,\n" +
            "          \"tamanhoColuna\": null,\n" +
            "          \"opcoes\": null\n" +
            "        },\n" +
            "        {\n" +
            "          \"id\": \"unidade_medida\",\n" +
            "          \"tipo\": \"selecao\",\n" +
            "          \"nome\": \"Unidade de Medida\",\n" +
            "          \"instrucao\": \"Selecione a unidade de medida correspondente ao objeto\",\n" +
            "          \"obrigatorio\": true,\n" +
            "          \"tamanhoColuna\": null,\n" +
            "          \"opcoes\": [\n" +
            "            { \"valor\": \"unidade\", \"rotulo\": \"Unidade\" },\n" +
            "            { \"valor\": \"metros\", \"rotulo\": \"Metros\" },\n" +
            "            { \"valor\": \"reais\", \"rotulo\": \"Reais\" },\n" +
            "            { \"valor\": \"grama\", \"rotulo\": \"Grama\" },\n" +
            "            { \"valor\": \"kilograma\", \"rotulo\": \"Kilograma\" },\n" +
            "            { \"valor\": \"litro\", \"rotulo\": \"Litro\" }\n" +
            "          ]\n" +
            "        }\n" +
            "      ]\n" +
            "    }\n" +
            "  ]\n" +
            "}" }
        ]
      },
      {
        titulo: "Antes de enviar, confira",
        blocos: [
          { tipo: "checklist", itens: [
            "O arquivo abre sem erro em um validador de JSON.",
            "Usei apenas atributos do modelo, sem acentos nos nomes dos atributos.",
            "Há pelo menos um grupo com pelo menos um campo.",
            "Todo grupo tem `id`, `nome` e `descricao`, com `id` único no arquivo.",
            "Todo campo tem `id`, `nome`, `tipo` e `instrucao`, com `id` único no grupo.",
            "Todo `tipo` é um dos nove valores válidos.",
            "Campos `selecao`, `opcao` e `selecaoMultipla` têm `opcoes` com `valor` e `rotulo`.",
            "Nenhum `valor` tem espaço, acento ou símbolo.",
            "Os UUIDs em `idsAgenciasObrigatorias` são de agências ativas.",
            "No formulário, o nome do grupo é inédito e há ao menos uma natureza e uma agência selecionadas."
          ] }
        ]
      }
    ]
  }
];
