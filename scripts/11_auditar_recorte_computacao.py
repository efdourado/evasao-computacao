from pathlib import Path
import unicodedata

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
HISTORICO = ROOT / "data" / "processed" / "historico"

BASE_COMPARAVEL = HISTORICO / "computacao_historico_cursos_comparavel.csv"
SAIDA_CANDIDATOS = HISTORICO / "auditoria_possiveis_cursos_fora_recorte.csv"
SAIDA_RESUMO = HISTORICO / "auditoria_recorte_computacao_resumo.csv"

CHAVE_CURSO = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]
DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]

PALAVRAS_CHAVE = [
    "ANALISE E DESENVOLVIMENTO",
    "ANALISE DE DADOS",
    "BANCO DE DADOS",
    "BIG DATA",
    "CIBER",
    "CIENCIA DE DADOS",
    "COMPUT",
    "CYBER",
    "DEFESA CIBERNETICA",
    "GESTAO DA TECNOLOGIA DA INFORMACAO",
    "INFORMAT",
    "INTELIGENCIA ARTIFICIAL",
    "INTERNET DAS COISAS",
    "JOGOS DIGITAIS",
    "REDES DE COMPUTADORES",
    "SEGURANCA DA INFORMACAO",
    "SEGURANCA CIBERNETICA",
    "SISTEMAS DE INFORMACAO",
    "SISTEMAS PARA INTERNET",
    "SOFTWARE",
    "TECNOLOGIA DA INFORMACAO",
    "TELEMATICA",
]


def detectar_delimitador(caminho):
    with caminho.open("rb") as arquivo:
        primeira_linha = arquivo.readline().decode("latin1", errors="replace")
    return max(DELIMITADORES_CANDIDATOS, key=primeira_linha.count)


def normalizar_texto(valor):
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return texto.upper().strip()


def normalizar_chaves(df):
    for coluna in CHAVE_CURSO:
        df[coluna] = df[coluna].astype(str).str.replace('"', "", regex=False).str.strip()
    return df


def read_csv_disponivel(caminho, colunas_desejadas=None):
    delimitador = detectar_delimitador(caminho)
    header = pd.read_csv(
        caminho,
        sep=delimitador,
        encoding="latin1",
        dtype=str,
        nrows=0,
    ).columns.tolist()

    if colunas_desejadas is None:
        usecols = header
    else:
        usecols = [coluna for coluna in colunas_desejadas if coluna in header]

    return pd.read_csv(
        caminho,
        sep=delimitador,
        encoding="latin1",
        dtype=str,
        usecols=usecols,
    )


def encontrar_arquivo(ano, nomes):
    pasta_ano = RAW / str(ano)
    if not pasta_ano.exists():
        return None

    nomes_normalizados = {nome.upper() for nome in nomes}
    for caminho in sorted(pasta_ano.rglob("*.CSV")) + sorted(pasta_ano.rglob("*.csv")):
        if caminho.name.upper() in nomes_normalizados:
            return caminho

    return None


def filtro_graduacao_sem_abi(df):
    if "TP_NIVEL_ACADEMICO" in df.columns:
        nivel = df["TP_NIVEL_ACADEMICO"].fillna("").astype(str).str.strip()
        filtro_nivel = nivel.eq("1")
    else:
        filtro_nivel = pd.Series(True, index=df.index)

    if "TP_ATRIBUTO_INGRESSO" in df.columns:
        atributo = df["TP_ATRIBUTO_INGRESSO"].fillna("").astype(str).str.strip()
        filtro_abi = ~atributo.eq("1")
    else:
        filtro_abi = pd.Series(True, index=df.index)

    return filtro_nivel & filtro_abi


def carregar_chaves_incluidas():
    base = pd.read_csv(BASE_COMPARAVEL, sep=";", encoding="utf-8-sig", dtype=str)
    normalizar_chaves(base)
    return set(map(tuple, base[CHAVE_CURSO].drop_duplicates().to_numpy()))


def marcar_candidatos(df, incluido):
    normalizar_chaves(df)
    textos = []
    for coluna in [
        "NO_CURSO",
        "NO_CINE_ROTULO",
        "NO_CINE_AREA_DETALHADA",
        "NO_OCDE",
        "NO_OCDE_AREA_DETALHADA",
    ]:
        if coluna in df.columns:
            textos.append(df[coluna].map(normalizar_texto))

    if not textos:
        return pd.DataFrame()

    texto_busca = textos[0]
    for texto in textos[1:]:
        texto_busca = texto_busca + " " + texto

    motivos = []
    for texto in texto_busca:
        encontrados = [palavra for palavra in PALAVRAS_CHAVE if palavra in texto]
        motivos.append("|".join(encontrados))

    df = df.copy()
    df["DS_MOTIVO_AUDITORIA"] = motivos
    df = df[df["DS_MOTIVO_AUDITORIA"].ne("")]

    chaves = list(map(tuple, df[CHAVE_CURSO].to_numpy()))
    df["IN_JA_INCLUIDO_RECORTE"] = [chave in incluido for chave in chaves]
    df = df[~df["IN_JA_INCLUIDO_RECORTE"]].copy()

    colunas_saida = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "DS_MOTIVO_AUDITORIA",
        "CO_CINE_ROTULO",
        "NO_CINE_ROTULO",
        "CO_OCDE",
        "NO_OCDE",
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
    ]
    for coluna in colunas_saida:
        if coluna not in df.columns:
            df[coluna] = pd.NA

    return df[colunas_saida]


def cursos_novos(ano):
    caminho = encontrar_arquivo(ano, [f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV"])
    if caminho is None:
        return pd.DataFrame()

    colunas = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "CO_CINE_ROTULO",
        "CO_CINE_ROTULO2",
        "NO_CINE_ROTULO",
        "CO_CINE_AREA_GERAL",
        "NO_CINE_AREA_GERAL",
        "CO_CINE_AREA_ESPECIFICA",
        "NO_CINE_AREA_ESPECIFICA",
        "CO_CINE_AREA_DETALHADA",
        "NO_CINE_AREA_DETALHADA",
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
    ]
    cursos = read_csv_disponivel(caminho, colunas)
    if "CO_CINE_ROTULO" not in cursos.columns:
        cursos["CO_CINE_ROTULO"] = pd.NA
    if "CO_CINE_ROTULO2" in cursos.columns:
        sem_rotulo = cursos["CO_CINE_ROTULO"].isna() | cursos["CO_CINE_ROTULO"].eq("")
        cursos.loc[sem_rotulo, "CO_CINE_ROTULO"] = cursos.loc[
            sem_rotulo, "CO_CINE_ROTULO2"
        ]
    return cursos[filtro_graduacao_sem_abi(cursos)].copy()


def cursos_cine_antigo(ano, caminho_curso, caminho_cine):
    colunas = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "CO_CINE_ROTULO",
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
    ]
    cursos = read_csv_disponivel(caminho_curso, colunas)
    cine = read_csv_disponivel(caminho_cine)
    cursos["CO_CINE_ROTULO"] = (
        cursos["CO_CINE_ROTULO"].fillna("").str.replace('"', "", regex=False).str.strip()
    )
    cine["CO_CINE_ROTULO"] = (
        cine["CO_CINE_ROTULO"].fillna("").str.replace('"', "", regex=False).str.strip()
    )
    cursos = cursos.merge(cine, on="CO_CINE_ROTULO", how="left")
    return cursos[filtro_graduacao_sem_abi(cursos)].copy()


def cursos_ocde_2017():
    caminho_curso = RAW / "2017" / "DM_CURSO.CSV"
    caminho_ocde = RAW / "2017" / "TB_AUX_AREA_OCDE.CSV"
    colunas = [
        "NU_ANO_CENSO",
        "CO_IES",
        "CO_CURSO",
        "NO_CURSO",
        "CO_OCDE_AREA_GERAL",
        "CO_OCDE_AREA_ESPECIFICA",
        "CO_OCDE_AREA_DETALHADA",
        "CO_OCDE",
        "TP_NIVEL_ACADEMICO",
        "TP_ATRIBUTO_INGRESSO",
    ]
    cursos = read_csv_disponivel(caminho_curso, colunas)
    ocde = read_csv_disponivel(caminho_ocde)
    cursos = cursos.merge(
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
    return cursos[filtro_graduacao_sem_abi(cursos)].copy()


def auditar():
    incluidos = carregar_chaves_incluidas()
    anos_cadastro = []
    for pasta in sorted(RAW.iterdir()):
        if not pasta.is_dir() or not pasta.name.isdigit():
            continue
        ano = pasta.name
        if ano in ["2017", "2018", "2019"]:
            continue
        if encontrar_arquivo(ano, [f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV"]):
            anos_cadastro.append(ano)

    partes = [
        cursos_ocde_2017(),
        cursos_cine_antigo(
            "2018",
            RAW / "2018" / "DM_CURSO.CSV",
            RAW / "2018" / "TB_AUX_CINE_BRASIL.CSV",
        ),
        cursos_cine_antigo(
            "2019",
            RAW / "2019" / "SUP_CURSO_2019.CSV",
            RAW / "2019" / "TB_AUX_CINE_BRASIL_2019.CSV",
        ),
    ]
    partes.extend(cursos_novos(ano) for ano in anos_cadastro)

    candidatos = [marcar_candidatos(parte, incluidos) for parte in partes]
    candidatos = [parte for parte in candidatos if not parte.empty]
    if candidatos:
        resultado = pd.concat(candidatos, ignore_index=True)
    else:
        resultado = pd.DataFrame(
            columns=[
                "NU_ANO_CENSO",
                "CO_IES",
                "CO_CURSO",
                "NO_CURSO",
                "DS_MOTIVO_AUDITORIA",
                "CO_CINE_ROTULO",
                "NO_CINE_ROTULO",
                "CO_OCDE",
                "NO_OCDE",
                "TP_NIVEL_ACADEMICO",
                "TP_ATRIBUTO_INGRESSO",
            ]
        )

    resumo = (
        resultado.groupby("NU_ANO_CENSO", dropna=False)
        .agg(
            QT_CANDIDATOS_FORA_RECORTE=("CO_CURSO", "size"),
            QT_CURSOS_DISTINTOS=("CO_CURSO", "nunique"),
            QT_NOMES_DISTINTOS=("NO_CURSO", "nunique"),
        )
        .reset_index()
        .sort_values("NU_ANO_CENSO")
    )

    return resultado.sort_values(["NU_ANO_CENSO", "NO_CURSO", "CO_IES", "CO_CURSO"]), resumo


def main():
    if not BASE_COMPARAVEL.exists():
        print(f"Base comparavel nao encontrada: {BASE_COMPARAVEL}")
        print("Execute primeiro: .venv/bin/python scripts/08_validar_historico.py")
        return

    HISTORICO.mkdir(parents=True, exist_ok=True)
    candidatos, resumo = auditar()
    candidatos.to_csv(SAIDA_CANDIDATOS, sep=";", index=False, encoding="utf-8-sig")
    resumo.to_csv(SAIDA_RESUMO, sep=";", index=False, encoding="utf-8-sig")

    print("Auditoria do recorte gerada:")
    print(SAIDA_CANDIDATOS)
    print(SAIDA_RESUMO)
    print(resumo)


if __name__ == "__main__":
    main()
