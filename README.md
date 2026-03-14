# Loyalty Predict Project

Projeto de Ciência de Dados realizado por Eduardo Ferreira da Silva. 

## Visão Geral do Projeto
Bem vindo ao meu projeto de predição de fidelidade de clientes utilizando dados do canal Teo Me Why da Twitch. Nele o **objetivo** foi construir uma **Tabela Base Analítica** (ABT) e um **modelo** de **aprendizado de máquina** (*machine learning*) para realizar **predições** sobre a **probabilidade** de um **cliente** se tornar **fiel** nos 28 dias seguintes a uma data específica.

Dessa forma, utilizando as características (*features*) construídas do cliente no dia 01/03/2026, por exemplo, é possível determinar a probabilidade dele se tornar fiel no dia 29/03/2026. Para construir e orquestrar essas predições foram utilizadas, principalmente, scripts **Python**, consultas em **SQL** e conhecimentos de **Estatística** e **Aprendizado de Máquina**.

Para desenvolvimento do projeto foi utilizada a metodologia *Cross-Industry Standard Process for Data Mining* (CRISP-DM) que estabelece 6 etapas: 
1. Entendimento do Negócio;
2. Entendimento dos dados;
3. Preparação dos dados;
4. Modelagem;  
5. Validação;
6. Implementação do projeto e acompanhamento.

Além disso, dentro da etapa de modelagem utilizou-se a metodologia *Sample-Explore-Modify-Model-Assess* (SEMMA) desenvolvida pela empresa SAS.

## Questão

A principal questão que pretende-se responder nesse projeto é:

* ``Qual a probabilidade de um cliente se tornar fiel daqui a 28 dias?``

Observação: Um cliente é considerado fiel se realizou ao menos uma transação nos últimos 7 dias considerando uma data específica.

## Ferramentas Utilizadas

Para construção da ABT e do modelo de predição de fidelidade foram utilizadas as seguintes ferramentas:

- **SQL**: entender e analisar os dados do negócio, construir as características dos cliente e criar a Tabela Base Analítica (ABT); 

- **Python**: Orquestrar a criação de tabelas com SQL, possibilitar o treinamento e teste de algoritmos de aprendizado de máquina, automatizar a obtenção de dados atualizados e criar uma *Application Programming Interface* (API) para realizar as predições de fidelidade. Também foram utilizadas, principalmente, as seguintes bibliotecas:  
    - **Biblioteca Pandas**: manipular e preparar dados para a modelagem;
    - **Biblioteca MLflow**: versionar e administrar modelos de aprendizado de máquina; 
    - **Biblioteca SQLAlchemy**: realizar conexões com bancos de dados e realizar consultas;
    - **Biblioteca Flask**: criar uma API para o modelo preditivo;
    - **Biblioteca Requests**: realizar requisições na API criada para o modelo;
    - **Biblioteca Matplotlib**: visualizar dados e estatísticas;
    - **Biblioteca Seaborn**: visualizar gráficos de dispersão com categorias;
    - **Biblioteca Feature_engine**: transformar as características dos clientes para o modelo, imputando valores faltantes, codificando variáveis categóricas e selecionando as características mais relevantes;
    - **Biblioteca Scikit-learn**: modelar o problema com algoritmos de aprendizado de máquina. Alguns dos algoritmos utilizados no caso desse projeto foram:
        - ***Decision Tree Classifier***: busca classificar os clientes em fieis e não fieis por meio de divisões sucessivas, chamados de nós, considerando características da ABT e gerar um *score* de probabilidade para cada uma das classificações;
        - ***Random Forest Classifier***: utiliza um conjunto de *Decision Tree Classifier* com amostras diferentes e combinar suas predições para classificar os clientes em fiéis e não fiéis, gerando *scores* de probabilidade para cada um;
        - ***Adaptive Boosting Classifier***: treina iterativamente modelos base, alterando o peso de cada observação e dando mais importância a aquelas que possuem um erro maior associado com o objetivo de classificar clientes em fieis e não fieis.
 
## Como Utilizar (Para Usuários)

## Entendimento do Negócio

O ecossistema Teo Me Why envolve um sistema de pontos que é movimentado por transações realizadas em troca de produtos virtuais e pelo engajamento nas transmissões ao vivo no canal [Teo Me Why](https://www.twitch.tv/teomewhy) na Twitch e na [plataforma de cursos](https://cursos.teomewhy.org/).

É possível ganhar pontos:
 - Enviando comentários nas transmissões ao vivo;
 - Assistindo as transmissões ao vivo;
 - Assinando uma lista de presença;
 - Completando cursos. 
 
 Com o saldo acumulado pode-se:
 - Comprar itens para um personagem virtual de RPG;
 - Comprar benefícios durante as lives; 
 - Trocar os pontos para obter outro tipo de moeda, utilizada em transações de itens físicos.  

As transmissões ao vivo na Twitch são realizadas de segunda à sexta na parte da manhã com o Teodoro Calvo realizando algum conteúdo relacionado a Tecnologia. Em alguns dias, são marcados cursos ou projetos de Ciência de Dados, sendo esse os dias mais movimentados.

Os vídeos das transmissões ficam salvos na Twitch para assinantes que apoiam o canal de lives. Além disso, os cursos e projetos são editados e postados no YouTube, compondo a plataforma de cursos, a qual é construída utilizando a biblioteca do Python Streamlit e permite que os usuários registrarem seu progresso.
 
Nesse projeto não são analisadas as transações financeiras do ecossistema Teo Me Why, pois o objetivo aqui está relacionado ao engajamento, o qual é inconstante durante o ano e necessita de ações a serem realizadas.

Uma dessas ações é a predição da probabilidade de clientes se tornarem fiéis para que, assim, seja possível tomar ações com o intuito de, por exemplo, aumentar o público que assiste e interage nas transmissões ao vivo semanalmente.

## Entendimento dos Dados

Os dados foram coletados e disponibilizados na forma de bancos de dados pelo Teodoro Calvo na plataforma Kaggle, sendo eles a base para o desenvolvimento desse projeto.

Para realizar as consultas, foi utilizada a linguagem SQL, com o SQLite como sistema para gerenciar banco de dados (SGDB).

### Fontes de Dados

O primeiro banco de dados conta com 4 tabelas sobre clientes, produtos, transações, sendo referente ao sistema de pontos do canal Teo Me Why da Twitch.


- **Sistema de Pontos**: [https://www.kaggle.com/datasets/teocalvo/teomewhy-loyalty-system](https://www.kaggle.com/datasets/teocalvo/teomewhy-loyalty-system)


O segundo banco de dados conta com 8 tabelas relacionadas à plataforma de cursos. Vale ressaltar que somente 10% da base tem informações cadastradas nessa plataforma.

- **Plataforma de Cursos**: [https://www.kaggle.com/datasets/teocalvo/teomewhy-education-platform](https://www.kaggle.com/datasets/teocalvo/teomewhy-education-platform)

### Esquema dos Bancos de Dados

![schema_loyalty_sytem](img\schema_loyalty_system.png)

![schema_loyalty_sytem](img\schema_education_platform.png)
### Análise do Engajamento dos Usuários

A primeira análise realizada tinha o objetivo de identificar se estava acontecendo perda ou ganho de engajamento dos usuários nas transmissões ao vivo do Teo Me Why.

#### Usuários Ativos Diariamente (DAU)

Para isso foi utilizada a métrica de **Usuários Ativos Diariamente (DAU)**, considerando como um usuário ativo aquele que realizou ao menos uma transação no sistema de pontos em um determinado dia.

Para calcular essa métrica, foi utilizada uma consulta em SQL ao banco de dados do sistema de pontos:

```SQL
-- DAU: Daily Active Users

-- Seleciona uma coluna que contém apenas a data 
SELECT DATE(DtCriacao) as dtDia,
       -- Conta clientes distintos em uma data (DAU) 
       COUNT(DISTINCT idCliente) as DAU

-- Define a consulta na tabela transacoes 
FROM transacoes

-- Agrupa pela data
GROUP BY dtDia

-- Ordena pela data na ordem ascendente
ORDER BY dtDia  
```

O gráfico da série temporal do DAU gerada por essa consulta é o seguinte:

![DAU](img/dau.png)

Entretanto, ao analisar esse gráfico não foi possível perceber uma tendência clara de crescimento ou de queda no engajamento. Isso ocorre porque as transmissões não são feitas de final de semana, o que gera variações de DAU entre dias com e sem atividades, introduzindo um nível alto de ruído na série temporal.

#### Usuários Ativos Mensalmente (MAU)

Por conta dos ruídos gerados no DAU, optou-se por utilizar a métrica de **Usuários Ativos Mensalmente (MAU)**, evitando os ruídos do final de semana. No MAU considerou-se um janela móvel de 28 dias, pois ela contém exatamente 4 vezes cada dia da semana, reduzindo distorções causadas pela sazonalidade semanal.

Para calcular a métrica MAU, foi utilizada a seguinte consulta em SQL:

```SQL
-- Constrói tabela com datas e usuários distintos 
WITH tb_daily_users AS (
     
    SELECT DISTINCT 
        DATE(DtCriacao) AS dtDia,
        idCliente
    FROM transacoes

),

-- Constrói tabela com todos os dias da base
tb_reference_day AS (
    
    SELECT DISTINCT 
        dtDia AS dtRef
    FROM tb_daily_users

),

-- Calcula Usuários Mensais Ativos (MAU)
tb_mau AS (

    SELECT t1.dtRef,
           -- Usuários distintos ativos nos últimos 28 dias
           COUNT(DISTINCT t2.idCliente) AS MAU,
           -- Quantidade de dias observados nos últimos 28 dias
           COUNT(DISTINCT t2.dtDia) AS qtdDias
    FROM tb_reference_day AS t1

    LEFT JOIN tb_daily_users AS t2
    ON  t2.dtDia <= t1.dtRef
    AND (JULIANDAY(t1.dtRef) - JULIANDAY(t2.dtDia)) < 28

    -- Agrupa pela data de referência
    GROUP BY t1.dtRef

)

SELECT *
FROM tb_mau
ORDER BY dtRef
```

O gráfico da série temporal do MAU, construído com os dados obtidos nessa consulta, pode ser observado abaixo:

![MAU](img/mau.png)

#### Interpretação Gráfico da métrica MAU

Ao analisar o gráfico da métrica MAU é possível observar que em alguns meses ocorrem picos no número de Usuários Ativos Mensalmente. Esses aumentos coincidem com períodos em que o canal Teo Me Why está promovendo cursos e projetos. 

Além disso, nota-se uma **tendência de queda** entre **março de 2024 e agosto de 2025**, indicando uma possível redução de engajamento dos usuários nesse período. Em seguida, observa-se um **aumento substancial** no **mês posterior** a essa janela, o que pode estar relacionado com o curso de SQL ministrado pelo Teodoro Calvo, estimulando maior engajamento dos usuários.

Na sequência, identifica-se uma **nova tendência de queda** entre **outubro de 2025 e janeiro de 2026**, sugerindo que que o aumento substancial anterior pode ter sido pontual e atribuído ao sucesso do curso.

Diante deste cenário, torna-se relevante tomar medidas para aumentar o engajamento do público e reverter a tendência de queda observada. 

Nesse contexto, um modelo de aprendizado de máquina capaz de prever os usuários com maior probabilidade de se tornarem fiéis pode auxiliar na definição de ações de Marketing com o intuito de incentivar o engajamento e recorrência desse público.

### Geração dos Gráficos para Análise
Para gerar os gráficos das métricas DAU e MAU foi utilizado o seguinte script Python:

```Python
#%%
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns

# Executa uma consulta SQL e retorna o resultado como DataFrame 
def load_metric(
        path: str, 
        engine: sqlalchemy.engine.base.Engine
) -> pd.DataFrame:
  
    # Abre, salva e fecha o arquivo contendo a consulta SQL 
    with open(path) as open_file:
        query = open_file.read()
  
    # Executa a consulta e armazena o resultado em um DataFrame
    df = pd.read_sql(query, engine)
  
    return df 

# Gera um gráfico de série temporal da métrica de Usuários Ativos  
def graph(
        df: pd.DataFrame, 
        x_date: str, 
        y_metric:str, 
        color: str, 
        title: str
):
    
    # Converte a coluna de data para datetime
    df[x_date] = pd.to_datetime(df[x_date])
    print(df.dtypes)
    # Define o tamanho da figura
    plt.figure(figsize=(12,6))
    
    # Cria um gráfico de linha a partir do DataFrame
    sns.lineplot(
        data=df, 
        x=x_date, 
        y=y_metric, 
        linewidth=2, 
        color=color)

    # Configura rótulos e títulos do gráfico 
    plt.xlabel("Data")
    plt.ylabel("Usuários Ativos")
    plt.title(title)

    # Adiciona uma grade ao gráfico
    plt.grid()

    # Exibe o gráfico
    plt.show()

# Cria uma engine do SQLAlchemy que gerencia conexões com o banco de dados SQLite
engine = sqlalchemy.create_engine(
    "sqlite:///../../data/loyalty-system/database.db"
)

# DataFrame do Daily Active Users (DAU)
df_dau = load_metric("dau.sql", engine)

# Gráfico do DAU
graph(
    df_dau, 
    "dtDia", 
    "DAU", 
    "blue", 
    "Daily Active Users (DAU)"
)

# DataFrame do Monthly Active Users (MAU)
df_mau = load_metric("mau.sql", engine)

# Gráfico do MAU em D28
graph(df_mau, 
      "dtRef", 
      "MAU", 
      "purple", 
      "Monthly Active Users (MAU) - D28"
)
```
## Preparação dos Dados
falar sobre

## Modelagem
SEMMA

## Avaliação 

## Deploy

## What I Learned
aaaa

## Insights

## Challenges I Faced

## Conclusion


## Ações

- Métricas gerais do TMW;
- Definição do Ciclo de Vida dos usuários;
- Análise de Agrupamento dos diferentes perfís de usuários;
- Criar modelo de Machine Learning que detecte a perda ou ganho de engajamento;
- Incentivo por meio de pontos para usuários mais engajados;

## Etapas

- Entendimento do negócio;
- Extração dos dados;
- Entendimento dos dados;
- Definição das variáveis;
- Criação das Feature Stores;
- Treinamento do modelo;
- Registro do modelo no MLFlow;
- Criação de App para Inferência em Tempo Real;
- Integração com Ecossistema TMW;

