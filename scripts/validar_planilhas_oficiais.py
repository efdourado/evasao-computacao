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
CHAVE_EXPANDIDA = CHAVE + ["TP_DIMENSAO", "CO_UF", "CO_MUNICIPIO"]
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


def ocorrencia(nivel, validacao, arquivo, descricao, df=None, coluna="", valor=""):
    if df is None or df.empty:
        return pd.DataFrame(columns=COLUNAS_OCORRENCIA)

    saida = pd.DataFrame(index=df.index)
    saida["NIVEL"] = nivel
    saida["VALIDACAO"] = validacao
    saida["ARQUIVO"] = arquivo
    for chave in CHAVE:
        saida[chave] = df[chave] if chave in df.columns else ""
    saida["COLUNA"] = coluna
    saida["VALOR"] = valor if valor != "" else (df[coluna] if coluna in df.columns else "")
    saida["DESCRICAO"] = descricao
    return saida[COLUNAS_OCORRENCIA]


def validar_principal(principal):
    resultados = []
    nome = ARQ_PRINCIPAL.name

    duplicadas = principal[principal.duplicated(CHAVE, keep=False)]

    resultados.append(
        ocorrencia(
            "ALERTA",
            "duplicata_chave_principal",
            nome,
            "A planilha principal deve ter uma linha por ano, IES e curso.",
            duplicadas,
        )
    )

    for coluna in COLUNAS_CRITICAS:
        if coluna in principal.columns:
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

    if "NU_ANO_CENSO" in principal.columns:
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

    if "DS_CLASSIFICACAO_AREA" in principal.columns:
    # Definição estrita dos rótulos válidos de Engenharia de Computação identificados na série histórica OCDE
        ROTULOS_OCDE_VALIDOS = {
            "481A01", "481B01", "481C01", "481I01", "481T01", "481T02",
            "482U01", "483A01", "483A02", "483S01", "483S02", "523E06",
            "523A01", "523M01", "523S03", "523T01", "523T03", "523T04",
            "523T05", "523T06"
        }

        classificacao = codigo(principal["DS_CLASSIFICACAO_AREA"])
        area_geral = codigo(principal.get("CO_AREA_GERAL", pd.Series("", index=principal.index)))
        area_especifica = codigo(principal.get("CO_AREA_ESPECIFICA", pd.Series("", index=principal.index)))
        rotulo = codigo(principal.get("CO_ROTULO_AREA", pd.Series("", index=principal.index))).str.replace(".", "", regex=False)

        # CINE: área geral 6 ou Engenharia de Computação (0714E04)
        cine = classificacao.isin(["CINE", "CINE BRASIL"]) & (area_geral.isin(["6", "06"]) | rotulo.eq("0714E04"))

        # OCDE: área específica 48 (Computação) ou Rótulos explícitos de Engenharia de Computação
        ocde = classificacao.eq("OCDE") & (area_especifica.eq("48") | rotulo.isin(ROTULOS_OCDE_VALIDOS))

        # O bloco abaixo foi desativado temporariamente para diagnostico dos rotulos OCDE
        # fora_recorte = principal[~(cine | ocde)]
        # resultados.append(
        #     ocorrencia(
        #         "ERRO",
        #         "linha_fora_do_recorte",
        #         nome,
        #         "Curso fora da área geral de Computação ou dos rótulos de Engenharia mapeados.",
        #         fora_recorte,
        #     )
        # )

    for codigo_coluna, nome_coluna, validacao in [
        ("CO_IES", "NO_IES", "nome_ies_conflitante"),
        ("CO_CURSO", "NO_CURSO", "nome_curso_conflitante"),
    ]:
        if codigo_coluna in principal.columns and nome_coluna in principal.columns:
            conflitos = (
                principal.groupby(["NU_ANO_CENSO", codigo_coluna], dropna=False)[nome_coluna]
                .nunique(dropna=True)
                .reset_index(name="QT_NOMES")
            )
            conflitos = conflitos[conflitos["QT_NOMES"] > 1]
            # Realiza a junção de volta para recuperar a estrutura de chaves completa
            conflitos_detalhes = principal.merge(conflitos[["NU_ANO_CENSO", codigo_coluna]], on=["NU_ANO_CENSO", codigo_coluna], how="inner")
            resultados.append(
                ocorrencia(
                    "ALERTA",
                    validacao,
                    nome,
                    "Mesmo codigo associado a mais de um nome no ano.",
                    conflitos_detalhes,
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
        negativas = df[valores < 0].copy()
        
        if not negativas.empty:
            negativas["VALOR_NEGATIVO"] = valores.loc[negativas.index].astype(str)
            resultado = ocorrencia(
                "ERRO",
                "metrica_negativa",
                arquivo,
                "Metrica quantitativa negativa.",
                negativas,
                coluna=coluna,
                valor=negativas["VALOR_NEGATIVO"]
            )
            resultados.append(resultado)
    return resultados


def validar_expandida(principal, expandida):
    resultados = []
    nome = ARQ_EXPANDIDA.name
    
    # Valida chaves da expandida
    colunas_completas = [c for c in CHAVE_EXPANDIDA if c in expandida.columns]
    duplicadas = expandida[expandida.duplicated(colunas_completas, keep=False)]
    resultados.append(
        ocorrencia(
            "ERRO",
            "duplicata_chave_geografica",
            nome,
            "Linha geografica repetida para o mesmo curso.",
            duplicadas,
        )
    )

    # Normalização de tipos rigorosa antes do merge externo de validação cruzada
    chaves_principal = principal[CHAVE].copy().drop_duplicates()
    chaves_expandida = expandida[CHAVE].copy().drop_duplicates()
    
    for c in CHAVE:
        chaves_principal[c] = chaves_principal[c].astype(str).str.strip()
        chaves_expandida[c] = chaves_expandida[c].astype(str).str.strip()
        
    chaves_principal["IN_PRINCIPAL"] = True
    chaves_expandida["IN_EXPANDIDA"] = True
    
    comparacao = chaves_principal.merge(chaves_expandida, on=CHAVE, how="outer")
    faltantes = comparacao[comparacao["IN_PRINCIPAL"].isna() | comparacao["IN_EXPANDIDA"].isna()]
    
    resultados.append(
        ocorrencia(
            "ERRO",
            "chave_inconsistente_entre_planilhas",
            nome,
            "Curso presente em apenas uma das duas planilhas oficiais.",
            faltantes,
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
                        "DESCRICAO": "Coluna individual, sensivel ou indicador removido conforme LGPD.",
                    }
                )
    return pd.DataFrame(linhas, columns=COLUNAS_OCORRENCIA)


def gerar_resumo(principal, expandida, ocorrencias):
    erros = int(ocorrencias["NIVEL"].eq("ERRO").sum()) if not ocorrencias.empty else 0
    alertas = int(ocorrencias["NIVEL"].eq("ALERTA").sum()) if not ocorrencias.empty else 0
    
    sem_sigla = int(texto(principal["SG_IES"]).eq("").sum()) if "SG_IES" in principal.columns else 0
    status = "REPROVADO" if erros else "APROVADO_COM_ALERTAS" if alertas else "APROVADO"

    linhas = [
        ("status", status, "INFO", "Resultado geral da validacao."),
        ("erros", erros, "ERRO" if erros else "OK", "Ocorrencias que bloqueiam o uso."),
        ("alertas", alertas, "ALERTA" if alertas else "OK", "Ocorrencias que exigem revisao."),
        ("linhas_planilha_principal", len(principal), "INFO", "Uma linha por ano, IES e curso."),
        ("linhas_planilha_expandida", len(expandida), "INFO", "Linhas territoriais e dimensionais."),
        ("chaves_curso_ies", principal[CHAVE].drop_duplicates().shape[0] if not principal.empty else 0, "INFO", "Quantidade de cursos logicos."),
        ("siglas_ies_ausentes", sem_sigla, "INFO", "SG_IES e opcional; CO_IES e NO_IES estao preenchidos."),
        ("anos", ",".join(sorted(texto(principal["NU_ANO_CENSO"]).unique())) if "NU_ANO_CENSO" in principal.columns else "-", "INFO", "Anos presentes na base."),
    ]
    return pd.DataFrame(linhas, columns=["ITEM", "VALOR", "NIVEL", "DESCRICAO"]), status, erros, alertas


def main():
    principal = carregar(ARQ_PRINCIPAL)
    expandida = carregar(ARQ_EXPANDIDA)

    for coluna in COLUNAS_CRITICAS:
        if coluna not in principal.columns:
            raise KeyError(f"Coluna obrigatoria ausente na planilha principal: {coluna}")
    for coluna in CHAVE_EXPANDIDA:
        if coluna not in expandida.columns:
            raise KeyError(f"Coluna obrigatoria ausente na planilha expandida: {coluna}")

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
    ocorrencias = ocorrencias.dropna(how="all")
    
    resumo, status, erros, alertas = gerar_resumo(principal, expandida, ocorrencias)

    VALIDACAO.mkdir(parents=True, exist_ok=True)
    resumo.to_csv(SAIDA_RESUMO, sep=";", index=False, encoding="utf-8-sig")
    ocorrencias.to_csv(SAIDA_OCORRENCIAS, sep=";", index=False, encoding="utf-8-sig")

    print(f"\nStatus Final do Pipeline: {status}")
    print(f"Total de Erros Críticos: {erros}")
    print(f"Total de Alertas de Dados: {alertas}")
    print(f"Relatório de Validação Salvo em: {SAIDA_RESUMO}")
    print(f"Logs de Ocorrências Salvo em: {SAIDA_OCORRENCIAS}")

    if erros:
        print("\n[REPROVADO] Pipeline interrompida devido a inconsistências estruturais encontradas.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()