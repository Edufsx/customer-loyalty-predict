# %%
import requests
import sqlalchemy
import pandas as pd
import json

# Caminho absoluto para base de dados analítica
db_path = r'C:\Users\edudu\OneDrive\Área de Trabalho\Cursos Ciência de Dados\Projetos para o GitHub\loyalty-predict\data\analytics\database.db'

# Conexão com o banco analítico
con = sqlalchemy.create_engine(f"sqlite:///{db_path}")
#%%
# --- Predição para um único cliente ----

# Seleciona dados de apenas um cliente
data = pd.read_sql("SELECT * FROM fs_all LIMIT 1", con)

# Estrutura dados no formato esperado pela API (json com chave "data")
data = {"data" : data.to_dict(orient='records')[0]}

# Envia requisição Post para a rota de predição individual
resp = requests.post("http://localhost:5001/predict", json=data)

# Visualizar resposta da API
resp.json()
# %%
# --- Predição para vários clientes ----

# Seleciona dados de vários clientes
data = pd.read_sql("SELECT * FROM fs_all LIMIT 30", con)

# Converte DataFrame no formato esperado pela API (json)
data = {"data": json.loads(data.to_json(orient='records'))}

# Envia requisição Post para a rota de predição em lote
resp = requests.post("http://localhost:5001/predict_many", json=data)

# Visualizar resposta da API
resp.json()