from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

entrada = PROCESSED / "computacao_2024_preliminar.csv"
saida = PROCESSED / "computacao_2024_tratada.csv"

df = pd.read_csv(
    entrada,
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
)

# 1. Remove espaços extras em textos
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].str.strip().str.replace(r"\s+", " ", regex=True)

# 2. Limpa códigos CINE que podem vir com aspas literais
colunas_codigo_cine = [
    "CO_CINE_ROTULO",
    "CO_CINE_AREA_GERAL",
    "CO_CINE_AREA_ESPECIFICA",
    "CO_CINE_AREA_DETALHADA",
]

for col in colunas_codigo_cine:
    if col in df.columns:
        df[col] = df[col].str.replace('"', "", regex=False).str.strip()

# 3. Converte indicadores numéricos
colunas_numericas = [
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "QT_SIT_TRANCADA",
    "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO",
    "QT_SIT_FALECIDO",
]

for col in colunas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 4. Cria rótulos simples para variáveis codificadas
mapa_tp_dimensao = {
    "1": "Presencial no Brasil",
    "2": "EaD no Brasil",
    "3": "EaD somente nível Brasil",
    "4": "EaD exterior",
}

df["DS_TP_DIMENSAO"] = df["TP_DIMENSAO"].map(mapa_tp_dimensao).fillna("Não informado")

mapa_modalidade = {
    "1": "Presencial",
    "2": "EaD",
}

df["DS_TP_MODALIDADE_ENSINO"] = (
    df["TP_MODALIDADE_ENSINO"].map(mapa_modalidade).fillna("Não informado")
)

mapa_nivel_geografico = {
    "1": "Curso presencial com localização municipal",
    "2": "Curso EaD com localização municipal/polo",
    "3": "Curso EaD com informação apenas nacional",
    "4": "Curso EaD no exterior",
}

df["DS_NIVEL_GEOGRAFICO"] = (
    df["TP_DIMENSAO"].map(mapa_nivel_geografico).fillna("Não informado")
)

# 5. Cria colunas indicando uso geográfico
df["IN_TEM_LOCALIZACAO_CURSO"] = (
    df["SG_UF"].notna()
    & df["NO_MUNICIPIO"].notna()
    & (df["SG_UF"].str.strip() != "")
    & (df["NO_MUNICIPIO"].str.strip() != "")
)

df["IN_USAR_MAPA_MUNICIPAL"] = (
    df["IN_TEM_LOCALIZACAO_CURSO"]
    & df["TP_DIMENSAO"].isin(["1", "2"])
)

# 6. Garante colunas de escopo
if "IN_ESCOPO_COMPUTACAO" not in df.columns:
    df["IN_ESCOPO_COMPUTACAO"] = True

if "DS_CRITERIO_ESCOPO" not in df.columns:
    df["DS_CRITERIO_ESCOPO"] = "Filtro preliminar por nome/CINE"

# 7. Cria versões normalizadas para facilitar filtros
df["NO_CURSO_NORMALIZADO"] = (
    df["NO_CURSO"]
    .fillna("")
    .str.upper()
    .str.strip()
)

df["NO_CINE_ROTULO_NORMALIZADO"] = (
    df["NO_CINE_ROTULO"]
    .fillna("")
    .str.upper()
    .str.strip()
)

# 8. Reordena colunas principais
colunas_principais = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "SG_IES",
    "TP_REDE",
    "TP_CATEGORIA_ADMINISTRATIVA",
    "TP_ORGANIZACAO_ACADEMICA",
    "CO_CURSO",
    "NO_CURSO",
    "NO_CURSO_NORMALIZADO",
    "IN_ESCOPO_COMPUTACAO",
    "DS_CRITERIO_ESCOPO",
    "CO_CINE_ROTULO",
    "NO_CINE_ROTULO",
    "NO_CINE_ROTULO_NORMALIZADO",
    "CO_CINE_AREA_GERAL",
    "NO_CINE_AREA_GERAL",
    "CO_CINE_AREA_ESPECIFICA",
    "NO_CINE_AREA_ESPECIFICA",
    "CO_CINE_AREA_DETALHADA",
    "NO_CINE_AREA_DETALHADA",
    "TP_GRAU_ACADEMICO",
    "TP_MODALIDADE_ENSINO",
    "DS_TP_MODALIDADE_ENSINO",
    "TP_DIMENSAO",
    "DS_TP_DIMENSAO",
    "DS_NIVEL_GEOGRAFICO",
    "IN_TEM_LOCALIZACAO_CURSO",
    "IN_USAR_MAPA_MUNICIPAL",
    "NO_REGIAO",
    "SG_UF",
    "NO_MUNICIPIO",
    "NO_REGIAO_IES",
    "SG_UF_IES",
    "NO_MUNICIPIO_IES",
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "QT_SIT_TRANCADA",
    "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO",
    "QT_SIT_FALECIDO",
]

colunas_existentes = [col for col in colunas_principais if col in df.columns]
df = df[colunas_existentes]

df.to_csv(saida, sep=";", index=False, encoding="utf-8-sig")

print("Base tratada gerada:")
print(saida)
print(df.shape)

print("\nRegistros com localização de curso:")
print(df["IN_TEM_LOCALIZACAO_CURSO"].value_counts(dropna=False))

print("\nDistribuição por dimensão:")
print(df["DS_TP_DIMENSAO"].value_counts(dropna=False))

print("\nCritério de escopo:")
print(df["DS_CRITERIO_ESCOPO"].value_counts(dropna=False))
