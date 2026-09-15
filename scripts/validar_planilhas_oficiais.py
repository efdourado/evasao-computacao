from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OFICIAL = ROOT / "data" / "processed" / "oficial"
VALIDACAO = ROOT / "data" / "processed" / "validacao"

ARQ_PRINCIPAL = OFICIAL / "planilha_oficial_computacao.csv"
ARQ_EXPANDIDA = OFICIAL / "planilha_oficial_computacao_expandida.csv"
SAIDA_RESUMO = VALIDACAO / "resumo_validacao.csv"
SAIDA_OCORRENCIAS = VALIDACAO / "ocorrencias_validacao.csv"

CHAVE = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]
CHAVE_EXPANDIDA = CHAVE + [
    "TP_DIMENSAO",
    "CO_UF",
    "CO_MUNICIPIO",
]
COLUNAS_CRITICAS = CHAVE + ["NO_IES", "NO_CURSO"]
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
COLUNAS_PROIBIDAS = [
    "ID_ALUNO",
    "CO_ALUNO",
    "CPF",
    "ID_DOCENTE",
    "CO_DOCENTE",
    "NO_ALUNO",
    "NU_CPF",
    "TX_DESVINCULADO_SOBRE_MAT",
]
ANOS = {str(ano) for ano in range(2009, 2025)}
COLUNAS_OCORRENCIA = [
    "NIVEL",
    "VALIDACAO",
    "ARQUIVO",
    "NU_ANO_CENSO",
    "CO_IES",
    "CO_CURSO",
    "COLUNA",
    "VALOR",
    "DESCRICAO",
]


def carregar(caminho):
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")
    return pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        low_memory=False,
    )


def texto(serie):
    return serie.fillna("").astype(str).str.strip()


def codigo(serie):
    return texto(serie).str.replace('"', "", regex=False).str.upper()


def ocorrencia(
    nivel,
    validacao,
    arquivo,
    descricao,
    df=None,
    coluna="",
    valor="",
):
    if df is None or df.empty:
        return pd.DataFrame(columns=COLUNAS_OCORRENCIA)

    saida = pd.DataFrame(index=df.index)
    saida["NIVEL"] = nivel
    saida["VALIDACAO"] = validacao
    saida["ARQUIVO"] = arquivo
    for chave in CHAVE:
        saida[chave] = df[chave] if chave in df.columns else ""
    saida["COLUNA"] = coluna
    saida["VALOR"] = valor
    saida["DESCRICAO"] = descricao
    return saida[COLUNAS_OCORRENCIA]


def validar_principal(principal):
    resultados = []
    nome = ARQ_PRINCIPAL.name

    duplicadas = principal[principal.duplicated(CHAVE, keep=False)]
    resultados.append(
        ocorrencia(
            "ERRO",
            "duplicata_chave_principal",
            nome,
            "A planilha principal deve ter uma linha por ano, IES e curso.",
            duplicadas,
        )
    )

    for coluna in COLUNAS_CRITICAS:
        ausentes = principal[texto(principal[coluna]).eq("")]
        resultados.append(
            ocorrencia(
                "ERRO",
                "valor_critico_ausente",
                nome,
                "Campo obrigatorio sem preenchimento.",
                ausentes,
                coluna=coluna,
            )
        )

    anos_invalidos = principal[~texto(principal["NU_ANO_CENSO"]).isin(ANOS)]
    resultados.append(
        ocorrencia(
            "ERRO",
            "ano_fora_da_serie_oficial",
            nome,
            "A serie oficial aceita apenas 2009 a 2024.",
            anos_invalidos,
            coluna="NU_ANO_CENSO",
        )
    )

    classificacao = codigo(principal["DS_CLASSIFICACAO_AREA"])
    area_geral = codigo(principal["CO_AREA_GERAL"])
    area_especifica = codigo(principal["CO_AREA_ESPECIFICA"])
    rotulo = codigo(principal["CO_ROTULO_AREA"])
    cine = classificacao.isin(["CINE", "CINE BRASIL"]) & (
        area_geral.isin(["6", "06"]) | rotulo.eq("0714E04")
    )
    ocde = classificacao.eq("OCDE") & (
        area_especifica.eq("48") | rotulo.isin(["5.23E+06", "523E04"])
    )
    fora_recorte = principal[~(cine | ocde)]
    resultados.append(
        ocorrencia(
            "ERRO",
            "linha_fora_do_recorte",
            nome,
            "Curso fora da area 6/0714E04 ou do proxy OCDE de 2017.",
            fora_recorte,
        )
    )

    nome_curso = texto(principal["NO_CURSO"]).str.upper()
    abi_no_nome = nome_curso.str.contains(
        r"(?:^|[^A-Z0-9])ABI(?:[^A-Z0-9]|$)|[ÁA]REA B[ÁA]SICA DE INGRESSO",
        regex=True,
    )
    abi_residual = principal[abi_no_nome]
    resultados.append(
        ocorrencia(
            "ERRO",
            "abi_residual",
            nome,
            "Area basica de ingresso nao deve aparecer como curso final.",
            abi_residual,
            coluna="NO_CURSO",
        )
    )

    for codigo_coluna, nome_coluna, validacao in [
        ("CO_IES", "NO_IES", "nome_ies_conflitante"),
        ("CO_CURSO", "NO_CURSO", "nome_curso_conflitante"),
    ]:
        conflitos = (
            principal.groupby(["NU_ANO_CENSO", codigo_coluna], dropna=False)[
                nome_coluna
            ]
            .nunique(dropna=True)
            .reset_index(name="QT_NOMES")
        )
        conflitos = conflitos[conflitos["QT_NOMES"] > 1]
        resultados.append(
            ocorrencia(
                "ALERTA",
                validacao,
                nome,
                "Mesmo codigo associado a mais de um nome no ano.",
                conflitos,
                coluna=nome_coluna,
            )
        )

    return resultados


def validar_numericas(df, arquivo):
    resultados = []
    for coluna in NUMERICAS:
        if coluna not in df.columns:
            continue
        valores = pd.to_numeric(df[coluna], errors="coerce")
        negativas = df[valores < 0]
        resultado = ocorrencia(
            "ERRO",
            "metrica_negativa",
            arquivo,
            "Metrica quantitativa negativa.",
            negativas,
            coluna=coluna,
        )
        if not resultado.empty:
            resultado["VALOR"] = valores.loc[negativas.index].astype(str)
        resultados.append(resultado)
    return resultados


def validar_expandida(principal, expandida):
    resultados = []
    nome = ARQ_EXPANDIDA.name
    duplicadas = expandida[expandida.duplicated(CHAVE_EXPANDIDA, keep=False)]
    resultados.append(
        ocorrencia(
            "ERRO",
            "duplicata_chave_geografica",
            nome,
            "Linha geografica repetida para o mesmo curso.",
            duplicadas,
        )
    )

    chaves_principal = principal[CHAVE].drop_duplicates().assign(IN_PRINCIPAL=True)
    chaves_expandida = expandida[CHAVE].drop_duplicates().assign(IN_EXPANDIDA=True)
    comparacao = chaves_principal.merge(chaves_expandida, on=CHAVE, how="outer")
    faltantes = comparacao[
        comparacao["IN_PRINCIPAL"].isna() | comparacao["IN_EXPANDIDA"].isna()
    ]
    resultados.append(
        ocorrencia(
            "ERRO",
            "chave_inconsistente_entre_planilhas",
            nome,
            "Curso presente em apenas uma das duas planilhas.",
            faltantes,
        )
    )

    for coluna in ["NO_IES", "NO_CURSO", "TP_MODALIDADE_ENSINO"]:
        conflitos = (
            expandida.groupby(CHAVE, dropna=False)[coluna]
            .nunique(dropna=True)
            .reset_index(name="QT_VALORES")
        )
        conflitos = conflitos[conflitos["QT_VALORES"] > 1]
        resultados.append(
            ocorrencia(
                "ERRO",
                "identificacao_diverge_entre_linhas_territoriais",
                nome,
                "As linhas territoriais do curso possuem identificacao divergente.",
                conflitos,
                coluna=coluna,
            )
        )

    principal_n = principal[CHAVE + NUMERICAS].copy()
    expandida_n = expandida[CHAVE + NUMERICAS].copy()
    for coluna in NUMERICAS:
        principal_n[coluna] = pd.to_numeric(principal_n[coluna], errors="coerce")
        expandida_n[coluna] = pd.to_numeric(expandida_n[coluna], errors="coerce")

    somas = (
        expandida_n.groupby(CHAVE, dropna=False)[NUMERICAS]
        .sum(min_count=1)
        .reset_index()
    )
    metricas = principal_n.merge(
        somas,
        on=CHAVE,
        how="outer",
        suffixes=("_PRINCIPAL", "_EXPANDIDA"),
    )
    for coluna in NUMERICAS:
        valor_principal = metricas[coluna + "_PRINCIPAL"]
        valor_expandida = metricas[coluna + "_EXPANDIDA"]
        divergente = valor_expandida.notna() & (
            valor_principal.isna()
            | ((valor_principal - valor_expandida).abs() > 1e-9)
        )
        casos = metricas[divergente].copy()
        resultado = ocorrencia(
            "ERRO",
            "metrica_nao_reconcilia_com_expandida",
            nome,
            "O total da principal deve ser a soma das linhas territoriais.",
            casos,
            coluna=coluna,
        )
        if not resultado.empty:
            resultado["VALOR"] = (
                "principal="
                + valor_principal.loc[casos.index].astype(str)
                + "; expandida="
                + valor_expandida.loc[casos.index].astype(str)
            )
        resultados.append(resultado)

    ead = expandida[codigo(expandida["TP_MODALIDADE_ENSINO"]).eq("2")].copy()
    dimensao = codigo(ead["TP_DIMENSAO"])
    for coluna in NUMERICAS:
        ead[coluna] = pd.to_numeric(ead[coluna], errors="coerce")
    oferta_positiva = (
        ead[["QT_VG_TOTAL", "QT_INSCRITO_TOTAL"]].fillna(0) > 0
    ).any(axis=1)
    oferta_fora_nacional = ead[dimensao.isin(["1", "2", "4"]) & oferta_positiva]
    resultados.append(
        ocorrencia(
            "ERRO",
            "oferta_ead_fora_dimensao_nacional",
            nome,
            "Vagas e inscritos EaD devem ficar apenas na dimensao nacional.",
            oferta_fora_nacional,
            coluna="QT_VG_TOTAL|QT_INSCRITO_TOTAL",
        )
    )

    academicas = [coluna for coluna in NUMERICAS if coluna not in [
        "QT_VG_TOTAL",
        "QT_INSCRITO_TOTAL",
    ]]
    atividade_positiva = (ead[academicas].fillna(0) > 0).any(axis=1)
    atividade_na_nacional = ead[dimensao.eq("3") & atividade_positiva]
    resultados.append(
        ocorrencia(
            "ERRO",
            "atividade_ead_na_dimensao_nacional",
            nome,
            "Indicadores academicos EaD devem ficar nas dimensoes territoriais.",
            atividade_na_nacional,
            coluna="|".join(academicas),
        )
    )
    return resultados


def validar_colunas(dfs):
    linhas = []
    for arquivo, df in dfs.items():
        for coluna in df.columns:
            termo = next(
                (item for item in COLUNAS_PROIBIDAS if item in coluna.upper()),
                None,
            )
            if termo:
                linhas.append(
                    {
                        "NIVEL": "ERRO",
                        "VALIDACAO": "coluna_proibida",
                        "ARQUIVO": arquivo,
                        "NU_ANO_CENSO": "",
                        "CO_IES": "",
                        "CO_CURSO": "",
                        "COLUNA": coluna,
                        "VALOR": termo,
                        "DESCRICAO": "Coluna individual, sensivel ou indicador removido.",
                    }
                )
    return pd.DataFrame(linhas, columns=COLUNAS_OCORRENCIA)


def gerar_resumo(principal, expandida, ocorrencias):
    erros = int(ocorrencias["NIVEL"].eq("ERRO").sum())
    alertas = int(ocorrencias["NIVEL"].eq("ALERTA").sum())
    sem_sigla = int(texto(principal["SG_IES"]).eq("").sum())
    status = "REPROVADO" if erros else "APROVADO_COM_ALERTAS" if alertas else "APROVADO"

    linhas = [
        ("status", status, "INFO", "Resultado geral da validacao."),
        ("erros", erros, "ERRO" if erros else "OK", "Ocorrencias que bloqueiam o uso."),
        (
            "alertas",
            alertas,
            "ALERTA" if alertas else "OK",
            "Ocorrencias que exigem revisao.",
        ),
        (
            "linhas_planilha_principal",
            len(principal),
            "INFO",
            "Uma linha por ano, IES e curso.",
        ),
        (
            "linhas_planilha_expandida",
            len(expandida),
            "INFO",
            "Linhas territoriais e dimensionais.",
        ),
        (
            "chaves_curso_ies",
            principal[CHAVE].drop_duplicates().shape[0],
            "INFO",
            "Quantidade de cursos logicos.",
        ),
        (
            "siglas_ies_ausentes",
            sem_sigla,
            "INFO",
            "SG_IES e opcional; CO_IES e NO_IES estao preenchidos.",
        ),
        (
            "anos",
            ",".join(sorted(texto(principal["NU_ANO_CENSO"]).unique())),
            "INFO",
            "Anos presentes na base.",
        ),
    ]
    return pd.DataFrame(
        linhas,
        columns=["ITEM", "VALOR", "NIVEL", "DESCRICAO"],
    ), status, erros, alertas


def main():
    principal = carregar(ARQ_PRINCIPAL)
    expandida = carregar(ARQ_EXPANDIDA)

    for coluna in COLUNAS_CRITICAS:
        if coluna not in principal.columns:
            raise KeyError(f"Coluna obrigatoria ausente: {coluna}")
    for coluna in CHAVE_EXPANDIDA:
        if coluna not in expandida.columns:
            raise KeyError(f"Coluna obrigatoria ausente na expandida: {coluna}")

    partes = validar_principal(principal)
    partes.extend(validar_numericas(principal, ARQ_PRINCIPAL.name))
    partes.extend(validar_numericas(expandida, ARQ_EXPANDIDA.name))
    partes.extend(validar_expandida(principal, expandida))
    partes.append(
        validar_colunas(
            {
                ARQ_PRINCIPAL.name: principal,
                ARQ_EXPANDIDA.name: expandida,
            }
        )
    )

    ocorrencias = pd.concat(partes, ignore_index=True)
    ocorrencias = ocorrencias[COLUNAS_OCORRENCIA]
    resumo, status, erros, alertas = gerar_resumo(
        principal,
        expandida,
        ocorrencias,
    )

    VALIDACAO.mkdir(parents=True, exist_ok=True)
    resumo.to_csv(
        SAIDA_RESUMO,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    ocorrencias.to_csv(
        SAIDA_OCORRENCIAS,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Status: {status}")
    print(f"Erros: {erros}")
    print(f"Alertas: {alertas}")
    print(SAIDA_RESUMO)
    print(SAIDA_OCORRENCIAS)

    if erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
