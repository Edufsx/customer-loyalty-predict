#%%
from flask import Flask, request
import mlflow 
import pandas as pd

# Conexão com o servidor do MLflow
mlflow.set_tracking_uri("http://localhost:5000")

# Busca versões registradas do modelo em produção
versions = mlflow.search_model_versions(filter_string="name='model_fiel'")

# Identifica a versão mais recente disponível
last_version = max([int(i.version) for i in versions])

# Carrega última versão registrada do modelo
model = mlflow.sklearn.load_model(f"models:///model_fiel/{last_version}")
#%%
# Inicializa a aplicação Web
app = Flask(__name__)

# Endpoint para monitoramento da API
@app.route("/health_check")
def health_check():
    return{"status" : "ok"}

# Endpoint de predição para um único cliente
@app.route("/predict", methods=['POST'])
def predict():
    
    try:
        # Lê dados json da requisição e os transforma em dicionário (um cliente)
        data = request.json["data"]

        # Converte entrada para DataFrame (formato esperado pelo modelo)
        df = pd.DataFrame([data])

        # Seleciona somente features utilizadas no treinamento
        X = df[model.feature_names_in_]

        # Realiza a predição de probabilidade de fidelidade
        predict = model.predict_proba(X)[:,1]

        # Retorna ID do cliente e respectivo Score
        return { "idCliente" : data["idCliente"], "score" : float(predict[-1])}
    
    # Tratamento de erro para entrada de dados incorreta
    except Exception as err:
        return {"erro" : "formato incorreto de dados"}, 400
    
# Endpoint de predição para vários clientes
@app.route("/predict_many", methods=['POST'])
def predict_many():
    try:
        # Lê dados json da requisição (vários clientes)
        data = request.json["data"]

        # Converte entrada para DataFrame 
        df = pd.DataFrame(data)

        # Seleciona somente features utilizadas no treinamento
        X = df[model.feature_names_in_]

        # Gera Score de fidelização para cada cliente
        df['score'] = model.predict_proba(X)[:,1]
        
        # Salva as predições em um dicionário e retorna ao usuário
        resp = df[['score', 'idCliente']].to_dict(orient='records')
        return {"result": resp}
    
    # Tratamento de erro para entrada de dados incorreta
    except Exception as err:
        return {"erro" : "formato incorreto de dados"}, 400