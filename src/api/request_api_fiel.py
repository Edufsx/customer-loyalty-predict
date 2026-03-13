# %%
import requests
import sqlalchemy
import pandas as pd
import json

db_path = r'C:\Users\edudu\OneDrive\Área de Trabalho\Cursos Ciência de Dados\Projetos para o GitHub\loyalty-predict\data\analytics\database.db'

con = sqlalchemy.create_engine(f"sqlite:///{db_path}")
#%%
data = pd.read_sql("SELECT * FROM fs_all LIMIT 1", con)
data = {"data" : data.to_dict(orient='records')[0]}

resp = requests.post("http://localhost:5001/predict", json=data)
resp.json()
# %%
data = pd.read_sql("SELECT * FROM fs_all LIMIT 10", con).to_json(orient='records')

data = {"data": json.loads(data)}

# data = {"data" : data.to_dict(orient='records')}
resp = requests.post("http://localhost:5001/predict_many", json=data)
resp.json()