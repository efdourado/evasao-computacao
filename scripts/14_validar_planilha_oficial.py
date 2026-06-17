from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OFICIAL = ROOT / "data" / "processed" / "oficial"
OUT = ROOT / "data" / "processed" / "validacao_oficial"

ARQ_COMPARAVEL = OFICIAL / "planilha_oficial_computacao.csv"
ARQ_EXPANDIDA = OFICIAL / "planilha_oficial_computacao_expandida.csv"

SAIDAS = {
    "resumo": OUT / "01_resumo_geral.csv",
    "duplicatas": OUT / "02_duplicatas_chave.csv",
    "nulos": OUT / "03_nulos_colunas_criticas.csv",
    "ies_conflitos": OUT / "04_instituicoes_nomes_conflitantes.csv",
    "curso_conflitos": OUT / "05_cursos_nomes_conflitantes.csv",
    "recorte_invalido": OUT / "06_recorte_cine_invalido.csv",
    "metricas": OUT / "07_metricas_negativas_ou_estranhas.csv",
    "sensiveis": OUT / "08_colunas_sensiveis_detectadas.csv",
    "comparacao": OUT / "09_comparacao_oficial_vs_expandida.csv",
    "relatorio": OUT / "relatorio_validacao_oficial.md",
}

CHAVE = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]
COLUNAS_CRITICAS = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO", "NO_IES", "NO_CURSO"]
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
    "TX_DESVINCULADO_SOBRE_MAT",
]
COLUNAS_PROIBIDAS = [
    "ID_ALUNO",
    "CO_ALUNO",
    "CPF",
    "ID_DOCENTE",
    "CO_DOCENTE",
    "NO_ALUNO",
    "NU_CPF",
]
ANOS_OFICIAIS = set(str(ano) for ano in range(2009, 2025))


def carregar_csv(caminho):
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")
    return pd.read_csv(caminho, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)


def texto_limpo(serie):
    return serie.fillna("").astype(str).str.strip()


def codigo_limpo(serie):
    return texto_limpo(serie).str.replace('"', "", regex=False).str.upper()


def salvar(df, caminho, colunas=None):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if colunas is not None:
        for coluna in colunas:
            if coluna not in df.columns:
                df[coluna] = pd.NA
        df = df[colunas]
    df.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")


def n_unicos_validos(serie):
    valores = texto_limpo(serie)
    valores = valores[valores.ne("")]
    return valores.nunique(dropna=True)


def lista_unicos(serie, limite=12):
    valores = sorted(
        {
            valor
            for valor in texto_limpo(serie)
            if valor and valor.lower() != "nan"
        }
    )
    if len(valores) > limite:
        return " | ".join(valores[:limite]) + f" | ... (+{len(valores) - limite})"
    return " | ".join(valores)


def validar_duplicatas(comparavel):
    duplicadas = comparavel[comparavel.duplicated(CHAVE, keep=False)].copy()
    duplicadas.insert(0, "NIVEL", "ERRO")
    duplicadas.insert(1, "VALIDACAO", "duplicata_chave_oficial")
    return duplicadas.sort_values(CHAVE)


def validar_nulos(comparavel):
    linhas = []
    for coluna in COLUNAS_CRITICAS:
        ausentes = texto_limpo(comparavel[coluna]).eq("").sum()
        linhas.append(
            {
                "NIVEL": "ERRO" if ausentes else "OK",
                "VALIDACAO": "nulo_coluna_critica",
                "COLUNA": coluna,
                "QT_LINHAS_NULAS": int(ausentes),
            }
        )

    if "SG_IES" in comparavel.columns:
        ausentes_sigla = texto_limpo(comparavel["SG_IES"]).eq("").sum()
        linhas.append(
            {
                "NIVEL": "ALERTA" if ausentes_sigla else "OK",
                "VALIDACAO": "ies_sem_sigla",
                "COLUNA": "SG_IES",
                "QT_LINHAS_NULAS": int(ausentes_sigla),
            }
        )

    return pd.DataFrame(linhas)


def validar_nomes_conflitantes(df, coluna_codigo, coluna_nome, validacao):
    conflito = (
        df.groupby(["NU_ANO_CENSO", coluna_codigo], dropna=False)
        .agg(
            QT_NOMES=(coluna_nome, n_unicos_validos),
            NOMES=(coluna_nome, lista_unicos),
            QT_LINHAS=(coluna_nome, "size"),
        )
        .reset_index()
    )
    conflito = conflito[conflito["QT_NOMES"] > 1].copy()
    conflito.insert(0, "NIVEL", "ALERTA")
    conflito.insert(1, "VALIDACAO", validacao)
    return conflito.sort_values(["NU_ANO_CENSO", coluna_codigo])


def validar_recorte(comparavel):
    area = codigo_limpo(comparavel["DS_CLASSIFICACAO_AREA"])
    co_area_geral = codigo_limpo(comparavel["CO_AREA_GERAL"])
    co_area_especifica = codigo_limpo(comparavel.get("CO_AREA_ESPECIFICA", pd.Series("", index=comparavel.index)))
    rotulo = codigo_limpo(comparavel["CO_ROTULO_AREA"])
    ano = texto_limpo(comparavel["NU_ANO_CENSO"])

    filtro_ano = ano.isin(ANOS_OFICIAIS)
    filtro_cine = area.isin(["CINE", "CINE BRASIL"]) & (
        co_area_geral.isin(["6", "06"]) | rotulo.eq("0714E04")
    )
    filtro_ocde = area.eq("OCDE") & (
        co_area_especifica.eq("48") | rotulo.eq("5.23E+06")
    )
    validas = filtro_ano & (filtro_cine | filtro_ocde)

    invalidas = comparavel[~validas].copy()
    invalidas.insert(0, "NIVEL", "ERRO")
    invalidas.insert(1, "VALIDACAO", "linha_fora_recorte_oficial")
    invalidas["MOTIVO_RECORTE_INVALIDO"] = ""
    invalidas.loc[~filtro_ano.loc[invalidas.index], "MOTIVO_RECORTE_INVALIDO"] = "ano_fora_2009_2024"
    invalidas.loc[
        filtro_ano.loc[invalidas.index]
        & ~area.loc[invalidas.index].isin(["CINE", "CINE BRASIL", "OCDE"]),
        "MOTIVO_RECORTE_INVALIDO",
    ] = "classificacao_area_nao_reconhecida"
    invalidas.loc[
        filtro_ano.loc[invalidas.index]
        & area.loc[invalidas.index].isin(["CINE", "CINE BRASIL"])
        & ~filtro_cine.loc[invalidas.index],
        "MOTIVO_RECORTE_INVALIDO",
    ] = "cine_fora_area_6_e_fora_0714E04"
    invalidas.loc[
        filtro_ano.loc[invalidas.index]
        & area.loc[invalidas.index].eq("OCDE")
        & ~filtro_ocde.loc[invalidas.index],
        "MOTIVO_RECORTE_INVALIDO",
    ] = "ocde_fora_area_48_e_fora_proxy"
    return invalidas


def validar_metricas(comparavel):
    linhas = []
    metricas = [coluna for coluna in NUMERICAS if coluna in comparavel.columns]
    dados = comparavel[CHAVE + metricas].copy()
    for coluna in metricas:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")
        negativas = dados[dados[coluna] < 0]
        for _, linha in negativas.iterrows():
            linhas.append(
                {
                    "NIVEL": "ERRO",
                    "VALIDACAO": "metrica_negativa",
                    "NU_ANO_CENSO": linha["NU_ANO_CENSO"],
                    "CO_IES": linha["CO_IES"],
                    "CO_CURSO": linha["CO_CURSO"],
                    "METRICA": coluna,
                    "VALOR": linha[coluna],
                    "OBSERVACAO": "Metrica numerica negativa.",
                }
            )

    qt_mat = pd.to_numeric(comparavel.get("QT_MAT", pd.Series(pd.NA, index=comparavel.index)), errors="coerce")
    qt_desv = pd.to_numeric(
        comparavel.get("QT_SIT_DESVINCULADO", pd.Series(pd.NA, index=comparavel.index)),
        errors="coerce",
    )
    taxa_desv = qt_desv / qt_mat
    estranhas = comparavel[(qt_mat > 0) & (taxa_desv > 1)].copy()
    for idx, linha in estranhas.iterrows():
        linhas.append(
            {
                "NIVEL": "ALERTA",
                "VALIDACAO": "desvinculados_maior_que_matriculas",
                "NU_ANO_CENSO": linha["NU_ANO_CENSO"],
                "CO_IES": linha["CO_IES"],
                "CO_CURSO": linha["CO_CURSO"],
                "METRICA": "QT_SIT_DESVINCULADO/QT_MAT",
                "VALOR": taxa_desv.loc[idx],
                "OBSERVACAO": "Razao acima de 1. Revisar antes de interpretar.",
            }
        )

    return pd.DataFrame(
        linhas,
        columns=[
            "NIVEL",
            "VALIDACAO",
            "NU_ANO_CENSO",
            "CO_IES",
            "CO_CURSO",
            "METRICA",
            "VALOR",
            "OBSERVACAO",
        ],
    )


def validar_colunas_sensiveis(dfs):
    linhas = []
    for nome_arquivo, df in dfs.items():
        for coluna in df.columns:
            coluna_upper = coluna.upper()
            for termo in COLUNAS_PROIBIDAS:
                if termo in coluna_upper:
                    linhas.append(
                        {
                            "NIVEL": "ERRO",
                            "VALIDACAO": "coluna_sensivel_detectada",
                            "ARQUIVO": nome_arquivo,
                            "COLUNA": coluna,
                            "TERMO_PROIBIDO": termo,
                        }
                    )
    return pd.DataFrame(
        linhas,
        columns=["NIVEL", "VALIDACAO", "ARQUIVO", "COLUNA", "TERMO_PROIBIDO"],
    )


def validar_comparacao_chaves(comparavel, expandida):
    chaves_comparavel = comparavel[CHAVE].drop_duplicates()
    chaves_expandida = expandida[CHAVE].drop_duplicates()

    chaves_comparavel["IN_COMPARAVEL"] = True
    chaves_expandida["IN_EXPANDIDA"] = True

    comparacao = chaves_comparavel.merge(chaves_expandida, on=CHAVE, how="outer")
    comparacao["IN_COMPARAVEL"] = comparacao["IN_COMPARAVEL"].fillna(False)
    comparacao["IN_EXPANDIDA"] = comparacao["IN_EXPANDIDA"].fillna(False)

    faltantes = comparacao[
        ~comparacao["IN_COMPARAVEL"] | ~comparacao["IN_EXPANDIDA"]
    ].copy()
    faltantes["NIVEL"] = "ERRO"
    faltantes["VALIDACAO"] = "chave_inconsistente_oficial_vs_expandida"
    faltantes["SITUACAO"] = "ok"
    faltantes.loc[~faltantes["IN_COMPARAVEL"], "SITUACAO"] = "existe_na_expandida_mas_nao_na_comparavel"
    faltantes.loc[~faltantes["IN_EXPANDIDA"], "SITUACAO"] = "existe_na_comparavel_mas_nao_na_expandida"

    return faltantes[
        ["NIVEL", "VALIDACAO", "SITUACAO"] + CHAVE + ["IN_COMPARAVEL", "IN_EXPANDIDA"]
    ].sort_values(CHAVE)


def contar_nivel(df, nivel):
    if "NIVEL" not in df.columns or df.empty:
        return 0
    return int(df["NIVEL"].eq(nivel).sum())


def gerar_resumo(comparavel, expandida, resultados):
    linhas = [
        {
            "ITEM": "linhas_planilha_comparavel",
            "VALOR": len(comparavel),
            "NIVEL": "INFO",
            "OBSERVACAO": "Uma linha por NU_ANO_CENSO + CO_IES + CO_CURSO.",
        },
        {
            "ITEM": "linhas_planilha_expandida",
            "VALOR": len(expandida),
            "NIVEL": "INFO",
            "OBSERVACAO": "Base com linhas territoriais/dimensionais.",
        },
        {
            "ITEM": "anos_planilha_comparavel",
            "VALOR": ",".join(sorted(texto_limpo(comparavel["NU_ANO_CENSO"]).unique())),
            "NIVEL": "INFO",
            "OBSERVACAO": "Anos disponíveis na planilha oficial.",
        },
        {
            "ITEM": "curso_ies_distintos",
            "VALOR": comparavel[CHAVE].drop_duplicates().shape[0],
            "NIVEL": "INFO",
            "OBSERVACAO": "Quantidade de chaves lógicas na planilha comparável.",
        },
    ]

    for nome, df in resultados.items():
        erros = contar_nivel(df, "ERRO")
        alertas = contar_nivel(df, "ALERTA")
        linhas.append(
            {
                "ITEM": nome,
                "VALOR": len(df),
                "NIVEL": "ERRO" if erros else ("ALERTA" if alertas else "OK"),
                "OBSERVACAO": f"{erros} erros; {alertas} alertas.",
            }
        )

    return pd.DataFrame(linhas)


def escrever_relatorio(resumo, resultados):
    total_erros = sum(contar_nivel(df, "ERRO") for df in resultados.values())
    total_alertas = sum(contar_nivel(df, "ALERTA") for df in resultados.values())
    status = "REPROVADO" if total_erros else "APROVADO_COM_ALERTAS" if total_alertas else "APROVADO"

    linhas = [
        "# Relatório de validação da planilha oficial",
        "",
        f"Status geral: **{status}**",
        "",
        f"* Erros: {total_erros}",
        f"* Alertas: {total_alertas}",
        "",
        "## Arquivos validados",
        "",
        f"* `{ARQ_COMPARAVEL.relative_to(ROOT)}`",
        f"* `{ARQ_EXPANDIDA.relative_to(ROOT)}`",
        "",
        "## Resumo",
        "",
        "| Item | Nível | Valor | Observação |",
        "| --- | --- | ---: | --- |",
    ]

    for _, linha in resumo.iterrows():
        linhas.append(
            f"| {linha['ITEM']} | {linha['NIVEL']} | {linha['VALOR']} | {linha['OBSERVACAO']} |"
        )

    linhas.extend(
        [
            "",
            "## Interpretação",
            "",
            "* `ERRO`: impede seguir sem correção.",
            "* `ALERTA`: exige revisão, mas não bloqueia a geração da planilha.",
            "* A planilha comparável deve ser usada para séries históricas e contagem de cursos.",
            "* A planilha expandida deve ser usada para mapas e filtros territoriais.",
            "",
            "## Saídas CSV",
            "",
        ]
    )

    for chave, caminho in SAIDAS.items():
        if chave == "relatorio":
            continue
        linhas.append(f"* `{caminho.relative_to(ROOT)}`")

    SAIDAS["relatorio"].write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return status, total_erros, total_alertas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    comparavel = carregar_csv(ARQ_COMPARAVEL)
    expandida = carregar_csv(ARQ_EXPANDIDA)

    for coluna in COLUNAS_CRITICAS:
        if coluna not in comparavel.columns:
            raise KeyError(f"Coluna obrigatoria ausente na planilha comparavel: {coluna}")
    for coluna in CHAVE:
        if coluna not in expandida.columns:
            raise KeyError(f"Coluna obrigatoria ausente na planilha expandida: {coluna}")

    resultados = {
        "duplicatas_chave": validar_duplicatas(comparavel),
        "nulos_colunas_criticas": validar_nulos(comparavel),
        "instituicoes_nomes_conflitantes": validar_nomes_conflitantes(
            comparavel, "CO_IES", "NO_IES", "ies_nome_conflitante_mesmo_ano"
        ),
        "cursos_nomes_conflitantes": validar_nomes_conflitantes(
            comparavel, "CO_CURSO", "NO_CURSO", "curso_nome_conflitante_mesmo_ano"
        ),
        "recorte_cine_invalido": validar_recorte(comparavel),
        "metricas_negativas_ou_estranhas": validar_metricas(comparavel),
        "colunas_sensiveis_detectadas": validar_colunas_sensiveis(
            {
                "planilha_oficial_computacao.csv": comparavel,
                "planilha_oficial_computacao_expandida.csv": expandida,
            }
        ),
        "comparacao_oficial_vs_expandida": validar_comparacao_chaves(
            comparavel, expandida
        ),
    }

    resumo = gerar_resumo(comparavel, expandida, resultados)

    salvar(resumo, SAIDAS["resumo"])
    salvar(resultados["duplicatas_chave"], SAIDAS["duplicatas"])
    salvar(resultados["nulos_colunas_criticas"], SAIDAS["nulos"])
    salvar(resultados["instituicoes_nomes_conflitantes"], SAIDAS["ies_conflitos"])
    salvar(resultados["cursos_nomes_conflitantes"], SAIDAS["curso_conflitos"])
    salvar(resultados["recorte_cine_invalido"], SAIDAS["recorte_invalido"])
    salvar(resultados["metricas_negativas_ou_estranhas"], SAIDAS["metricas"])
    salvar(resultados["colunas_sensiveis_detectadas"], SAIDAS["sensiveis"])
    salvar(resultados["comparacao_oficial_vs_expandida"], SAIDAS["comparacao"])

    status, total_erros, total_alertas = escrever_relatorio(resumo, resultados)

    print("Validacao oficial gerada:")
    print(OUT)
    print(f"Status: {status}")
    print(f"Erros: {total_erros}")
    print(f"Alertas: {total_alertas}")

    if total_erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
