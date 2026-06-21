from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUT = PROCESSED / ".pipeline"

SAIDA_BASE = OUT / "cursos_expandida.csv"

DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]
ROTULO_ENGENHARIA_COMPUTACAO = "0714E04"
OCDE_PROXY_ENGENHARIA_COMPUTACAO = "5.23E+06"
ANOS_CADASTRO_CINE = [
    "2009",
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
]

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
    "DS_NIVEL_COMPARABILIDADE",
    "DS_OBSERVACAO_COMPARABILIDADE",
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


def colunas_csv(caminho):
    return pd.read_csv(
        caminho,
        sep=detectar_delimitador(caminho),
        encoding="latin1",
        dtype=str,
        nrows=0,
    ).columns.tolist()


def read_csv_disponivel(caminho, colunas_desejadas):
    colunas_disponiveis = colunas_csv(caminho)
    usecols = [coluna for coluna in colunas_desejadas if coluna in colunas_disponiveis]
    return read_csv(caminho, usecols=usecols)


def encontrar_arquivo(ano, nomes):
    pasta_ano = RAW / str(ano)
    if not pasta_ano.exists():
        return None

    nomes_normalizados = {nome.upper() for nome in nomes}
    for caminho in sorted(pasta_ano.rglob("*.CSV")) + sorted(pasta_ano.rglob("*.csv")):
        if caminho.name.upper() in nomes_normalizados:
            return caminho

    return None


def limpar_codigo(serie):
    return serie.fillna("").str.replace('"', "", regex=False).str.strip().str.upper()


def normalizar(serie):
    return serie.fillna("").str.upper().str.strip()


def filtro_graduacao_sem_abi(df):
    nivel = (
        df.get("TP_NIVEL_ACADEMICO", pd.Series("", index=df.index))
        .fillna("")
        .astype(str)
        .str.strip()
    )
    atributo = (
        df.get("TP_ATRIBUTO_INGRESSO", pd.Series("", index=df.index))
        .fillna("")
        .astype(str)
        .str.strip()
    )
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
    ano = str(ano)
    arq_cursos = encontrar_arquivo(ano, [f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV"])
    arq_ies = encontrar_arquivo(
        ano,
        [
            f"MICRODADOS_ED_SUP_IES_{ano}.CSV",
            f"MICRODADOS_CADASTRO_IES_{ano}.CSV",
        ],
    )

    if arq_cursos is None:
        print(f"[{ano}] Arquivo de cursos não encontrado.")
        return pd.DataFrame()
    if arq_ies is None:
        print(f"[{ano}] Arquivo de IES não encontrado.")
        return pd.DataFrame()

    cols_cursos = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "NO_CINE_ROTULO",
        "CO_CINE_ROTULO",
        "CO_CINE_ROTULO2",
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
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
        "NO_REGIAO",
        "CO_UF",
        "SG_UF",
        "CO_MUNICIPIO",
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
    cursos = read_csv_disponivel(arq_cursos, cols_cursos)
    for col in cols_cursos:
        if col not in cursos.columns:
            cursos[col] = pd.NA

    if "CO_CINE_ROTULO2" in cursos.columns:
        sem_rotulo = cursos["CO_CINE_ROTULO"].isna() | cursos["CO_CINE_ROTULO"].eq("")
        cursos.loc[sem_rotulo, "CO_CINE_ROTULO"] = cursos.loc[
            sem_rotulo, "CO_CINE_ROTULO2"
        ]

    cursos = cursos[filtro_graduacao_sem_abi(cursos)].copy()

    cols_ies = ["NU_ANO_CENSO", "CO_IES", "NO_IES", "SG_IES"]
    ies = read_csv_disponivel(arq_ies, cols_ies)
    for col in cols_ies:
        if col not in ies.columns:
            ies[col] = pd.NA

    for col in [
        "CO_CINE_ROTULO",
        "CO_CINE_AREA_GERAL",
        "CO_CINE_AREA_ESPECIFICA",
        "CO_CINE_AREA_DETALHADA",
    ]:
        cursos[col] = limpar_codigo(cursos[col])

    filtro_area = cursos["CO_CINE_AREA_GERAL"].isin(["6", "06"])
    filtro_eng = cursos["CO_CINE_ROTULO"].eq(ROTULO_ENGENHARIA_COMPUTACAO)

    base = cursos[filtro_area | filtro_eng].copy()
    base["DS_CRITERIO_ESCOPO"] = "CINE área geral 6 Computação/TIC"
    base.loc[
        filtro_eng.loc[base.index] & ~filtro_area.loc[base.index],
        "DS_CRITERIO_ESCOPO",
    ] = "CINE rótulo 0714E04 Engenharia de Computação"

    base = base.merge(ies, on=["NU_ANO_CENSO", "CO_IES"], how="left")

    base["DS_MODELO_DADOS"] = "cadastro_cursos"
    base["DS_CLASSIFICACAO_AREA"] = "CINE"
    base["DS_NIVEL_COMPARABILIDADE"] = "alta_cine"
    base["DS_OBSERVACAO_COMPARABILIDADE"] = (
        "Recorte oficial por CINE area geral 6 ou rotulo 0714E04."
    )
    base["CO_AREA_GERAL"] = base["CO_CINE_AREA_GERAL"]
    base["NO_AREA_GERAL"] = base["NO_CINE_AREA_GERAL"]
    base["CO_AREA_ESPECIFICA"] = base["CO_CINE_AREA_ESPECIFICA"]
    base["NO_AREA_ESPECIFICA"] = base["NO_CINE_AREA_ESPECIFICA"]
    base["CO_AREA_DETALHADA"] = base["CO_CINE_AREA_DETALHADA"]
    base["NO_AREA_DETALHADA"] = base["NO_CINE_AREA_DETALHADA"]
    base["CO_ROTULO_AREA"] = base["CO_CINE_ROTULO"]
    base["NO_ROTULO_AREA"] = base["NO_CINE_ROTULO"]
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
    if arq_curso is None or not arq_curso.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_curso}")
        return pd.DataFrame()
    if arq_ies is None or not arq_ies.exists():
        print(f"[{ano}] Arquivo não encontrado: {arq_ies}")
        return pd.DataFrame()
    if arq_cine is None or not arq_cine.exists():
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
    filtro_eng = base["CO_CINE_ROTULO"].eq(ROTULO_ENGENHARIA_COMPUTACAO)

    base = base[filtro_graduacao_sem_abi(base) & (filtro_area | filtro_eng)].copy()
    base["DS_CRITERIO_ESCOPO"] = "CINE Brasil área geral 6 Computação/TIC"
    base.loc[
        filtro_eng.loc[base.index] & ~filtro_area.loc[base.index],
        "DS_CRITERIO_ESCOPO",
    ] = "CINE Brasil rótulo 0714E04 Engenharia de Computação"

    base = base.merge(ies, on=["NU_ANO_CENSO", "CO_IES"], how="left")

    base["DS_MODELO_DADOS"] = "antigo"
    base["DS_CLASSIFICACAO_AREA"] = "CINE Brasil"
    base["DS_NIVEL_COMPARABILIDADE"] = "alta_cine_brasil_modelo_antigo"
    base["DS_OBSERVACAO_COMPARABILIDADE"] = (
        "Recorte oficial por CINE Brasil area geral 6 ou rotulo 0714E04."
    )
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
    arq_curso = encontrar_arquivo("2017", ["DM_CURSO.CSV"])
    arq_ies = encontrar_arquivo("2017", ["DM_IES.CSV"])
    arq_ocde = encontrar_arquivo("2017", ["TB_AUX_AREA_OCDE.CSV"])

    if arq_curso is None or not arq_curso.exists():
        print(f"[2017] Arquivo não encontrado: {arq_curso}")
        return pd.DataFrame()
    if arq_ies is None or not arq_ies.exists():
        print(f"[2017] Arquivo não encontrado: {arq_ies}")
        return pd.DataFrame()
    if arq_ocde is None or not arq_ocde.exists():
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
    filtro_eng = limpar_codigo(base["CO_OCDE"]).eq(OCDE_PROXY_ENGENHARIA_COMPUTACAO)

    base = base[filtro_graduacao_sem_abi(base) & (filtro_area | filtro_eng)].copy()
    base["DS_CRITERIO_ESCOPO"] = "OCDE área específica 48 Computação"
    base.loc[
        filtro_eng.loc[base.index] & ~filtro_area.loc[base.index],
        "DS_CRITERIO_ESCOPO",
    ] = "OCDE proxy 5.23E+06 Engenharia/Computação"

    base = base.merge(ies, on=["NU_ANO_CENSO", "CO_IES"], how="left")

    base["DS_MODELO_DADOS"] = "antigo"
    base["DS_CLASSIFICACAO_AREA"] = "OCDE"
    base["DS_NIVEL_COMPARABILIDADE"] = "media_ocde_proxy"
    base["DS_OBSERVACAO_COMPARABILIDADE"] = (
        "2017 nao possui CINE; usa OCDE area especifica 48 e proxy "
        "5.23E+06 para Engenharia/Computacao."
    )
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    partes = [processar_ano_novo(ano) for ano in ANOS_CADASTRO_CINE if ano < "2017"]
    partes.extend(
        [
            processar_ano_ocde_2017(),
            processar_ano_cine_antigo(
                "2018",
                encontrar_arquivo("2018", ["DM_CURSO.CSV"]),
                encontrar_arquivo("2018", ["DM_IES.CSV"]),
                encontrar_arquivo("2018", ["TB_AUX_CINE_BRASIL.CSV"]),
            ),
            processar_ano_cine_antigo(
                "2019",
                encontrar_arquivo("2019", ["SUP_CURSO_2019.CSV"]),
                encontrar_arquivo("2019", ["SUP_IES_2019.CSV"]),
                encontrar_arquivo("2019", ["TB_AUX_CINE_BRASIL_2019.CSV"]),
            ),
        ]
    )
    partes.extend(
        processar_ano_novo(ano) for ano in ANOS_CADASTRO_CINE if ano > "2019"
    )

    partes_validas = [p for p in partes if not p.empty]

    if not partes_validas:
        print("Erro: Nenhum arquivo de curso foi encontrado em data/raw para consolidar.")
        return

    base = pd.concat(partes_validas, ignore_index=True)
    base.to_csv(SAIDA_BASE, sep=";", index=False, encoding="utf-8-sig")

    print("Cursos consolidados:")
    print(SAIDA_BASE)
    print(base.shape)


if __name__ == "__main__":
    main()
