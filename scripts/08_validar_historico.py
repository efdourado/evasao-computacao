from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HISTORICO = ROOT / "data" / "processed" / "historico"

BASE_EXPANDIDA = HISTORICO / "computacao_historico_cursos.csv"
BASE_COMPARAVEL = HISTORICO / "computacao_historico_cursos_comparavel.csv"

SAIDA_VALIDACAO_ANO = HISTORICO / "validacao_historico_por_ano.csv"
SAIDA_VALIDACAO_METRICAS = HISTORICO / "validacao_historico_metricas.csv"
SAIDA_VALIDACAO_DIMENSAO = HISTORICO / "validacao_historico_dimensao_metricas.csv"
SAIDA_LINHAS_CURSO = HISTORICO / "validacao_linhas_por_curso.csv"
SAIDA_TOP_MULTILINHAS = HISTORICO / "validacao_top_cursos_multilinhas.csv"

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


def soma_minima(serie):
    return pd.to_numeric(serie, errors="coerce").sum(min_count=1)


def maximo_minimo(serie):
    serie = pd.to_numeric(serie, errors="coerce")
    if serie.notna().any():
        return serie.max()
    return pd.NA


def primeiro_valido(serie):
    serie = serie.dropna()
    serie = serie[serie.astype(str).str.strip().ne("")]
    if serie.empty:
        return pd.NA
    return serie.iloc[0]


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


def divisao_segura(numerador, denominador):
    if pd.isna(numerador) or pd.isna(denominador) or denominador == 0:
        return pd.NA
    return numerador / denominador


def subtracao_segura(numerador, denominador):
    if pd.isna(numerador) or pd.isna(denominador):
        return pd.NA
    return numerador - denominador


def valor_serie(serie, chave):
    valor = serie.get(chave, pd.NA)
    if valor is None:
        return pd.NA
    return valor


def metricas_disponiveis(base):
    return [coluna for coluna in NUMERICAS if coluna in base.columns]


def carregar_base_expandida():
    if not BASE_EXPANDIDA.exists():
        raise FileNotFoundError(
            "Base histórica expandida não encontrada. "
            "Execute primeiro: .venv/bin/python scripts/07_consolidar_historico_cursos.py"
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

    codigo_municipio = base.get(
        "CO_MUNICIPIO", pd.Series(pd.NA, index=base.index)
    ).fillna("")
    nome_municipio = base.get(
        "NO_MUNICIPIO", pd.Series(pd.NA, index=base.index)
    ).fillna("")
    codigo_municipio = codigo_municipio.astype(str).str.strip()
    nome_municipio = nome_municipio.astype(str).str.strip()

    base["ID_MUNICIPIO_VALIDACAO"] = codigo_municipio.mask(
        codigo_municipio.eq("") | codigo_municipio.str.lower().eq("nan"),
        nome_municipio,
    )

    return base


def gerar_linhas_por_curso(base):
    metricas = metricas_disponiveis(base)
    agregacoes = {
        "NO_IES": ("NO_IES", primeiro_valido),
        "NO_CURSO": ("NO_CURSO", primeiro_valido),
        "DS_TP_MODALIDADE_ENSINO": ("DS_TP_MODALIDADE_ENSINO", primeiro_valido),
        "QT_LINHAS_POR_CURSO": ("CO_CURSO", "size"),
        "QT_UFS_DISTINTAS": ("SG_UF", contar_unicos),
        "SG_UF_LISTA": ("SG_UF", valores_unicos),
        "QT_MUNICIPIOS_DISTINTOS": ("ID_MUNICIPIO_VALIDACAO", contar_unicos),
        "TP_DIMENSAO_LISTA": ("TP_DIMENSAO", valores_unicos),
        "DS_TP_DIMENSAO_LISTA": ("DS_TP_DIMENSAO", valores_unicos),
    }

    linhas = (
        base.groupby(CHAVE_CURSO, dropna=False)
        .agg(**agregacoes)
        .reset_index()
    )

    if metricas:
        grupo_metricas = base.groupby(CHAVE_CURSO, dropna=False)[metricas]
        somas = grupo_metricas.sum(min_count=1).add_suffix("_SOMA_LINHAS")
        maximos = grupo_metricas.max().add_suffix("_MAX_LINHA")
        linhas = (
            linhas.merge(somas.reset_index(), on=CHAVE_CURSO, how="left")
            .merge(maximos.reset_index(), on=CHAVE_CURSO, how="left")
        )

    linhas["IN_TEM_MULTIPLAS_LINHAS"] = linhas["QT_LINHAS_POR_CURSO"] > 1

    for metrica in metricas:
        soma = f"{metrica}_SOMA_LINHAS"
        maximo = f"{metrica}_MAX_LINHA"
        diferenca = f"DIF_{metrica}_SOMA_MENOS_MAX"
        linhas[diferenca] = linhas[soma] - linhas[maximo]

    return linhas.sort_values(
        ["NU_ANO_CENSO", "QT_LINHAS_POR_CURSO", "CO_IES", "CO_CURSO"],
        ascending=[True, False, True, True],
    )


def gerar_base_comparavel(base):
    metricas = metricas_disponiveis(base)
    agregacoes = {
        coluna: (coluna, primeiro_valido)
        for coluna in COLUNAS_IDENTIFICACAO
        if coluna in base.columns
    }

    agregacoes.update(
        {
            "QT_LINHAS_EXPANDIDAS": ("CO_CURSO", "size"),
            "QT_UFS_DISTINTAS": ("SG_UF", contar_unicos),
            "SG_UF_LISTA": ("SG_UF", valores_unicos),
            "QT_MUNICIPIOS_DISTINTOS": ("ID_MUNICIPIO_VALIDACAO", contar_unicos),
            "TP_DIMENSAO_LISTA": ("TP_DIMENSAO", valores_unicos),
            "DS_TP_DIMENSAO_LISTA": ("DS_TP_DIMENSAO", valores_unicos),
            "DS_NIVEL_GEOGRAFICO_LISTA": ("DS_NIVEL_GEOGRAFICO", valores_unicos),
            "IN_USAR_MAPA_MUNICIPAL": ("IN_USAR_MAPA_MUNICIPAL", algum_verdadeiro),
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

    comparavel["IN_TEM_MULTIPLAS_LINHAS"] = comparavel["QT_LINHAS_EXPANDIDAS"] > 1

    colunas_ordenadas = (
        CHAVE_CURSO
        + [col for col in COLUNAS_IDENTIFICACAO if col in comparavel.columns]
        + [
            "QT_LINHAS_EXPANDIDAS",
            "IN_TEM_MULTIPLAS_LINHAS",
            "QT_UFS_DISTINTAS",
            "SG_UF_LISTA",
            "QT_MUNICIPIOS_DISTINTOS",
            "TP_DIMENSAO_LISTA",
            "DS_TP_DIMENSAO_LISTA",
            "DS_NIVEL_GEOGRAFICO_LISTA",
            "IN_USAR_MAPA_MUNICIPAL",
        ]
        + [col for col in NUMERICAS if col in comparavel.columns]
    )

    return comparavel[colunas_ordenadas].sort_values(CHAVE_CURSO)


def gerar_validacao_metricas(base):
    anos = sorted(base["NU_ANO_CENSO"].dropna().unique())
    linhas = []

    for metrica in NUMERICAS:
        if metrica not in base.columns:
            continue

        expandida = base.groupby("NU_ANO_CENSO", dropna=False)[metrica].sum(min_count=1)
        linhas_com_valor = base.groupby("NU_ANO_CENSO", dropna=False)[metrica].count()

        grupo_curso = base.groupby(CHAVE_CURSO, dropna=False)[metrica]
        por_curso = pd.concat(
            [
                grupo_curso.sum(min_count=1).rename("SOMA_CURSO"),
                grupo_curso.max().rename("MAX_CURSO"),
                grupo_curso.count().rename("QT_LINHAS_COM_VALOR"),
            ],
            axis=1,
        ).reset_index()

        agregada_soma = por_curso.groupby("NU_ANO_CENSO", dropna=False)["SOMA_CURSO"].sum(
            min_count=1
        )
        agregada_max = por_curso.groupby("NU_ANO_CENSO", dropna=False)["MAX_CURSO"].sum(
            min_count=1
        )
        cursos_com_valor = (
            por_curso[por_curso["QT_LINHAS_COM_VALOR"] > 0]
            .groupby("NU_ANO_CENSO", dropna=False)
            .size()
        )

        for ano in anos:
            soma_expandida = valor_serie(expandida, ano)
            soma_agregada = valor_serie(agregada_soma, ano)
            soma_max = valor_serie(agregada_max, ano)

            linhas.append(
                {
                    "NU_ANO_CENSO": ano,
                    "METRICA": metrica,
                    "QT_LINHAS_COM_VALOR": linhas_com_valor.get(ano, 0),
                    "QT_CURSOS_COM_VALOR": cursos_com_valor.get(ano, 0),
                    "SOMA_EXPANDIDA": soma_expandida,
                    "SOMA_AGREGADA_CURSO_SOMA": soma_agregada,
                    "DIF_EXPANDIDA_VS_AGREGADA_SOMA": subtracao_segura(
                        soma_expandida, soma_agregada
                    ),
                    "SOMA_AGREGADA_CURSO_MAX": soma_max,
                    "DIF_EXPANDIDA_VS_AGREGADA_MAX": subtracao_segura(
                        soma_expandida, soma_max
                    ),
                    "RAZAO_EXPANDIDA_SOBRE_MAX_CURSO": divisao_segura(
                        soma_expandida, soma_max
                    ),
                }
            )

    return pd.DataFrame(linhas)


def gerar_validacao_por_ano(base, linhas_por_curso, validacao_metricas):
    resumo_linhas = (
        linhas_por_curso.groupby("NU_ANO_CENSO", dropna=False)
        .agg(
            QT_CURSO_IES_DISTINTOS=("CO_CURSO", "size"),
            MEDIA_LINHAS_POR_CURSO=("QT_LINHAS_POR_CURSO", "mean"),
            MEDIANA_LINHAS_POR_CURSO=("QT_LINHAS_POR_CURSO", "median"),
            P95_LINHAS_POR_CURSO=("QT_LINHAS_POR_CURSO", lambda serie: serie.quantile(0.95)),
            MAX_LINHAS_POR_CURSO=("QT_LINHAS_POR_CURSO", "max"),
            QT_CURSOS_MULTILINHAS=("IN_TEM_MULTIPLAS_LINHAS", "sum"),
        )
        .reset_index()
    )
    resumo_linhas["PCT_CURSOS_MULTILINHAS"] = (
        resumo_linhas["QT_CURSOS_MULTILINHAS"] / resumo_linhas["QT_CURSO_IES_DISTINTOS"]
    )

    resumo_base = (
        base.groupby("NU_ANO_CENSO", dropna=False)
        .agg(
            QT_LINHAS_EXPANDIDA=("CO_CURSO", "size"),
            QT_CURSOS_DISTINTOS_CO_CURSO=("CO_CURSO", "nunique"),
            QT_IES_DISTINTAS=("CO_IES", "nunique"),
        )
        .reset_index()
    )

    qt_mat = validacao_metricas[validacao_metricas["METRICA"].eq("QT_MAT")].copy()
    qt_mat = qt_mat.rename(
        columns={
            "SOMA_EXPANDIDA": "SOMA_QT_MAT_EXPANDIDA",
            "SOMA_AGREGADA_CURSO_SOMA": "SOMA_QT_MAT_AGREGADA_CURSO_SOMA",
            "DIF_EXPANDIDA_VS_AGREGADA_SOMA": "DIF_QT_MAT_EXPANDIDA_VS_AGREGADA_SOMA",
            "SOMA_AGREGADA_CURSO_MAX": "SOMA_QT_MAT_AGREGADA_CURSO_MAX",
            "DIF_EXPANDIDA_VS_AGREGADA_MAX": "DIF_QT_MAT_EXPANDIDA_VS_AGREGADA_MAX",
            "RAZAO_EXPANDIDA_SOBRE_MAX_CURSO": "RAZAO_QT_MAT_EXPANDIDA_SOBRE_MAX_CURSO",
        }
    )
    qt_mat = qt_mat[
        [
            "NU_ANO_CENSO",
            "SOMA_QT_MAT_EXPANDIDA",
            "SOMA_QT_MAT_AGREGADA_CURSO_SOMA",
            "DIF_QT_MAT_EXPANDIDA_VS_AGREGADA_SOMA",
            "SOMA_QT_MAT_AGREGADA_CURSO_MAX",
            "DIF_QT_MAT_EXPANDIDA_VS_AGREGADA_MAX",
            "RAZAO_QT_MAT_EXPANDIDA_SOBRE_MAX_CURSO",
        ]
    ]

    return (
        resumo_base.merge(resumo_linhas, on="NU_ANO_CENSO", how="left")
        .merge(qt_mat, on="NU_ANO_CENSO", how="left")
        .sort_values("NU_ANO_CENSO")
    )


def gerar_validacao_dimensao(base):
    colunas_grupo = ["NU_ANO_CENSO", "TP_DIMENSAO", "DS_TP_DIMENSAO"]
    agregacoes = {
        "QT_LINHAS_EXPANDIDA": ("CO_CURSO", "size"),
        "QT_CURSOS_DISTINTOS_CO_CURSO": ("CO_CURSO", "nunique"),
        "QT_IES_DISTINTAS": ("CO_IES", "nunique"),
        "QT_UFS_DISTINTAS": ("SG_UF", contar_unicos),
        "QT_MUNICIPIOS_DISTINTOS": ("ID_MUNICIPIO_VALIDACAO", contar_unicos),
    }
    agregacoes.update({coluna: (coluna, soma_minima) for coluna in NUMERICAS})

    validacao = (
        base.groupby(colunas_grupo, dropna=False)
        .agg(**agregacoes)
        .reset_index()
        .sort_values(colunas_grupo, na_position="last")
    )
    validacao["TP_DIMENSAO"] = validacao["TP_DIMENSAO"].fillna("SEM_TP_DIMENSAO")
    validacao["DS_TP_DIMENSAO"] = validacao["DS_TP_DIMENSAO"].fillna(
        "Sem TP_DIMENSAO"
    )
    return validacao


def gerar_top_multilinhas(linhas_por_curso, limite_por_ano=20):
    top = linhas_por_curso[linhas_por_curso["IN_TEM_MULTIPLAS_LINHAS"]].copy()
    if top.empty:
        return top

    top = top.sort_values(
        ["NU_ANO_CENSO", "QT_LINHAS_POR_CURSO"],
        ascending=[True, False],
    )
    return top.groupby("NU_ANO_CENSO", group_keys=False).head(limite_por_ano)


def main():
    HISTORICO.mkdir(parents=True, exist_ok=True)

    base = carregar_base_expandida()
    linhas_por_curso = gerar_linhas_por_curso(base)
    base_comparavel = gerar_base_comparavel(base)
    validacao_metricas = gerar_validacao_metricas(base)
    validacao_ano = gerar_validacao_por_ano(base, linhas_por_curso, validacao_metricas)
    validacao_dimensao = gerar_validacao_dimensao(base)
    top_multilinhas = gerar_top_multilinhas(linhas_por_curso)

    base_comparavel.to_csv(BASE_COMPARAVEL, sep=";", index=False, encoding="utf-8-sig")
    validacao_ano.to_csv(SAIDA_VALIDACAO_ANO, sep=";", index=False, encoding="utf-8-sig")
    validacao_metricas.to_csv(
        SAIDA_VALIDACAO_METRICAS, sep=";", index=False, encoding="utf-8-sig"
    )
    validacao_dimensao.to_csv(
        SAIDA_VALIDACAO_DIMENSAO, sep=";", index=False, encoding="utf-8-sig"
    )
    linhas_por_curso.to_csv(SAIDA_LINHAS_CURSO, sep=";", index=False, encoding="utf-8-sig")
    top_multilinhas.to_csv(
        SAIDA_TOP_MULTILINHAS, sep=";", index=False, encoding="utf-8-sig"
    )

    print("Validação histórica gerada.")
    print(f"Base expandida: {BASE_EXPANDIDA}")
    print(f"Base comparável por curso: {BASE_COMPARAVEL}")
    print(f"Validação por ano: {SAIDA_VALIDACAO_ANO}")
    print("\nResumo por ano:")
    print(validacao_ano)


if __name__ == "__main__":
    main()
