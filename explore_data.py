import pandas as pd

df = pd.read_csv("data/manutencao_preditiva.csv")
print("Shape:", df.shape)
print("Columns:", list(df.columns))
print("\nNulls:")
print(df.isnull().sum())
print("\nfalha_maquina:")
print(df["falha_maquina"].value_counts())
print("\nDuplicates:", df.duplicated().sum())
print("\ntipo:", df["tipo"].value_counts().to_dict())
print("\nDescribe:")
print(df.describe())
