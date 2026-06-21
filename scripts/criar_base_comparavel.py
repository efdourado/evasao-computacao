from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "data" / "processed" / ".pipeline"

BASE_EXPANDIDA = PIPELINE / "cursos_expandida.csv"
BASE_COMPARAVEL = PIPELINE / "cursos_comparavel.csv"

CHAVE_CURSO = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]

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

COLUNAS_IDENTIFICACAO = [
    "DS_MODELO_DADOS",
    "DS_CLASSIFICACAO_AREA",
    "DS_NIVEL_COMPARABILIDADE",
    "DS_OBSERVACAO_COMPARABILIDADE",
    "NO_IES",
    "SG_IES",
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
    "CO_AREA_GERAL",
    "NO_AREA_GERAL",
    "CO_AREA_ESPECIFICA",
    "NO_AREA_ESPECIFICA",
    "CO_AREA_DETALHADA",
    "NO_AREA_DETALHADA",
    "CO_ROTULO_AREA",
    "NO_ROTULO_AREA",
    "DS_CRITERIO_ESCOPO",
]


def valores_unicos(serie):
    valores = {
        str(valor).strip()
        for valor in serie.dropna()
        if str(valor).strip() and str(valor).strip().lower() != "nan"
    }
    return "|".join(sorted(valores))


def contar_unicos(serie):
    return len(
        {
            str(valor).strip()
            for valor in serie.dropna()
            if str(valor).strip() and str(valor).strip().lower() != "nan"
        }
    )


def algum_verdadeiro(serie):
    return (
        serie.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "sim", "yes"])
        .any()
    )


def carregar_base_expandida():
    if not BASE_EXPANDIDA.exists():
        raise FileNotFoundError(
            "Cursos consolidados nao encontrados. Execute consolidar_cursos.py."
        )

    base = pd.read_csv(
        BASE_EXPANDIDA,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        low_memory=False,
    )

    for coluna in NUMERICAS:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(base[coluna], errors="coerce")

    codigo = base.get("CO_MUNICIPIO", pd.Series(pd.NA, index=base.index)).fillna("")
    nome = base.get("NO_MUNICIPIO", pd.Series(pd.NA, index=base.index)).fillna("")
    codigo = codigo.astype(str).str.strip()
    nome = nome.astype(str).str.strip()
    base["ID_MUNICIPIO"] = codigo.mask(
        codigo.eq("") | codigo.str.lower().eq("nan"),
        nome,
    )
    return base


def gerar_base_comparavel(base):
    metricas = [coluna for coluna in NUMERICAS if coluna in base.columns]
    agregacoes = {
        coluna: (coluna, "first")
        for coluna in COLUNAS_IDENTIFICACAO
        if coluna in base.columns
    }
    agregacoes.update(
        {
            "QT_LINHAS_EXPANDIDAS": ("CO_CURSO", "size"),
            "QT_UFS_DISTINTAS": ("SG_UF", contar_unicos),
            "SG_UF_LISTA": ("SG_UF", valores_unicos),
            "QT_MUNICIPIOS_DISTINTOS": ("ID_MUNICIPIO", contar_unicos),
            "TP_DIMENSAO_LISTA": ("TP_DIMENSAO", valores_unicos),
            "DS_TP_DIMENSAO_LISTA": ("DS_TP_DIMENSAO", valores_unicos),
            "IN_USAR_MAPA_MUNICIPAL": (
                "IN_USAR_MAPA_MUNICIPAL",
                algum_verdadeiro,
            ),
        }
    )

    comparavel = (
        base.groupby(CHAVE_CURSO, dropna=False)
        .agg(**agregacoes)
        .reset_index()
    )

    if metricas:
        somas = (
            base.groupby(CHAVE_CURSO, dropna=False)[metricas]
            .sum(min_count=1)
            .reset_index()
        )
        comparavel = comparavel.merge(somas, on=CHAVE_CURSO, how="left")

    comparavel["IN_TEM_MULTIPLAS_LINHAS"] = (
        comparavel["QT_LINHAS_EXPANDIDAS"] > 1
    )

    ordem = (
        CHAVE_CURSO
        + [coluna for coluna in COLUNAS_IDENTIFICACAO if coluna in comparavel.columns]
        + [
            "QT_LINHAS_EXPANDIDAS",
            "IN_TEM_MULTIPLAS_LINHAS",
            "QT_UFS_DISTINTAS",
            "SG_UF_LISTA",
            "QT_MUNICIPIOS_DISTINTOS",
            "TP_DIMENSAO_LISTA",
            "DS_TP_DIMENSAO_LISTA",
            "IN_USAR_MAPA_MUNICIPAL",
        ]
        + metricas
    )
    return comparavel[ordem].sort_values(CHAVE_CURSO)


def main():
    PIPELINE.mkdir(parents=True, exist_ok=True)
    comparavel = gerar_base_comparavel(carregar_base_expandida())
    comparavel.to_csv(
        BASE_COMPARAVEL,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    print("Base comparavel criada:")
    print(BASE_COMPARAVEL)
    print(comparavel.shape)


if __name__ == "__main__":
    main()
