# %%
from exec_query import exec_query
import datetime

# Define de referência (execução diária) 
now = datetime.datetime.now().strftime('%Y-%m-%d')

# --- Definição do Pipeline ---
# Cada passo contém os argumentos para uma execução de exec_query
steps = [
    # 
    {
        "table" : "life_cycle",
        "db_origin" : "loyalty-system",
        "db_target" : "analytics",
        "dt_start" : now,
        "dt_stop" : now,
        "mode" : "append",
    },
    {
        "table" : "fs_transacional",
        "db_origin" : "loyalty-system",
        "db_target" : "analytics",
        "dt_start" : now,
        "dt_stop" : now,
        "mode" : "append",
    },
    {
        "table" : "fs_education",
        "db_origin" : "education-platform",
        "db_target" : "analytics",
        "dt_start" : now,
        "dt_stop" : now,
        "mode" : "append",
    },
    {
        "table" : "fs_life_cycle",
        "db_origin" : "analytics",
        "db_target" : "analytics",
        "dt_start" : now,
        "dt_stop" : now,
        "mode" : "append",
    },
    {
        "table" : "fs_all",
        "db_origin" : "analytics",
        "db_target" : "analytics",
        "dt_start" : now,
        "dt_stop" : now,
        "mode" : "replace",
    },
]
# %%
# --- Execução do Pipeline ---
for s in steps:
    # Executa cada passo passando parâmetros com kwargs
    exec_query(**s)