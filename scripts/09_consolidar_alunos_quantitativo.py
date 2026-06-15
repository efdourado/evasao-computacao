from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
HISTORICO = ROOT / "data" / "processed" / "historico"

BASE_CURSOS = HISTORICO / "computacao_historico_cursos_comparavel.csv"
SAIDA_ALUNOS = HISTORICO / "alunos_computacao_quantitativo.csv"

ANOS_ALVO = ["2017", "2018", "2019", "2022", "2024"]
CHAVE_CURSO = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]
DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]

MAPA_SITUACAO = {
    "2": "QT_ALUNO_CURSANDO",
    "3": "QT_ALUNO_TRANCADA",
    "4": "QT_ALUNO_DESVINCULADO",
    "5": "QT_ALUNO_TRANSFERIDO",
    "6": "QT_ALUNO_FORMADO",
    "7": "QT_ALUNO_FALECIDO",
}

COLUNAS_ALUNO = list(MAPA_SITUACAO.values())
COLUNAS_SAIDA = CHAVE_CURSO + COLUNAS_ALUNO + ["QT_ALUNO_TOTAL_VINCULOS"]


def detectar_delimitador(caminho):
    with caminho.open("rb") as arquivo:
        primeira_linha = arquivo.readline().decode("latin1", errors="replace")
    return max(DELIMITADORES_CANDIDATOS, key=primeira_linha.count)


def localizar_arquivo_aluno(ano):
    pasta_ano = RAW / ano
    if not pasta_ano.exists():
        return None

    candidatos = [
        f"MICRODADOS_CADASTRO_ALUNOS_{ano}.CSV",
        f"SUP_ALUNO_{ano}.CSV",
        "SUP_ALUNO.CSV",
        "DM_ALUNO.CSV",
    ]

    for nome in candidatos:
        caminho = pasta_ano / nome
        if caminho.exists():
            return caminho

    arquivos = sorted(pasta_ano.glob("*ALUNO*.CSV")) + sorted(
        pasta_ano.glob("*ALUNO*.csv")
    )
    return arquivos[0] if arquivos else None


def primeira_coluna_existente(colunas, candidatos):
    return next((coluna for coluna in candidatos if coluna in colunas), None)


def normalizar_chaves(df, colunas):
    for coluna in colunas:
        df[coluna] = df[coluna].astype(str).str.replace('"', "", regex=False).str.strip()
    return df


def processar_ano_aluno(ano, cursos_validos):
    caminho = localizar_arquivo_aluno(ano)
    if caminho is None:
        print(f"[{ano}] Arquivo de alunos nao encontrado. Pulando.")
        return pd.DataFrame(columns=COLUNAS_SAIDA)
    if caminho.stat().st_size == 0:
        print(f"[{ano}] Arquivo de alunos esta vazio: {caminho}. Pulando.")
        return pd.DataFrame(columns=COLUNAS_SAIDA)

    delimitador = detectar_delimitador(caminho)
    print(f"[{ano}] Processando {caminho.name} com delimitador {delimitador!r}")

    header = pd.read_csv(
        caminho,
        sep=delimitador,
        encoding="latin1",
        nrows=0,
    ).columns

    col_situacao = primeira_coluna_existente(
        header,
        ["TP_SITUACAO", "TP_SITUACAO_VINCULO", "CO_ALUNO_SITUACAO"],
    )
    col_nivel = primeira_coluna_existente(
        header,
        ["TP_NIVEL_ACADEMICO", "CO_NIVEL_ACADEMICO"],
    )
    col_ies = primeira_coluna_existente(header, ["CO_IES"])
    col_curso = primeira_coluna_existente(header, ["CO_CURSO"])

    obrigatorias = {
        "situacao": col_situacao,
        "CO_IES": col_ies,
        "CO_CURSO": col_curso,
    }
    ausentes = [nome for nome, coluna in obrigatorias.items() if coluna is None]
    if ausentes:
        print(f"[{ano}] Colunas obrigatorias ausentes: {', '.join(ausentes)}. Pulando.")
        return pd.DataFrame(columns=COLUNAS_SAIDA)

    colunas_para_ler = [col_situacao, col_ies, col_curso]
    if col_nivel is not None:
        colunas_para_ler.append(col_nivel)

    chaves_ano = cursos_validos[cursos_validos["NU_ANO_CENSO"].eq(ano)][
        ["CO_IES", "CO_CURSO"]
    ].drop_duplicates()
    if chaves_ano.empty:
        print(f"[{ano}] Nenhum curso de Computacao encontrado na base comparavel.")
        return pd.DataFrame(columns=COLUNAS_SAIDA)

    chaves_ano = normalizar_chaves(chaves_ano.copy(), ["CO_IES", "CO_CURSO"])
    cursos_do_ano = set(chaves_ano["CO_CURSO"])

    contagens = []
    total_linhas_lidas = 0
    total_linhas_recorte = 0

    for chunk in pd.read_csv(
        caminho,
        sep=delimitador,
        encoding="latin1",
        dtype=str,
        usecols=colunas_para_ler,
        chunksize=250_000,
    ):
        total_linhas_lidas += len(chunk)
        normalizar_chaves(chunk, [col_ies, col_curso])

        if col_nivel is not None:
            chunk[col_nivel] = chunk[col_nivel].astype(str).str.strip()
            chunk = chunk[chunk[col_nivel].eq("1")]

        chunk = chunk[chunk[col_curso].isin(cursos_do_ano)]
        if chunk.empty:
            continue

        chunk = chunk.merge(
            chaves_ano,
            left_on=[col_ies, col_curso],
            right_on=["CO_IES", "CO_CURSO"],
            how="inner",
        )
        if chunk.empty:
            continue

        total_linhas_recorte += len(chunk)
        chunk["INDICADOR"] = chunk[col_situacao].astype(str).str.strip().map(
            MAPA_SITUACAO
        )
        chunk = chunk.dropna(subset=["INDICADOR"])
        if chunk.empty:
            continue

        contagem = (
            chunk.groupby(["CO_IES", "CO_CURSO", "INDICADOR"], dropna=False)
            .size()
            .reset_index(name="QTD")
        )
        contagens.append(contagem)

    print(f"[{ano}] Linhas lidas: {total_linhas_lidas:,}")
    print(f"[{ano}] Linhas no recorte Computacao/TIC: {total_linhas_recorte:,}")

    if not contagens:
        return pd.DataFrame(columns=COLUNAS_SAIDA)

    agregado = (
        pd.concat(contagens, ignore_index=True)
        .groupby(["CO_IES", "CO_CURSO", "INDICADOR"], dropna=False)["QTD"]
        .sum()
        .reset_index()
    )

    pivotado = (
        agregado.pivot(
            index=["CO_IES", "CO_CURSO"],
            columns="INDICADOR",
            values="QTD",
        )
        .fillna(0)
        .reset_index()
    )
    pivotado.columns.name = None
    pivotado["NU_ANO_CENSO"] = ano

    for coluna in COLUNAS_ALUNO:
        if coluna not in pivotado.columns:
            pivotado[coluna] = 0
        pivotado[coluna] = pd.to_numeric(pivotado[coluna], errors="coerce").fillna(0)

    pivotado["QT_ALUNO_TOTAL_VINCULOS"] = pivotado[COLUNAS_ALUNO].sum(axis=1)
    return pivotado[COLUNAS_SAIDA]


def main():
    if not BASE_CURSOS.exists():
        print(f"Base comparavel nao encontrada: {BASE_CURSOS}")
        print("Execute primeiro: .venv/bin/python scripts/08_validar_historico.py")
        return

    HISTORICO.mkdir(parents=True, exist_ok=True)
    cursos = pd.read_csv(BASE_CURSOS, sep=";", encoding="utf-8-sig", dtype=str)
    cursos_validos = cursos[CHAVE_CURSO].dropna().drop_duplicates()
    normalizar_chaves(cursos_validos, CHAVE_CURSO)

    resultados = []
    for ano in ANOS_ALVO:
        resultado_ano = processar_ano_aluno(ano, cursos_validos)
        if not resultado_ano.empty:
            resultados.append(resultado_ano)

    if not resultados:
        print("Nenhum arquivo de aluno foi processado. Etapa permanece em stand-by.")
        return

    base_alunos = (
        pd.concat(resultados, ignore_index=True)
        .groupby(CHAVE_CURSO, dropna=False)[COLUNAS_ALUNO + ["QT_ALUNO_TOTAL_VINCULOS"]]
        .sum()
        .reset_index()
        .sort_values(CHAVE_CURSO)
    )
    base_alunos.to_csv(SAIDA_ALUNOS, sep=";", index=False, encoding="utf-8-sig")

    print("Base quantitativa de alunos gerada:")
    print(SAIDA_ALUNOS)
    print(base_alunos.groupby("NU_ANO_CENSO")["CO_CURSO"].count())


if __name__ == "__main__":
    main()
