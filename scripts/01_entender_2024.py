from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

RAW_2024 = ROOT / "data" / "raw" / "2024"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

ARQ_CURSOS = RAW_2024 / "MICRODADOS_CADASTRO_CURSOS_2024.CSV"
ARQ_IES = RAW_2024 / "MICRODADOS_ED_SUP_IES_2024.CSV"


COLUNAS_CURSOS = [
    "NU_ANO_CENSO",
    "CO_IES",
    "CO_CURSO",
    "NO_CURSO",
    "NO_CINE_ROTULO",
    "CO_CINE_ROTULO",
    "CO_CINE_AREA_GERAL",
    "NO_CINE_AREA_GERAL",
    "CO_CINE_AREA_ESPECIFICA",
    "NO_CINE_AREA_ESPECIFICA",
    "CO_CINE_AREA_DETALHADA",
    "NO_CINE_AREA_DETALHADA",
    "TP_GRAU_ACADEMICO",
    "TP_MODALIDADE_ENSINO",
    "TP_DIMENSAO",
    "NO_REGIAO",
    "SG_UF",
    "NO_MUNICIPIO",
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

COLUNAS_IES = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "SG_IES",
    "NO_REGIAO_IES",
    "SG_UF_IES",
    "NO_MUNICIPIO_IES",
    "TP_ORGANIZACAO_ACADEMICA",
    "TP_REDE",
    "TP_CATEGORIA_ADMINISTRATIVA",
]


def limpar_codigo(serie):
    return serie.fillna("").str.replace('"', "", regex=False).str.strip()


def normalizar_texto(serie):
    return serie.fillna("").str.upper().str.strip()


def carregar_dados():
    print("Carregando cursos...")
    cursos = pd.read_csv(
        ARQ_CURSOS,
        sep=";",
        encoding="latin1",
        dtype=str,
        usecols=COLUNAS_CURSOS,
    )

    print("Carregando IES...")
    ies = pd.read_csv(
        ARQ_IES,
        sep=";",
        encoding="latin1",
        dtype=str,
        usecols=COLUNAS_IES,
    )

    print(f"Cursos: {cursos.shape}")
    print(f"IES: {ies.shape}")

    return cursos, ies


def filtrar_computacao(cursos):
    co_area_geral = limpar_codigo(cursos["CO_CINE_AREA_GERAL"])
    no_area_geral = normalizar_texto(cursos["NO_CINE_AREA_GERAL"])
    no_cine = normalizar_texto(cursos["NO_CINE_ROTULO"])
    no_curso = normalizar_texto(cursos["NO_CURSO"])

    filtro_cine_tic = (
        co_area_geral.isin(["6", "06"])
        | no_area_geral.str.contains(
            "COMPUTAÇÃO E TECNOLOGIAS DA INFORMAÇÃO",
            regex=False,
        )
    )

    filtro_licenciatura = no_cine.str.contains(
        "COMPUTAÇÃO FORMAÇÃO DE PROFESSOR",
        regex=False,
    )

    filtro_eng_computacao = (
        no_cine.str.contains("ENGENHARIA DE COMPUTAÇÃO", regex=False)
        | no_curso.str.contains("ENGENHARIA DE COMPUTAÇÃO", regex=False)
    )

    computacao = cursos[
        filtro_cine_tic | filtro_licenciatura | filtro_eng_computacao
    ].copy()

    computacao["IN_ESCOPO_COMPUTACAO"] = True
    computacao["DS_CRITERIO_ESCOPO"] = "CINE área geral Computação/TIC"
    computacao.loc[
        filtro_licenciatura.loc[computacao.index],
        "DS_CRITERIO_ESCOPO",
    ] = "CINE rótulo Computação formação de professor"
    computacao.loc[
        filtro_eng_computacao.loc[computacao.index],
        "DS_CRITERIO_ESCOPO",
    ] = "Nome/rótulo Engenharia de Computação"

    print(f"Registros de Computação/TIC encontrados: {computacao.shape}")
    print("Critérios de entrada:")
    print(computacao["DS_CRITERIO_ESCOPO"].value_counts(dropna=False))

    return computacao


def cruzar_com_ies(computacao, ies):
    base = computacao.merge(
        ies,
        on=["NU_ANO_CENSO", "CO_IES"],
        how="left",
    )

    print(f"Base cruzada: {base.shape}")

    return base


def gerar_resumos(base):
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

    for coluna in colunas_numericas:
        base[coluna] = pd.to_numeric(base[coluna], errors="coerce").fillna(0).astype(int)

    resumo_uf = (
        base.groupby("SG_UF", dropna=False)[colunas_numericas]
        .sum()
        .reset_index()
        .sort_values("QT_MAT", ascending=False)
    )

    resumo_modalidade = (
        base.groupby("TP_MODALIDADE_ENSINO", dropna=False)[colunas_numericas]
        .sum()
        .reset_index()
        .sort_values("QT_MAT", ascending=False)
    )

    resumo_cine = (
        base.groupby("NO_CINE_ROTULO", dropna=False)
        .size()
        .reset_index(name="QT_REGISTROS")
        .sort_values("QT_REGISTROS", ascending=False)
    )

    resumo_uf.to_csv(
        PROCESSED / "resumo_computacao_2024_por_uf.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    resumo_modalidade.to_csv(
        PROCESSED / "resumo_computacao_2024_por_modalidade.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    resumo_cine.to_csv(
        PROCESSED / "resumo_computacao_2024_por_cine.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )


def main():
    cursos, ies = carregar_dados()
    computacao = filtrar_computacao(cursos)
    base = cruzar_com_ies(computacao, ies)

    saida = PROCESSED / "computacao_2024_preliminar.csv"
    base.to_csv(saida, sep=";", index=False, encoding="utf-8-sig")

    gerar_resumos(base)

    print("Arquivos gerados em:", PROCESSED)
    print("Principal:", saida)


if __name__ == "__main__":
    main()
