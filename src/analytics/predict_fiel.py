# %%
""" 
Pipeline de scoring (execução offline, sem API):
1. Carrega modelo mais recente registrado no MLflow;
2. Extrai dados da feature store (fs_all);
3. Gera probabilidade de fidelização dos usuários;
4. Persiste resultados para consumo de outras aplicações;
"""

import pandas as pd
import sqlalchemy
import mlflow

# Conexão com o banco analítico
con = sqlalchemy.create_engine(
    "sqlite:///data/analytics/database.db"
) 

#%%
# Conexão com o servidor do MLflow
mlflow.set_tracking_uri("http://localhost:5000")

# Busca versões registradas do modelo em produção
versions = mlflow.search_model_versions(filter_string="name='model_fiel'")

# Identifica a versão mais recente do modelo
last_version = max([int(i.version) for i in versions])

# Carrega última versão registrada do modelo
model = mlflow.sklearn.load_model(f"models:///model_fiel/{last_version}")

#%%
# Dados mais recentes para predição do score
data = pd.read_sql("SELECT * FROM fs_all", con)

# Gera Probabilidade de fidelidade dos usuários de acordo com o modelo
predict = model.predict_proba(data[model.feature_names_in_])[:,1]
data['predictFiel'] = predict 

# Seleciona colunas relevantes para outras aplicações
data = data[["dtRef", "idCliente", "predictFiel"]]
#%%
# Persistir predições no banco analítico para consumo de outras aplicações
data.to_sql(
    "score_fiel", 
    con, 
    index=False, 
    if_exists='replace'
)