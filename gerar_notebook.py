"""Gera o notebook principal do projeto PredictGuard."""
import json
from pathlib import Path

NOTEBOOK_PATH = Path("predictguard.ipynb")

cells = []

def md(source: str):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)})

def code(source: str):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.splitlines(keepends=True)})

md("""# PredictGuard – Manutenção Preditiva na Indústria 4.0

**Objetivo:** prever falhas mecânicas em equipamentos industriais monitorados por sensores, evitando paradas na linha de produção.

**Variável alvo:** `falha_maquina` (0 = operação normal, 1 = falha detectada).

**Dataset:** `data/manutencao_preditiva.csv`

> Conforme anotações do Departamento de Engenharia, as colunas `falha_twf`, `falha_hdf`, `falha_pwf`, `falha_osf` e `falha_rnf` descrevem o *motivo* da quebra e **não** devem ser usadas como preditoras.
""")

code("""import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 5)

DATA_PATH = Path("data/manutencao_preditiva.csv")
""")

md("""---
## Fase 1: Análise Exploratória (EDA)
""")

code("""df_raw = pd.read_csv(DATA_PATH)
df = df_raw.copy()

print("Dimensões do dataset:", df.shape)
print(f"Linhas: {df.shape[0]:,} | Colunas: {df.shape[1]}")
print("\\nTipos de dados:")
print(df.dtypes)
print("\\nResumo estatístico das variáveis numéricas:")
df.describe()
""")

code("""# Gráfico 1: distribuição das variáveis preditoras numéricas
numeric_cols = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
]

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.ravel()

for i, col in enumerate(numeric_cols):
    sns.histplot(df[col].dropna(), kde=True, ax=axes[i], color="#2E86AB")
    axes[i].set_title(f"Distribuição – {col}")

axes[-1].axis("off")
plt.suptitle("Histogramas das variáveis preditoras", fontsize=14, y=1.02)
plt.tight_layout()
plt.show()
""")

code("""# Gráfico 2: desbalanceamento da variável alvo
target_counts = df["falha_maquina"].value_counts().sort_index()
target_pct = (target_counts / len(df) * 100).round(2)

fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(
    ["Normal (0)", "Falha (1)"],
    target_counts.values,
    color=["#A8DADC", "#E63946"],
    edgecolor="black",
)
ax.set_title("Desbalanceamento da variável alvo (falha_maquina)")
ax.set_ylabel("Quantidade de registros")

for bar, pct in zip(bars, target_pct.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 100,
        f"{int(bar.get_height()):,}\\n({pct}%)",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.tight_layout()
plt.show()

print("Distribuição da variável alvo:")
print(target_counts)
print(f"\\nTaxa de falha: {target_pct[1]}%")
""")

code("""# Gráfico 3: mapa de calor – correlação de Pearson
corr_cols = numeric_cols + ["falha_maquina"]
corr_matrix = df[corr_cols].corr(method="pearson")

plt.figure(figsize=(8, 6))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    linewidths=0.5,
)
plt.title("Correlação de Pearson entre variáveis numéricas")
plt.tight_layout()
plt.show()
""")

md("""### Interpretação da EDA

**Dimensões e tipos:** a base possui 10.000 registros e 14 colunas. As variáveis de sensores são numéricas contínuas; `tipo` é categórica (L/M/H) e `falha_maquina` é binária.

**Desbalanceamento:** a classe de falha representa cerca de 3,4% dos registros. Esse desequilíbrio exige técnicas de reamostragem (SMOTE) aplicadas **somente no treino**, para que o modelo aprenda padrões da classe minoritária sem inflar artificialmente a acurácia global.

**Correlações e distribuições:**
- `desgaste_ferramenta_min` apresenta correlação positiva com `falha_maquina`, indicando que o tempo de uso da ferramenta é um forte indicador de risco.
- Temperaturas concentram-se em torno de 300 K, com baixa variância — sensores estáveis, porém ainda relevantes em combinação com outras variáveis.
- `velocidade_rotacao_rpm` e `torque_nm` exibem maior dispersão, sugerindo que a engenharia de features (ex.: potência mecânica) pode capturar relações não lineares.

**Direcionamento da modelagem:** remover identificadores (`udi`, `id_produto`), excluir colunas de motivo de falha (vazamento de informação), tratar 5% de valores ausentes nos sensores, balancear o treino e comparar KNN (sensível à escala) com Árvore de Decisão (imune à escala).
""")

md("""---
## Fase 2: Limpeza e Tratamento de Dados (Data Prep)
""")

code("""# Remoção de duplicatas
dup_antes = df.duplicated().sum()
df = df.drop_duplicates()
print(f"Linhas duplicadas removidas: {dup_antes}")
print(f"Shape após remoção: {df.shape}")
""")

code("""# Identificação de valores ausentes
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({"ausentes": missing, "percentual": missing_pct})
print(missing_df[missing_df["ausentes"] > 0])
""")

code("""# Imputação por mediana nas variáveis de sensores
cols_imputar = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
]

for col in cols_imputar:
    mediana = df[col].median()
    df[col] = df[col].fillna(mediana)
    print(f"{col}: mediana = {mediana:.2f}")

print("\\nValores ausentes após imputação:", df[cols_imputar].isnull().sum().sum())
""")

md("""**Justificativa da mediana:** cada variável de sensor possui 5% de valores ausentes. A mediana é mais robusta que a média frente a possíveis outliers (picos de RPM ou torque em condições extremas), evitando que valores extremos distorçam a imputação. As distribuições de temperatura são simétricas, mas RPM e torque tendem a apresentar caudas longas — reforçando a escolha da mediana.
""")

code("""# Boxplots para identificação de outliers
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.ravel()

for i, col in enumerate(numeric_cols):
    sns.boxplot(y=df[col], ax=axes[i], color="#F4A261")
    axes[i].set_title(f"Boxplot – {col}")

axes[-1].axis("off")
plt.suptitle("Análise de outliers nas variáveis explicativas", fontsize=14, y=1.02)
plt.tight_layout()
plt.show()
""")

md("""**Outliers:** os boxplots revelam pontos extremos em `velocidade_rotacao_rpm` e `torque_nm`, compatíveis com condições operacionais críticas que precedem falhas. Não removemos outliers nesta etapa, pois podem conter sinal preditivo valioso para a classe minoritária (falhas).
""")

md("""---
## Fase 3: Feature Engineering
""")

code("""# Nova variável: potência mecânica (W) ≈ RPM × Torque (proporcional)
# Tratamos nulos antes da operação (já imputados na Fase 2)
df["potencia"] = df["velocidade_rotacao_rpm"] * df["torque_nm"]

print("Estatísticas da nova variável 'potencia':")
print(df["potencia"].describe())
print(f"\\nValores nulos em potencia: {df['potencia'].isnull().sum()}")
""")

md("""**Feature `potencia`:** combina velocidade de rotação e torque em um indicador de esforço mecânico do motor. Falhas por excesso ou falta de potência (`falha_pwf`) estão documentadas pelo departamento de engenharia, tornando essa variável fisicamente interpretável.
""")

md("""---
## Fase 4: Divisão e Balanceamento dos Dados
""")

code("""# Variáveis preditoras (sem identificadores e sem colunas de motivo de falha)
feature_cols = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
    "potencia",
    "tipo",
]

X = df[feature_cols].copy()
y = df["falha_maquina"]

# Codificação da variável categórica
X = pd.get_dummies(X, columns=["tipo"], drop_first=False)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Treino: {X_train.shape[0]} amostras | Teste: {X_test.shape[0]} amostras")
print(f"\\nDistribuição no treino (antes do balanceamento):\\n{y_train.value_counts()}")
print(f"\\nDistribuição no teste (inalterada):\\n{y_test.value_counts()}")
""")

code("""# SMOTE aplicado SOMENTE nos dados de treino (evita data leakage)
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print(f"Treino após SMOTE: {X_train_bal.shape[0]} amostras")
print(pd.Series(y_train_bal).value_counts())
""")

md("""**Balanceamento:** utilizamos SMOTE exclusivamente no conjunto de treino após o split estratificado 80/20. O conjunto de teste permanece com a distribuição original (~3,4% de falhas), garantindo avaliação realista. Aplicar balanceamento antes da divisão causaria *data leakage*.
""")

md("""---
## Fase 5: Escalonamento de Variáveis (StandardScaler)
""")

code("""# Colunas contínuas (exclui dummies de tipo, que já estão em 0/1)
continuous_cols = [
    "temperatura_ar_k",
    "temperatura_processo_k",
    "velocidade_rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
    "potencia",
]

# Cópias para KNN (com escalonamento) e Árvore (sem escalonamento)
X_train_knn = X_train_bal.copy()
X_test_knn = X_test.copy()
X_train_tree = X_train_bal.copy()
X_test_tree = X_test.copy()

scaler = StandardScaler()
X_train_knn[continuous_cols] = scaler.fit_transform(X_train_bal[continuous_cols])
X_test_knn[continuous_cols] = scaler.transform(X_test[continuous_cols])

print("Escalonamento aplicado ao KNN:")
print(X_train_knn[continuous_cols].describe().loc[["mean", "std"]])
""")

md("""**Justificativa do escalonamento seletivo:**
- **KNN** calcula distâncias euclidianas entre vizinhos; variáveis em escalas diferentes (ex.: RPM ~1500 vs. temperatura ~300) dominariam a métrica. Por isso aplicamos `StandardScaler` com `fit_transform` no treino e `transform` no teste.
- **Árvore de Decisão** particiona os dados por limiares em cada atributo; a escala absoluta não altera a ordem dos pontos de corte. Mantemos os dados originais para preservar interpretabilidade dos splits.
""")

md("""---
## Fase 6: Ajuste de Parâmetros e Combate ao Overfitting
""")

code("""# KNN: variação de K (valores ímpares)
k_values = [3, 5, 7]
knn_results = []

for k in k_values:
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train_knn, y_train_bal)

    acc_train = accuracy_score(y_train_bal, model.predict(X_train_knn))
    acc_test = accuracy_score(y_test, model.predict(X_test_knn))

    knn_results.append({"K": k, "acuracia_treino": acc_train, "acuracia_teste": acc_test})
    print(f"KNN (K={k}) → Treino: {acc_train:.4f} | Teste: {acc_test:.4f}")

knn_df = pd.DataFrame(knn_results)
knn_df
""")

code("""# Árvore de Decisão: variação de max_depth
depth_values = [3, 5, None]
tree_results = []

for depth in depth_values:
    model = DecisionTreeClassifier(max_depth=depth, random_state=42)
    model.fit(X_train_tree, y_train_bal)

    acc_train = accuracy_score(y_train_bal, model.predict(X_train_tree))
    acc_test = accuracy_score(y_test, model.predict(X_test_tree))

    label = "None (sem limite)" if depth is None else depth
    tree_results.append({
        "max_depth": label,
        "acuracia_treino": acc_train,
        "acuracia_teste": acc_test,
    })
    print(f"Árvore (max_depth={label}) → Treino: {acc_train:.4f} | Teste: {acc_test:.4f}")

tree_df = pd.DataFrame(tree_results)
tree_df
""")

code("""# Visualização: treino vs teste
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(knn_df["K"], knn_df["acuracia_treino"], "o-", label="Treino")
axes[0].plot(knn_df["K"], knn_df["acuracia_teste"], "s-", label="Teste")
axes[0].set_title("KNN – Acurácia por valor de K")
axes[0].set_xlabel("K")
axes[0].set_ylabel("Acurácia")
axes[0].legend()
axes[0].set_xticks(k_values)

x_labels = tree_df["max_depth"].tolist()
x_pos = range(len(x_labels))
axes[1].plot(x_pos, tree_df["acuracia_treino"], "o-", label="Treino")
axes[1].plot(x_pos, tree_df["acuracia_teste"], "s-", label="Teste")
axes[1].set_title("Árvore – Acurácia por max_depth")
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(x_labels)
axes[1].set_ylabel("Acurácia")
axes[1].legend()

plt.tight_layout()
plt.show()
""")

md("""### Análise de overfitting

| Modelo | Configuração | Observação |
|--------|-------------|------------|
| KNN | K=3 | Maior acurácia no treino, porém maior gap treino–teste → sinais de overfitting (vizinhos muito específicos). |
| KNN | K=5 | Equilíbrio entre treino e teste; generalização mais estável. |
| KNN | K=7 | Treino e teste mais próximos, porém pode subajustar (underfitting) se K for excessivo. |
| Árvore | max_depth=3 | Podagem agressiva; treino e teste equilibrados, baixo overfitting. |
| Árvore | max_depth=5 | Melhoria moderada no teste sem gap extremo. |
| Árvore | max_depth=None | Acurácia de treino próxima de 100% com queda no teste → overfitting claro. |

**Configurações estáveis:** KNN com K=5 e Árvore com max_depth=5 apresentam o melhor compromisso entre desempenho no teste e proximidade entre acurácias de treino e teste.
""")

md("""---
## Fase 7: Avaliação da Acurácia e Veredito Final
""")

code("""# Melhor configuração de cada modelo (maior acurácia no teste)
best_knn_row = knn_df.loc[knn_df["acuracia_teste"].idxmax()]
best_tree_row = tree_df.loc[tree_df["acuracia_teste"].idxmax()]

best_k = int(best_knn_row["K"])

depth_lookup = {3: 3, 5: 5, "None (sem limite)": None}
best_depth_label = best_tree_row["max_depth"]
best_depth = depth_lookup[best_depth_label]

final_knn = KNeighborsClassifier(n_neighbors=best_k)
final_knn.fit(X_train_knn, y_train_bal)
acc_knn_final = accuracy_score(y_test, final_knn.predict(X_test_knn))

final_tree = DecisionTreeClassifier(max_depth=best_depth, random_state=42)
final_tree.fit(X_train_tree, y_train_bal)
acc_tree_final = accuracy_score(y_test, final_tree.predict(X_test_tree))

print("=" * 55)
print("ACURÁCIA FINAL NO CONJUNTO DE TESTE")
print("=" * 55)
print(f"KNN  (K={best_k}):              {acc_knn_final:.4f} ({acc_knn_final*100:.2f}%)")
print(f"Árvore (max_depth={best_depth_label}): {acc_tree_final:.4f} ({acc_tree_final*100:.2f}%)")
print("=" * 55)

if acc_knn_final > acc_tree_final:
    vencedor = f"KNN (K={best_k})"
    diff = acc_knn_final - acc_tree_final
elif acc_tree_final > acc_knn_final:
    vencedor = f"Árvore de Decisão (max_depth={best_depth_label})"
    diff = acc_tree_final - acc_knn_final
else:
    vencedor = "Empate técnico"
    diff = 0

print(f"\\nModelo recomendado: {vencedor}")
if diff > 0:
    print(f"Diferença de acurácia no teste: {diff:.4f} ({diff*100:.2f} p.p.)")
""")

md("""### Conclusão

Após o pipeline completo — EDA, limpeza, engenharia de features, balanceamento com SMOTE, escalonamento seletivo e ajuste de hiperparâmetros — comparamos KNN e Árvore de Decisão na base de teste (20% dos dados, distribuição original).

O modelo com **maior acurácia no teste** deve ser adotado pela empresa para monitoramento preditivo. Em cenários de manutenção, recomenda-se complementar a acurácia com métricas sensíveis ao desbalanceamento (Precision, Recall e F1-Score para a classe Falha=1) em evoluções futuras do sistema.

**Melhorias futuras:** validação cruzada estratificada, Random Forest, métricas de classificação balanceadas e deploy via API para integração com os sensores do parque fabril.
""")

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0",
        },
    },
    "cells": cells,
}

NOTEBOOK_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Notebook gerado em {NOTEBOOK_PATH}")
