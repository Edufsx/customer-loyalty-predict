# %%
import pandas as pd
import sqlalchemy 
from sklearn import (
    model_selection,
    tree, 
    metrics, 
    ensemble, 
    pipeline
)
from feature_engine import (
    selection, 
    imputation, 
    encoding
)
import mlflow
import matplotlib.pyplot as plt

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment(experiment_id=1)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

con = sqlalchemy.create_engine("sqlite:///../../data/analytics/database.db")

# %%
# SAMPLE - IMPORT dos dados

df = pd.read_sql("SELECT * FROM abt_fiel", con)

#%%
# Sample - oot

df_oot = df[df["dtRef"] == df["dtRef"].max()].reset_index(drop=True)

#%%
# Sample Test e Treino
target = "flFiel"
features = df.columns.to_list()[3:]

df_train_test = df[df["dtRef"] < df["dtRef"].max()].reset_index(drop=True)

X = df_train_test[features]
y = df_train_test[target]

#%%
# Sample - Train and Test SPLIT

X_train, X_test, y_train, y_test =  model_selection.train_test_split(
    X, y,
    test_size= 0.2,
    random_state=42,
    stratify=y,
)

print(f"Base Treino: {y_train.shape[0]} Unid. | Tx. Target: {100 * y_train.mean():.2f}%")
print(f"Base Teste: {y_test.shape[0]} Unid. | Tx. Target: {100 * y_test.mean():.2f}%")


# %%
# Explore - missing
# Que número iremos colocar para cada variável
s_nas = X_train.isna().mean()
s_nas = s_nas[s_nas > 0]
s_nas


#%%
# Explore
# Colocar mais carinho nessa parte - fazer mais analises estatisticas
# Análise Bivariada

cat_features = ['descLifeCycleAtual', 'descLifeCycleD28']

num_features = list(set(features) - set(cat_features))

df_train = X_train.copy()
df_train[target] = y_train.copy()

df_train[num_features] = df_train[num_features].astype(float) 

bivariada = df_train.groupby(target)[num_features].median().T

bivariada['ratio'] = (bivariada[1] + 0.001) / (bivariada[0] + 0.001)

bivariada = bivariada.sort_values(by='ratio', ascending = False)
# df_train.groupby('descLifeCycleAtual')[target].mean()
# df_train.groupby('descLifeCycleD28')[target].mean()

# %%
# Modify - DROP
X_train[num_features] = X_train[num_features].astype(float) 

to_remove = bivariada[bivariada['ratio'] == 1].index.tolist()

drop_features = selection.DropFeatures(to_remove)

#%%
# Análise Descritiva
""" 
s_na = X_train_transform.isna().mean()
s_na[s_na>0] 
"""

# %%
# Modify - missing

fill_0 = ['github2025', 'python2025', 'sql2020', 'qtdeCursosCompletos']

imput_0 = imputation.ArbitraryNumberImputer(arbitrary_number=0, 
                                            variables=fill_0)

imput_new = imputation.CategoricalImputer(
    fill_value='Nao-Usuario', 
    variables=['descLifeCycleD28']
)

imput_1000 = imputation.ArbitraryNumberImputer(
    arbitrary_number=1000, 
    variables=["avgIntervaloDiasVida", 
               "avgIntervaloDiasD28",
               "qtdDiasUltimaAtiv"]
)

# Modify - onehot

onehot = encoding.OneHotEncoder(variables=cat_features)


#%%
# Model

# Cross Validation (CV) -> Apenas para encontrar os melhores hiperparametros
# Depois coloca esses parametros na base inteira

model = tree.DecisionTreeClassifier(random_state=42)
# model = ensemble.RandomForestClassifier(random_state=42, n_jobs=1)

# model = ensemble.AdaBoostClassifier(random_state=42,)
# "learning_rate" : [0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 0.9, 0.9 ]
# "n_estimators" : [100, 200, 400, 500, 1000],

# Grid
params = {
    
    "min_samples_leaf" : [10, 20, 30, 50, 75, 100],
}

grid = model_selection.GridSearchCV(model,
                                    param_grid=params,
                                    cv=3,
                                    scoring="roc_auc",
                                    refit=True,
                                    verbose=3,
                                    n_jobs=-1)
# %%
# Pipeline
with mlflow.start_run() as r:

    mlflow.sklearn.autolog()
    
    model_pipeline = pipeline.Pipeline(steps=[
        ('Remocao de Features', drop_features),
        ('Imputacao de Zeros', imput_0),
        ('Imputacao de Nao-usuario', imput_new),
        ('Imputacao de 1000', imput_1000),
        ('OneHot Encoding', onehot),
        ('Algoritmo', grid),
    ])


    model_pipeline.fit(X_train, y_train)

    """ 
    Hard Coding
    X_train_transform = drop_features.fit_transform(X_train)
    X_train_transform = imput_0.fit_transform(X_train_transform)
    X_train_transform = imput_new.fit_transform(X_train_transform)
    X_train_transform = imput_1000.fit_transform(X_train_transform)
    X_train_transform = onehot.fit_transform(X_train_transform)
    model.fit(X_train_transform, y_train)
    """

    # Assess - Métricas

    # Peguei o dado que eu treinei o modelo e quero ver se aprendeu algo
    # Lista de exercício com gabarito
    y_pred_train = model_pipeline.predict(X_train)
    y_proba_train = model_pipeline.predict_proba(X_train)

    acc_train = metrics.accuracy_score(y_train, y_pred_train)
    auc_train = metrics.roc_auc_score(y_train, y_proba_train[:,1])

    # OVERFITT NA BASE DE TREINO

    print("Acurácia Treino:", acc_train)
    print("AUC Treino:", auc_train)

    # A Métrica de Acurácia não é uma boa métrica
    """ # TEM QUE SER SÓ TRANSFORM, não usar informações novas, só o que já fiz
    # em treinamento
    X_test_transform = drop_features.transform(X_test)
    X_test_transform = imput_0.transform(X_test_transform)
    X_test_transform = imput_new.transform(X_test_transform)
    X_test_transform = imput_1000.transform(X_test_transform)
    X_test_transform = onehot.transform(X_test_transform)
    """

    y_pred_test = model_pipeline.predict(X_test)
    y_proba_test = model_pipeline.predict_proba(X_test)

    acc_test = metrics.accuracy_score(y_test, y_pred_test)
    auc_test = metrics.roc_auc_score(y_test, y_proba_test[:,1])

    print("Acurácia Teste:", acc_test)
    print("AUC Teste:", auc_test)

    # Chutando tudo igual a zero
    # BASELINE para a CURVA ROC
    y_pred_fodase = pd.Series([0]*y_test.shape[0])

    # Colocar todo mundo com a mesma probabilidade sendo a média da minha base
    y_proba_fodase = pd.Series([y_train.mean()]*y_test.shape[0])

    acc_fodase = metrics.accuracy_score(y_test, y_pred_fodase)
    auc_fodase = metrics.roc_auc_score(y_test, y_proba_fodase)

    print("Acurácia fodase:", acc_fodase)
    print("AUC fodase:", auc_fodase)


    # Assess Out Of Time
    X_oot = df_oot[features]
    y_oot = df_oot[target]

    """ X_oot_transform = drop_features.transform(X_oot)
    X_oot_transform = imput_0.transform(X_oot_transform)
    X_oot_transform = imput_new.transform(X_oot_transform)
    X_oot_transform = imput_1000.transform(X_oot_transform)
    X_oot_transform = onehot.transform(X_oot_transform)
    """

    y_pred_oot = model_pipeline.predict(X_oot)
    y_proba_oot = model_pipeline.predict_proba(X_oot)

    acc_oot = metrics.accuracy_score(y_oot, y_pred_oot)
    auc_oot = metrics.roc_auc_score(y_oot, y_proba_oot[:,1])

    print("Acurácia OOT:", acc_oot)
    print("AUC OOT:", auc_oot)

    mlflow.log_metrics({
        "acc_train" : acc_train,
        "auc_train" : auc_train,
        "acc_test" : acc_test,
        "auc_test" : auc_test,
        "acc_oot" : acc_oot,
        "auc_oot" : auc_oot,
    })
    
    # PLOT CURVA ROC
    roc_train = metrics.roc_curve(y_train, y_proba_train[:,1])
    roc_test = metrics.roc_curve(y_test, y_proba_test[:,1])
    roc_oot = metrics.roc_curve(y_oot, y_proba_oot[:,1])

    plt.figure(dpi=100)

    plt.plot(roc_train[0], roc_train[1])
    plt.plot(roc_test[0], roc_test[1])
    plt.plot(roc_oot[0], roc_oot[1])
    plt.legend([f"Treino: {auc_train:.4f}",
                f"Teste: {auc_test:.4f}",
                f"OOT: {auc_oot:.4f}"])
    plt.plot([0,1], [0,1], '--', color='black')
    plt.grid(True)
    plt.title("Curva ROC")
    plt.savefig("curva_roc.png")
    
    mlflow.log_artifact('curva_roc.png')
# %%
# Feature Importance

features_names = model_pipeline[:-1].transform(X_train.head(1)).columns.tolist()
feature_importance = pd.Series(model_pipeline[-1].feature_importances_, 
                               index=features_names)

# A importancia das variaveis está muito bem distribuído
feature_importance.sort_values(ascending=False)

# Data leakage 
# Todas as métricas independentes das bases
# Prever quem vai ganhar a corrida e usar o tempo de prova
# É variável resposta só que de um jeito diferente
# Probabilidade de uma pessoa cancelar plano de internet e usar a quantidade de vezes que ela ligou para cancelar

# ASSESS - Persistir Modelo

""" model_series = pd.Series({
    "model" : model_pipeline,
    "features" : X_train.columns.tolist(),
    "auc_train" : auc_train,
    "auc_test" : auc_test,
    "auc_oot" : auc_oot
})

model_series.to_pickle("model_fiel.pkl") """