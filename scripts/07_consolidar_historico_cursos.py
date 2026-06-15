from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUT = PROCESSED / "historico"

SAIDA_BASE = OUT / "computacao_historico_cursos.csv"
SAIDA_RESUMO_ANO = OUT / "resumo_historico_por_ano.csv"

DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]

MAPA_UF = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}

MAPA_GRAU = {
    "1": "Bacharelado",
    "2": "Licenciatura",
    "3": "Tecnológico",
    "4": "Bacharelado e Licenciatura",
    ".": "Não aplicável",
}

MAPA_MODALIDADE = {
    "1": "Presencial",
    "2": "EaD",
}

MAPA_CATEGORIA = {
    "1": "Pública Federal",
    "2": "Pública Estadual",
    "3": "Pública Municipal",
    "4": "Privada com fins lucrativos",
    "5": "Privada sem fins lucrativos",
    "6": "Privada - Particular em sentido estrito",
    "7": "Especial",
    "8": "Privada comunitária",
    "9": "Privada confessional",
}

MAPA_ORGANIZACAO = {
    "1": "Universidade",
    "2": "Centro Universitário",
    "3": "Faculdade",
    "4": "Instituto Federal de Educação, Ciência e Tecnologia",
    "5": "Centro Federal de Educação Tecnológica",
}

COLUNAS_SAIDA = [
    "NU_ANO_CENSO",
    "DS_MODELO_DADOS",
    "DS_CLASSIFICACAO_AREA",
    "CO_IES",
    "NO_IES",
    "SG_IES",
    "CO_CURSO",
    "NO_CURSO",
    "NO_CURSO_NORMALIZADO",
    "TP_CATEGORIA_ADMINISTRATIVA",
    "DS_TP_CATEGORIA_ADMINISTRATIVA",
    "TP_REDE",
    "DS_TP_REDE",
    "TP_ORGANIZACAO_ACADEMICA",
    "DS_TP_ORGANIZACAO_ACADEMICA",
    "TP_GRAU_ACADEMICO",
    "DS_TP_GRAU_ACADEMICO",
    "TP_MODALIDADE_ENSINO",
    "DS_TP_MODALIDADE_ENSINO",
    "TP_DIMENSAO",
    "DS_TP_DIMENSAO",
    "DS_NIVEL_GEOGRAFICO",
    "IN_USAR_MAPA_MUNICIPAL",
    "CO_UF",
    "SG_UF",
    "CO_MUNICIPIO",
    "NO_MUNICIPIO",
    "CO_AREA_GERAL",
    "NO_AREA_GERAL",
    "CO_AREA_ESPECIFICA",
    "NO_AREA_ESPECIFICA",
    "CO_AREA_DETALHADA",
    "NO_AREA_DETALHADA",
    "CO_ROTULO_AREA",
    "NO_ROTULO_AREA",
    "DS_CRITERIO_ESCOPO",
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

NUMERICAS = [
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


def detectar_delimitador(caminho):
    with caminho.open("rb") as arquivo:
        primeira_linha = arquivo.readline().decode("latin1", errors="replace")
    return max(DELIMITADORES_CANDIDATOS, key=primeira_linha.count)


def read_csv(caminho, usecols=None):
    return pd.read_csv(
        caminho,
        sep=detectar_delimitador(caminho),
        encoding="latin1",
        dtype=str,
        usecols=usecols,
    )


def limpar_codigo(serie):
    return serie.fillna("").str.replace('"', "", regex=False).str.strip()


def normalizar(serie):
    return serie.fillna("").str.upper().str.strip()


def filtro_graduacao_sem_abi(df):
    nivel = df.get("TP_NIVEL_ACADEMICO", pd.Series("", index=df.index)).fillna("")
    atributo = df.get("TP_ATRIBUTO_INGRESSO", pd.Series("", index=df.index)).fillna("")
    return nivel.eq("1") & ~atributo.eq("1")


def adicionar_rotulos(df):
    df["DS_TP_GRAU_ACADEMICO"] = (
        df["TP_GRAU_ACADEMICO"].map(MAPA_GRAU).fillna("Não informado")
    )
    df["DS_TP_MODALIDADE_ENSINO"] = (
        df["TP_MODALIDADE_ENSINO"].map(MAPA_MODALIDADE).fillna("Não informado")
    )
    df["DS_TP_CATEGORIA_ADMINISTRATIVA"] = (
        df["TP_CATEGORIA_ADMINISTRATIVA"].map(MAPA_CATEGORIA).fillna("Não informado")
    )
    df["DS_TP_ORGANIZACAO_ACADEMICA"] = (
        df["TP_ORGANIZACAO_ACADEMICA"].map(MAPA_ORGANIZACAO).fillna("Não informado")
    )

    if "TP_REDE" not in df.columns:
        df["TP_REDE"] = pd.NA

    rede_derivada = df["TP_CATEGORIA_ADMINISTRATIVA"].map(
        {
            "1": "Pública",
            "2": "Pública",
            "3": "Pública",
            "4": "Privada",
            "5": "Privada",
            "6": "Privada",
            "8": "Privada",
            "9": "Privada",
        }
    )

    df["DS_TP_REDE"] = df["TP_REDE"].map({"1": "Pública", "2": "Privada"})
    df["DS_TP_REDE"] = df["DS_TP_REDE"].fillna(rede_derivada).fillna("Não informado")

    return df


def finalizar(df):
    for col in COLUNAS_SAIDA:
        if col not in df.columns:
            df[col] = pd.NA

    for col in NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["NO_CURSO_NORMALIZADO"] = normalizar(df["NO_CURSO"])

    return df[COLUNAS_SAIDA]


def processar_ano_novo(ano):
    arq_cursos = RAW / ano / f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV"
    arq_ies = RAW / ano / f"MICRODADOS_ED_SUP_IES_{ano}.CSV"

    if not arq_cursos.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_cursos}")
        return pd.DataFrame()
    if not arq_ies.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_ies}")
        return pd.DataFrame()

    cols_cursos = [
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
        "TP_REDE",
        "TP_CATEGORIA_ADMINISTRATIVA",
        "TP_ORGANIZACAO_ACADEMICA",
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
    cursos = read_csv(arq_cursos, usecols=cols_cursos)

    ies_cols_disponiveis = read_csv(arq_ies, usecols=None).columns.tolist()
    cols_ies = [
        col
        for col in [
            "NU_ANO_CENSO",
            "CO_IES",
            "NO_IES",
            "SG_IES",
        ]
        if col in ies_cols_disponiveis
    ]
    ies = read_csv(arq_ies, usecols=cols_ies)

    for col in [
        "CO_CINE_ROTULO",
        "CO_CINE_AREA_GERAL",
        "CO_CINE_AREA_ESPECIFICA",
        "CO_CINE_AREA_DETALHADA",
    ]:
        cursos[col] = limpar_codigo(cursos[col])

    filtro_area = cursos["CO_CINE_AREA_GERAL"].isin(["6", "06"])

    base = cursos[filtro_area].copy()
    base["DS_CRITERIO_ESCOPO"] = "CINE área geral 6 Computação/TIC"

    base = base.merge(ies, on=["NU_ANO_CENSO", "CO_IES"], how="left")

    base["DS_MODELO_DADOS"] = "novo"
    base["DS_CLASSIFICACAO_AREA"] = "CINE"
    base["CO_AREA_GERAL"] = base["CO_CINE_AREA_GERAL"]
    base["NO_AREA_GERAL"] = base["NO_CINE_AREA_GERAL"]
    base["CO_AREA_ESPECIFICA"] = base["CO_CINE_AREA_ESPECIFICA"]
    base["NO_AREA_ESPECIFICA"] = base["NO_CINE_AREA_ESPECIFICA"]
    base["CO_AREA_DETALHADA"] = base["CO_CINE_AREA_DETALHADA"]
    base["NO_AREA_DETALHADA"] = base["NO_CINE_AREA_DETALHADA"]
    base["CO_ROTULO_AREA"] = base["CO_CINE_ROTULO"]
    base["NO_ROTULO_AREA"] = base["NO_CINE_ROTULO"]
    base["CO_UF"] = pd.NA
    mapa_dimensao = {
        "1": "Presencial no Brasil",
        "2": "EaD no Brasil",
        "3": "EaD somente nível Brasil",
        "4": "EaD exterior",
    }
    mapa_nivel = {
        "1": "Curso presencial com localização municipal",
        "2": "Curso EaD com localização municipal/polo",
        "3": "Curso EaD com informação apenas nacional",
        "4": "Curso EaD no exterior",
    }
    base["DS_TP_DIMENSAO"] = base["TP_DIMENSAO"].map(mapa_dimensao)
    base["DS_NIVEL_GEOGRAFICO"] = base["TP_DIMENSAO"].map(mapa_nivel)
    base["IN_USAR_MAPA_MUNICIPAL"] = (
        base["TP_DIMENSAO"].isin(["1", "2"])
        & base["SG_UF"].notna()
        & base["NO_MUNICIPIO"].notna()
    )

    base = adicionar_rotulos(base)
    return finalizar(base)


def processar_ano_cine_antigo(ano, arq_curso, arq_ies, arq_cine):
    if not arq_curso.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_curso}")
        return pd.DataFrame()
    if not arq_ies.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_ies}")
        return pd.DataFrame()
    if not arq_cine.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_cine}")
        return pd.DataFrame()

    cols_curso = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "CO_LOCAL_OFERTA",
        "CO_UF",
        "CO_MUNICIPIO",
        "CO_CINE_ROTULO",
        "TP_CATEGORIA_ADMINISTRATIVA",
        "TP_ORGANIZACAO_ACADEMICA",
        "TP_GRAU_ACADEMICO",
        "TP_MODALIDADE_ENSINO",
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
        "QT_MATRICULA_TOTAL",
        "QT_CONCLUINTE_TOTAL",
        "QT_INGRESSO_TOTAL",
        "QT_VAGA_TOTAL",
        "QT_INSCRITO_TOTAL",
    ]
    cursos = read_csv(arq_curso, usecols=cols_curso)
    cine = read_csv(arq_cine)
    ies = read_csv(arq_ies, usecols=["NU_ANO_CENSO", "CO_IES", "NO_IES", "SG_IES"])

    cursos["CO_CINE_ROTULO"] = limpar_codigo(cursos["CO_CINE_ROTULO"])
    cine["CO_CINE_ROTULO"] = limpar_codigo(cine["CO_CINE_ROTULO"])

    base = cursos.merge(cine, on="CO_CINE_ROTULO", how="left")
    filtro_area = limpar_codigo(base["CO_CINE_AREA_GERAL"]).isin(["6", "06"])

    base = base[filtro_graduacao_sem_abi(base) & filtro_area].copy()
    base["DS_CRITERIO_ESCOPO"] = "CINE Brasil área geral 6 Computação/TIC"

    base = base.merge(ies, on=["NU_ANO_CENSO", "CO_IES"], how="left")

    base["DS_MODELO_DADOS"] = "antigo"
    base["DS_CLASSIFICACAO_AREA"] = "CINE Brasil"
    base["CO_AREA_GERAL"] = limpar_codigo(base["CO_CINE_AREA_GERAL"])
    base["NO_AREA_GERAL"] = base["NO_CINE_AREA_GERAL"]
    base["CO_AREA_ESPECIFICA"] = base["CO_CINE_AREA_ESPECIFICA"]
    base["NO_AREA_ESPECIFICA"] = base["NO_CINE_AREA_ESPECIFICA"]
    base["CO_AREA_DETALHADA"] = base["CO_CINE_AREA_DETALHADA"]
    base["NO_AREA_DETALHADA"] = base["NO_CINE_AREA_DETALHADA"]
    base["CO_ROTULO_AREA"] = base["CO_CINE_ROTULO"]
    base["NO_ROTULO_AREA"] = base["NO_CINE_ROTULO"]
    base["SG_UF"] = base["CO_UF"].map(MAPA_UF)
    base["NO_MUNICIPIO"] = pd.NA
    base["TP_DIMENSAO"] = pd.NA
    base["DS_TP_DIMENSAO"] = "Não existia no modelo antigo"
    base["DS_NIVEL_GEOGRAFICO"] = base["TP_MODALIDADE_ENSINO"].map(
        {
            "1": "Curso presencial com localização no curso",
            "2": "Curso EaD sem polos identificáveis na tabela de curso",
        }
    )
    base["IN_USAR_MAPA_MUNICIPAL"] = (
        base["TP_MODALIDADE_ENSINO"].eq("1")
        & base["CO_MUNICIPIO"].notna()
        & base["CO_MUNICIPIO"].ne("")
    )
    base["QT_VG_TOTAL"] = base["QT_VAGA_TOTAL"]
    base["QT_ING"] = base["QT_INGRESSO_TOTAL"]
    base["QT_MAT"] = base["QT_MATRICULA_TOTAL"]
    base["QT_CONC"] = base["QT_CONCLUINTE_TOTAL"]

    base = adicionar_rotulos(base)
    return finalizar(base)


def processar_ano_ocde_2017():
    arq_curso = RAW / "2017" / "DM_CURSO.CSV"
    arq_ies = RAW / "2017" / "DM_IES.CSV"
    arq_ocde = RAW / "2017" / "TB_AUX_AREA_OCDE.CSV"

    if not arq_curso.exists():
        print(f"[2017] Arquivo não encontrado: {arq_curso}")
        return pd.DataFrame()
    if not arq_ies.exists():
        print(f"[2017] Arquivo não encontrado: {arq_ies}")
        return pd.DataFrame()
    if not arq_ocde.exists():
        print(f"[2017] Arquivo não encontrado: {arq_ocde}")
        return pd.DataFrame()

    cols_curso = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "CO_LOCAL_OFERTA",
        "CO_UF",
        "CO_MUNICIPIO",
        "CO_OCDE_AREA_GERAL",
        "CO_OCDE_AREA_ESPECIFICA",
        "CO_OCDE_AREA_DETALHADA",
        "CO_OCDE",
        "TP_CATEGORIA_ADMINISTRATIVA",
        "TP_ORGANIZACAO_ACADEMICA",
        "TP_GRAU_ACADEMICO",
        "TP_MODALIDADE_ENSINO",
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
        "QT_MATRICULA_TOTAL",
        "QT_CONCLUINTE_TOTAL",
        "QT_INGRESSO_TOTAL",
        "QT_VAGA_TOTAL",
    ]

    cursos = read_csv(arq_curso, usecols=cols_curso)
    ocde = read_csv(arq_ocde)
    ies = read_csv(arq_ies, usecols=["NU_ANO_CENSO", "CO_IES", "NO_IES", "SG_IES"])

    base = cursos.merge(
        ocde,
        on=[
            "NU_ANO_CENSO",
            "CO_OCDE_AREA_GERAL",
            "CO_OCDE_AREA_ESPECIFICA",
            "CO_OCDE_AREA_DETALHADA",
            "CO_OCDE",
        ],
        how="left",
    )

    filtro_area = base["CO_OCDE_AREA_ESPECIFICA"].eq("48")

    base = base[filtro_graduacao_sem_abi(base) & filtro_area].copy()
    base["DS_CRITERIO_ESCOPO"] = "OCDE área específica 48 Computação"

    base = base.merge(ies, on=["NU_ANO_CENSO", "CO_IES"], how="left")

    base["DS_MODELO_DADOS"] = "antigo"
    base["DS_CLASSIFICACAO_AREA"] = "OCDE"
    base["CO_AREA_GERAL"] = base["CO_OCDE_AREA_GERAL"]
    base["NO_AREA_GERAL"] = base["NO_OCDE_AREA_GERAL"]
    base["CO_AREA_ESPECIFICA"] = base["CO_OCDE_AREA_ESPECIFICA"]
    base["NO_AREA_ESPECIFICA"] = base["NO_OCDE_AREA_ESPECIFICA"]
    base["CO_AREA_DETALHADA"] = base["CO_OCDE_AREA_DETALHADA"]
    base["NO_AREA_DETALHADA"] = base["NO_OCDE_AREA_DETALHADA"]
    base["CO_ROTULO_AREA"] = base["CO_OCDE"]
    base["NO_ROTULO_AREA"] = base["NO_OCDE"]
    base["SG_UF"] = base["CO_UF"].map(MAPA_UF)
    base["NO_MUNICIPIO"] = pd.NA
    base["TP_DIMENSAO"] = pd.NA
    base["DS_TP_DIMENSAO"] = "Não existia no modelo antigo"
    base["DS_NIVEL_GEOGRAFICO"] = base["TP_MODALIDADE_ENSINO"].map(
        {
            "1": "Curso presencial com localização no curso",
            "2": "Curso EaD sem polos identificáveis na tabela de curso",
        }
    )
    base["IN_USAR_MAPA_MUNICIPAL"] = (
        base["TP_MODALIDADE_ENSINO"].eq("1")
        & base["CO_MUNICIPIO"].notna()
        & base["CO_MUNICIPIO"].ne("")
    )
    base["QT_VG_TOTAL"] = base["QT_VAGA_TOTAL"]
    base["QT_INSCRITO_TOTAL"] = pd.NA
    base["QT_ING"] = base["QT_INGRESSO_TOTAL"]
    base["QT_MAT"] = base["QT_MATRICULA_TOTAL"]
    base["QT_CONC"] = base["QT_CONCLUINTE_TOTAL"]

    base = adicionar_rotulos(base)
    return finalizar(base)


def gerar_resumo(base):
    def soma_minima(serie):
        return serie.sum(min_count=1)

    resumo = (
        base.groupby("NU_ANO_CENSO", dropna=False)
        .agg(
            QT_REGISTROS=("CO_CURSO", "size"),
            QT_CURSOS_DISTINTOS=("CO_CURSO", "nunique"),
            QT_IES_DISTINTAS=("CO_IES", "nunique"),
            QT_REGISTROS_MAPA_MUNICIPAL=("IN_USAR_MAPA_MUNICIPAL", "sum"),
            **{col: (col, soma_minima) for col in NUMERICAS},
        )
        .reset_index()
        .sort_values("NU_ANO_CENSO")
    )

    resumo["TX_DESVINCULADO_SOBRE_MAT"] = (
        resumo["QT_SIT_DESVINCULADO"] / resumo["QT_MAT"]
    ).where(resumo["QT_MAT"] > 0)

    return resumo


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    partes = [
        processar_ano_ocde_2017(),
        processar_ano_cine_antigo(
            "2018",
            RAW / "2018" / "DM_CURSO.CSV",
            RAW / "2018" / "DM_IES.CSV",
            RAW / "2018" / "TB_AUX_CINE_BRASIL.CSV",
        ),
        processar_ano_cine_antigo(
            "2019",
            RAW / "2019" / "SUP_CURSO_2019.CSV",
            RAW / "2019" / "SUP_IES_2019.CSV",
            RAW / "2019" / "TB_AUX_CINE_BRASIL_2019.CSV",
        ),
        processar_ano_novo("2022"),
        processar_ano_novo("2024"),
    ]

    partes_validas = [p for p in partes if not p.empty]
    
    if not partes_validas:
        print("Erro: Nenhum arquivo de curso foi encontrado em data/raw para consolidar.")
        return

    base = pd.concat(partes_validas, ignore_index=True)
    base.to_csv(SAIDA_BASE, sep=";", index=False, encoding="utf-8-sig")

    resumo = gerar_resumo(base)
    resumo.to_csv(SAIDA_RESUMO_ANO, sep=";", index=False, encoding="utf-8-sig")

    print("Base histórica gerada:")
    print(SAIDA_BASE)
    print(base.shape)
    print("\nResumo por ano:")
    print(SAIDA_RESUMO_ANO)
    print(resumo)


if __name__ == "__main__":
    main()
