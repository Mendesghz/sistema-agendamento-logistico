import pandas as pd

arquivo = "Invoices.xlsx"  # coloca o nome exato aqui

# Lendo com engine correto
df = pd.read_excel(arquivo, engine="openpyxl")

# Limpando espaços
df.columns = df.columns.str.strip()

# Convertendo datas no formato brasileiro
df["Vencimento_Demurrage"] = pd.to_datetime(
    df["Vencimento_Demurrage"],
    dayfirst=True,
    errors="coerce"
)

df["ETA_SZ"] = pd.to_datetime(
    df["ETA_SZ"],
    dayfirst=True,
    errors="coerce"
)

print("Primeiras linhas:")
print(df.head())

print("\nTipos de dados:")
print(df.dtypes)