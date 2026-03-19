# %%
import dotenv
from kaggle import api
import shutil

# Carrega credenciais de acesso do Kaggle a partir do arquivo .env
dotenv.load_dotenv('../../.env')

# Lista de Datasets utilizados no projeto (fonte do Kaggle)
datasets = [
    'teocalvo/teomewhy-loyalty-system',
    'teocalvo/teomewhy-education-platform'
]

for d in datasets:
     
    # Baixa arquivo do Dataset
    api.dataset_download_file(d, 'database.db')
    
    # Extrai nome do Dataset para salvar localmente 
    dataset_name = d.split("teomewhy-")[-1]

    # Define o caminho de destino 
    path = f'../../data/{dataset_name}/database.db'

    # Move o Dataset para o diretório do projeto
    shutil.move('database.db', path)