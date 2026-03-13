# %%
import pandas as pd 
import sqlalchemy
import matplotlib.pyplot as plt

engine = sqlalchemy.create_engine(
    "sqlite:///../../data/loyalty-system/database.db"
)

def import_query(path):
    with open(path) as open_file:
        return open_file.read()
    
query = import_query("frequencia_valor.sql")

# %%
df = pd.read_sql(query, engine)

df = df[df["qtdePontosPos"] < 4000]

# %%
plt.plot(df["qtdeFrequencia"], df["qtdePontosPos"], 'o')
plt.grid(True)
plt.xlabel("frequencia")
plt.ylabel("valor")
plt.show()

#%%
from sklearn import cluster, preprocessing

# PADRONIZANDO para clusterizar 
minmax = preprocessing.MinMaxScaler()
X = minmax.fit_transform(df[["qtdeFrequencia", "qtdePontosPos"]])

kmean = cluster.KMeans(n_clusters=5, 
                       random_state=42, 
                       max_iter=1000)
kmean.fit(X)

df["cluster_calc"] = kmean.labels_
df.groupby(by="cluster_calc")["idCliente"].count()

#%%
import seaborn as sns

# É dificil explicar para o time de negócio o porque estamos agrupando desse jeito
# Uma bolinha laranja ta bem perto da azul, pq ela é de um time e não de outro?
# Na hora de plotar eu não uso a normalização para interpretar
sns.scatterplot(data=df, 
                x="qtdeFrequencia",
                y="qtdePontosPos",
                hue="cluster_calc",
                palette="deep")

plt.hlines(y=1500, xmin=0, xmax=25, colors="black")
plt.hlines(y=750, xmin=0, xmax=25, colors="black")

plt.vlines(x=4, ymin=0, ymax=750, colors="black")
plt.vlines(x=10, ymin=0, ymax=3000, colors="black")
plt.grid()

#%%
sns.scatterplot(data=df, 
                x="qtdeFrequencia",
                y="qtdePontosPos",
                hue="cluster",
                palette="deep")
plt.grid()