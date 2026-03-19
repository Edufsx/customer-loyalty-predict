#%%
import pandas as pd
import sqlalchemy
import datetime
from tqdm import tqdm
import argparse

def date_range(
        start:str, 
        stop:str
) -> list:
    """
    Gera uma lista de datas entre start e stop (intervalo inclusivo).

    Parâmetros:
        start (str): Data inicial no formato YYYY-MM-DD
        stop (str): Data final no formato YYYY-MM-DD

    Retorno:
        list: Lista de datas no formato YYYY-MM-DD
    """

    dates = []

    while start <= stop:
        
        # Adiciona a data atual à lista
        dates.append(start)

        # Incrementa 1 dia na data atual
        dt_start = datetime.datetime.strptime(start, '%Y-%m-%d') + datetime.timedelta(days=1)

        # Atualiza a variável de controle do loop
        start = datetime.datetime.strftime(dt_start, '%Y-%m-%d')
    
    return dates

# Função auxiliar para carregar consultas a partir arquivos
def import_query(path: str) -> str:
    """
    Salva uma Query contida em um arquivo SQL.
   
    Parâmetros:
        path (str): caminho do arquivo que contém a Query
    """

    with open(path, encoding="utf-8") as open_file:
        query = open_file.read()
    return query

def exec_query(
        table: str,
        db_origin: str, 
        db_target: str, 
        dt_start: str, 
        dt_stop: str, 
        mode='append'
):
    """
    Executa uma query SQL por intervalo de datas em um banco de origem
    e salva o resultado em outro banco analítico.

    Parâmetros:
        table (str): nome da tabela/query
        db_origin (str): banco de origem
        db_target (str): banco de destino (analítico)
        dt_start (str): data inicial (YYYY-MM-DD)
        dt_stop (str): data final (YYYY-MM-DD)
        mode (str): modo de escrita no destino ('append', 'replace')
    """

    # Conexões com banco de origem e de destino   
    engine_app = sqlalchemy.create_engine(
        f"sqlite:///../../data/{db_origin}/database.db"
    )
    engine_analytical = sqlalchemy.create_engine(
        f"sqlite:///../../data/{db_target}/database.db"
    )
    
    # Consulta base
    query = import_query(f"{table}.sql")
    
    # Intervalos de datas a serem processados
    dates = date_range(dt_start, dt_stop)

    # Loop por data de referência
    for i in tqdm(dates):

        # Formata a consulta colocando a data atual de i
        query_format = query.format(date=i)
        # Executa a consulta e extrai os dados em um DataFrame 
        df = pd.read_sql(query_format, engine_app)

        # Abre uma conexão com o banco de dados de destino
        with engine_analytical.begin() as con:

            # Se o modo escolhido for append, deleta as datas existentes
            if mode == "append":
                try:
                    # Remove dados da data anterior para evitar duplicidade
                    query_delete = f"DELETE FROM {table} WHERE dtRef = date('{i}', '-1 day')"
                    con.execute(sqlalchemy
                                .text(query_delete))
                except Exception as err:
                    print(err)
            
            # Salva as informações no banco de destino 
            df.to_sql(
                table, 
                con, 
                index=False, 
                if_exists=mode
            )
   
def main():
    """
    Ponto de entrada do script.

    Permite executar queries por linha de comando, definindo
    origem, destino, tabela e intervalo de datas.
    """
    
    # Valores de input para executar o script
    parser = argparse.ArgumentParser()

    # Banco Origem
    parser.add_argument(
        "--db_origin", 
        choices=['loyalty-system', 'education-platform', 'analytics'], 
        default='loyalty-system'
    )
    
    # Banco Analítico
    parser.add_argument(
        "--db_target", 
        choices=['analytics'],
        default='analytics'
    )
    
    # Nome da tabela (mesmo nome do arquivo SQL)
    parser.add_argument(
        "--table", 
        type=str, 
        help='Tabela que será processada com o mesmo nome do arquivo.'
    )
    
    # Data de inicio da consulta
    parser.add_argument(
        "--start", 
        default="2024-03-01"
    )

    # Data final com o padrão sendo hoje
    stop = datetime.datetime.now().strftime("%Y-%m-%d")
    parser.add_argument(
        "--stop",
        type=str,
        default=stop
    )
    
    # Modo de escrita no banco analítico
    parser.add_argument(
        "--mode",
        type=str,
        default='append',
        choices=['append', 'replace']
    )

    args = parser.parse_args()

    # Dispara a execução das consultas no intervalo de datas
    exec_query(
        args.table, 
        args.db_origin, 
        args.db_target, 
        args.start, 
        args.stop, 
        args.mode
    )

# Executa o script apenas quando chamado diretamente
if __name__ == "__main__":
    main()