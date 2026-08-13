# Processo de negócio suportado

## O problema real

Quem precisa entender o schema `CAD_OCORRENCIA` do SINESP CAD 3 — para escrever uma consulta,
integrar um sistema, auditar um dado ou responder a um pedido de informação — tem como fonte
primária um PDF de 87 páginas exportado do Oracle SQL Developer Data Modeler.

Um PDF de 87 páginas com 71 tabelas e 831 colunas responde mal às perguntas que as pessoas
realmente fazem:

- "Em que tabela fica o dado X?"
- "O que significa esta coluna?"
- "Quem referencia esta tabela? A que ela se liga?"
- "Qual o DDL aproximado para eu montar um ambiente de teste?"

Buscar num PDF é linear, não entende acento e não segue relacionamento. O resultado prático é
retrabalho: cada pessoa refaz a mesma leitura, e a resposta obtida não fica disponível para a
próxima.

## As pessoas atendidas

| Papel | O que precisa | O que o site entrega |
|---|---|---|
| Analista de dados / BI | localizar tabela e coluna por nome ou por descrição | busca global sem sensibilidade a acentos, com trechos destacados |
| Desenvolvedor de integração | conhecer contratos, tipos e obrigatoriedade | grade de colunas com tipo, PK/FK/NN e link para a coluna referenciada |
| DBA / arquiteto | ver o modelo, índices e constraints | diagrama de vizinhança por tabela, mapa geral e exportação de DDL |
| Gestor / auditor | entender o que o sistema registra | descrições de tabela e coluna em linguagem corrente, navegáveis |

## O fluxo

```
  PDF oficial do modelo
          │
          ▼
  extração (pdfplumber)  ──►  validação automática  ──►  falha = publicação bloqueada
          │
          ▼
  dicionário navegável (GitHub Pages)
          │
          ├─► buscar por nome, coluna ou descrição
          ├─► navegar pelos relacionamentos (FK ida e volta)
          ├─► visualizar o modelo (vizinhança e mapa geral)
          └─► exportar (DDL, JSON, CSV, Mermaid)
```

A extração não é confiança cega: `tools/extrair_pdf.py` aborta com código 1 se a leitura regredir —
se alguma tabela não tiver o número de colunas que ela mesma declara, se alguma seção do PDF não for
reconhecida, se alguma FK apontar para tabela inexistente, ou se as duas visões de um relacionamento
(`Refering To` na origem, `Referred From` no destino) não fecharem.

## O que muda com o Padrão Digital de Governo

O conteúdo é o mesmo; muda quem consegue usá-lo e com que confiança.

- **Reconhecimento.** Cabeçalho, rodapé, tipografia e paleta oficiais dizem, sem precisar explicar,
  que é um sistema institucional e não uma página pessoal.
- **Familiaridade.** Quem já usa serviços gov.br encontra a busca, o menu e os atalhos de teclado
  onde espera. Não há interface nova para aprender.
- **Acesso.** VLibras para pessoas surdas; navegação completa por teclado com os `accesskey` 1 a 4;
  contraste e semântica conforme WCAG 2.2 AA (ABNT NBR 17225:2025).
- **Rastreabilidade.** O rodapé declara a origem: data de geração, arquivo PDF de origem e a ressalva
  de que o conteúdo é reproduzido como está no documento original.

## Limites conhecidos

O dicionário reproduz a fonte, inclusive suas imprecisões (`Refering To`, `Chamdo`). O DDL exportado
é aproximado: tipos são traduzidos do modelador para Oracle, mas defaults e check constraints
precisam de conferência antes de qualquer uso real — as checks saem apenas como comentário. Os campos
`Domain Name`, `Security` e `Abbreviation` estão vazios nas 831 colunas do documento e por isso não
aparecem na interface, embora sigam preservados no JSON.
