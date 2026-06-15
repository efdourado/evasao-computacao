from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HISTORICO = ROOT / "data" / "processed" / "historico"

BASE_CURSOS = HISTORICO / "computacao_historico_cursos_comparavel.csv"
BASE_ALUNOS = HISTORICO / "alunos_computacao_quantitativo.csv"
SAIDA_FINAL = HISTORICO / "computacao_historico_com_evasao.csv"
SAIDA_VALIDACAO = HISTORICO / "validacao_evasao_alunos_vs_cursos.csv"

CHAVE_CURSO = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]

MAPA_PREENCHIMENTO = {
    "QT_SIT_TRANCADA": "QT_ALUNO_TRANCADA",
    "QT_SIT_DESVINCULADO": "QT_ALUNO_DESVINCULADO",
    "QT_SIT_TRANSFERIDO": "QT_ALUNO_TRANSFERIDO",
    "QT_SIT_FALECIDO": "QT_ALUNO_FALECIDO",
}

COLUNAS_ALUNO = [
    "QT_ALUNO_CURSANDO",
    "QT_ALUNO_TRANCADA",
    "QT_ALUNO_DESVINCULADO",
    "QT_ALUNO_TRANSFERIDO",
    "QT_ALUNO_FORMADO",
    "QT_ALUNO_FALECIDO",
    "QT_ALUNO_TOTAL_VINCULOS",
]

COLUNAS_CURSO_SITUACAO = list(MAPA_PREENCHIMENTO.keys())


def normalizar_chaves(df):
    for coluna in CHAVE_CURSO:
        df[coluna] = df[coluna].astype(str).str.replace('"', "", regex=False).str.strip()
    return df


def converter_numericas(df, colunas):
    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = pd.NA
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df


def soma_minima(serie):
    return serie.sum(min_count=1)


def carregar_cursos():
    if not BASE_CURSOS.exists():
        raise FileNotFoundError(
            "Base comparavel nao encontrada. "
            "Execute primeiro: .venv/bin/python scripts/08_validar_historico.py"
        )

    cursos = pd.read_csv(BASE_CURSOS, sep=";", encoding="utf-8-sig", dtype=str)
    normalizar_chaves(cursos)
    converter_numericas(cursos, COLUNAS_CURSO_SITUACAO + ["QT_MAT", "QT_CONC"])
    return cursos


def carregar_alunos():
    if not BASE_ALUNOS.exists():
        print(f"Base quantitativa de alunos nao encontrada: {BASE_ALUNOS}")
        print("Etapa em stand-by. Execute o script 09 quando os arquivos de aluno existirem.")
        return None

    alunos = pd.read_csv(BASE_ALUNOS, sep=";", encoding="utf-8-sig", dtype=str)
    normalizar_chaves(alunos)
    converter_numericas(alunos, COLUNAS_ALUNO)

    return (
        alunos.groupby(CHAVE_CURSO, dropna=False)[COLUNAS_ALUNO]
        .sum(min_count=1)
        .reset_index()
    )


def gerar_validacao(df):
    agregacoes = {
        "QT_CURSOS_BASE_FINAL": ("CO_CURSO", "size"),
        "QT_CURSOS_COM_DADOS_ALUNO": ("QT_ALUNO_TOTAL_VINCULOS", "count"),
        "QT_MAT": ("QT_MAT", soma_minima),
        "QT_CONC": ("QT_CONC", soma_minima),
    }

    for coluna in COLUNAS_CURSO_SITUACAO + COLUNAS_ALUNO:
        if coluna in df.columns:
            agregacoes[coluna] = (coluna, soma_minima)

    validacao = (
        df.groupby("NU_ANO_CENSO", dropna=False)
        .agg(**agregacoes)
        .reset_index()
        .sort_values("NU_ANO_CENSO")
    )

    validacao["TX_DESVINCULADO_SOBRE_MAT_FINAL"] = (
        validacao["QT_SIT_DESVINCULADO"] / validacao["QT_MAT"]
    ).where(validacao["QT_MAT"] > 0)
    validacao["QT_ALUNO_CURSANDO_FORMADO"] = (
        validacao["QT_ALUNO_CURSANDO"] + validacao["QT_ALUNO_FORMADO"]
    )
    validacao["DIF_QT_MAT_VS_ALUNO_CURSANDO_FORMADO"] = (
        validacao["QT_MAT"] - validacao["QT_ALUNO_CURSANDO_FORMADO"]
    )
    validacao["DIF_QT_CONC_VS_ALUNO_FORMADO"] = (
        validacao["QT_CONC"] - validacao["QT_ALUNO_FORMADO"]
    )

    return validacao


def main():
    HISTORICO.mkdir(parents=True, exist_ok=True)

    cursos = carregar_cursos()
    alunos = carregar_alunos()
    if alunos is None:
        return

    print(f"Linhas na base comparavel de cursos: {len(cursos):,}")
    print(f"Linhas na base quantitativa de alunos: {len(alunos):,}")

    merged = cursos.merge(alunos, on=CHAVE_CURSO, how="left")

    for coluna_curso, coluna_aluno in MAPA_PREENCHIMENTO.items():
        merged[f"{coluna_curso}_ORIGINAL_CURSO"] = merged[coluna_curso]
        merged[coluna_curso] = merged[coluna_curso].combine_first(merged[coluna_aluno])

    merged["IN_SITUACAO_PREENCHIDA_POR_ALUNO"] = False
    for coluna_curso, coluna_aluno in MAPA_PREENCHIMENTO.items():
        original = f"{coluna_curso}_ORIGINAL_CURSO"
        preenchida = merged[original].isna() & merged[coluna_aluno].notna()
        merged["IN_SITUACAO_PREENCHIDA_POR_ALUNO"] = (
            merged["IN_SITUACAO_PREENCHIDA_POR_ALUNO"] | preenchida
        )

    merged["TX_DESVINCULADO_SOBRE_MAT"] = (
        merged["QT_SIT_DESVINCULADO"] / merged["QT_MAT"]
    ).where(merged["QT_MAT"] > 0)

    validacao = gerar_validacao(merged)

    merged.to_csv(SAIDA_FINAL, sep=";", index=False, encoding="utf-8-sig")
    validacao.to_csv(SAIDA_VALIDACAO, sep=";", index=False, encoding="utf-8-sig")

    print("Base historica com situacao academica gerada:")
    print(SAIDA_FINAL)
    print("Validacao gerada:")
    print(SAIDA_VALIDACAO)
    print(validacao)


if __name__ == "__main__":
    main()
