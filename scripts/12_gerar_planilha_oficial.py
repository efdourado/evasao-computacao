from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HISTORICO = ROOT / "data" / "processed" / "historico"
OUT = ROOT / "data" / "processed" / "oficial"

BASE_FINAL = HISTORICO / "computacao_historico_com_evasao.csv"
BASE_EXPANDIDA = HISTORICO / "computacao_historico_cursos.csv"

SAIDA_COMPARAVEL = OUT / "planilha_oficial_computacao.csv"
SAIDA_EXPANDIDA = OUT / "planilha_oficial_computacao_expandida.csv"
SAIDA_DICIONARIO = OUT / "dicionario_planilha_oficial.csv"

COLUNAS_COMPARAVEL = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "SG_IES",
    "CO_CURSO",
    "NO_CURSO",
    "NO_CURSO_NORMALIZADO",
    "DS_CRITERIO_ESCOPO",
    "DS_CLASSIFICACAO_AREA",
    "CO_AREA_GERAL",
    "NO_AREA_GERAL",
    "CO_AREA_ESPECIFICA",
    "NO_AREA_ESPECIFICA",
    "CO_AREA_DETALHADA",
    "NO_AREA_DETALHADA",
    "CO_ROTULO_AREA",
    "NO_ROTULO_AREA",
    "TP_GRAU_ACADEMICO",
    "DS_TP_GRAU_ACADEMICO",
    "TP_MODALIDADE_ENSINO",
    "DS_TP_MODALIDADE_ENSINO",
    "TP_CATEGORIA_ADMINISTRATIVA",
    "DS_TP_CATEGORIA_ADMINISTRATIVA",
    "TP_REDE",
    "DS_TP_REDE",
    "TP_ORGANIZACAO_ACADEMICA",
    "DS_TP_ORGANIZACAO_ACADEMICA",
    "QT_LINHAS_EXPANDIDAS",
    "IN_TEM_MULTIPLAS_LINHAS",
    "QT_UFS_DISTINTAS",
    "SG_UF_LISTA",
    "QT_MUNICIPIOS_DISTINTOS",
    "TP_DIMENSAO_LISTA",
    "DS_TP_DIMENSAO_LISTA",
    "IN_USAR_MAPA_MUNICIPAL",
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "QT_SIT_TRANCADA",
    "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO",
    "QT_SIT_FALECIDO",
    "TX_DESVINCULADO_SOBRE_MAT",
]

COLUNAS_EXPANDIDA = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "SG_IES",
    "CO_CURSO",
    "NO_CURSO",
    "DS_CRITERIO_ESCOPO",
    "DS_CLASSIFICACAO_AREA",
    "CO_AREA_GERAL",
    "NO_AREA_GERAL",
    "CO_ROTULO_AREA",
    "NO_ROTULO_AREA",
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

DICIONARIO = {
    "NU_ANO_CENSO": "Ano do Censo da Educação Superior.",
    "CO_IES": "Código da instituição no INEP.",
    "NO_IES": "Nome da instituição.",
    "SG_IES": "Sigla da instituição, quando disponível.",
    "CO_CURSO": "Código do curso no INEP.",
    "NO_CURSO": "Nome do curso.",
    "DS_CRITERIO_ESCOPO": "Critério usado para o curso entrar no recorte oficial.",
    "DS_CLASSIFICACAO_AREA": "Classificação de área usada no ano: CINE, CINE Brasil ou OCDE.",
    "CO_AREA_GERAL": "Código da área geral na classificação disponível no ano.",
    "NO_AREA_GERAL": "Nome da área geral na classificação disponível no ano.",
    "CO_ROTULO_AREA": "Código do rótulo CINE/OCDE usado no ano.",
    "NO_ROTULO_AREA": "Nome do rótulo CINE/OCDE usado no ano.",
    "DS_TP_MODALIDADE_ENSINO": "Modalidade do curso: presencial ou EaD.",
    "DS_TP_GRAU_ACADEMICO": "Grau acadêmico do curso.",
    "QT_LINHAS_EXPANDIDAS": "Quantidade de linhas territoriais/dimensionais agregadas no curso lógico.",
    "IN_TEM_MULTIPLAS_LINHAS": "Indica se o curso aparece em mais de uma linha na base expandida.",
    "QT_UFS_DISTINTAS": "Quantidade de UFs associadas ao curso na base expandida.",
    "SG_UF_LISTA": "Lista de UFs associadas ao curso na base expandida.",
    "QT_MUNICIPIOS_DISTINTOS": "Quantidade de municípios associados ao curso na base expandida.",
    "TP_DIMENSAO_LISTA": "Lista de dimensões territoriais associadas ao curso.",
    "IN_USAR_MAPA_MUNICIPAL": "Indica se o registro pode alimentar mapa municipal.",
    "QT_VG_TOTAL": "Total de vagas.",
    "QT_INSCRITO_TOTAL": "Total de inscritos, quando disponível.",
    "QT_ING": "Total de ingressantes.",
    "QT_MAT": "Total de matrículas.",
    "QT_CONC": "Total de concluintes.",
    "QT_SIT_TRANCADA": "Total de vínculos trancados, quando disponível/reconstruído.",
    "QT_SIT_DESVINCULADO": "Total de vínculos desvinculados, quando disponível/reconstruído.",
    "QT_SIT_TRANSFERIDO": "Total de vínculos transferidos, quando disponível/reconstruído.",
    "QT_SIT_FALECIDO": "Total de vínculos falecidos, quando disponível/reconstruído.",
    "TX_DESVINCULADO_SOBRE_MAT": "Indicador exploratório: desvinculados dividido por matrículas.",
}


def selecionar_colunas(df, colunas):
    return df[[coluna for coluna in colunas if coluna in df.columns]].copy()


def gerar_dicionario():
    linhas = [
        {"coluna": coluna, "descricao": descricao}
        for coluna, descricao in DICIONARIO.items()
    ]
    return pd.DataFrame(linhas)


def main():
    if not BASE_FINAL.exists():
        raise FileNotFoundError(
            "Base final nao encontrada. Execute primeiro o script 10."
        )
    if not BASE_EXPANDIDA.exists():
        raise FileNotFoundError(
            "Base expandida nao encontrada. Execute primeiro o script 07."
        )

    OUT.mkdir(parents=True, exist_ok=True)

    comparavel = pd.read_csv(BASE_FINAL, sep=";", encoding="utf-8-sig", dtype=str)
    expandida = pd.read_csv(BASE_EXPANDIDA, sep=";", encoding="utf-8-sig", dtype=str)

    selecionar_colunas(comparavel, COLUNAS_COMPARAVEL).to_csv(
        SAIDA_COMPARAVEL,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    selecionar_colunas(expandida, COLUNAS_EXPANDIDA).to_csv(
        SAIDA_EXPANDIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    gerar_dicionario().to_csv(
        SAIDA_DICIONARIO,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print("Planilhas oficiais geradas:")
    print(SAIDA_COMPARAVEL)
    print(SAIDA_EXPANDIDA)
    print(SAIDA_DICIONARIO)


if __name__ == "__main__":
    main()
