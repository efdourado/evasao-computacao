from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CAMINHO = ROOT / "data" / "processed" / "computacao_2024_preliminar.csv"

df = pd.read_csv(
    CAMINHO,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

print(df.shape)
print(df.columns.tolist())
print(df.head())
