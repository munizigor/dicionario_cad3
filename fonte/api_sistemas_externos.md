# APIs para Sistemas Externos

Documentação das APIs destinadas ao consumo e gerenciamento de dados por sistemas externos integrados.

> **Referência:** documento alinhado à especificação OpenAPI *CAD Serviços Agente Operacional* — versão **0.7.2**.

---

## Índice

1. [Informações Gerais](#informações-gerais)
   - [URL Base](#url-base)
   - [Headers Obrigatórios](#headers-obrigatórios)
2. [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados)
3. [API de Unidade de Serviço](#api-de-unidade-de-serviço)
   - [Listar Unidades de Serviço](#listar-unidades-de-serviço)
   - [Detalhar Pessoa da Equipe](#detalhar-pessoa-da-equipe)
   - [Criar Unidade de Serviço](#criar-unidade-de-serviço)
   - [Editar Unidade de Serviço](#editar-unidade-de-serviço)
   - [Iniciar Serviço da Unidade de Serviço](#iniciar-serviço-da-unidade-de-serviço)
   - [Encerrar Serviço da Unidade de Serviço](#encerrar-serviço-da-unidade-de-serviço)
   - [Ativar Unidade de Serviço](#ativar-unidade-de-serviço)
   - [Inativar Unidade de Serviço](#inativar-unidade-de-serviço)
   - [Excluir Unidade de Serviço](#excluir-unidade-de-serviço)
   - [Vincular Pessoa à Equipe](#vincular-pessoa-à-equipe)
   - [Desvincular Pessoa da Equipe](#desvincular-pessoa-da-equipe)
   - [Vincular Equipamento à Unidade de Serviço](#vincular-equipamento-à-unidade-de-serviço)
   - [Desvincular Equipamento da Unidade de Serviço](#desvincular-equipamento-da-unidade-de-serviço)
   - [Alterar Equipe em Serviço](#alterar-equipe-em-serviço)
   - [Criar Equipe](#criar-equipe)
   - [Editar Equipe](#editar-equipe)
   - [Excluir Equipe](#excluir-equipe)
4. [API de Equipamento](#api-de-equipamento)
   - [Criar Equipamento](#criar-equipamento)
   - [Alterar Equipamento](#alterar-equipamento)
   - [Listar Equipamentos](#listar-equipamentos)
   - [Excluir Equipamento](#excluir-equipamento)
   - [Listar Tipos de Equipamento](#listar-tipos-de-equipamento)
5. [API de Pessoa](#api-de-pessoa)
   - [Criar Pessoa](#criar-pessoa)
   - [Alterar Pessoa](#alterar-pessoa)
   - [Listar Pessoas](#listar-pessoas)
   - [Excluir Pessoa](#excluir-pessoa)
   - [Listar Cargos Ativos por Agência](#listar-cargos-ativos-por-agência)
   - [Obter Cargo por UUID](#obter-cargo-por-uuid)
6. [API de Posições](#api-de-posições)
   - [Consultar Histórico de Posições Geográficas de uma Pessoa](#consultar-histórico-de-posições-geográficas-de-uma-pessoa)
   - [Consultar Últimas Posições Geográficas](#consultar-últimas-posições-geográficas)
   - [Pesquisar Histórico de Posições Geográficas](#pesquisar-histórico-de-posições-geográficas)
7. [Histórico de Alterações do Documento](#histórico-de-alterações-do-documento)

---

## Informações Gerais

### URL Base

Todas as APIs deste documento são expostas sob o caminho comum:

```
/agente-campo/v3
```

A URL completa de cada endpoint é composta por: **`{servidor}` + `/agente-campo/v3` + `{prefixo da API}` + `{caminho do endpoint}`**.

| API | URL Base Completa |
|-----|-------------------|
| Unidade de Serviço | `/agente-campo/v3/cad-unidade-servico-api` |
| Equipamento | `/agente-campo/v3/cad-equipamento-api` |
| Pessoa | `/agente-campo/v3/cad-pessoa-api` |
| Posições | `/agente-campo/v3/cad-posicoes-api` |

**Exemplo:**

```
POST {servidor}/agente-campo/v3/cad-unidade-servico-api/listar-unidade-servico
```

> **Nota:** Nos endpoints descritos neste documento, o caminho é apresentado de forma completa (a partir de `/agente-campo/v3`), bastando acrescentar o endereço do servidor do ambiente utilizado.

### Headers Obrigatórios

**Todos os endpoints deste documento** exigem os seguintes headers HTTP:

| Header | Tipo | Obrigatório | Restrições | Descrição |
|--------|------|-------------|------------|-----------|
| `cpf` | Texto | Sim | — | CPF do usuário responsável pela requisição |
| `nome` | Texto | Sim | Mínimo 1, máximo 255 caracteres | Nome do usuário responsável pela requisição |
| `sinesp-username` | Texto | Sim | Mínimo 1 caractere | Identificador do usuário/sistema no SINESP |

Para requisições com corpo, também deve ser enviado:

| Header | Valor |
|--------|-------|
| `Content-Type` | `application/json` |

**Exemplo de requisição:**

```http
POST /agente-campo/v3/cad-unidade-servico-api/listar-unidade-servico HTTP/1.1
Host: {servidor}
Content-Type: application/json
cpf: 12345678901
nome: João da Silva
sinesp-username: usuario.sistema

{
  "pagina": 1,
  "tamanhoPagina": 10
}
```

---

## Validações Comuns de Compartilhamento de Dados

Todos os endpoints desta API realizam validações relacionadas ao compartilhamento de dados do sistema integrado. As seguintes validações são aplicadas conforme o contexto de cada operação:

### 1. Compartilhamento de Dados Vazio

O sistema integrado deve ter pelo menos uma agência configurada no compartilhamento de dados.

**Mensagem de erro (400 Bad Request):**
```json
{
  "mensagem": "Não existem agências disponíveis no compartilhamento de dados com o sistema Integrado <nome sistema>"
}
```

### 2. Agências no Compartilhamento

Quando agências são informadas como parâmetro de entrada ou quando uma entidade (Unidade de Serviço, Equipamento, Pessoa) pertence a uma agência, esta deve estar disponível no compartilhamento de dados do sistema integrado.

**Mensagem de erro (400 Bad Request):**
```json
{
  "mensagem": "A agência <uuid> não disponível nos dados compartilhados com o Sistema Integrado <nome sistema>"
}
```

### 3. Regiões de Atuação no Compartilhamento

Quando existe Região de Atuação nos parâmetros de entrada ou quando uma entidade possui região de atuação, esta deve pertencer a uma agência que esteja disponível no compartilhamento de dados do sistema integrado.

**Mensagem de erro (400 Bad Request):**
```json
{
  "mensagem": "A região de atuação <uuid> pertence a uma agência não disponível no compartilhamento de dados com o sistema Integrado <nome sistema>"
}
```

### 4. Unidade de Serviço no Compartilhamento

Quando uma Unidade de Serviço é referenciada, suas regiões de atuação devem pertencer a agências disponíveis no compartilhamento de dados.

**Mensagem de erro (400 Bad Request):**
```json
{
  "mensagem": "A Unidade de Serviço pertence a uma agência não disponível no compartilhamento de dados com o sistema Integrado <nome sistema>"
}
```

---

## API de Unidade de Serviço

API destinada ao consumo de dados de unidades de serviço por sistemas externos integrados.

### Base URL

```
/agente-campo/v3/cad-unidade-servico-api
```

### Endpoints

### Listar Unidades de Serviço

Lista as unidades de serviço disponíveis para o sistema externo, incluindo seus equipamentos e equipes.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/listar-unidade-servico`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Lógica de Filtros

> **IMPORTANTE:** A API utiliza a seguinte lógica para combinar filtros:
>
> - **Relação entre campos diferentes:** `AND` (E) - Todos os filtros informados devem ser satisfeitos simultaneamente.
> - **Relação entre valores do mesmo campo:** `OR` (OU) - Basta satisfazer qualquer um dos valores informados.

**Exemplo prático:**

```json
{
  "situacoesUnidadeServico": ["AT", "ES"],
  "uuidsAgencia": ["uuid-agencia-1"]
}
```

Esta consulta retornará unidades de serviço que:
- Pertençam à agência `uuid-agencia-1` **E**
- Tenham situação `AT` (Ativa) **OU** `ES` (Em Serviço)

**Request Body:**

```json
{
  "pagina": 1,
  "tamanhoPagina": 10,
  "uuidsUnidadeServico": ["uuid-us-1", "uuid-us-2"],
  "uuidsAgencia": ["uuid-agencia-1", "uuid-agencia-2"],
  "uuidsRegiaoAtuacao": ["uuid-regiao-1"],
  "nomes": ["Nome US"],
  "numerosTicket": ["TICKET001"],
  "situacoesUnidadeServico": ["AT", "ES", "EP"],
  "prefixos": ["VTR-001", "VTR-002"],
  "placas": ["ABC1234", "DEF5678"],
  "nomesOuNomesFuncionais": ["João Silva", "Maria Santos"],
  "matriculas": ["MAT001", "MAT002"],
  "dataCriacaoInicio": "2024-01-01",
  "dataCriacaoFim": "2024-12-31",
  "dataInicioServicoInicio": "2024-01-01",
  "dataInicioServicoFim": "2024-12-31",
  "ordenacao": "nome",
  "sentido": "crescente",
  "omitirEquipes": false,
  "omitirEquipamentos": false
}
```

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `pagina` | Número inteiro | Não | Número da página (padrão: 1) |
| `tamanhoPagina` | Número inteiro | Não | Registros por página (máximo: 25, padrão: 5) |
| `uuidsUnidadeServico` | Array de UUID | Não | UUIDs das unidades de serviço para filtrar |
| `uuidsAgencia` | Array de UUID | Não | UUIDs das agências para filtrar |
| `uuidsRegiaoAtuacao` | Array de UUID | Não | UUIDs das regiões de atuação |
| `nomes` | Array de texto | Não | Nomes das unidades (busca parcial, mín. 3 caracteres) |
| `numerosTicket` | Array de texto | Não | Números dos tickets |
| `situacoesUnidadeServico` | Array de texto | Não | Situações da unidade de serviço (ver tabela abaixo) |
| `prefixos` | Array de texto | Não | Prefixos dos equipamentos para filtrar |
| `placas` | Array de texto | Não | Placas dos equipamentos para filtrar |
| `nomesOuNomesFuncionais` | Array de texto | Não | Nomes ou nomes funcionais dos integrantes das equipes para filtrar |
| `matriculas` | Array de texto | Não | Matrículas dos integrantes das equipes para filtrar |
| `dataCriacaoInicio` | Data (YYYY-MM-DD) | Não | Data inicial de criação. **Se informado, `dataCriacaoFim` também deve ser informado.** |
| `dataCriacaoFim` | Data (YYYY-MM-DD) | Não | Data final de criação. **Se informado, `dataCriacaoInicio` também deve ser informado.** |
| `dataInicioServicoInicio` | Data (YYYY-MM-DD) | Não | Data inicial de início do serviço. **Se informado, `dataInicioServicoFim` também deve ser informado.** |
| `dataInicioServicoFim` | Data (YYYY-MM-DD) | Não | Data final de início do serviço. **Se informado, `dataInicioServicoInicio` também deve ser informado.** |
| `ordenacao` | Texto | Não | Campo de ordenação: `nome`, `ticket`, `data_criacao` |
| `sentido` | Texto | Não | Sentido: `crescente`, `decrescente` |
| `omitirEquipes` | Booleano | Não | Se `true`, não retorna as equipes de cada unidade de serviço |
| `omitirEquipamentos` | Booleano | Não | Se `true`, não retorna os equipamentos de cada unidade de serviço |

> **Importante:** Os campos de data trabalham em pares. Se uma data de início for informada, a data de fim correspondente também deve ser informada, e vice-versa. O intervalo máximo permitido entre as datas é de **365 dias (1 ano)**.

### Situações da Unidade de Serviço

| Sigla | Descrição |
|-------|-----------|
| `AT` | Ativa |
| `IN` | Inativa |
| `EX` | Excluída |
| `ES` | Em Serviço |
| `EP` | Empenhada |
| `PO` | Em Pausa Operacional |

> **Comportamento Padrão:** Se o campo `situacoesUnidadeServico` não for informado, a API retorna automaticamente todas as situações **exceto "Excluída" (EX)**. Para consultar unidades de serviço excluídas, é necessário informar explicitamente a situação `EX` no filtro.

**Response (200 OK):**

```json
{
  "metadados": {
    "paginaAtual": 1,
    "registrosPorPagina": 10,
    "totalRegistros": 50,
    "totalPaginas": 5
  },
  "dados": [
    {
      "uuid": "uuid-unidade-servico",
      "ticket": "TICKET001",
      "observacao": "Observação da US",
      "nome": "Nome da Unidade de Serviço",
      "situacao": "ES",
      "idModalidade": 1,
      "descricaoModalidade": "Modalidade A",
      "regioesAtuacao": ["uuid-regiao-1", "uuid-regiao-2"],
      "areaAtuacao": "Área Centro",
      "dataInicioServico": "2024-01-15T08:00:00",
      "dataCriacao": "2024-01-10T10:30:00",
      "siglaFusoHorario": "BRT",
      "equipamentos": [
        {
          "uuid": "uuid-equipamento",
          "prefixo": "VTR-001",
          "placa": "ABC1234",
          "marca": "Chevrolet",
          "modelo": "S10",
          "situacao": "ATIVO",
          "tipoEquipamentoId": 1,
          "tipoEquipamentoNome": "Viatura",
          "uuidAgencia": "uuid-agencia",
          "uuidRegiaoAtuacao": "uuid-regiao"
        }
      ],
      "equipes": [
        {
          "uuid": "uuid-equipe",
          "nome": "Equipe Alpha",
          "telefone": "(11) 99999-9999",
          "situacao": "EM_SERVICO",
          "dataInicioServico": "2024-01-15T08:00:00",
          "pessoas": ["uuid-pessoa-1", "uuid-pessoa-2"]
        }
      ]
    }
  ],
  "ordenacao": "nome",
  "sentido": "crescente"
}
```

**Campos do Response - Metadados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `paginaAtual` | Número inteiro | Página atual da consulta |
| `registrosPorPagina` | Número inteiro | Quantidade de registros por página |
| `totalRegistros` | Número inteiro | Total de registros encontrados |
| `totalPaginas` | Número inteiro | Total de páginas disponíveis |

> **Notas:**
> - Quando `omitirEquipes` ou `omitirEquipamentos` estiver `true`, os campos correspondentes (`equipes` ou `equipamentos`) não aparecerão no JSON de resposta.
> - O campo `pessoas` dentro de cada equipe contém uma lista de **UUIDs** das pessoas que compõem a equipe.

#### Validações

A API realiza as seguintes validações para este endpoint, retornando `400 Bad Request` em caso de violação:

> **Nota:** As validações de compartilhamento de dados (agências, regiões de atuação) estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### 1. Tamanho da Página

O parâmetro `tamanhoPagina` deve ser no máximo **25**.

**Mensagem de erro:**
```
O tamanho da página deve ser no máximo 25
```

##### 2. Validação de Intervalos de Data

Os campos de data devem ser informados em pares (início e fim). Se um for informado, o outro também deve ser.

**Mensagens de erro:**
```
Quando 'dataCriacaoInicio' é informado, 'dataCriacaoFim' também deve ser informado
```
```
Quando 'dataInicioServicoFim' é informado, 'dataInicioServicoInicio' também deve ser informado
```

##### 3. Data de Início Posterior à Data de Fim

A data de início não pode ser posterior à data de fim.

**Mensagem de erro:**
```
A 'dataCriacaoInicio' não pode ser posterior à 'dataCriacaoFim'
```

##### 4. Intervalo Máximo de Data

O intervalo entre as datas de início e fim não pode ser superior a 1 ano (365 dias).

**Mensagem de erro:**
```
O intervalo entre 'dataCriacaoInicio' e 'dataCriacaoFim' não pode ser superior a 1 ano (365 dias)
```

##### 5. Campos Desconhecidos

A API rejeita requisições que contenham campos não mapeados no body JSON.

**Mensagem de erro:**
```
Campo desconhecido no corpo da requisição: '<nome_campo>'
```

#### Comportamentos Padrão

| Condição | Comportamento |
|----------|---------------|
| Nenhuma agência e nenhuma região de atuação informada | Utiliza automaticamente as agências do compartilhamento de dados |
| Campo `situacoesUnidadeServico` não informado | Retorna todas as situações **exceto "Excluída" (EX)** |
| `omitirEquipes = true` | Campo `equipes` não aparece no JSON de resposta |
| `omitirEquipamentos = true` | Campo `equipamentos` não aparece no JSON de resposta |

---

### Detalhar Pessoa da Equipe

Retorna os dados detalhados de uma pessoa vinculada a uma equipe.

**Endpoint:** `GET /agente-campo/v3/cad-unidade-servico-api/detalhar-pessoa-equipe/{uuidEquipe}/{uuidPessoa}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidEquipe` | UUID | Sim | UUID da equipe |
| `uuidPessoa` | UUID | Sim | UUID da pessoa |

**Response (200 OK):**

```json
{
  "uuid": "uuid-pessoa",
  "cpf": "12345678901",
  "registroFuncional": "RF001",
  "nome": "João da Silva",
  "nomeFuncional": "João Silva",
  "uuidCargo": "uuid-cargo",
  "nomeCargo": "Policial",
  "uuidFuncao": "uuid-funcao",
  "nomeFuncao": "Condutor",
  "telefoneFixo": "1133334444",
  "telefoneCelular": "11999998888",
  "uuidAgencia": "uuid-agencia",
  "uuidRegiaoAtuacao": "uuid-regiao",
  "dataInicioServicoOperadorBrt": "2024-01-15T08:00:00"
}
```

**Campos do Response:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID da pessoa |
| `cpf` | Texto | CPF da pessoa |
| `registroFuncional` | Texto | Registro funcional da pessoa |
| `nome` | Texto | Nome completo da pessoa |
| `nomeFuncional` | Texto | Nome funcional da pessoa |
| `uuidCargo` | UUID | UUID do cargo da pessoa |
| `nomeCargo` | Texto | Nome do cargo |
| `uuidFuncao` | UUID | UUID da função na equipe |
| `nomeFuncao` | Texto | Nome da função na equipe |
| `telefoneFixo` | Texto | Telefone fixo da pessoa |
| `telefoneCelular` | Texto | Telefone celular da pessoa |
| `uuidAgencia` | UUID | UUID da agência da pessoa |
| `uuidRegiaoAtuacao` | UUID | UUID da região de atuação da pessoa |
| `dataInicioServicoOperadorBrt` | Data/Hora | Data e hora de início do serviço do operador (horário de Brasília) |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados (Unidade de Serviço) estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a equipe, a unidade de serviço ou a pessoa não é encontrada.

**Possíveis mensagens:**

```json
{
  "mensagem": "Equipe não encontrada"
}
```

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

```json
{
  "mensagem": "Pessoa não encontrada na equipe"
}
```

---

### Criar Unidade de Serviço

Cria uma nova Unidade de Serviço para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/criar-unidade-servico`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

**Request Body:**

```json
{
  "nome": "Nome da Unidade de Serviço",
  "areaAtuacao": "Área Centro",
  "regioesAtuacao": ["uuid-regiao-1", "uuid-regiao-2"],
  "idModalidade": 2,
  "descricaoModalidade": "Descrição quando modalidade é Outros",
  "observacao": "Observação opcional",
  "siglaFusoHorario": "BRT"
}
```

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `nome` | Texto | Sim | Nome da Unidade de Serviço (máximo 80 caracteres) |
| `areaAtuacao` | Texto | Sim | Área de atuação (máximo 50 caracteres) |
| `regioesAtuacao` | Array de UUID | Sim | Lista de UUIDs das regiões de atuação a serem vinculadas |
| `idModalidade` | Número inteiro | Sim | ID da modalidade (1 = Outros, requer descricaoModalidade) |
| `descricaoModalidade` | Texto | Condicional | Obrigatório quando `idModalidade` = 1 (Outros). Máximo 50 caracteres |
| `observacao` | Texto | Não | Observação (máximo 100 caracteres) |
| `siglaFusoHorario` | Texto | Sim | Sigla do fuso horário (ex: BRT, AMT, ACT, FNT) |

**Fusos Horários Disponíveis:**

| Sigla | Descrição |
|-------|-----------|
| `BRT` | Horário de Brasília (UTC-3) |
| `AMT` | Horário do Amazonas (UTC-4) |
| `ACT` | Horário do Acre (UTC-5) |
| `FNT` | Horário de Fernando de Noronha (UTC-2) |

**Response (200 OK):**

Retorna o UUID da Unidade de Serviço criada.

```json
"uuid-da-unidade-servico-criada"
```

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados (regiões de atuação) estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Campos Obrigatórios**

Todos os campos obrigatórios devem ser informados.

```json
{
  "mensagem": "O campo 'Nome' é obrigatório"
}
```

**2. Tamanho Máximo de Campos**

Os campos de texto possuem limites de tamanho.

```json
{
  "mensagem": "O campo 'Nome' deve ter no máximo 80 caracteres"
}
```

**3. Modalidade "Outros"**

Quando `idModalidade` = 1 (Outros), o campo `descricaoModalidade` é obrigatório.

```json
{
  "mensagem": "O campo 'Descrição da Modalidade' é obrigatório"
}
```

**4. Fuso Horário Inválido**

O fuso horário informado deve ser válido.

```json
{
  "mensagem": "O campo 'Fuso Horário' é inválido"
}
```

**5. Modalidade Inválida**

A modalidade informada deve existir.

```json
{
  "mensagem": "O campo 'Modalidade' é inválido"
}
```

**6. Regiões de Atuação Repetidas**

Não é permitido informar a mesma região de atuação mais de uma vez.

```json
{
  "mensagem": "Existem regiões de atuação repetidas"
}
```

**7. Região de Atuação Inválida**

A região de atuação informada deve existir e estar ativa.

```json
{
  "mensagem": "O campo 'Região de Atuação' é inválido - UUID: <uuid>"
}
```

**8. Campos Desconhecidos**

A API rejeita requisições que contenham campos não mapeados no body JSON.

```json
{
  "mensagem": "Campo desconhecido no corpo da requisição: '<nome_campo>'"
}
```

---

### Editar Unidade de Serviço

Edita uma Unidade de Serviço existente para sistemas externos. **Suporta edição parcial:** apenas os campos informados serão alterados, os demais mantêm seus valores atuais.

**Endpoint:** `PUT /agente-campo/v3/cad-unidade-servico-api/editar-unidade-servico/{uuid}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Unidade de Serviço a ser editada |

**Request Body:**

```json
{
  "nome": "Novo Nome da Unidade de Serviço",
  "areaAtuacao": "Nova Área de Atuação",
  "regioesAtuacaoNovas": ["uuid-nova-regiao-1"],
  "regioesAtuacaoRemover": ["uuid-regiao-remover-1"],
  "idModalidade": 2,
  "descricaoModalidade": "Nova descrição quando modalidade é Outros",
  "observacao": "Nova observação",
  "siglaFusoHorario": "BRT"
}
```

> **Edição Parcial:** Todos os campos são opcionais. Informe apenas os campos que deseja alterar. Campos não informados (ou com valor `null`) manterão seus valores atuais.

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `nome` | Texto | Não | Nome da Unidade de Serviço (máximo 80 caracteres). Se não informado, mantém o valor atual |
| `areaAtuacao` | Texto | Não | Área de atuação (máximo 50 caracteres). Se não informado, mantém o valor atual |
| `regioesAtuacaoNovas` | Array de UUID | Não | Lista de UUIDs de **novas** regiões de atuação a serem **adicionadas** |
| `regioesAtuacaoRemover` | Array de UUID | Não | Lista de UUIDs de regiões de atuação a serem **removidas**. Requer que a US esteja na situação **Ativa** |
| `idModalidade` | Número inteiro | Não | ID da modalidade. Se não informado, mantém o valor atual. Se informado como 1 (Outros), requer `descricaoModalidade` |
| `descricaoModalidade` | Texto | Condicional | Obrigatório quando `idModalidade` = 1 (Outros). Máximo 50 caracteres. Se não informado, mantém o valor atual |
| `observacao` | Texto | Não | Observação (máximo 100 caracteres). Se não informado, mantém o valor atual |
| `siglaFusoHorario` | Texto | Não | Sigla do fuso horário (ex: BRT, AMT, ACT, FNT). Se não informado, mantém o valor atual |

#### Exemplos de Edição Parcial

**Alterar apenas o nome:**
```json
{
  "nome": "Novo Nome da US"
}
```

**Alterar nome e área de atuação:**
```json
{
  "nome": "Novo Nome",
  "areaAtuacao": "Nova Área"
}
```

**Adicionar novas regiões de atuação sem alterar outros campos:**
```json
{
  "regioesAtuacaoNovas": ["uuid-nova-regiao-1", "uuid-nova-regiao-2"]
}
```

**Remover regiões de atuação existentes:**
```json
{
  "regioesAtuacaoRemover": ["uuid-regiao-1", "uuid-regiao-2"]
}
```

**Adicionar e remover regiões simultaneamente:**
```json
{
  "regioesAtuacaoNovas": ["uuid-nova-regiao-1"],
  "regioesAtuacaoRemover": ["uuid-regiao-antiga-1"]
}
```

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados (Unidade de Serviço, regiões de atuação) estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Tamanho Máximo de Campos**

Os campos de texto possuem limites de tamanho quando informados.

```json
{
  "mensagem": "O campo 'Nome' deve ter no máximo 80 caracteres"
}
```

**2. Modalidade "Outros"**

Quando `idModalidade` = 1 (Outros), o campo `descricaoModalidade` é obrigatório.

```json
{
  "mensagem": "O campo 'Descrição da Modalidade' é obrigatório"
}
```

**3. Fuso Horário Inválido**

O fuso horário informado deve ser válido.

```json
{
  "mensagem": "O campo 'Fuso Horário' é inválido"
}
```

**4. Modalidade Inválida**

A modalidade informada deve existir.

```json
{
  "mensagem": "O campo 'Modalidade' é inválido"
}
```

**5. Regiões de Atuação Novas Repetidas**

Não é permitido informar a mesma região de atuação nova mais de uma vez.

```json
{
  "mensagem": "Existem regiões de atuação repetidas"
}
```

**6. Região de Atuação Nova Inválida**

A região de atuação nova informada deve existir e estar ativa.

```json
{
  "mensagem": "O campo 'Região de Atuação' é inválido - UUID: <uuid>"
}
```

**7. Região de Atuação Já Vinculada**

A região de atuação nova não pode já estar vinculada à Unidade de Serviço.

```json
{
  "mensagem": "Região de atuação já vinculada à Unidade de Serviço: <uuid>"
}
```

**8. Região de Atuação Não Vinculada**

As regiões de atuação a remover devem estar vinculadas à Unidade de Serviço.

```json
{
  "mensagem": "A região de atuação <uuid> não está vinculada à Unidade de Serviço"
}
```

**9. Unidade de Serviço Não Ativa para Remoção**

A Unidade de Serviço deve estar na situação **Ativa** para remover regiões de atuação.

```json
{
  "mensagem": "A Unidade de Serviço deve estar na situação Ativa para remover regiões de atuação"
}
```

**10. Região em Ambas as Listas**

Uma região não pode estar simultaneamente nas listas de novas e de remoção.

```json
{
  "mensagem": "A região de atuação <uuid> não pode estar nas listas de novas e de remoção simultaneamente"
}
```

**11. Regiões a Remover Repetidas**

Não é permitido informar a mesma região de atuação a remover mais de uma vez.

```json
{
  "mensagem": "Existem regiões de atuação repetidas"
}
```

**12. Campos Desconhecidos**

A API rejeita requisições que contenham campos não mapeados no body JSON.

```json
{
  "mensagem": "Campo desconhecido no corpo da requisição: '<nome_campo>'"
}
```

---

### Iniciar Serviço da Unidade de Serviço

Inicia o serviço de uma Unidade de Serviço para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuid}/iniciar-servico`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Unidade de Serviço |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Situação da Unidade de Serviço Não Permite Iniciar Serviço**

A Unidade de Serviço deve estar na situação Ativa para iniciar o serviço.

```json
{
  "mensagem": "A Unidade de Serviço {0} não está na situação Ativa."
}
```

---

### Encerrar Serviço da Unidade de Serviço

Encerra o serviço de uma Unidade de Serviço para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuid}/encerrar-servico`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Unidade de Serviço |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Unidade de Serviço Não Está em Serviço**

A Unidade de Serviço deve estar na situação Em Serviço para ser encerrada.

```json
{
  "mensagem": "A Unidade de Serviço {0} não está na situação Em Serviço."
}
```

---

### Ativar Unidade de Serviço

Ativa uma Unidade de Serviço que estava inativa para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuid}/ativar`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Unidade de Serviço |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Situação da Unidade de Serviço Não Permite Ativação**

A Unidade de Serviço deve estar na situação Inativa para ser ativada.

```json
{
  "mensagem": "A Unidade de Serviço {0} não está na situação Inativa."
}
```

---

### Inativar Unidade de Serviço

Inativa uma Unidade de Serviço para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuid}/inativar`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Unidade de Serviço |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Situação da Unidade de Serviço Não Permite Inativação**

A Unidade de Serviço deve estar na situação Ativa para ser inativada.

```json
{
  "mensagem": "A Unidade de Serviço {0} não está na situação Ativa."
}
```

---

### Excluir Unidade de Serviço

Exclui uma Unidade de Serviço para sistemas externos.

**Endpoint:** `DELETE /agente-campo/v3/cad-unidade-servico-api/{uuid}/excluir`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Unidade de Serviço |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Situação da Unidade de Serviço Não Permite Exclusão**

A Unidade de Serviço deve estar na situação Ativa ou Inativa para ser excluída.

```json
{
  "mensagem": "A Unidade de Serviço {0} não está na situação Ativa ou Inativa."
}
```

---

### Vincular Pessoa à Equipe

Vincula uma pessoa a uma equipe da unidade de serviço.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuidUS}/{uuidEquipe}/vincular-pessoa/{uuidPessoa}/{uuidFuncao}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidUS` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipe` | UUID | Sim | UUID da Equipe |
| `uuidPessoa` | UUID | Sim | UUID da Pessoa a ser vinculada |
| `uuidFuncao` | UUID | Sim | UUID da Função da pessoa na equipe |

**Response (200 OK):**

Sem corpo de resposta. Status 200 indica sucesso na vinculação.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

**1. Sistema Integrado Não Encontrado**

```json
{
  "mensagem": "Sistema integrado não encontrado: <header>"
}
```

**2. Unidade de Serviço Não Encontrada**

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipe Não Pertence à US**

```json
{
  "mensagem": "A equipe <uuid equipe> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Erros de Validação Automática**

Mensagens de erro retornadas pelo serviço interno:
- "Pessoa não encontrada ou inativa"
- "Função não encontrada ou inativa"
- "Pessoa e função pertencem a agências diferentes"
- "Pessoa já está vinculada a outra equipe em serviço"
- "Pessoa já está vinculada a esta equipe"

---

### Desvincular Pessoa da Equipe

Remove o vínculo de uma pessoa com a equipe da unidade de serviço.

**Endpoint:** `DELETE /agente-campo/v3/cad-unidade-servico-api/{uuidUS}/{uuidEquipe}/desvincular-pessoa/{uuidPessoa}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidUS` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipe` | UUID | Sim | UUID da Equipe |
| `uuidPessoa` | UUID | Sim | UUID da Pessoa a ser desvinculada |

**Response (200 OK):**

Sem corpo de resposta. Status 200 indica sucesso na desvinculação.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

**1. Sistema Integrado Não Encontrado**

```json
{
  "mensagem": "Sistema integrado não encontrado: <header>"
}
```

**2. Unidade de Serviço Não Encontrada**

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipe Não Pertence à US**

```json
{
  "mensagem": "A equipe <uuid equipe> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Pessoa Não Está na Equipe**

```json
{
  "mensagem": "A pessoa <uuid pessoa> não está vinculada à equipe <uuid equipe>"
}
```

**3. Erros de Validação**

Mensagens de erro retornadas pelo serviço interno:
- "Pessoa não está vinculada à equipe"
- "Não é possível desvincular a pessoa. A equipe deve ter no mínimo 1 pessoa"

---

### Vincular Equipamento à Unidade de Serviço

Vincula um equipamento a uma unidade de serviço.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuidUS}/vincular-equipamento/{uuidEquipamento}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidUS` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipamento` | UUID | Sim | UUID do Equipamento a ser vinculado |

**Response (200 OK):**

Sem corpo de resposta. Status 200 indica sucesso na vinculação.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

**1. Sistema Integrado Não Encontrado**

```json
{
  "mensagem": "Sistema integrado não encontrado: <header>"
}
```

**2. Unidade de Serviço Não Encontrada**

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipamento Não Pertence à US**

```json
{
  "mensagem": "O equipamento <uuid equipamento> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Erros de Validação**

Mensagens de erro retornadas pelo serviço interno:
- "Equipamento não encontrado ou inativo"
- "Equipamento já está vinculado à unidade de serviço"

---

### Desvincular Equipamento da Unidade de Serviço

Remove o vínculo de um equipamento com a unidade de serviço.

**Endpoint:** `DELETE /agente-campo/v3/cad-unidade-servico-api/{uuidUS}/desvincular-equipamento/{uuidEquipamento}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidUS` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipamento` | UUID | Sim | UUID do Equipamento a ser desvinculado |

**Response (200 OK):**

Sem corpo de resposta. Status 200 indica sucesso na desvinculação.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

**1. Sistema Integrado Não Encontrado**

```json
{
  "mensagem": "Sistema integrado não encontrado: <header>"
}
```

**2. Unidade de Serviço Não Encontrada**

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipamento Não Pertence à US**

```json
{
  "mensagem": "O equipamento <uuid equipamento> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Erros de Validação**

Mensagens de erro retornadas pelo serviço interno:
- "Equipamento não está vinculado à unidade de serviço"

---

### Alterar Equipe em Serviço

Altera a equipe em serviço de uma Unidade de Serviço para sistemas externos.

**Endpoint:** `PUT /agente-campo/v3/cad-unidade-servico-api/{uuidUnidadeServico}/alterar-equipe-em-servico/{uuidEquipe}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidUnidadeServico` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipe` | UUID | Sim | UUID da Equipe a ser selecionada como equipe em serviço |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipe Não Pertence à US**

A equipe informada deve pertencer à Unidade de Serviço.

```json
{
  "mensagem": "A equipe <uuid equipe> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Erros de Validação Automática**

Mensagens de erro retornadas pelo serviço interno:
- "A Unidade de Serviço não está em serviço"
- "A equipe não está em serviço"
- "A equipe já é a equipe em serviço da Unidade de Serviço"

---

### Criar Equipe

Cria uma nova equipe dentro de uma Unidade de Serviço para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-unidade-servico-api/{uuidUnidadeServico}/criar-equipe`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidUnidadeServico` | UUID | Sim | UUID da Unidade de Serviço |

#### Request Body

```json
{
  "nome": "Equipe Alpha",
  "telefone": 61999998888,
  "pessoas": [
    {
      "cpf": "12345678901",
      "uuidFuncao": "uuid-funcao-1"
    },
    {
      "cpf": "98765432100",
      "uuidFuncao": "uuid-funcao-2"
    }
  ]
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `nome` | String | Sim | Nome da equipe |
| `telefone` | Long | Não | Telefone da equipe (somente números, com DDD) |
| `pessoas` | Array | Sim | Lista de pessoas a serem vinculadas à equipe com suas respectivas funções |
| `pessoas[].cpf` | String | Sim | CPF da pessoa |
| `pessoas[].uuidFuncao` | UUID | Sim | UUID da função da pessoa na equipe |

**Response (200 OK):**

Retorna o UUID da equipe criada.

```json
"uuid-equipe-criada"
```

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

Retornado quando uma pessoa informada não é encontrada.

```json
{
  "mensagem": "Pessoa com CPF <cpf> não encontrada"
}
```

##### Response (400 Bad Request)

**1. Nome Obrigatório**

```json
{
  "mensagem": "O nome da equipe não pode ser nulo ou vazio"
}
```

**2. Pessoas Obrigatórias**

```json
{
  "mensagem": "A lista de pessoas não pode ser nula ou vazia"
}
```

**3. CPF da Pessoa Obrigatório**

```json
{
  "mensagem": "O CPF da pessoa não pode ser nulo ou vazio"
}
```

**4. Função da Pessoa Obrigatória**

```json
{
  "mensagem": "O UUID da função não pode ser nulo"
}
```

**5. Pessoa Não Pertence ao Compartilhamento**

A pessoa informada deve pertencer a uma agência disponível no compartilhamento de dados.

```json
{
  "mensagem": "A pessoa com CPF <cpf> pertence a uma agência não disponível no compartilhamento de dados com o sistema Integrado <nome sistema>"
}
```

---

### Editar Equipe

Edita uma equipe existente de uma Unidade de Serviço para sistemas externos.

**Endpoint:** `PUT /agente-campo/v3/cad-unidade-servico-api/{uuidUnidadeServico}/editar-equipe/{uuidEquipe}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidUnidadeServico` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipe` | UUID | Sim | UUID da Equipe a ser editada |

#### Request Body

```json
{
  "nome": "Equipe Alpha Atualizada",
  "telefone": 61988887777
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `nome` | String | Sim | Nome da equipe |
| `telefone` | Long | Não | Telefone da equipe (somente números, com DDD) |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipe Não Pertence à US**

```json
{
  "mensagem": "A equipe <uuid equipe> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Nome Obrigatório**

```json
{
  "mensagem": "O nome da equipe não pode ser nulo ou vazio"
}
```

---

### Excluir Equipe

Exclui uma equipe de uma Unidade de Serviço para sistemas externos.

**Endpoint:** `DELETE /agente-campo/v3/cad-unidade-servico-api/{uuidUnidadeServico}/excluir-equipe/{uuidEquipe}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidUnidadeServico` | UUID | Sim | UUID da Unidade de Serviço |
| `uuidEquipe` | UUID | Sim | UUID da Equipe a ser excluída |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Unidade de Serviço não é encontrada.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

##### Response (400 Bad Request)

**1. Equipe Não Pertence à US**

```json
{
  "mensagem": "A equipe <uuid equipe> não pertence à Unidade de Serviço <uuid US>"
}
```

**2. Erros de Validação Automática**

Mensagens de erro retornadas pelo serviço interno (ex: equipe em serviço não pode ser excluída).

---

## API de Equipamento

API destinada ao consumo e gerenciamento de dados de equipamentos por sistemas externos integrados.

### Base URL

```
/agente-campo/v3/cad-equipamento-api
```

---

### Criar Equipamento

Cria um novo equipamento no sistema.

**Endpoint:** `POST /agente-campo/v3/cad-equipamento-api/criar-equipamento`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

**Request Body:**

```json
{
  "uuidAgencia": "uuid-agencia",
  "uuidRegiaoAtuacao": "uuid-regiao-atuacao",
  "uuidTipoEquipamento": "uuid-tipo-equipamento",
  "prefixo": "VTR-001",
  "placa": "ABC1234",
  "marca": "Toyota",
  "modelo": "Hilux"
}
```

| Campo | Tipo | Obrigatório | Min | Max | Descrição |
|-------|------|-------------|-----|-----|-----------|
| `uuidAgencia` | UUID | Sim | - | - | UUID da agência do equipamento |
| `uuidRegiaoAtuacao` | UUID | Não | - | - | UUID da região de atuação |
| `uuidTipoEquipamento` | UUID | Sim | - | - | UUID do tipo de equipamento |
| `prefixo` | String | Sim | 1 | 50 | Prefixo do equipamento |
| `placa` | String | Não | 0 | 7 | Placa do equipamento |
| `marca` | String | Não | 0 | 20 | Marca do equipamento |
| `modelo` | String | Não | 0 | 20 | Modelo do equipamento |

**Response (200 OK):** `UUID` do equipamento criado

```json
"uuid-do-equipamento-criado"
```

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Campos Desconhecidos**

A API rejeita requisições que contenham campos não mapeados no body JSON.

```json
{
  "mensagem": "Campo desconhecido no corpo da requisição: '<nome_campo>'"
}
```

---

### Alterar Equipamento

Altera um equipamento existente. A agência não pode ser alterada. Campos não informados mantêm os valores atuais (edição parcial).

**Endpoint:** `PUT /agente-campo/v3/cad-equipamento-api/alterar-equipamento/{uuid}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID do Equipamento a ser alterado |

**Request Body:**

```json
{
  "uuidRegiaoAtuacao": "uuid-regiao-atuacao",
  "uuidTipoEquipamento": "uuid-tipo-equipamento",
  "prefixo": "VTR-002",
  "placa": "DEF5678",
  "marca": "Ford",
  "modelo": "Ranger"
}
```

| Campo | Tipo | Obrigatório | Min | Max | Descrição |
|-------|------|-------------|-----|-----|-----------|
| `uuidRegiaoAtuacao` | UUID | Não | - | - | UUID da região de atuação |
| `uuidTipoEquipamento` | UUID | Não | - | - | UUID do tipo de equipamento |
| `prefixo` | String | Não | 1 | 50 | Prefixo do equipamento |
| `placa` | String | Não | 0 | 7 | Placa do equipamento |
| `marca` | String | Não | 0 | 20 | Marca do equipamento |
| `modelo` | String | Não | 0 | 20 | Modelo do equipamento |

**Response (200 OK):** sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando o Equipamento não é encontrado.

```json
{
  "mensagem": "Equipamento não encontrado"
}
```

---

### Listar Equipamentos

Pesquisa equipamentos com filtros múltiplos.

**Endpoint:** `POST /agente-campo/v3/cad-equipamento-api/listar-equipamentos`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Lógica de Filtros

> **IMPORTANTE:** A API utiliza a seguinte lógica para combinar filtros:
>
> - **Relação entre campos diferentes:** `AND` (E) - Todos os filtros informados devem ser satisfeitos simultaneamente.
> - **Relação entre valores do mesmo campo:** `OR` (OU) - Basta satisfazer qualquer um dos valores informados.

**Exemplo prático:**

```json
{
  "uuidsAgencias": ["uuid-agencia-1"],
  "prefixos": ["VTR-001", "VTR-002"]
}
```

Esta consulta retornará equipamentos que:
- Pertençam à agência `uuid-agencia-1` **E**
- Tenham prefixo `VTR-001` **OU** `VTR-002`

**Request Body:**

```json
{
  "uuidsAgencias": ["uuid-agencia-1", "uuid-agencia-2"],
  "uuidsEquipamentos": ["uuid-equip-1"],
  "uuidsTiposEquipamento": ["uuid-tipo-1"],
  "prefixos": ["VTR-001"],
  "placas": ["ABC1234"],
  "marcas": ["Toyota"],
  "modelos": ["Hilux"],
  "numeroPagina": 0,
  "tamanhoPagina": 20
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidsAgencias` | Array de UUID | Não* | UUIDs das agências. Se não informadas, usa agências do compartilhamento |
| `uuidsEquipamentos` | Array de UUID | Não | UUIDs dos equipamentos |
| `uuidsTiposEquipamento` | Array de UUID | Não | UUIDs dos tipos de equipamento |
| `prefixos` | Array de texto | Não | Prefixos (busca fonética) |
| `placas` | Array de texto | Não | Placas (busca fonética) |
| `marcas` | Array de texto | Não | Marcas (busca fonética) |
| `modelos` | Array de texto | Não | Modelos (busca fonética) |
| `numeroPagina` | Número inteiro | Não | Número da página, iniciando em 0 (padrão: 0, mínimo: 0) |
| `tamanhoPagina` | Número inteiro | Não | Tamanho da página (padrão: 20, mínimo: 1, máximo: 25) |

\* Pelo menos um campo de busca deve ser informado.

**Response (200 OK):**

```json
{
  "metadados": {
    "paginaAtual": 0,
    "registrosPorPagina": 20,
    "totalRegistros": 50,
    "totalPaginas": 3
  },
  "dados": [
    {
      "uuid": "uuid-equipamento",
      "uuidAgencia": "uuid-agencia",
      "nomeAgencia": "Nome Agência",
      "siglaAgencia": "AG",
      "uuidRegiaoAtuacao": "uuid-regiao",
      "nomeRegiaoAtuacao": "Nome Região",
      "siglaRegiaoAtuacao": "RG",
      "uuidTipoEquipamento": "uuid-tipo",
      "nomeTipoEquipamento": "Viatura",
      "prefixo": "VTR-001",
      "placa": "ABC1234",
      "marca": "Toyota",
      "modelo": "Hilux"
    }
  ]
}
```

**Campos do Response - Metadados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `paginaAtual` | Número inteiro | Página atual da consulta |
| `registrosPorPagina` | Número inteiro | Quantidade de registros por página |
| `totalRegistros` | Número inteiro | Total de registros encontrados |
| `totalPaginas` | Número inteiro | Total de páginas disponíveis |

**Campos do Response - Dados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID do equipamento |
| `uuidAgencia` | UUID | UUID da agência |
| `nomeAgencia` | Texto | Nome da agência |
| `siglaAgencia` | Texto | Sigla da agência |
| `uuidRegiaoAtuacao` | UUID | UUID da região de atuação |
| `nomeRegiaoAtuacao` | Texto | Nome da região de atuação |
| `siglaRegiaoAtuacao` | Texto | Sigla da região de atuação |
| `uuidTipoEquipamento` | UUID | UUID do tipo de equipamento |
| `nomeTipoEquipamento` | Texto | Nome do tipo de equipamento |
| `prefixo` | Texto | Prefixo do equipamento |
| `placa` | Texto | Placa do equipamento |
| `marca` | Texto | Marca do equipamento |
| `modelo` | Texto | Modelo do equipamento |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Tamanho da Página**

O parâmetro `tamanhoPagina` deve ser no máximo **25**.

```json
{
  "mensagem": "O tamanho da página deve ser no máximo 25"
}
```

**2. Filtro Obrigatório**

Pelo menos um campo de busca deve ser informado.

```json
{
  "mensagem": "Pelo menos um campo de busca deve ser informado"
}
```

#### Comportamentos Padrão

| Condição | Comportamento |
|----------|---------------|
| Nenhuma agência informada | Utiliza automaticamente as agências do compartilhamento de dados |
| `numeroPagina` não informado | Retorna a primeira página (página 0) |
| `tamanhoPagina` não informado | Usa o valor padrão de 20 registros por página |

---

### Excluir Equipamento

Exclui um equipamento existente.

**Endpoint:** `DELETE /agente-campo/v3/cad-equipamento-api/excluir-equipamento/{uuid}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID do Equipamento a ser excluído |

**Response (200 OK):** sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

---

### Listar Tipos de Equipamento

Lista todos os tipos de equipamento ativos disponíveis no sistema.

**Endpoint:** `GET /agente-campo/v3/cad-equipamento-api/listar-tipos-equipamento`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

> **Nota:** Este endpoint não requer filtros ou parâmetros de busca (apenas os headers obrigatórios). Retorna todos os tipos de equipamento na situação **Ativa**.

**Response (200 OK):**

```json
[
  {
    "uuid": "uuid-tipo-1",
    "nome": "Viatura"
  },
  {
    "uuid": "uuid-tipo-2",
    "nome": "Motocicleta"
  },
  {
    "uuid": "uuid-tipo-3",
    "nome": "Aeronave"
  }
]
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID do tipo de equipamento |
| `nome` | String | Nome do tipo de equipamento |

---

## API de Pessoa

API destinada ao consumo e manipulação de dados de pessoas por sistemas externos integrados.

### Base URL

```
/agente-campo/v3/cad-pessoa-api
```

---

### Criar Pessoa

Cria uma nova Pessoa para sistemas externos.

**Endpoint:** `POST /agente-campo/v3/cad-pessoa-api/criar-pessoa`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

**Request Body:**

```json
{
  "uuidAgencia": "uuid-agencia",
  "uuidRegiaoAtuacao": "uuid-regiao-atuacao",
  "nome": "Nome Completo da Pessoa",
  "nomeFuncional": "Nome Funcional",
  "cpf": "12345678901",
  "registroFuncional": "RF001",
  "uuidCargo": "uuid-cargo",
  "telefoneFixo": "1133334444",
  "telefoneCelular": "11999998888"
}
```

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidAgencia` | UUID | Sim | UUID da agência à qual a pessoa será vinculada |
| `uuidRegiaoAtuacao` | UUID | Não | UUID da região de atuação da pessoa |
| `nome` | Texto | Sim | Nome completo da pessoa (1 a 80 caracteres) |
| `nomeFuncional` | Texto | Não | Nome funcional da pessoa (máximo 80 caracteres) |
| `cpf` | Texto | Sim | CPF da pessoa (somente números, 11 dígitos, válido) |
| `registroFuncional` | Texto | Sim | Registro funcional da pessoa (1 a 50 caracteres) |
| `uuidCargo` | UUID | Não | UUID do cargo da pessoa |
| `telefoneFixo` | Texto | Não | Telefone fixo da pessoa (somente números, máximo 11 caracteres) |
| `telefoneCelular` | Texto | Não | Telefone celular da pessoa (somente números, máximo 11 caracteres) |

**Response (200 OK):**

Retorna o UUID da Pessoa criada.

```json
"uuid-da-pessoa-criada"
```

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Cargo Não Encontrado**

O cargo informado deve existir.

```json
{
  "mensagem": "Cargo não encontrado: <uuid>"
}
```

**2. Cargo de Agência Diferente**

O cargo deve pertencer à mesma agência da pessoa.

```json
{
  "mensagem": "O Cargo selecionado não pertence à mesma Agência da Pessoa. Selecione um Cargo da mesma Agência."
}
```

**3. CPF Já Cadastrado**

O CPF não pode estar cadastrado para outra pessoa ativa ou inativa.

```json
{
  "mensagem": "O CPF informado já está sendo utilizado em outra Pessoa <situação> na Agência <sigla> - <nome>"
}
```

**4. Registro Funcional Já Cadastrado**

O registro funcional não pode estar cadastrado para outra pessoa ativa ou inativa na mesma agência.

```json
{
  "mensagem": "O Registro Funcional informado já está sendo utilizado em outra Pessoa nesta Agência, com a situação <situação>"
}
```

---

### Alterar Pessoa

Altera uma Pessoa existente para sistemas externos. **Suporta edição parcial:** apenas os campos informados serão alterados, os demais mantêm seus valores atuais. **A agência da pessoa não pode ser alterada.**

**Endpoint:** `PUT /agente-campo/v3/cad-pessoa-api/alterar-pessoa/{uuid}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Pessoa a ser alterada |

**Request Body:**

```json
{
  "uuidRegiaoAtuacao": "uuid-nova-regiao-atuacao",
  "nome": "Novo Nome Completo",
  "nomeFuncional": "Novo Nome Funcional",
  "cpf": "98765432109",
  "registroFuncional": "RF002",
  "uuidCargo": "uuid-novo-cargo",
  "telefoneFixo": "1144445555",
  "telefoneCelular": "11888887777"
}
```

> **Edição Parcial:** Todos os campos são opcionais. Informe apenas os campos que deseja alterar. Campos não informados (ou com valor `null`) manterão seus valores atuais.

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidRegiaoAtuacao` | UUID | Não | UUID da nova região de atuação. Se não informado, mantém o valor atual |
| `nome` | Texto | Não | Nome completo da pessoa (1 a 80 caracteres). Se não informado, mantém o valor atual |
| `nomeFuncional` | Texto | Não | Nome funcional da pessoa (máximo 80 caracteres). Se não informado, mantém o valor atual |
| `cpf` | Texto | Não | CPF da pessoa (somente números, 11 dígitos, válido). Se não informado, mantém o valor atual |
| `registroFuncional` | Texto | Não | Registro funcional da pessoa (1 a 50 caracteres). Se não informado, mantém o valor atual |
| `uuidCargo` | UUID | Não | UUID do cargo da pessoa. Se não informado, mantém o valor atual |
| `telefoneFixo` | Texto | Não | Telefone fixo da pessoa (somente números, máximo 11 caracteres). Se não informado, mantém o valor atual |
| `telefoneCelular` | Texto | Não | Telefone celular da pessoa (somente números, máximo 11 caracteres). Se não informado, mantém o valor atual |

> **Importante:** A agência da pessoa **não pode ser alterada**. A pessoa permanecerá vinculada à mesma agência.

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Pessoa não é encontrada.

```json
{
  "mensagem": "Pessoa não encontrada"
}
```

##### Response (400 Bad Request)

**1. Cargo Não Encontrado**

Se informado, o cargo deve existir.

```json
{
  "mensagem": "Cargo não encontrado: <uuid>"
}
```

**2. Cargo de Agência Diferente**

Se informado, o cargo deve pertencer à mesma agência da pessoa.

```json
{
  "mensagem": "O Cargo selecionado não pertence à mesma Agência da Pessoa. Selecione um Cargo da mesma Agência."
}
```

---

### Listar Pessoas

Pesquisa pessoas para sistemas externos com filtros múltiplos.

**Endpoint:** `POST /agente-campo/v3/cad-pessoa-api/listar-pessoas`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Lógica de Filtros

> **IMPORTANTE:** A API utiliza a seguinte lógica para combinar filtros:
>
> - **Relação entre campos diferentes:** `AND` (E) - Todos os filtros informados devem ser satisfeitos simultaneamente.
> - **Relação entre valores do mesmo campo:** `OR` (OU) - Basta satisfazer qualquer um dos valores informados.

**Exemplo prático:**

```json
{
  "uuidsAgencias": ["uuid-agencia-1"],
  "nomes": ["João", "Maria"]
}
```

Esta consulta retornará pessoas que:
- Pertençam à agência `uuid-agencia-1` **E**
- Tenham nome "João" **OU** "Maria"

**Request Body:**

```json
{
  "uuidsAgencias": ["uuid-agencia-1", "uuid-agencia-2"],
  "uuidsPessoas": ["uuid-pessoa-1", "uuid-pessoa-2"],
  "cpfs": ["12345678901", "98765432109"],
  "nomes": ["João Silva", "Maria Santos"],
  "nomesFuncionais": ["João", "Maria"],
  "registrosFuncionais": ["RF001", "RF002"],
  "numeroPagina": 0,
  "tamanhoPagina": 20
}
```

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidsAgencias` | Array de UUID | Não | UUIDs das agências para filtrar. Se não informado, usa as agências do compartilhamento |
| `uuidsPessoas` | Array de UUID | Não | UUIDs das pessoas para filtrar |
| `cpfs` | Array de texto | Não | CPFs das pessoas para filtrar (somente números) |
| `nomes` | Array de texto | Não | Nomes das pessoas para filtrar (busca parcial) |
| `nomesFuncionais` | Array de texto | Não | Nomes funcionais das pessoas para filtrar (busca parcial) |
| `registrosFuncionais` | Array de texto | Não | Registros funcionais das pessoas para filtrar |
| `numeroPagina` | Número inteiro | Não | Número da página, iniciando em 0 (padrão: 0, mínimo: 0) |
| `tamanhoPagina` | Número inteiro | Não | Registros por página (padrão: 20, mínimo: 1, máximo: 25) |

> **Importante:** Pelo menos um campo de busca deve ser informado (além da paginação).

**Response (200 OK):**

```json
{
  "metadados": {
    "paginaAtual": 0,
    "registrosPorPagina": 20,
    "totalRegistros": 50,
    "totalPaginas": 3
  },
  "dados": [
    {
      "uuid": "uuid-pessoa",
      "uuidAgencia": "uuid-agencia",
      "nomeAgencia": "Nome da Agência",
      "siglaAgencia": "AG1",
      "uuidRegiaoAtuacao": "uuid-regiao",
      "nomeRegiaoAtuacao": "Nome da Região",
      "siglaRegiaoAtuacao": "REG1",
      "nome": "João da Silva",
      "nomeFuncional": "João Silva",
      "cpf": "12345678901",
      "registroFuncional": "RF001",
      "uuidCargo": "uuid-cargo",
      "nomeCargo": "Policial",
      "telefoneFixo": "1133334444",
      "telefoneCelular": "11999998888",
      "situacao": "Ativa"
    }
  ]
}
```

**Campos do Response - Metadados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `paginaAtual` | Número inteiro | Página atual da consulta |
| `registrosPorPagina` | Número inteiro | Quantidade de registros por página |
| `totalRegistros` | Número inteiro | Total de registros encontrados |
| `totalPaginas` | Número inteiro | Total de páginas disponíveis |

**Campos do Response - Dados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID da pessoa |
| `uuidAgencia` | UUID | UUID da agência da pessoa |
| `nomeAgencia` | Texto | Nome da agência |
| `siglaAgencia` | Texto | Sigla da agência |
| `uuidRegiaoAtuacao` | UUID | UUID da região de atuação (pode ser nulo) |
| `nomeRegiaoAtuacao` | Texto | Nome da região de atuação (pode ser nulo) |
| `siglaRegiaoAtuacao` | Texto | Sigla da região de atuação (pode ser nulo) |
| `nome` | Texto | Nome completo da pessoa |
| `nomeFuncional` | Texto | Nome funcional da pessoa |
| `cpf` | Texto | CPF da pessoa |
| `registroFuncional` | Texto | Registro funcional da pessoa |
| `uuidCargo` | UUID | UUID do cargo (pode ser nulo) |
| `nomeCargo` | Texto | Nome do cargo (pode ser nulo) |
| `telefoneFixo` | Texto | Telefone fixo da pessoa |
| `telefoneCelular` | Texto | Telefone celular da pessoa |
| `situacao` | Texto | Situação da pessoa (Ativa, Inativa) |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Tamanho da Página**

O parâmetro `tamanhoPagina` deve ser no máximo **25**.

```json
{
  "mensagem": "O tamanho da página deve ser no máximo 25"
}
```

**2. Filtro Obrigatório**

Pelo menos um campo de busca deve ser informado.

```json
{
  "mensagem": "Pelo menos um campo de busca deve ser informado"
}
```

#### Comportamentos Padrão

| Condição | Comportamento |
|----------|---------------|
| Nenhuma agência informada | Utiliza automaticamente as agências do compartilhamento de dados |
| `numeroPagina` não informado | Retorna a primeira página (página 0) |
| `tamanhoPagina` não informado | Usa o valor padrão de 20 registros por página |

---

### Excluir Pessoa

Exclui uma Pessoa existente para sistemas externos.

**Endpoint:** `DELETE /agente-campo/v3/cad-pessoa-api/excluir-pessoa/{uuid}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuid` | UUID | Sim | UUID da Pessoa a ser excluída |

**Response (200 OK):**

Retorna sucesso sem corpo de resposta.

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando a Pessoa não é encontrada.

```json
{
  "mensagem": "Pessoa não encontrada"
}
```

##### Response (400 Bad Request)

**1. Pessoa Possui Vínculos com Unidades de Serviço**

A pessoa não pode ser excluída se estiver vinculada a unidades de serviço ativas ou em serviço.

```json
{
  "mensagem": "A pessoa está vinculada a <quantidade> unidade(s) de serviço Ativa ou Em Serviço e não pode ser excluída."
}
```

---

### Listar Cargos Ativos por Agência

Lista todos os cargos ativos de uma agência para sistemas externos.

**Endpoint:** `GET /agente-campo/v3/cad-pessoa-api/listar-cargos/{uuidAgencia}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidAgencia` | UUID | Sim | UUID da agência cujos cargos serão listados |

**Response (200 OK):**

```json
[
  {
    "uuid": "uuid-cargo-1",
    "nome": "Policial Civil",
    "sigla": "PC"
  },
  {
    "uuid": "uuid-cargo-2",
    "nome": "Delegado",
    "sigla": "DEL"
  }
]
```

**Campos do Response:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID do cargo |
| `nome` | Texto | Nome do cargo |
| `sigla` | Texto | Sigla do cargo |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

---

### Obter Cargo por UUID

Retorna os dados de um cargo específico pelo UUID para sistemas externos.

**Endpoint:** `GET /agente-campo/v3/cad-pessoa-api/cargo/{uuidCargo}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidCargo` | UUID | Sim | UUID do cargo a ser consultado |

**Response (200 OK):**

Retorna os dados do cargo solicitado.

```json
{
  "uuid": "uuid-cargo",
  "uuidAgencia": "uuid-agencia",
  "nome": "Policial Civil",
  "sigla": "PC"
}
```

**Campos do Response:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID do cargo |
| `uuidAgencia` | UUID | UUID da agência à qual o cargo pertence |
| `nome` | Texto | Nome do cargo |
| `sigla` | Texto | Sigla do cargo |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (404 Not Found)

Retornado quando o Cargo não é encontrado.

```json
{
  "mensagem": "Cargo não encontrado"
}
```

##### Response (400 Bad Request)

**1. Cargo Não Está Ativo**

O cargo solicitado deve estar ativo.

```json
{
  "mensagem": "O cargo solicitado não está ativo"
}
```

---

## API de Posições

API destinada à consulta de posições geográficas de pessoas em equipes por sistemas externos integrados.

### Base URL

```
/agente-campo/v3/cad-posicoes-api
```

### Endpoints

### Consultar Histórico de Posições Geográficas de uma Pessoa

Retorna o histórico de posições geográficas de uma pessoa vinculada a uma equipe dentro de um intervalo de tempo.

**Endpoint:** `POST /agente-campo/v3/cad-posicoes-api/consultar-posicoes-historico/{uuidEquipe}/{uuidPessoa}`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidEquipe` | UUID | Sim | UUID da equipe |
| `uuidPessoa` | UUID | Sim | UUID da pessoa |

**Request Body:**

```json
{
  "data": "02/02/2026",
  "horaInicio": "08:00",
  "horaFim": "10:00"
}
```

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `data` | Data (dd/MM/yyyy) | Sim | Data da consulta no formato brasileiro (ex: 02/02/2026) |
| `horaInicio` | Hora (HH:mm) | Sim | Hora de início do intervalo (formato 24h, ex: 08:00, 14:30) |
| `horaFim` | Hora (HH:mm) | Sim | Hora de fim do intervalo (formato 24h, ex: 10:00, 16:30) |

> **Importante:**
> - O intervalo máximo permitido entre `horaInicio` e `horaFim` é de **2 horas**.
> - Os horários devem estar no formato 24 horas (00:00 a 23:59).
> - A consulta é limitada a um único dia.
> - Todos os horários são considerados no **horário de Brasília (BRT)**.

**Response (200 OK):**

Retorna uma lista de posições geográficas ordenadas por data/hora decrescente (mais recentes primeiro).

```json
[
  {
    "dataHoraBrt": "02/02/2026 09:45:00",
    "latitude": -15.7801,
    "longitude": -47.9292,
    "uuidEquipamento": "uuid-equipamento-1"
  },
  {
    "dataHoraBrt": "02/02/2026 09:30:00",
    "latitude": -15.7805,
    "longitude": -47.9288,
    "uuidEquipamento": "uuid-equipamento-1"
  },
  {
    "dataHoraBrt": "02/02/2026 09:15:00",
    "latitude": -15.7810,
    "longitude": -47.9285,
    "uuidEquipamento": null
  }
]
```

**Campos do Response:**

| Campo | Tipo | Sempre presente | Descrição |
|-------|------|-----------------|-----------|
| `dataHoraBrt` | String (dd/MM/yyyy HH:mm:ss) | Sim | Data e hora da posição geográfica no formato brasileiro (horário de Brasília) |
| `latitude` | Número | Sim | Latitude da posição geográfica |
| `longitude` | Número | Sim | Longitude da posição geográfica |
| `uuidEquipamento` | UUID | Não | UUID do equipamento associado à posição (pode ser `null`) |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Campos Obrigatórios**

Os campos `data`, `horaInicio` e `horaFim` são obrigatórios.

```json
{
  "mensagem": "O campo 'data' é obrigatório"
}
```

```json
{
  "mensagem": "O campo 'horaInicio' é obrigatório"
}
```

```json
{
  "mensagem": "O campo 'horaFim' é obrigatório"
}
```

**2. Formato de Data Inválido**

A data deve estar no formato dd/MM/yyyy.

```json
{
  "mensagem": "O campo 'data' deve estar no formato dd/MM/yyyy (ex: 02/02/2026). Valor informado: 2026-02-02"
}
```

**3. Formato de Hora Inválido**

Os horários devem estar no formato HH:mm.

```json
{
  "mensagem": "O campo 'horaInicio' deve estar no formato HH:mm (ex: 08:00). Valor informado: 8:00"
}
```

**4. Hora de Início Posterior à Hora de Fim**

A hora de início não pode ser posterior à hora de fim.

```json
{
  "mensagem": "A 'horaInicio' não pode ser posterior à 'horaFim'"
}
```

**5. Intervalo Máximo Excedido**

O intervalo entre os horários não pode ser superior a 2 horas.

```json
{
  "mensagem": "O intervalo entre 'horaInicio' e 'horaFim' não pode ser superior a 2 horas"
}
```

**6. Pessoa Não Vinculada à Equipe**

A pessoa deve estar vinculada à equipe informada.

```json
{
  "mensagem": "A pessoa <uuid pessoa> não está vinculada à equipe <uuid equipe>"
}
```

##### Response (404 Not Found)

**1. Equipe Não Encontrada**

```json
{
  "mensagem": "Equipe não encontrada"
}
```

**2. Unidade de Serviço Não Encontrada**

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

**3. Pessoa Não Encontrada**

```json
{
  "mensagem": "Pessoa não encontrada"
}
```

#### Comportamentos

| Condição | Comportamento |
|----------|---------------|
| Nenhuma posição no intervalo | Retorna lista vazia `[]` |
| Posição sem equipamento | Campo `uuidEquipamento` retorna `null` |
| Ordenação | Sempre decrescente por `dataHoraBrt` (mais recentes primeiro) |

---

### Consultar Últimas Posições Geográficas

Retorna as últimas posições geográficas das pessoas em equipes em serviço, agrupadas por Unidade de Serviço e Equipe.

**Endpoint:** `GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

#### Query Parameters (Filtros Opcionais)

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `uuidUnidadeServico` | UUID | Não | Filtra por uma Unidade de Serviço específica |
| `uuidEquipe` | UUID | Não | Filtra por uma Equipe específica |
| `uuidAgencia` | UUID | Não | Filtra equipes de US que possuem região de atuação na agência informada |
| `uuidPessoa` | UUID | Não | Retorna apenas a posição da pessoa específica (deve estar em equipe acessível) |

> **Importante:**
> - Todos os filtros são opcionais e combináveis
> - Sem filtros, retorna todas as equipes em serviço das agências do compartilhamento
> - Limite máximo de **500 pessoas** no resultado
> - Apenas equipes **em serviço** são retornadas

**Exemplos de uso:**

```
GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes
(sem filtros - retorna todas as equipes em serviço das agências do compartilhamento)

GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes?uuidAgencia=uuid-agencia-1
(filtra por agência específica)

GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes?uuidUnidadeServico=uuid-us-1
(filtra por Unidade de Serviço específica)

GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes?uuidEquipe=uuid-equipe-1
(filtra por Equipe específica)

GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes?uuidPessoa=uuid-pessoa-1
(retorna apenas a posição de uma pessoa específica)

GET /agente-campo/v3/cad-posicoes-api/ultimas-posicoes?uuidAgencia=uuid-agencia-1&uuidUnidadeServico=uuid-us-1
(combina filtros: agência E unidade de serviço)
```

**Response (200 OK):**

Retorna uma lista de Unidades de Serviço, cada uma contendo suas equipes em serviço com as posições das pessoas.

```json
[
  {
    "uuidUnidadeServico": "uuid-us-1",
    "nomeUnidadeServico": "US Alpha",
    "equipes": [
      {
        "uuidEquipe": "uuid-equipe-1",
        "nomeEquipe": "Equipe 01",
        "posicoesPessoas": [
          {
            "uuidPessoa": "uuid-pessoa-1",
            "cpfPessoa": "12345678901",
            "latitude": -15.7801,
            "longitude": -47.9292,
            "uuidEquipamento": "uuid-equipamento-1",
            "dataHoraEnvio": "10/02/2026 14:30:25"
          },
          {
            "uuidPessoa": "uuid-pessoa-2",
            "cpfPessoa": "98765432109",
            "latitude": -15.7805,
            "longitude": -47.9288,
            "uuidEquipamento": null,
            "dataHoraEnvio": "10/02/2026 14:29:15"
          }
        ],
        "pessoasSemPosicaoEnviada": [
          {
            "uuid": "uuid-pessoa-3",
            "cpf": "11122233344"
          }
        ]
      }
    ]
  },
  {
    "uuidUnidadeServico": "uuid-us-2",
    "nomeUnidadeServico": "US Bravo",
    "equipes": [
      {
        "uuidEquipe": "uuid-equipe-2",
        "nomeEquipe": "Equipe 02",
        "posicoesPessoas": [
          {
            "uuidPessoa": "uuid-pessoa-4",
            "cpfPessoa": "55566677788",
            "latitude": -15.7900,
            "longitude": -47.9400,
            "uuidEquipamento": "uuid-equipamento-2",
            "dataHoraEnvio": "10/02/2026 14:31:00"
          }
        ],
        "pessoasSemPosicaoEnviada": []
      }
    ]
  }
]
```

**Estrutura do Response:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuidUnidadeServico` | UUID | UUID da Unidade de Serviço |
| `nomeUnidadeServico` | String | Nome da Unidade de Serviço |
| `equipes` | Array | Lista de equipes em serviço da Unidade de Serviço |

**Estrutura de cada Equipe:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuidEquipe` | UUID | UUID da Equipe |
| `nomeEquipe` | String | Nome da Equipe |
| `posicoesPessoas` | Array | Lista de pessoas com posição geográfica enviada |
| `pessoasSemPosicaoEnviada` | Array | Lista de pessoas que ainda não enviaram posição |

**Estrutura de `posicoesPessoas`:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuidPessoa` | UUID | UUID da pessoa |
| `cpfPessoa` | String | CPF da pessoa |
| `latitude` | Number | Latitude da última posição enviada |
| `longitude` | Number | Longitude da última posição enviada |
| `uuidEquipamento` | UUID | UUID do equipamento associado (pode ser `null`) |
| `dataHoraEnvio` | String (dd/MM/yyyy HH:mm:ss) | Data e hora do envio da posição no formato brasileiro |

**Estrutura de `pessoasSemPosicaoEnviada`:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `uuid` | UUID | UUID da pessoa |
| `cpf` | String | CPF da pessoa |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Limite de Pessoas Excedido**

O resultado não pode conter mais de 500 pessoas.

```json
{
  "mensagem": "A consulta retornou mais de 500 pessoas. Refine os filtros para reduzir o resultado."
}
```

**2. Pessoa Não Encontrada em Equipe Acessível**

Quando filtrado por `uuidPessoa`, a pessoa deve estar em uma equipe em serviço acessível pelo compartilhamento de dados.

```json
{
  "mensagem": "Pessoa não encontrada em equipes em serviço acessíveis"
}
```

##### Response (404 Not Found)

**1. Unidade de Serviço Não Encontrada**

Quando filtrado por `uuidUnidadeServico`, a US deve existir.

```json
{
  "mensagem": "Unidade de Serviço não encontrada"
}
```

**2. Equipe Não Encontrada**

Quando filtrado por `uuidEquipe`, a equipe deve existir.

```json
{
  "mensagem": "Equipe não encontrada"
}
```

**3. Agência Não Encontrada**

Quando filtrado por `uuidAgencia`, a agência deve existir.

```json
{
  "mensagem": "Agência não encontrada"
}
```

**4. Pessoa Não Encontrada**

Quando filtrado por `uuidPessoa`, a pessoa deve existir.

```json
{
  "mensagem": "Pessoa não encontrada"
}
```

#### Comportamentos

| Condição | Comportamento |
|----------|---------------|
| Nenhum filtro informado | Retorna todas as equipes em serviço das agências do compartilhamento |
| Pessoa sem posição enviada | Aparece na lista `pessoasSemPosicaoEnviada` |
| Posição sem equipamento | Campo `uuidEquipamento` retorna `null` |
| Nenhuma equipe encontrada | Retorna lista vazia `[]` |
| Filtro por `uuidAgencia` | Filtra US que possuem região de atuação na agência informada |
| Filtro por `uuidPessoa` | Retorna apenas a US e equipe que contêm a pessoa especificada |
| Lista `pessoasSemPosicaoEnviada` vazia | A lista pode estar vazia se todas as pessoas da equipe enviaram posição |

---

### Pesquisar Histórico de Posições Geográficas

Pesquisa no histórico de posições geográficas com filtros combináveis. Retorna resultado sem agrupamento (lista simples), paginado e ordenado por data/hora decrescente. Valida o compartilhamento de dados, mas **não restringe por situação da equipe ou da unidade de serviço**.

**Endpoint:** `POST /agente-campo/v3/cad-posicoes-api/pesquisar-posicoes-historico`

**Headers:** `cpf`, `nome`, `sinesp-username` — ver [Headers Obrigatórios](#headers-obrigatórios).

**Request Body:**

```json
{
  "uuidUnidadeServico": "uuid-us-1",
  "uuidEquipe": "uuid-equipe-1",
  "uuidAgencia": "uuid-agencia-1",
  "uuidPessoa": "uuid-pessoa-1",
  "data": "02/02/2026",
  "horaInicio": "08:00",
  "horaFim": "10:00",
  "numeroPagina": 1,
  "tamanhoPagina": 200
}
```

**Parâmetros do Request:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `uuidUnidadeServico` | UUID | Não* | UUID da Unidade de Serviço |
| `uuidEquipe` | UUID | Não* | UUID da Equipe |
| `uuidAgencia` | UUID | Não* | UUID da Agência (filtra equipes de US com região de atuação na agência) |
| `uuidPessoa` | UUID | Não* | UUID da Pessoa (filtra posições da pessoa específica) |
| `data` | Data (dd/MM/yyyy) | Não** | Data da consulta no formato brasileiro. Se não informada, considera a data atual |
| `horaInicio` | Hora (HH:mm) | Não** | Hora de início do intervalo (formato 24h). Se não informada, considera 2 horas antes da `horaFim` |
| `horaFim` | Hora (HH:mm) | Não** | Hora de fim do intervalo (formato 24h). Se não informada, considera a hora atual |
| `numeroPagina` | Número inteiro | Não | Número da página (padrão: 1, começando em 1) |
| `tamanhoPagina` | Número inteiro | Não | Registros por página (padrão: 200, máximo: 200) |

> \* **Pelo menos um filtro** deve ser informado: `uuidUnidadeServico`, `uuidEquipe`, `uuidAgencia` ou `uuidPessoa`.
>
> \** **Data e horários:** Se não informados, considera automaticamente as **últimas 2 horas**. Se algum campo de data/hora for informado, todos os três (`data`, `horaInicio`, `horaFim`) devem ser informados. O intervalo máximo permitido é de **2 horas**.

**Response (200 OK):**

```json
{
  "metadados": {
    "paginaAtual": 1,
    "registrosPorPagina": 200,
    "totalRegistros": 450,
    "totalPaginas": 3
  },
  "dados": [
    {
      "dataHoraBrt": "02/02/2026 09:45:00",
      "latitude": -15.7801,
      "longitude": -47.9292,
      "uuidEquipamento": "uuid-equipamento-1",
      "uuidEquipe": "uuid-equipe-1",
      "uuidUnidadeServico": "uuid-us-1",
      "uuidPessoa": "uuid-pessoa-1",
      "cpfPessoa": "12345678901"
    },
    {
      "dataHoraBrt": "02/02/2026 09:44:30",
      "latitude": -15.7805,
      "longitude": -47.9288,
      "uuidEquipamento": null,
      "uuidEquipe": "uuid-equipe-1",
      "uuidUnidadeServico": "uuid-us-1",
      "uuidPessoa": "uuid-pessoa-2",
      "cpfPessoa": "98765432109"
    }
  ]
}
```

**Campos do Response - Metadados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `paginaAtual` | Número | Página atual da consulta |
| `registrosPorPagina` | Número | Quantidade de registros por página |
| `totalRegistros` | Número | Total de registros encontrados |
| `totalPaginas` | Número | Total de páginas disponíveis |

**Campos do Response - Dados:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `dataHoraBrt` | String (dd/MM/yyyy HH:mm:ss) | Data e hora da posição geográfica (horário de Brasília) |
| `latitude` | Número | Latitude da posição geográfica |
| `longitude` | Número | Longitude da posição geográfica |
| `uuidEquipamento` | UUID | UUID do equipamento associado (pode ser `null`) |
| `uuidEquipe` | UUID | UUID da equipe |
| `uuidUnidadeServico` | UUID | UUID da Unidade de Serviço |
| `uuidPessoa` | UUID | UUID da pessoa |
| `cpfPessoa` | String | CPF da pessoa |

#### Validações e Respostas de Erro

> **Nota:** As validações de compartilhamento de dados estão descritas na seção [Validações Comuns de Compartilhamento de Dados](#validações-comuns-de-compartilhamento-de-dados).

##### Response (400 Bad Request)

**1. Filtro Obrigatório**

Pelo menos um filtro de entidade deve ser informado.

```json
{
  "mensagem": "Pelo menos um filtro deve ser informado: uuidUnidadeServico, uuidEquipe, uuidAgencia ou uuidPessoa"
}
```

**2. Tamanho da Página**

O parâmetro `tamanhoPagina` deve ser no máximo **200**.

```json
{
  "mensagem": "O tamanho da página deve ser no máximo 200"
}
```

**3. Campos de Data/Hora Incompletos**

Quando algum campo de data/hora é informado, todos devem ser.

```json
{
  "mensagem": "O campo 'data' é obrigatório quando horaInicio ou horaFim são informados"
}
```

```json
{
  "mensagem": "O campo 'horaInicio' é obrigatório quando data ou horaFim são informados"
}
```

**4. Formato de Data Inválido**

```json
{
  "mensagem": "O campo 'data' deve estar no formato dd/MM/yyyy (ex: 02/02/2026). Valor informado: 2026-02-02"
}
```

**5. Formato de Hora Inválido**

```json
{
  "mensagem": "O campo 'horaInicio' deve estar no formato HH:mm (ex: 08:00). Valor informado: 8:00"
}
```

**6. Hora de Início Posterior à Hora de Fim**

```json
{
  "mensagem": "A 'horaInicio' não pode ser posterior à 'horaFim'"
}
```

**7. Intervalo Máximo Excedido**

```json
{
  "mensagem": "O intervalo entre 'horaInicio' e 'horaFim' não pode ser superior a 2 horas"
}
```

**8. Pessoa Não Encontrada em Equipe Acessível**

```json
{
  "mensagem": "A pessoa informada não pertence a nenhuma equipe em serviço acessível"
}
```

##### Response (404 Not Found)

**1. Equipe Não Encontrada**

```json
{
  "mensagem": "Equipe não encontrada"
}
```

**2. Pessoa Não Encontrada**

```json
{
  "mensagem": "Pessoa não encontrada"
}
```

#### Comportamentos

| Condição | Comportamento |
|----------|---------------|
| Data/hora não informados | Considera as últimas 2 horas (horário atual menos 2 horas) |
| Nenhuma posição no intervalo | Retorna lista vazia com `totalRegistros: 0` |
| Posição sem equipamento | Campo `uuidEquipamento` retorna `null` |
| Ordenação | Sempre decrescente por `dataHoraBrt` (mais recentes primeiro) |
| Paginação padrão | 200 registros por página, página 1 |
| Filtro por `uuidAgencia` | Filtra equipes de US com região de atuação na agência informada |
| Filtro por `uuidPessoa` | Posições são buscadas de todas as equipes acessíveis, mas o campo `uuidPessoa` permite identificar quais pertencem à pessoa desejada |

---

## Histórico de Alterações do Documento

| Item | Alteração |
|------|-----------|
| URL Base | Incluído o caminho comum `/agente-campo/v3` antes do prefixo de cada API (`cad-unidade-servico-api`, `cad-equipamento-api`, `cad-pessoa-api`, `cad-posicoes-api`). Todos os endpoints passaram a ser apresentados com o caminho completo. |
| Headers | Criada a seção [Headers Obrigatórios](#headers-obrigatórios) (`cpf`, `nome`, `sinesp-username`), exigidos por todos os endpoints conforme o Swagger, e referenciada em cada endpoint. |
| Criar Pessoa | Incluído o campo obrigatório `registroFuncional` (1 a 50 caracteres). Ajustados limites: `nome` 1 a 80, `nomeFuncional` até 80, telefones somente números até 11 caracteres. |
| Alterar Pessoa | Incluído o campo `registroFuncional` (1 a 50 caracteres). Ajustados os mesmos limites de `nome`, `nomeFuncional` e telefones. |
| Alterar Equipamento | Incluída a tabela de parâmetro de path (`uuid`). Incluído tamanho mínimo de `prefixo` (1). |
| Criar Equipamento | Incluído tamanho mínimo de `prefixo` (1). |
| Excluir Equipamento | Incluída a tabela de parâmetro de path (`uuid`). |
| Listar Equipamentos / Listar Pessoas | Metadados do response alinhados ao Swagger (`registrosPorPagina` e `totalPaginas`). Incluídos limites mínimos de paginação. Incluída tabela de campos do response de equipamentos. |
| Listar Unidades de Serviço | Metadados do response alinhados ao Swagger (`registrosPorPagina` no lugar de `tamanhoPagina`). Removido o campo `agrupamento`, inexistente no Swagger. |
| Pesquisar Histórico de Posições | Detalhado o comportamento padrão individual de `data`, `horaInicio` e `horaFim`; registrado que não há restrição por situação da equipe/US. |
| Geral | Corrigida a numeração duplicada/salteada das listas de erros e padronizados os exemplos de telefone para somente números. |
