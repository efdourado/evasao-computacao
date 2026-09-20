"""Gera as listas de conferencia da curadoria em data/processed/curadoria/.

Cada arquivo e um extrato para leitura manual. Nenhum altera as planilhas
oficiais. Documentacao: docs/02_curadoria.md

Uso:
    .venv/bin/python scripts/gerar_extratos_curadoria.py
"""
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OFICIAL = ROOT / "data" / "processed" / "oficial"
SAIDA = ROOT / "data" / "processed" / "curadoria"

ARQ_PRINCIPAL = OFICIAL / "planilha_oficial_computacao.csv"
ARQ_EXPANDIDA = OFICIAL / "planilha_oficial_computacao_expandida.csv"

METRICAS = [
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

BASE_COLS = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "CO_CURSO",
    "NO_CURSO",
    "DS_TP_MODALIDADE_ENSINO",
    "DS_TP_GRAU_ACADEMICO",
    "CO_ROTULO_AREA",
    "NO_ROTULO_AREA",
    "DS_CLASSIFICACAO_AREA",
    "DS_CRITERIO_ESCOPO",
]

CONFIG_NOME_ROTULO = ROOT / "config" / "curadoria_nome_rotulo.csv"


def _cursos_por_resultado():
    """Decisoes manuais sobre nome x rotulo, editaveis em config/curadoria_nome_rotulo.csv."""
    df = pd.read_csv(CONFIG_NOME_ROTULO, sep=";", encoding="utf-8-sig", dtype=str)
    return {r: set(g["CO_CURSO"]) for r, g in df.groupby("RESULTADO")}


_DECISOES_NOME_ROTULO = _cursos_por_resultado()
CURSOS_NOME_ROTULO_COMPATIVEL = _DECISOES_NOME_ROTULO.get("compativel", set())
CURSOS_NOME_ROTULO_DIVERGENTE = _DECISOES_NOME_ROTULO.get("divergente", set())
CURSOS_COM_MUDANCA_HISTORICA_CONFIRMADA = _DECISOES_NOME_ROTULO.get("mudanca_historica", set())



def carregar(caminho):
    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        low_memory=False,
    )
    for coluna in METRICAS:
        df[coluna + "_n"] = pd.to_numeric(df[coluna], errors="coerce")
    df["ANO"] = df["NU_ANO_CENSO"].astype(str).str.strip()
    return df


def normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = texto.encode("ascii", "ignore").decode("ascii").upper()
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def juntar_valores(serie):
    valores = {
        str(valor).strip()
        for valor in serie.dropna()
        if str(valor).strip() and str(valor).strip().lower() != "nan"
    }
    return " | ".join(sorted(valores))


def salvar(df, nome, motivo):
    df = df.copy()
    df["STATUS_VERIFICACAO_FONTE"] = "pendente; triagem automatica nao confirma preenchimento da IES"
    df.insert(0, "MOTIVO_CURADORIA", motivo)
    df.to_csv(SAIDA / nome, sep=";", index=False, encoding="utf-8-sig")
    print(f"  {nome}: {len(df)} linhas")


def nome_x_rotulo(P):
    cine = P[P["DS_CLASSIFICACAO_AREA"].ne("OCDE")].copy()
    nome = cine["NO_CURSO"].map(normalizar_texto)
    rotulo = cine["NO_ROTULO_AREA"].map(normalizar_texto)

    regras = [
        (r"^(?:BACHARELADO EM )?ENGENHARIA DE SOFTWARE(?: .*)?$", ["ENGENHARIA DE SOFTWARE"], "ENGENHARIA DE SOFTWARE"),
        (r"CIENCIAS? DA COMPUTACAO", ["CIENCIA DA COMPUTACAO"], "CIENCIA DA COMPUTACAO"),
        (r"SISTEMAS? DE INFORMACAO", ["SISTEMAS DE INFORMACAO"], "SISTEMAS DE INFORMACAO"),
        (r"ANALISE E DESENVOLVIMENTO DE SISTEMAS", ["SISTEMAS DE INFORMACAO"], "ADS"),
        (r"REDES? DE COMPUTADORES", ["REDES DE COMPUTADORES"], "REDES DE COMPUTADORES"),
        (r"BANCO DE DADOS", ["BANCO DE DADOS"], "BANCO DE DADOS"),
        (r"SISTEMAS PARA (?:A )?INTERNET", ["SISTEMAS PARA INTERNET"], "SISTEMAS PARA INTERNET"),
        (r"ENGENHARIA (?:DA|DE) COMPUTACAO", ["ENGENHARIA DE COMPUTACAO"], "ENGENHARIA DE COMPUTACAO"),
    ]

    mask = pd.Series(False, index=cine.index)
    regra_encontrada = pd.Series("", index=cine.index, dtype="object")
    for padrao, esperados, regra in regras:
        candidata = nome.str.contains(padrao, regex=True, na=False)
        compativel = rotulo.apply(
            lambda valor: any(esperado in valor for esperado in esperados)
        )
        divergente = candidata & ~compativel
        mask |= divergente
        regra_encontrada.loc[divergente] = regra

    sub = cine.loc[mask, BASE_COLS].copy()
    sub["TIPO_INFERIDO_PELO_NOME"] = regra_encontrada.loc[mask]
    sub["RESULTADO_CURADORIA"] = "revisar em nova rodada"
    sub.loc[
        sub["CO_CURSO"].isin(CURSOS_NOME_ROTULO_COMPATIVEL),
        "RESULTADO_CURADORIA",
    ] = "compativel com nome historico ou nome composto"
    sub.loc[
        sub["CO_CURSO"].isin(CURSOS_NOME_ROTULO_DIVERGENTE),
        "RESULTADO_CURADORIA",
    ] = "rotulo da fonte diverge do nome, mas ambos pertencem ao escopo"
    sub.loc[
        sub["CO_CURSO"].isin(CURSOS_COM_MUDANCA_HISTORICA_CONFIRMADA),
        "RESULTADO_CURADORIA",
    ] = "mudanca historica de nome; preservar o valor de cada ano"
    revisados = (
        CURSOS_NOME_ROTULO_COMPATIVEL
        | CURSOS_NOME_ROTULO_DIVERGENTE
        | CURSOS_COM_MUDANCA_HISTORICA_CONFIRMADA
    )
    sub["IMPACTO_NO_RECORTE"] = np.where(
        sub["CO_CURSO"].isin(revisados),
        "nenhum",
        "a confirmar",
    )
    sub["ACAO_RECOMENDADA"] = np.where(
        sub["CO_CURSO"].isin(revisados),
        "manter; usar NO_CURSO como nome e NO_ROTULO_AREA como classificacao declarada",
        "revisar",
    )
    agrupadores = [coluna for coluna in BASE_COLS if coluna != "NU_ANO_CENSO"] + [
        "TIPO_INFERIDO_PELO_NOME",
        "RESULTADO_CURADORIA",
        "IMPACTO_NO_RECORTE",
        "ACAO_RECOMENDADA",
    ]
    sub = (
        sub.groupby(agrupadores, dropna=False)
        .agg(
            ANO_INICIAL=("NU_ANO_CENSO", "min"),
            ANO_FINAL=("NU_ANO_CENSO", "max"),
            QT_ANOS=("NU_ANO_CENSO", "nunique"),
        )
        .reset_index()
        .sort_values(["CO_CURSO", "ANO_INICIAL"])
    )
    salvar(
        sub,
        "01_nome_curso_x_rotulo_divergente.csv",
        "divergencia aparente entre nome e rotulo; conferir a fonte e manter os valores declarados",
    )


def rotulo_muda_na_serie(P):
    cine = P[P["DS_CLASSIFICACAO_AREA"].ne("OCDE")].copy()
    cine["ROTULO_CANONICO"] = cine["NO_ROTULO_AREA"].map(normalizar_texto)
    engenharia = cine["ROTULO_CANONICO"].str.startswith(
        "ENGENHARIA DE COMPUTACAO",
        na=False,
    )
    cine.loc[engenharia, "ROTULO_CANONICO"] = "ENGENHARIA DE COMPUTACAO"
    contagem = cine.groupby(["CO_IES", "CO_CURSO"])["ROTULO_CANONICO"].nunique()
    chaves = contagem[contagem > 1].reset_index()[["CO_IES", "CO_CURSO"]]
    sub = cine.merge(chaves, on=["CO_IES", "CO_CURSO"], how="inner")
    sub = (
        sub.groupby(["CO_IES", "CO_CURSO"], dropna=False)
        .agg(
            ANO_INICIAL=("NU_ANO_CENSO", "min"),
            ANO_FINAL=("NU_ANO_CENSO", "max"),
            NO_IES_LISTA=("NO_IES", juntar_valores),
            NO_CURSO_LISTA=("NO_CURSO", juntar_valores),
            ROTULOS_CINE_NA_SERIE=("NO_ROTULO_AREA", juntar_valores),
            ROTULOS_CANONICOS=("ROTULO_CANONICO", juntar_valores),
        )
        .reset_index()
        .sort_values(["CO_CURSO", "ANO_INICIAL"])
    )
    sub["DECISAO_CURADORIA"] = (
        "manter; a classificacao declarada em cada ano pode mudar sem alterar o recorte"
    )
    salvar(
        sub,
        "02_co_curso_rotulo_muda_na_serie.csv",
        "mudancas reais apos unificar as tres descricoes de Engenharia de Computacao",
    )


def co_curso_varias_ies(P):
    contagem = P.groupby("CO_CURSO")["CO_IES"].nunique()
    multi = contagem[contagem > 1].index
    sub = (
        P[P["CO_CURSO"].isin(multi)]
        .groupby("CO_CURSO", dropna=False)
        .agg(
            ANO_INICIAL=("NU_ANO_CENSO", "min"),
            ANO_FINAL=("NU_ANO_CENSO", "max"),
            QT_IES=("CO_IES", "nunique"),
            CO_IES_LISTA=("CO_IES", juntar_valores),
            NO_IES_LISTA=("NO_IES", juntar_valores),
            NO_CURSO_LISTA=("NO_CURSO", juntar_valores),
        )
        .reset_index()
        .sort_values("CO_CURSO")
    )
    sub["DECISAO_CURADORIA"] = (
        "nao relacionar anos apenas por CO_CURSO; usar CO_IES + CO_CURSO"
    )
    salvar(
        sub,
        "03_co_curso_em_varias_ies.csv",
        "o mesmo numero de CO_CURSO aparece em IES diferentes ao longo da serie, sem sobreposicao anual",
    )


def vagas_repetidas(P):
    linhas = []
    for (ano, ies), grupo in P.groupby(["ANO", "CO_IES"]):
        vagas = grupo["QT_VG_TOTAL_n"].dropna()
        vagas = vagas[vagas > 0]
        if len(vagas) < 4:
            continue
        contagem = vagas.value_counts()
        if contagem.iloc[0] >= 4:
            linhas.append(
                {
                    "NU_ANO_CENSO": ano,
                    "CO_IES": ies,
                    "NO_IES": grupo["NO_IES"].iloc[0],
                    "N_CURSOS_COMPUTACAO": len(grupo),
                    "VALOR_VAGAS": int(contagem.index[0]),
                    "N_CURSOS_COM_ESSE_VALOR": int(contagem.iloc[0]),
                    "TOTAL_DECLARADO_NESSES_CURSOS": int(
                        contagem.index[0] * contagem.iloc[0]
                    ),
                }
            )
    resumo = pd.DataFrame(linhas).sort_values(
        ["NU_ANO_CENSO", "N_CURSOS_COM_ESSE_VALOR"],
        ascending=[True, False],
    )
    resumo["DECISAO_CURADORIA"] = (
        "manter: repeticao de capacidade planejada nao comprova duplicidade"
    )
    salvar(
        resumo,
        "04_vagas_repetidas_por_ies_ano.csv",
        "mesmo valor de vagas aparece em pelo menos quatro cursos da IES",
    )


def igualdades_inscritos(P):
    suspeito = P[
        ((P["QT_INSCRITO_TOTAL_n"] > 0) & (P["QT_INSCRITO_TOTAL_n"] == P["QT_VG_TOTAL_n"]))
        | ((P["QT_INSCRITO_TOTAL_n"] > 0) & (P["QT_INSCRITO_TOTAL_n"] == P["QT_ING_n"]))
    ].copy()
    igual = np.where(
        suspeito["QT_INSCRITO_TOTAL_n"] == suspeito["QT_VG_TOTAL_n"], "VAGAS", ""
    )
    suspeito["INSCRITO_IGUAL_A"] = igual
    suspeito.loc[
        suspeito["QT_INSCRITO_TOTAL_n"] == suspeito["QT_ING_n"], "INSCRITO_IGUAL_A"
    ] = (suspeito["INSCRITO_IGUAL_A"] + " ING").str.strip()
    suspeito["DECISAO_CURADORIA"] = (
        "manter: igualdade aritmetica isolada nao demonstra erro de declaracao"
    )
    salvar(
        suspeito[
            BASE_COLS
            + ["QT_VG_TOTAL", "QT_INSCRITO_TOTAL", "QT_ING", "QT_MAT", "INSCRITO_IGUAL_A", "DECISAO_CURADORIA"]
        ],
        "05_igualdades_inscritos.csv",
        "QT_INSCRITO_TOTAL igual a vagas ou ingressantes; igualdade nao comprova erro",
    )


def contradicoes_metricas(P):
    total_vinculos = (
        P["QT_MAT_n"].fillna(0)
        + P["QT_SIT_TRANCADA_n"].fillna(0)
        + P["QT_SIT_DESVINCULADO_n"].fillna(0)
        + P["QT_SIT_TRANSFERIDO_n"].fillna(0)
        + P["QT_SIT_FALECIDO_n"].fillna(0)
    )
    incoerente = P[
        (P["QT_CONC_n"] > P["QT_MAT_n"])
        | (P["QT_ING_n"] > total_vinculos)
    ].copy()
    incoerente["QT_TOTAL_VINCULOS"] = total_vinculos.loc[incoerente.index]

    def diagnostico(linha):
        itens = []
        if linha["QT_CONC_n"] > linha["QT_MAT_n"]:
            itens.append("CONC>MAT")
        if linha["QT_ING_n"] > linha["QT_TOTAL_VINCULOS"]:
            itens.append("ING>TOTAL_VINCULOS")
        return "; ".join(itens)

    incoerente["DIAGNOSTICO"] = incoerente.apply(diagnostico, axis=1)
    salvar(
        incoerente[
            BASE_COLS
            + [
                "QT_ING",
                "QT_MAT",
                "QT_CONC",
                "QT_TOTAL_VINCULOS",
                "DIAGNOSTICO",
            ]
        ],
        "06_contradicoes_metricas.csv",
        "contradicao estrutural: concluinte fora de matriculas ou ingressante fora dos vinculos",
    )


def inscritos_zerados(P):
    zerados = P[P["QT_INSCRITO_TOTAL_n"] == 0].copy()
    zerados["ING_POSITIVO"] = np.where(zerados["QT_ING_n"] > 0, "sim", "nao")
    zerados["DECISAO_CURADORIA"] = (
        "manter; zero pode ser campo nao informado; nao usar em medias de demanda"
    )
    salvar(
        zerados[
            BASE_COLS
            + ["QT_VG_TOTAL", "QT_INSCRITO_TOTAL", "QT_ING", "QT_MAT", "ING_POSITIVO", "DECISAO_CURADORIA"]
        ],
        "18_inscritos_zerados.csv",
        "QT_INSCRITO_TOTAL igual a zero; o dado nao distingue zero real de campo nao informado",
    )


def linhas_tudo_zero(P):
    colunas = [c + "_n" for c in METRICAS]
    zerado = P[P[colunas].fillna(0).sum(axis=1) == 0].copy()
    zerado["DECISAO_CURADORIA"] = (
        "manter na base; excluir apenas de visuais que exigem curso com atividade"
    )
    salvar(
        zerado[BASE_COLS + ["DECISAO_CURADORIA"]],
        "07_linhas_tudo_zero.csv",
        "registro de curso sem atividade em nenhuma metrica disponivel no ano",
    )


def series_baixa_atividade(P):
    def baixa_atividade(grupo):
        if len(grupo) < 3:
            return False
        mat = grupo["QT_MAT_n"].fillna(0)
        return (mat == 0).mean() >= 0.5 and mat.sum() < 20

    sub = P.groupby(["CO_IES", "CO_CURSO"]).filter(baixa_atividade)
    sub = sub.copy()
    sub["DECISAO_CURADORIA"] = (
        "manter; aplicar filtro de atividade conforme a pergunta do visual"
    )
    salvar(
        sub[BASE_COLS + ["QT_MAT", "QT_ING", "QT_CONC", "DECISAO_CURADORIA"]].sort_values(
            ["CO_IES", "CO_CURSO", "NU_ANO_CENSO"]
        ),
        "08_series_baixa_atividade.csv",
        "serie de baixa atividade: >=3 anos, metade com 0 matricula e menos de 20 no total",
    )


def cursos_interdisciplinares(P):
    padrao = r"INTERDISCIPLINAR|BC&T"
    cursos = P[P["NO_CURSO"].fillna("").str.upper().str.contains(padrao)].copy()
    cursos["DECISAO_CURADORIA"] = (
        "manter: e curso de graduacao classificado na area 6, nao ABI"
    )
    salvar(
        cursos[BASE_COLS + ["DECISAO_CURADORIA"]],
        "09_cursos_interdisciplinares.csv",
        "bacharelados interdisciplinares mantidos pelo criterio oficial da area 6",
    )


def ead_distribuicao_municipal_atipica(E):
    municipal = E[
        (E["TP_MODALIDADE_ENSINO"] == "2")
        & E["IN_USAR_MAPA_MUNICIPAL"].fillna("").str.lower().eq("true")
    ].copy()
    municipal["mat"] = municipal["QT_MAT_n"].fillna(0)
    resumo = (
        municipal.groupby(
            ["NU_ANO_CENSO", "CO_IES", "NO_IES", "CO_CURSO", "NO_CURSO"]
        )["mat"]
        .agg(
            MUNICIPIOS="count",
            MUNICIPIOS_SEM_MATRICULA=lambda s: int((s == 0).sum()),
            MAT_TOTAL_MUNICIPAL="sum",
            MAT_MAIOR_MUNICIPIO="max",
        )
        .reset_index()
    )
    resumo = resumo[resumo["MUNICIPIOS"] >= 5]
    resumo["FRAC_MUNICIPIOS_ZERADOS"] = (
        resumo["MUNICIPIOS_SEM_MATRICULA"] / resumo["MUNICIPIOS"]
    ).round(3)
    resumo["FRAC_NO_MAIOR_MUNICIPIO"] = (
        resumo["MAT_MAIOR_MUNICIPIO"]
        / resumo["MAT_TOTAL_MUNICIPAL"].replace(0, np.nan)
    ).round(3)
    resumo = resumo[
        (resumo["MAT_TOTAL_MUNICIPAL"] > 0)
        & (
            (resumo["FRAC_MUNICIPIOS_ZERADOS"] >= 0.6)
            | (resumo["FRAC_NO_MAIOR_MUNICIPIO"] >= 0.9)
        )
    ]
    muitos_zeros = resumo["FRAC_MUNICIPIOS_ZERADOS"] >= 0.6
    concentrado = resumo["FRAC_NO_MAIOR_MUNICIPIO"] >= 0.9
    resumo["PADRAO_ATIPICO"] = np.select(
        [muitos_zeros & concentrado, muitos_zeros, concentrado],
        [
            "muitos municipios zerados e concentracao",
            "muitos municipios zerados",
            "concentracao no maior municipio",
        ],
        default="",
    )
    resumo["PRIORIDADE_SE_PUBLICAR_MAPA"] = np.where(
        muitos_zeros & (resumo["MAT_TOTAL_MUNICIPAL"] >= 100),
        "conferir os municipios no mapa",
        "conferir distribuicao; prioridade secundaria",
    )
    resumo["DECISAO_CURADORIA"] = (
        "manter os totais; nao interpretar municipio associado como polo fisico"
    )
    salvar(
        resumo.sort_values("MUNICIPIOS", ascending=False),
        "10_ead_distribuicao_municipal_atipica.csv",
        "distribuicao municipal EaD concentrada ou com muitas linhas sem matricula; nao comprova erro da IES",
    )


def disponibilidade_metricas(P):
    linhas = []
    for ano, grupo in P.groupby("ANO"):
        linha = {"NU_ANO_CENSO": ano, "LINHAS": len(grupo)}
        for coluna in METRICAS:
            valores = pd.to_numeric(grupo[coluna], errors="coerce")
            linha[coluna + "_pct_preenchido"] = round(valores.notna().mean() * 100, 1)
            linha[coluna + "_pct_maior_zero"] = round((valores > 0).mean() * 100, 1)
        linhas.append(linha)
    pd.DataFrame(linhas).to_csv(
        SAIDA / "11_disponibilidade_metricas_por_ano.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    print("  11_disponibilidade_metricas_por_ano.csv")


def auditar_proxy_ocde_2017(P):
    proxy = P[
        (P["ANO"] == "2017")
        & P["DS_CRITERIO_ESCOPO"].fillna("").str.contains("proxy", case=False)
    ].copy()
    nome = proxy["NO_CURSO"].map(normalizar_texto)
    proxy["TIPO_INFERIDO_PELO_NOME"] = np.select(
        [
            nome.str.contains("ENGENHARIA DE SOFTWARE", regex=False),
            nome.str.contains(r"ENGENHARIA (?:DA|DE)? ?COMPUTACAO", regex=True),
        ],
        ["ENGENHARIA DE SOFTWARE", "ENGENHARIA DE COMPUTACAO"],
        default="OUTRO CURSO RELACIONADO",
    )
    proxy["DECISAO_CURADORIA"] = (
        "manter: 523E04 e o rotulo OCDE oficial de Engenharia de Computacao"
    )
    salvar(
        proxy[BASE_COLS + ["TIPO_INFERIDO_PELO_NOME", "DECISAO_CURADORIA"]],
        "12_proxy_ocde_2017.csv",
        "cursos incluidos pelo codigo OCDE 523E04; nomes divergentes permanecem como declarados na fonte",
    )


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    P = carregar(ARQ_PRINCIPAL)
    E = carregar(ARQ_EXPANDIDA)

    nome_x_rotulo(P)
    rotulo_muda_na_serie(P)
    co_curso_varias_ies(P)
    vagas_repetidas(P)
    igualdades_inscritos(P)
    inscritos_zerados(P)
    contradicoes_metricas(P)
    linhas_tudo_zero(P)
    series_baixa_atividade(P)
    cursos_interdisciplinares(P)
    auditar_proxy_ocde_2017(P)
    ead_distribuicao_municipal_atipica(E)
    disponibilidade_metricas(P)

    print(f"\nExtratos em {SAIDA}")


if __name__ == "__main__":
    main()
