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
  
  # Abre, salva o conteúdo do arquivo contendo a consulta SQL e o fecha
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