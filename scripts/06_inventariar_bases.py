from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SAIDA_INVENTARIO = PROCESSED / "inventario_bases_raw.csv"
SAIDA_COMPARACAO = PROCESSED / "comparacao_colunas_raw.csv"


PADROES = {
    "cursos": [
        "MICRODADOS_CADASTRO_CURSOS",
        "DM_CURSO",
        "SUP_CURSO",
    ],
    "ies": [
        "MICRODADOS_ED_SUP_IES",
        "DM_IES",
        "SUP_IES",
    ],
    "local_oferta": [
        "DM_LOCAL_OFERTA",
        "SUP_LOCAL_OFERTA",
    ],
    "aluno": [
        "MICRODADOS_CADASTRO_ALUNOS",
        "DM_ALUNO",
        "SUP_ALUNO",
    ],
    "docente": [
        "MICRODADOS_CADASTRO_DOCENTES",
        "DM_DOCENTE",
        "SUP_DOCENTE",
    ],
    "cine_brasil": [
        "TB_AUX_CINE_BRASIL",
    ],
    "ocde": [
        "TB_AUX_AREA_OCDE",
    ],
    "licenciatura": [
        "LICENCIATURA",
    ],
}

DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]


def contar_linhas_csv(caminho):
    with caminho.open("rb") as arquivo:
        return max(sum(1 for _ in arquivo) - 1, 0)


def detectar_delimitador(caminho):
    with caminho.open("rb") as arquivo:
        primeira_linha = arquivo.readline().decode("latin1", errors="replace")
    if not primeira_linha:
        return ""

    contagens = {
        delimitador: primeira_linha.count(delimitador)
        for delimitador in DELIMITADORES_CANDIDATOS
    }
    return max(contagens, key=contagens.get)


def ler_colunas_csv(caminho, delimitador):
    if caminho.stat().st_size == 0:
        return []

    return pd.read_csv(
        caminho,
        sep=delimitador,
        encoding="latin1",
        dtype=str,
        nrows=0,
    ).columns.tolist()


def ler_colunas_excel(caminho):
    planilha = pd.ExcelFile(caminho)
    aba = planilha.sheet_names[0]
    df = pd.read_excel(caminho, sheet_name=aba, dtype=str, nrows=0)
    return df.columns.tolist()


def contar_linhas_excel(caminho):
    planilha = pd.ExcelFile(caminho)
    aba = planilha.sheet_names[0]
    return len(pd.read_excel(caminho, sheet_name=aba, usecols=[0]))


def tipo_arquivo(caminho):
    nome = caminho.name.upper()
    for tipo, padroes in PADROES.items():
        if any(padrao in nome for padrao in padroes):
            return tipo
    return "outro"


def inventariar():
    registros = []

    for caminho in sorted(RAW.glob("*/*")):
        if not caminho.is_file():
            continue

        sufixo = caminho.suffix.lower()
        if sufixo not in [".csv", ".xlsx"]:
            continue

        ano = caminho.parent.name
        tipo = tipo_arquivo(caminho)
        delimitador = ""

        if sufixo == ".csv":
            delimitador = detectar_delimitador(caminho)
            colunas = ler_colunas_csv(caminho, delimitador)
            linhas = contar_linhas_csv(caminho)
        else:
            colunas = ler_colunas_excel(caminho)
            linhas = contar_linhas_excel(caminho)

        registros.append(
            {
                "ANO": ano,
                "TIPO": tipo,
                "ARQUIVO": str(caminho.relative_to(ROOT)),
                "DELIMITADOR": delimitador,
                "QTD_LINHAS": linhas,
                "QTD_COLUNAS": len(colunas),
                "COLUNAS": "|".join(colunas),
            }
        )

    return pd.DataFrame(registros)


def comparar_colunas(inventario):
    comparacoes = []
    referencia = inventario[inventario["ANO"].eq("2024")]

    for _, linha in inventario.iterrows():
        ref = referencia[referencia["TIPO"].eq(linha["TIPO"])]
        if ref.empty or linha["TIPO"] == "outro":
            continue

        colunas_ref = set(ref.iloc[0]["COLUNAS"].split("|"))
        colunas_atual = set(linha["COLUNAS"].split("|"))

        comparacoes.append(
            {
                "ANO": linha["ANO"],
                "TIPO": linha["TIPO"],
                "ARQUIVO": linha["ARQUIVO"],
                "QTD_COLUNAS": linha["QTD_COLUNAS"],
                "QTD_COLUNAS_REFERENCIA_2024": len(colunas_ref),
                "QTD_COLUNAS_AUSENTES_VS_2024": len(colunas_ref - colunas_atual),
                "QTD_COLUNAS_EXTRAS_VS_2024": len(colunas_atual - colunas_ref),
                "COLUNAS_AUSENTES_VS_2024": "|".join(sorted(colunas_ref - colunas_atual)),
                "COLUNAS_EXTRAS_VS_2024": "|".join(sorted(colunas_atual - colunas_ref)),
            }
        )

    return pd.DataFrame(comparacoes)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)

    inventario = inventariar()
    inventario.to_csv(SAIDA_INVENTARIO, sep=";", index=False, encoding="utf-8-sig")

    comparacao = comparar_colunas(inventario)
    comparacao.to_csv(SAIDA_COMPARACAO, sep=";", index=False, encoding="utf-8-sig")

    print("Inventário gerado:")
    print(SAIDA_INVENTARIO)
    print(
        inventario[
            ["ANO", "TIPO", "DELIMITADOR", "QTD_LINHAS", "QTD_COLUNAS", "ARQUIVO"]
        ]
    )

    print("\nComparação com 2024:")
    print(SAIDA_COMPARACAO)
    print(
        comparacao[
            [
                "ANO",
                "TIPO",
                "QTD_COLUNAS_AUSENTES_VS_2024",
                "QTD_COLUNAS_EXTRAS_VS_2024",
            ]
        ]
    )


if __name__ == "__main__":
    main()
