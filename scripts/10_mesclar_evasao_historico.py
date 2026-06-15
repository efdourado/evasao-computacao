from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HISTORICO = ROOT / "data" / "processed" / "historico"

BASE_CURSOS = HISTORICO / "computacao_historico_cursos_comparavel.csv"
BASE_ALUNOS = HISTORICO / "alunos_computacao_quantitativo.csv"
SAIDA_FINAL = HISTORICO / "computacao_historico_com_evasao.csv"


def main():
    if not BASE_CURSOS.exists() or not BASE_ALUNOS.exists():
        print("Erro: Bases necessárias não encontradas.")
        return

    print("Carregando bases...")
    df_cursos = pd.read_csv(BASE_CURSOS, sep=";", encoding="utf-8-sig", dtype=str)
    df_alunos = pd.read_csv(BASE_ALUNOS, sep=";", encoding="utf-8-sig", dtype=str)

    # Converte para numérico na base de cursos
    colunas_sit_curso = ["QT_SIT_TRANCADA", "QT_SIT_DESVINCULADO", "QT_SIT_TRANSFERIDO"]
    for col in colunas_sit_curso:
        df_cursos[col] = pd.to_numeric(df_cursos[col], errors="coerce")

    # Converte para numérico na base de alunos recém gerada
    colunas_sit_aluno = ["QT_TRANCADO", "QT_DESVINCULADO", "QT_TRANSFERIDO", "QT_CURSANDO", "QT_FORMADO"]
    for col in colunas_sit_aluno:
        df_alunos[col] = pd.to_numeric(df_alunos[col], errors="coerce")

    print(f"Linhas na base de cursos (comparável): {len(df_cursos)}")
    print(f"Linhas extraídas de alunos: {len(df_alunos)}")

    # Faz o cruzamento (Merge Left para garantir que nenhum curso suma)
    df_merged = df_cursos.merge(
        df_alunos, 
        on=["NU_ANO_CENSO", "CO_IES", "CO_CURSO"], 
        how="left"
    )

    # Preenche as lacunas de 2017-2019 com os dados extraídos de DM_ALUNO
    df_merged["QT_SIT_TRANCADA"] = df_merged["QT_SIT_TRANCADA"].fillna(df_merged["QT_TRANCADO"])
    df_merged["QT_SIT_DESVINCULADO"] = df_merged["QT_SIT_DESVINCULADO"].fillna(df_merged["QT_DESVINCULADO"])
    df_merged["QT_SIT_TRANSFERIDO"] = df_merged["QT_SIT_TRANSFERIDO"].fillna(df_merged["QT_TRANSFERIDO"])

    # Salva a base suprema pronta para análise
    df_merged.to_csv(SAIDA_FINAL, sep=";", index=False, encoding="utf-8-sig")

    print("\nMerge concluído com sucesso!")
    print(f"Arquivo final salvo em: {SAIDA_FINAL}")
    
    print("\nPrévia de dados de Evasão preenchidos (Não nulos por ano):")
    print(df_merged.groupby("NU_ANO_CENSO")["QT_SIT_DESVINCULADO"].count())


if __name__ == "__main__":
    main()