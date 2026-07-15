"""Valida o pipeline completo e imprime métricas finais."""
import warnings
from pathlib import Path

import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

df = pd.read_csv("data/manutencao_preditiva.csv")
df = df.drop_duplicates()

cols_imputar = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
]
for col in cols_imputar:
    df[col] = df[col].fillna(df[col].median())

df["potencia"] = df["velocidade_rotacao_rpm"] * df["torque_nm"]

feature_cols = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
    "potencia",
    "tipo",
]
X = pd.get_dummies(df[feature_cols], columns=["tipo"], drop_first=False)
y = df["falha_maquina"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train_bal, y_train_bal = SMOTE(random_state=42).fit_resample(X_train, y_train)

continuous_cols = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
    "potencia",
]

X_train_knn = X_train_bal.copy()
X_test_knn = X_test.copy()
scaler = StandardScaler()
X_train_knn[continuous_cols] = scaler.fit_transform(X_train_bal[continuous_cols])
X_test_knn[continuous_cols] = scaler.transform(X_test[continuous_cols])

print("=== KNN ===")
for k in [3, 5, 7]:
    m = KNeighborsClassifier(n_neighbors=k).fit(X_train_knn, y_train_bal)
    print(f"K={k} train={accuracy_score(y_train_bal, m.predict(X_train_knn)):.4f} test={accuracy_score(y_test, m.predict(X_test_knn)):.4f}")

print("\n=== TREE ===")
for depth in [3, 5, None]:
    m = DecisionTreeClassifier(max_depth=depth, random_state=42).fit(X_train_bal, y_train_bal)
    print(f"depth={depth} train={accuracy_score(y_train_bal, m.predict(X_train_bal)):.4f} test={accuracy_score(y_test, m.predict(X_test)):.4f}")
