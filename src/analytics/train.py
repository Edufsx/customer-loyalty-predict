# %%
import pandas as pd
import sqlalchemy
import mlflow
import matplotlib.pyplot as plt
from feature_engine import (
    selection, 
    imputation, 
    encoding
)
from sklearn import (
    model_selection,
    tree, 
    metrics, 
    ensemble, 
    pipeline
)

# Configuração MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment(experiment_id=1)

# Exibe todas as colunas e linhas (análise)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Conexão com o banco de dados analítico
con = sqlalchemy.create_engine("sqlite:///../../data/analytics/database.db")

# %%
# --- Data Load ---

# Carrega Analytical Base Table (ABT)
df = pd.read_sql("SELECT * FROM abt_fiel", con)
df.head()

#%%
# --- SAMPLE: Out Of Time (OOT) ---

# Separa amostra mais recente para validação temporal (OOT)
df_oot = df[df["dtRef"] >= "2025-10-01"].reset_index(drop=True)

#%%
# --- SAMPLE: Train/Test ---

# Define target e features
target = "flFiel"
features = df.columns.to_list()[3:]

# Remove OOT para manter dados para Treino e Teste
df_train_test = df[df["dtRef"] < "2025-10-01"].reset_index(drop=True)

# Matriz de features
X = df_train_test[features]
# Vetor do target
y = df_train_test[target]

#%%
# --- SAMPLE: Train and Test SPLIT ---

# Divide dados em Treino (80%) e Teste (20%)
X_train, X_test, y_train, y_test =  model_selection.train_test_split(
    X, y,
    test_size= 0.2,
    random_state=42,
    # Mantém proporção do target
    stratify=y,
)

# Resumo das bases: quantidade e taxa do Target
print(f"Base Treino: {y_train.shape[0]} Unid. | Tx. Target: {100 * y_train.mean():.2f}%")
print(f"Base Teste: {y_test.shape[0]} Unid. | Tx. Target: {100 * y_test.mean():.2f}%")

#%%
# --- EXPLORE (EDA): Bivariate Analysis --- 

# Features Categóricas
cat_features = [
    'descLifeCycleAtual', 
    'descLifeCycleD28', 
    'descClusterAtual', 
    'descClusterD28'
]

# Features Numéricas
num_features = list(set(features) - set(cat_features))

# Cópia da Base de Treino com Target
df_train = X_train.copy()
df_train[target] = y_train.copy()

# Garante tipo Float para análise
df_train[num_features] = df_train[num_features].astype(float) 

# Mediana das features numéricas por classe do target
bivariada = df_train.groupby(target)[num_features].median().T

# Razão entre medianas = fiéis (classe 1) / não fiéis (classe 0)
bivariada['ratio'] = (bivariada[1] + 0.001) / (bivariada[0] + 0.001)

# Ordenada as features por poder de discriminação (razão entre medianas)
bivariada = bivariada.sort_values(by='ratio', ascending = False)
bivariada

#%%
# Taxa média do target por categoria
print(df_train.groupby('descLifeCycleAtual')[target].mean())
print(df_train.groupby('descLifeCycleD28')[target].mean())
print(df_train.groupby('descClusterAtual')[target].mean())
print(df_train.groupby('descClusterD28')[target].mean())

# %%
# --- MODIFY: Type Handling and Features Selection --- 

# Garante tipo numérico adequado para modelagem
X_train[num_features] = X_train[num_features].astype(float) 

# Identifica Features sem poder discriminativo (ratio = 1) 
to_remove = bivariada[bivariada['ratio'] == 1].index.tolist()

# Configura remoção de features sem poder discriminativo 
drop_features = selection.DropFeatures(to_remove)

#%%
# --- EXPLORE (EDA): Missing Values ---

# Proporção de valores faltantes em cada feature numérica 
s_na = (X_train[list(set(num_features) - set(to_remove)) + cat_features]
        .isna()
        .mean()
)

# Filtra apenas as features com valores faltantes
s_na = s_na[s_na>0] 

s_na

# %%
# --- MODIFY: Missing Handling ---

# Features que a ausência de valor significa 0
fill_0 = [
    'github2025', 
    'python2025', 
    'qtdeCursosCompletos',
    'qtdeFrequencia',
    'avgFreqGrupo'
]

# Imputação com 0 
imput_0 = imputation.ArbitraryNumberImputer(arbitrary_number=0, 
                                            variables=fill_0)

# Imputação com 1
imput_1 = imputation.ArbitraryNumberImputer(arbitrary_number=1, 
                                            variables=['ratioFreqGrupo'])


# Imputação de categoria (usuários com apenas 1 transação na base)
imput_cat = imputation.CategoricalImputer(
    fill_value='Missing', 
    variables=cat_features
)

# Imputação com valor alto (intervalo indefinido / usuário nunca voltou)
imput_1000 = imputation.ArbitraryNumberImputer(
    arbitrary_number=1000, 
    variables=["avgIntervaloDiasVida", 
               "avgIntervaloDiasD28",
               "qtdDiasUltimaAtiv"]
)

# --- MODIFY: Encoding ---

# One-hot encoding para features categóricas
onehot = encoding.OneHotEncoder(variables=cat_features)

#%%
# --- MODEL ---

# Modelos candidatos
models = {
    "decision_tree": tree.DecisionTreeClassifier(random_state=42),
    "random_forest": ensemble.RandomForestClassifier(random_state=42, n_jobs=1),
    "adaboost": ensemble.AdaBoostClassifier(random_state=42),
}

# Busca de Hiperparâmetros por modelo
grid_options = {
    "decision_tree": {
        "max_depth": [3, 5, 8, 12, None],
        "min_samples_leaf" : [1, 10, 50],
        "min_samples_split": [2, 10, 30],
        },
    "random_forest": {
        "n_estimators": [100, 300, 500],
        "max_depth": [5, 10, 20, None],
        "min_samples_leaf": [1, 5, 10, 20],
    },
    "adaboost": {
        "n_estimators" : [100, 200, 400, 500, 1000],
        "learning_rate" : [0.01, 0.1, 0.2, 0.5, 0.9],
    },
}

# Seleciona modelo e respectiva busca de Hiperparâmetros 
model_name = "adaboost"
model = models[model_name]
params = grid_options[model_name]

# Busca de Hiperparâmetros com validação cruzada
grid = model_selection.GridSearchCV(
    model,
    param_grid=params,
    cv=3,
    scoring="roc_auc", # Métrica de avaliação dos modelos
    refit=True, # Treina o modelo  com melhores parâmetros no final
    verbose=3,
    n_jobs=-1
)

# %%
# --- MODEL and ASSES: Training Pipeline and Evaluation ---

# Executa experimento no MLflow
with mlflow.start_run() as r:

    # Ativa logging automático (parâmetros, métricas e modelo)
    mlflow.sklearn.autolog()
    
    # Pipeline de transformações + Modelo
    model_pipeline = pipeline.Pipeline(steps=[
        ('Remocao de Features', drop_features),
        ('Imputacao de Zeros', imput_0),
        ('Imputacao de um', imput_1),
        ('Imputacao categorica', imput_cat),
        ('Imputacao de 1000', imput_1000),
        ('OneHot Encoding', onehot),
        ('Algoritmo', grid),
    ])

    # --- MODEL ---
    # Treinamento do Pipeline
    model_pipeline.fit(X_train, y_train)

    # --- ASSESS: Train ---

    # Predições na base de Treino
    y_pred_train = model_pipeline.predict(X_train)
    y_proba_train = model_pipeline.predict_proba(X_train)

    # Métricas de Treino 
    acc_train = metrics.accuracy_score(y_train, y_pred_train)
    auc_train = metrics.roc_auc_score(y_train, y_proba_train[:,1])
    print("Acurácia Treino:", acc_train)
    print("AUC Treino:", auc_train)

    # --- ASSESS: Test ---
    # Predições na base de Teste
    y_pred_test = model_pipeline.predict(X_test)
    y_proba_test = model_pipeline.predict_proba(X_test)

    # Métricas de Teste
    acc_test = metrics.accuracy_score(y_test, y_pred_test)
    auc_test = metrics.roc_auc_score(y_test, y_proba_test[:,1])

    print("Acurácia Teste:", acc_test)
    print("AUC Teste:", auc_test)

    # --- BASELINE (predição constante) ---

    # Predição constante (todos como 0)
    y_pred_chute = pd.Series([0]*y_test.shape[0])

    # Probabilidade constante (média do target)
    y_proba_chute = pd.Series([y_train.mean()]*y_test.shape[0])

    # Métricas Baseline
    acc_chute = metrics.accuracy_score(y_test, y_pred_chute)
    auc_chute = metrics.roc_auc_score(y_test, y_proba_chute)

    print("Acurácia chute:", acc_chute)
    print("AUC chute:", auc_chute)

    # --- ASSESS: Out of Time (OOT)
    
    # Base OOT (dados futuros)
    X_oot = df_oot[features]
    y_oot = df_oot[target]

    # Predições na base OOT
    y_pred_oot = model_pipeline.predict(X_oot)
    y_proba_oot = model_pipeline.predict_proba(X_oot)

    # Métricas OOT 
    acc_oot = metrics.accuracy_score(y_oot, y_pred_oot)
    auc_oot = metrics.roc_auc_score(y_oot, y_proba_oot[:,1])

    print("Acurácia OOT:", acc_oot)
    print("AUC OOT:", auc_oot)

    # Log manual de métricas no MLflow 
    mlflow.log_metrics({
        "acc_train" : acc_train,
        "auc_train" : auc_train,
        "acc_test" : acc_test,
        "auc_test" : auc_test,
        "acc_oot" : acc_oot,
        "auc_oot" : auc_oot,
    })
    
    # --- ROC CURVE ---

    # Calcula curvas ROC nas bases de treino, teste e OOT
    roc_train = metrics.roc_curve(y_train, y_proba_train[:,1])
    roc_test = metrics.roc_curve(y_test, y_proba_test[:,1])
    roc_oot = metrics.roc_curve(y_oot, y_proba_oot[:,1])

    # Plot das curvas
    plt.figure(dpi=100)

    plt.plot(roc_train[0], roc_train[1])
    plt.plot(roc_test[0], roc_test[1])
    plt.plot(roc_oot[0], roc_oot[1])

    plt.legend([
        f"Treino: {auc_train:.4f}",
        f"Teste: {auc_test:.4f}",
        f"OOT: {auc_oot:.4f}"]
    )
    
    # Linha base 
    plt.plot([0,1], [0,1], '--', color='black')

    plt.grid(True)
    plt.title("Curva ROC")
    plt.savefig("curva_roc.png")
    
    # Save e registra como artefato no MLflow  
    mlflow.log_artifact('curva_roc.png')
# %%
# --- FEATURE IMPORTANCE ---

# Recupera melhor modelo após GridSearch
best_model = model_pipeline.named_steps['Algoritmo'].best_estimator_

# Aplica transformações do pipeline sem o modelo
X_transformed = model_pipeline[:-1].transform(X_train)

# Nome das features após encoding
features_names = X_transformed.columns.tolist()

# Calcula importância das features
feature_importance = pd.Series(
    best_model.feature_importances_, 
    index=features_names
).sort_values(ascending=False)

feature_importance