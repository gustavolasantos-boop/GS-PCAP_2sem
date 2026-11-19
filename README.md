# Citizen Assist Idoso

**GS 2026.2 — 1CC-PCP: Pensamento Computacional e Automação com Python**  
**Público:** pessoas idosas e familiares/cuidadores que procuram orientações sobre Cartão SUS, vacinação, transporte gratuito e direitos básicos.

> **Aviso importante:** este assistente não é canal oficial. Ele oferece orientação geral a partir de uma base local de fontes públicas verificadas. Não substitui a prefeitura, a unidade de saúde, a empresa de transporte ou a orientação profissional.

## 1. Problema e proposta

Informações sobre saúde e direitos da pessoa idosa ficam espalhadas por páginas diferentes, e nem sempre é fácil identificar quais são oficiais. O Citizen Assist Idoso organiza orientações em linguagem simples, mostra a fonte e a data de verificação e ajuda a encontrar uma orientação por pergunta livre ou por categoria.

O programa não usa API de IA nem envia consultas à internet. A busca é determinística e executada localmente sobre `data/base_conhecimento.json`.

## 2. Integrantes

Preencher antes da entrega:

- Integrante 1: **[NOME COMPLETO]** — RM **[RM]**
- Integrante 2: **[NOME COMPLETO]** — RM **[RM]**
- Integrante 3 (se houver): **[NOME COMPLETO]** — RM **[RM]**

## 3. Objetivos de Desenvolvimento Sustentável (ODS)

- **ODS 3 — Saúde e bem-estar:** facilita localizar orientações oficiais sobre Cartão SUS e vacinação.
- **ODS 10 — Redução das desigualdades:** organiza informações em linguagem simples e acessível para um público que pode enfrentar barreiras digitais.
- **ODS 11 — Cidades e comunidades sustentáveis:** inclui orientação sobre transporte público e benefícios para viagens interestaduais.
- **ODS 16 — Paz, justiça e instituições eficazes:** informa direitos prioritários e canais oficiais para denúncia de violações contra pessoas idosas.

Essa relação com os ODS é a justificativa do projeto, não uma certificação institucional.

## 4. Funcionalidades implementadas

- Carrega a base local de `data/base_conhecimento.json`.
- Inclui **12 orientações** distribuídas em **3 categorias**: Saúde, Transporte e Direitos e proteção.
- Usa as classes `Orientacao`, `BaseConhecimento` e `Assistente`, com composição entre elas.
- Pesquisa texto livre com normalização de acentos, pontuação e maiúsculas/minúsculas.
- Pontua cada palavra-chave correspondente com **+3** e cada palavra da pergunta com 4 ou mais letras que aparece no título com **+1**.
- Exibe confiança **ALTA** a partir de 6 pontos e **MÉDIA** de 3 a 5. Abaixo de 3, não apresenta a orientação como resposta e sugere reformulação ou navegação por categoria.
- Mostra a melhor orientação e até duas alternativas com pelo menos 3 pontos.
- Permite navegar pelas categorias e escolher orientações numeradas. As telas de navegação oferecem `0` para voltar.
- Valida entradas vazias, opções fora da faixa e respostas diferentes de `s/n` sem fechar o programa.
- Recusa perguntas que contenham `@` ou oito ou mais dígitos. A entrada recusada não é guardada no histórico.
- Não pede nome, CPF, telefone ou e-mail. **Não digite nenhum dado pessoal no assistente.** O filtro automático cobre os padrões exigidos no enunciado, mas não consegue reconhecer todo tipo possível de dado pessoal.
- Registra atendimentos em `data/historico.json`, gera `data/atendimentos.csv` com `csv.DictWriter` e guarda notas de facilidade em `data/avaliacoes_facilidade.json`.
- Calcula taxa de respostas encontradas, taxa de resolução, tempo médio, tentativas médias, média de facilidade e lista de dúvidas sem solução confirmada.
- Se a base ou o histórico JSON estiver ausente/corrompido, mostra um aviso e tenta continuar sem derrubar o programa.

## 5. Estrutura do projeto

```text
citizen-assist-idosos/
├── README.md
├── main.py
├── orientacao.py
├── base_conhecimento.py
├── assistente.py
├── FONTES_CONSULTADAS.md
├── RELATORIO_TESTE_DEMONSTRATIVO.md
├── ROTEIRO_TESTE_USUARIOS.md
├── ROTEIRO_VIDEO.md
├── ENTREGA_FIAP.txt
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    ├── avaliacoes_facilidade.json
    ├── atendimentos.csv
    └── teste_usuarios_demonstrativo.csv  # exemplo separado, não operacional
```

### Relação com os exemplos das aulas no ZIP

- `aula07-dicionarios-tuplas`: a base é uma lista de dicionários JSON e `buscar()` retorna tuplas `(pontos, orientacao)` ordenadas.
- `aula08-mini-crm/control.py`: leitura e gravação de JSON com `pathlib.Path` e tratamento de arquivo ausente/corrompido.
- `aula09-mini-crm/control.py`: exportação CSV usando `csv.DictWriter`.
- `aula10-orientacao-objetos`: uso de classes, `__init__`, `self`, listas de objetos e composição. Neste projeto, `Assistente` contém um `BaseConhecimento`, que mantém uma lista de objetos `Orientacao`.
- A lógica de menu usa condicionais e laços `while`, seguindo as aulas de condicionais e repetição.

## 6. Como executar

Requisitos: **Python 3.10 ou superior**. O projeto usa somente a biblioteca padrão; não precisa instalar pacotes.

1. Extraia a pasta `citizen-assist-idosos`.
2. Abra o terminal dentro dela.
3. Execute:

```bash
python main.py
```

No Windows, se o comando `python` não funcionar, tente `py main.py`.

Menu principal:

```text
[1] Fazer uma pergunta
[2] Navegar por categorias
[3] Ver indicadores
[0] Sair
```

Ao sair, é solicitada uma nota opcional de facilidade de uso de 1 a 5 (`0` pula a avaliação), o CSV é atualizado e os indicadores são exibidos.

## 7. Regra de pontuação

1. A pergunta, o título e as palavras-chave são normalizados: minúsculas, sem acentos e sem pontuação.
2. Cada palavra-chave ou expressão cadastrada que aparece na pergunta soma **3 pontos**.
3. Cada palavra única da pergunta com 4 ou mais letras que também aparece no título soma **1 ponto**.
4. A lista de resultados é ordenada da maior para a menor pontuação e é retornada como tuplas `(pontos, orientação)`.
5. `6+` pontos = confiança **ALTA**; `3–5` = confiança **MÉDIA**; `0–2` = a orientação não é apresentada como resposta.

Os valores e limites seguem a tabela do enunciado. A pontuação é uma medida de correspondência textual, não uma probabilidade estatística nem uma garantia de que a orientação resolveu a dúvida.

## 8. Histórico, indicadores e privacidade

Cada atendimento registra data/hora, origem (`pergunta` ou `categoria`), pergunta, ID da orientação (ou `null`), se encontrou orientação, se ajudou (ou `null` quando a pessoa voltou sem avaliar), número de tentativas e tempo em segundos.

- **Resposta encontrada (%):** atendimentos que encontraram orientação com pontuação mínima 3 ÷ atendimentos registrados.
- **Taxa de acerto/ajudou (%):** avaliações positivas ÷ avaliações `sim` ou `não` conhecidas. Casos em que a pessoa voltou sem responder não entram nesse denominador.
- **Tempo médio:** média de `tempo_segundos` dos atendimentos registrados.
- **Tentativas por atendimento:** média do campo `tentativas`.
- **Facilidade de uso:** média das notas de 1 a 5 em `avaliacoes_facilidade.json`.
- **Dúvidas sem solução confirmada:** atendimentos sem orientação encontrada ou sem confirmação de que resolveu.

O programa não solicita identificadores pessoais. Perguntas com `@` ou 8+ dígitos são recusadas antes de serem registradas. Ainda assim, o filtro não reconhece todos os possíveis dados pessoais: não forneça nomes, endereços, números de documento, telefone, e-mail, senhas ou informações de saúde particulares. O histórico contém o texto das perguntas aceitas para permitir a análise de dúvidas não resolvidas; trate os arquivos de dados com cuidado.

## 9. Fontes da base de conhecimento

As fontes são páginas de órgãos públicos federais; a equipe conferiu os conteúdos em **19/11/2026**. Cada registro também tem seu próprio campo `fonte` e `verificado_em`. Os detalhes e a relação de cada orientação com sua fonte estão em [`FONTES_CONSULTADAS.md`](FONTES_CONSULTADAS.md).

**Limitação importante:** benefícios de transporte municipal podem depender da cidade. A base não presume que a regra de um município vale em outro. Calendários vacinais individuais dependem do histórico e da avaliação do serviço de saúde.

## 10. Teste com usuários e demonstração de indicadores

O projeto inclui [`RELATORIO_TESTE_DEMONSTRATIVO.md`](RELATORIO_TESTE_DEMONSTRATIVO.md) e [`data/teste_usuarios_demonstrativo.csv`](data/teste_usuarios_demonstrativo.csv) para demonstrar o formato de registro, o cálculo dos indicadores e a identificação de perguntas sem solução. **Esses dados são simulados e servem somente para demonstração técnica; não são evidência de entrevistas realizadas.** Eles ficam separados de `historico.json`, `atendimentos.csv` e `avaliacoes_facilidade.json` para não contaminar as métricas de execução real.

O enunciado exige teste com **pelo menos 3 pessoas de fora da equipe e 10 atendimentos reais**. Essa etapa continua **PENDENTE** até que a equipe execute o teste. Use [`ROTEIRO_TESTE_USUARIOS.md`](ROTEIRO_TESTE_USUARIOS.md), não registre nomes ou dados pessoais e substitua os resultados demonstrativos pelos resultados realmente observados ao concluir a avaliação. A melhoria efetivamente feita a partir da avaliação real também deve ser descrita nesta seção.

## 11. Integrações e limitações

- Integração entre disciplinas: a estrutura de dados em dicionários/listas e a busca com pontuação se relacionam a programação, lógica, organização de dados e fundamentos de algoritmos. A solução não integra APIs ou modelos de IA.
- A base é local e precisa ser revisada quando páginas oficiais ou regras mudarem.
- O resultado depende das palavras-chave cadastradas; perguntas com sinônimos não previstos podem não ser encontradas.
- O programa não consulta horários, disponibilidade de atendimento ou regras específicas da cidade em tempo real.
- O filtro de dados pessoais é intencionalmente simples e não substitui uma solução completa de prevenção de envio de dados.
- O assistente oferece orientação geral e não substitui serviços oficiais, avaliação médica ou aconselhamento jurídico.

## 12. Entrega e vídeo

- Repositório público GitHub: **[INSERIR LINK APÓS PUBLICAÇÃO]**
- Vídeo técnico não listado no YouTube (5 a 8 minutos): **[INSERIR LINK APÓS GRAVAÇÃO]**

Consulte [`ROTEIRO_VIDEO.md`](ROTEIRO_VIDEO.md) para cobrir todos os tópicos obrigatórios. O arquivo [`ENTREGA_FIAP.txt`](ENTREGA_FIAP.txt) contém o modelo do `.txt` exigido no portal.
