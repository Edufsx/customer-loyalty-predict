#%%
# PySpark seria melhor, demora muito assim
import pandas as pd
import sqlalchemy
import datetime
from tqdm import tqdm
import argparse

def date_range(start, stop):
    dates = []
    while start <= stop:
        dates.append(start)
        dt_start = datetime.datetime.strptime(start, '%Y-%m-%d') + datetime.timedelta(days=1)
        start = datetime.datetime.strftime(dt_start, '%Y-%m-%d')
    return dates

def import_query(path):
    with open(path, encoding="utf-8") as open_file:
        query = open_file.read()
    return query
    
def exec_query(table, db_origin, db_target, dt_start, dt_stop, mode='append'):
    engine_app = sqlalchemy.create_engine(
        f"sqlite:///../../data/{db_origin}/database.db"
    )
    engine_analytical = sqlalchemy.create_engine(
        f"sqlite:///../../data/{db_target}/database.db"
    )

    query = import_query(f"{table}.sql")
    dates = date_range(dt_start, dt_stop)

    for i in tqdm(dates):

        query_format = query.format(date=i)
        df = pd.read_sql(query_format, engine_app)

        with engine_analytical.begin() as con:

            if mode == "append":
                try:
                    query_delete = f"DELETE FROM {table} WHERE dtRef = date('{i}', '-1 day')"
                    con.execute(sqlalchemy
                                .text(query_delete))
                except Exception as err:
                    print(err)
            
            df.to_sql(table, 
                    con, 
                    index=False, 
                    if_exists=mode)
        
def main():

    # valores de input na chamada do nosso script
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_origin", 
                        choices=['loyalty-system', 'education-platform', 'analytics'], 
                        default='loyalty-system')
    
    parser.add_argument("--db_target", choices=['analytics'], 
                        default='analytics')
    parser.add_argument("--table", type=str, 
                        help='Tabela que será processada com o mesmo nome do arquivo.')
    parser.add_argument("--start", default="2024-03-01")

    stop = datetime.datetime.now().strftime("%Y-%m-%d")
    parser.add_argument("--stop", type=str, default=stop)
    
    parser.add_argument("--mode", type=str, default='append', choices=['append', 'replace'])


    args = parser.parse_args()

    exec_query(args.table, args.db_origin, args.db_target, args.start, args.stop, args.mode)

# Quando o script é o primeiro a ser executado o nome dele está como main, então
# ele passa por esse if e executa o código
# Se eu quiser importar essas funções para outro script ele não vai executar esse programa
if __name__ == "__main__":
    main()