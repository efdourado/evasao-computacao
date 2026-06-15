from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
HISTORICO = PROCESSED / "historico"

BASE_CURSOS = HISTORICO / "computacao_historico_cursos_comparavel.csv"
SAIDA_ALUNOS = HISTORICO / "alunos_computacao_quantitativo.csv"

DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]

MAPA_SITUACAO = {
    "2": "QT_CURSANDO",
    "3": "QT_TRANCADO",
    "4": "QT_DESVINCULADO",
    "5": "QT_TRANSFERIDO",
    "6": "QT_FORMADO",
}

COLUNAS_SAIDA = [
    "NU_ANO_CENSO",
    "CO_IES",
    "CO_CURSO",
    "QT_CURSANDO",
    "QT_TRANCADO",
    "QT_DESVINCULADO",
    "QT_TRANSFERIDO",
    "QT_FORMADO",
]


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

    for candidato in candidatos:
        caminho = pasta_ano / candidato
        if caminho.exists():
            return caminho

    # Tenta achar qualquer arquivo que contenha 'ALUNO' no nome
    arquivos = list(pasta_ano.glob("*ALUNO*.CSV")) + list(pasta_ano.glob("*ALUNO*.csv"))
    return arquivos[0] if arquivos else None


def processar_ano_aluno(ano, cursos_validos):
    caminho = localizar_arquivo_aluno(ano)
    if not caminho:
        print(f"[{ano}] Arquivo de alunos não encontrado. Pulando...")
        return pd.DataFrame()

    delimitador = detectar_delimitador(caminho)
    print(f"[{ano}] Processando: {caminho.name} (Delimitador: '{delimitador}')")

    # Lê apenas o cabeçalho para descobrir o nome exato das colunas
    header = pd.read_csv(caminho, sep=delimitador, encoding="latin1", nrows=0).columns
    
    # Harmonização dos nomes de colunas ao longo dos anos
    col_situacao = next((c for c in ["TP_SITUACAO_VINCULO", "CO_ALUNO_SITUACAO", "TP_SITUACAO"] if c in header), None)
    col_nivel = next((c for c in ["TP_NIVEL_ACADEMICO", "CO_NIVEL_ACADEMICO"] if c in header), None)
    col_curso = "CO_CURSO"
    col_ies = "CO_IES"

    if not col_situacao:
        print(f"[{ano}] ERRO: Coluna de situação de vínculo não encontrada. Pulando...")
        return pd.DataFrame()

    colunas_para_ler = [c for c in [col_situacao, col_nivel, col_curso, col_ies] if c is not None]

    # Para otimização de memória, converte o set de cursos válidos do ano atual
    cursos_do_ano = set(cursos_validos[cursos_validos["NU_ANO_CENSO"].eq(ano)]["CO_CURSO"])
    if not cursos_do_ano:
        print(f"[{ano}] Nenhum curso de Computação encontrado na base histórica para este ano.")
        return pd.DataFrame()

    chunks_processados = []
    total_linhas_lidas = 0

    # Lê o arquivo enorme em pedaços de 100.000 linhas
    for chunk in pd.read_csv(
        caminho,
        sep=delimitador,
        encoding="latin1",
        dtype=str,
        usecols=colunas_para_ler,
        chunksize=100000,
    ):
        total_linhas_lidas += len(chunk)

        # 1. Filtra graduação (se a coluna existir no ano)
        if col_nivel:
            chunk = chunk[chunk[col_nivel].eq("1")]

        # 2. Filtra apenas os cursos de computação
        chunk = chunk[chunk[col_curso].isin(cursos_do_ano)]

        # Se não sobrou nada no chunk após o filtro, pula para o próximo
        if chunk.empty:
            continue

        # 3. Mapeia a situação do vínculo
        chunk["INDICADOR"] = chunk[col_situacao].map(MAPA_SITUACAO)
        
        # Descarta situações que não estamos mapeando (ex: falecidos, etc)
        chunk = chunk.dropna(subset=["INDICADOR"])

        # 4. Conta os alunos por curso, IES e situação neste chunk
        contagem_chunk = chunk.groupby([col_ies, col_curso, "INDICADOR"]).size().reset_index(name="QTD")
        chunks_processados.append(contagem_chunk)

    print(f"[{ano}] Lidas {total_linhas_lidas:,} linhas. Agregando resultados...")

    if not chunks_processados:
        return pd.DataFrame()

    # Junta as contagens de todos os chunks
    todas_contagens = pd.concat(chunks_processados, ignore_index=True)
    
    # Agrega novamente (pois o mesmo curso pode ter aparecido em múltiplos chunks)
    agregado_final = todas_contagens.groupby([col_ies, col_curso, "INDICADOR"])["QTD"].sum().reset_index()

    # 5. Pivota a tabela para transformar as situações em colunas (QT_CURSANDO, QT_TRANCADO, etc)
    df_pivotado = agregado_final.pivot(
        index=[col_ies, col_curso], 
        columns="INDICADOR", 
        values="QTD"
    ).fillna(0).astype(int).reset_index()

    df_pivotado["NU_ANO_CENSO"] = ano

    return df_pivotado


def main():
    if not BASE_CURSOS.exists():
        print(f"Erro: Base de cursos não encontrada ({BASE_CURSOS}).")
        print("Execute primeiro o script '08_validar_historico.py'.")
        return

    print("Carregando lista de cursos de Computação válidos...")
    df_cursos = pd.read_csv(BASE_CURSOS, sep=";", encoding="utf-8-sig", dtype=str)
    cursos_validos = df_cursos[["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]].dropna().drop_duplicates()

    anos_alvo = ["2017", "2018", "2019", "2022", "2024"]
    resultados_anos = []

    for ano in anos_alvo:
        df_ano = processar_ano_aluno(ano, cursos_validos)
        if not df_ano.empty:
            resultados_anos.append(df_ano)

    if resultados_anos:
        print("\nConsolidando série histórica de alunos...")
        base_final = pd.concat(resultados_anos, ignore_index=True)

        # Garante que todas as colunas de saída existam, mesmo que fiquem com 0
        for col in COLUNAS_SAIDA:
            if col not in base_final.columns:
                base_final[col] = 0

        # Reordena e salva
        base_final = base_final[COLUNAS_SAIDA].sort_values(["NU_ANO_CENSO", "CO_IES", "CO_CURSO"])
        base_final.to_csv(SAIDA_ALUNOS, sep=";", index=False, encoding="utf-8-sig")
        
        print(f"\nSucesso! Arquivo gerado: {SAIDA_ALUNOS}")
        print(base_final.head())
    else:
        print("\nNenhum dado quantitativo de alunos foi extraído.")


if __name__ == "__main__":
    main()