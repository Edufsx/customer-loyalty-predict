# %%
import pandas as pd 
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import cluster, preprocessing

# Função auxiliar para carregar consultas a partir arquivos
def import_query(path):
    with open(path) as open_file:
        return open_file.read()

# Cria conexão com o banco SQLite
engine = sqlalchemy.create_engine(
    "sqlite:///../../data/loyalty-system/database.db"
)

# Importa a consulta de frequência e valor
query = import_query("frequencia_valor.sql")

# Executa a consulta considerando uma data de referência
df = pd.read_sql(query.format(date='2025-09-01'), engine)

# Visualização inicial da relação entre frequência e valor
plt.plot(df["qtdeFrequencia"], df["qtdePontosPos"], 'o')
plt.xlabel("Frequência")
plt.ylabel("Valor")
plt.title("Frequência (Dias Ativos D28) x Valor (Pontos Positivos D28)")
plt.grid(True)
plt.savefig("../../img/freq_value_scatter.png")

# %%
# Remoção do Outlier para evitar distorção do agrupamento
df = df[df["qtdePontosPos"] < 4000]

# Padroniza os dados para mesma escala (necessário para agrupamento)   
minmax = preprocessing.MinMaxScaler(feature_range=(0,1))
X = minmax.fit_transform(df[["qtdeFrequencia", "qtdePontosPos"]])

# Aplicação do algoritmo KMeans para segmentação de clientes
kmean = cluster.KMeans(n_clusters=5,
                       random_state=42, 
                       max_iter=1000)
kmean.fit(X)

# Atribui o agrupamento correspondente a cada cliente
df["cluster_calc"] = kmean.labels_

# Distribuição de clientes por agrupamento 
qtde_dados_grupo = df.groupby(by="cluster_calc")["IdCliente"].count()
print(qtde_dados_grupo)

# Visualização dos agrupamento obtidos pelo algoritmo
sns.scatterplot(data=df, 
                x="qtdeFrequencia",
                y="qtdePontosPos",
                hue="cluster_calc",
                palette="deep")
plt.xlabel("Frequência")
plt.ylabel("Valor")
plt.title("Frequência D28 x Valor D28 - Agrupado")
plt.grid()
plt.savefig("../../img/cluster_freq_value_scatter.png")
# %%
# Visualização dos corte manuais para construção dos segmentos
sns.scatterplot(data=df, 
                x="qtdeFrequencia",
                y="qtdePontosPos",
                hue="cluster_calc",
                palette="deep")

# Linhas de separação baseadas na distribuição dos dados apresentadas pelo algoritmo
plt.hlines(y=1500, xmin=0, xmax=25, colors="black")
plt.hlines(y=750, xmin=0, xmax=25, colors="black")
plt.vlines(x=4, ymin=0, ymax=750, colors="black")
plt.vlines(x=10, ymin=0, ymax=3000, colors="black")

plt.grid()
plt.show()