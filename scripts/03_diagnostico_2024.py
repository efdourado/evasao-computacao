from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

ARQ_BASE = PROCESSED / "computacao_2024_preliminar.csv"

df = pd.read_csv(
    ARQ_BASE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
)

print("\n=== TAMANHO DA BASE ===")
print(df.shape)

print("\n=== COLUNAS ===")
for col in df.columns:
    print(col)

print("\n=== PRIMEIRAS LINHAS ===")
print(df.head(10))

print("\n=== VALORES AUSENTES POR COLUNA ===")
ausentes = (
    df.isna()
    .sum()
    .reset_index()
)
ausentes.columns = ["coluna", "qtd_ausentes"]
ausentes["percentual"] = (ausentes["qtd_ausentes"] / len(df) * 100).round(2)
print(ausentes.sort_values("qtd_ausentes", ascending=False))

print("\n=== DISTRIBUIÇÃO POR TP_DIMENSAO ===")
print(df["TP_DIMENSAO"].value_counts(dropna=False))

print("\n=== DISTRIBUIÇÃO POR UF DO CURSO ===")
print(df["SG_UF"].value_counts(dropna=False).head(30))

print("\n=== DISTRIBUIÇÃO POR UF DA IES ===")
print(df["SG_UF_IES"].value_counts(dropna=False).head(30))

print("\n=== DISTRIBUIÇÃO POR MODALIDADE ===")
print(df["TP_MODALIDADE_ENSINO"].value_counts(dropna=False))

print("\n=== DISTRIBUIÇÃO POR GRAU ACADÊMICO ===")
print(df["TP_GRAU_ACADEMICO"].value_counts(dropna=False))

print("\n=== TOP 30 NOMES DE CURSO ===")
print(df["NO_CURSO"].value_counts(dropna=False).head(30))

print("\n=== TOP 30 CINE RÓTULO ===")
print(df["NO_CINE_ROTULO"].value_counts(dropna=False).head(30))

print("\n=== REGISTROS DUPLICADOS POR CO_IES + CO_CURSO + TP_DIMENSAO + UF + MUNICÍPIO ===")
chaves = ["CO_IES", "CO_CURSO", "TP_DIMENSAO", "SG_UF", "NO_MUNICIPIO"]
duplicados = df.duplicated(subset=chaves, keep=False).sum()
print(duplicados)

# Salva relatórios em CSV para você abrir no Data Wrangler/Excel
ausentes.to_csv(PROCESSED / "diagnostico_ausentes.csv", sep=";", index=False, encoding="utf-8-sig")

df["TP_DIMENSAO"].value_counts(dropna=False).reset_index().to_csv(
    PROCESSED / "diagnostico_tp_dimensao.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig",
)

df["NO_CURSO"].value_counts(dropna=False).head(100).reset_index().to_csv(
    PROCESSED / "diagnostico_top_cursos.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig",
)

df["NO_CINE_ROTULO"].value_counts(dropna=False).head(100).reset_index().to_csv(
    PROCESSED / "diagnostico_top_cine.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig",
)

print("\nDiagnósticos salvos em data/processed/")