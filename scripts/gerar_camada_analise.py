"""Etapa 3: camada de analise sobre as planilhas oficiais.

Le o recorte (data/processed/oficial), os extratos da curadoria e as decisoes
de config/, marca cada achado como flag e resolve, para cada analise, quais
linhas podem ser usadas. Nao altera a base oficial: exclusao aqui e uma coluna
IN_USO_<ANALISE>, nunca a remocao de uma linha.

Saidas em data/processed/analise/:
    fato_curso_ano.csv          principal + flags + IN_USO_* (uma linha por curso e ano)
    fato_municipio_ano.csv      linhas municipais mapeaveis + flags herdadas + IN_USO_*
    dim_flag.csv                catalogo de flags, com o texto explicativo em portugues simples
    dim_uso.csv                 catalogo de analises, com o aviso que cada grafico deve exibir
    matriz_flag_uso.csv         tratamento de cada flag em cada analise (formato longo)
    cobertura_uso.csv           quanto cada analise usa, exclui e nao tem por ano
    decisoes_manuais_aplicadas.csv  efeito de cada excecao de config/decisoes_manuais.csv

Documentacao: docs/03_manual_de_uso.md

Uso:
    .venv/bin/python scripts/gerar_camada_analise.py
"""
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OFICIAL = ROOT / "data" / "processed" / "oficial"
CURADORIA = ROOT / "data" / "processed" / "curadoria"
CONFIG = ROOT / "config"
SAIDA = ROOT / "data" / "processed" / "analise"

CHAVE = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]
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
TRATAMENTOS = {"excluir", "sinalizar", "-"}
NIVEIS = {"Suspeito": 2, "Baixo impacto": 1, "Estrutural": 1}
GRAOS = {"curso_ano", "municipio_ano"}
PUBLICAR = {"sim", "exploratorio", "nao"}
GRAVIDADES = ["Sem observações", "Informação", "Atenção", "Alerta"]
COLUNAS_TEXTO = ["TITULO", "O_QUE_E", "POR_QUE_IMPORTA", "O_QUE_FAZER", "ONDE_LER_MAIS"]

# regra da vistoria (extrato 13) -> flag de nivel curso e ano
REGRAS_VISTORIA = {
    "todas_metricas_informadas_zero": "FL_TUDO_ZERO",
    "zero_matriculas_com_ingresso": "FL_MAT_ZERO_COM_ING",
    "zero_matriculas_com_ingresso_1_a_19": "FL_MAT_ZERO_COM_ING",
    "matriculas_caem_a_zero": "FL_MAT_CAI_A_ZERO",
    "zero_entre_anos_com_50_ou_mais": "FL_ZERO_LACUNA_50",
    "salto_matriculas_5x_500": "FL_SALTO_MAT",
    "classificacao_em_definicao": "FL_ROTULO_EM_DEFINICAO",
    "ead_todos_municipios_zero": "FL_EAD_TODOS_MUN_ZERO",
    "ead_muitos_zeros_sem_piso_matriculas": "FL_EAD_MUNICIPIOS_ZERADOS_AMPLA",
    "mudanca_distribuicao_municipal": "FL_MUDANCA_DISTRIBUICAO",
}


class ErroConfiguracao(Exception):
    pass


# ---------------------------------------------------------------- leitura

def ler(caminho):
    return pd.read_csv(
        caminho, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False
    )


def numerico(serie):
    return pd.to_numeric(serie, errors="coerce")


def carregar_config():
    flags = ler(CONFIG / "flags.csv")
    usos = ler(CONFIG / "usos.csv")
    matriz = ler(CONFIG / "matriz_flag_uso.csv")
    decisoes = ler(CONFIG / "decisoes_manuais.csv")
    validar_config(flags, usos, matriz, decisoes)
    return flags, usos, matriz.set_index("FLAG"), decisoes


def carregar_textos(flags):
    """Textos em portugues simples de cada flag e configuracao do portal."""
    textos = ler(CONFIG / "textos_flags.csv")
    if set(textos["FLAG"]) != set(flags["FLAG"]) or textos["FLAG"].duplicated().any():
        dif = set(textos["FLAG"]) ^ set(flags["FLAG"])
        raise ErroConfiguracao(f"textos_flags.csv e flags.csv divergem em {sorted(dif)}")
    for coluna in COLUNAS_TEXTO:
        vazias = textos.loc[textos[coluna].str.strip() == "", "FLAG"].tolist()
        if vazias:
            raise ErroConfiguracao(f"textos_flags.csv sem {coluna} em {vazias}")
    portal = dict(ler(CONFIG / "portal.csv")[["CHAVE", "VALOR"]].itertuples(index=False))
    return textos.set_index("FLAG"), portal


def lista_pt(itens):
    """Junta itens em portugues: a, b e c."""
    itens = list(itens)
    if len(itens) <= 1:
        return "".join(itens)
    return ", ".join(itens[:-1]) + " e " + itens[-1]


def derivar_efeitos(flags, textos, matriz, usos, portal):
    """O que o painel faz com cada flag, derivado da matriz para nunca contradize-la."""
    nome = usos.set_index("USO")["NOME_AMIGAVEL"]
    nivel = flags.set_index("FLAG")["NIVEL"]
    contato = portal.get("CONTATO_PROJETO", "").strip()
    linhas = []
    for flag in flags["FLAG"]:
        celulas = matriz.loc[flag]
        fora = [nome[u] for u in nome.index if celulas[u] == "excluir"]
        aviso = [nome[u] for u in nome.index if celulas[u] == "sinalizar"]
        if fora:
            gravidade = "Alerta"
        elif nivel[flag] == "Suspeito":
            gravidade = "Atenção"
        else:
            gravidade = "Informação"
        partes = []
        if fora:
            partes.append("Fica de fora de: " + lista_pt(fora) + ".")
        if aviso:
            partes.append("Aparece com aviso em: " + lista_pt(aviso) + ".")
        if not partes:
            partes.append("Não altera nenhum gráfico. É só informativo.")
        fazer = textos.loc[flag, "O_QUE_FAZER"]
        if contato:
            fazer += f" Se preferir, fale com a equipe do projeto: {contato}."
        linhas.append(
            {
                "FLAG": flag,
                "TITULO": textos.loc[flag, "TITULO"],
                "GRAVIDADE": gravidade,
                "NV": GRAVIDADES.index(gravidade),
                "FICA_DE_FORA_DE": lista_pt(fora),
                "APARECE_COM_AVISO_EM": lista_pt(aviso),
                "COMO_TRATAMOS": " ".join(partes),
                "O_QUE_FAZER": fazer,
            }
        )
    return pd.DataFrame(linhas).set_index("FLAG")


def montar_dim_flag(flags, textos, efeitos):
    saida = flags.set_index("FLAG").join(
        textos[["O_QUE_E", "POR_QUE_IMPORTA", "ONDE_LER_MAIS"]]
    ).join(
        efeitos[["TITULO", "GRAVIDADE", "COMO_TRATAMOS", "FICA_DE_FORA_DE",
                 "APARECE_COM_AVISO_EM", "O_QUE_FAZER"]]
    ).reset_index()
    saida = saida.rename(columns={"DESCRICAO": "DESCRICAO_TECNICA"})
    return saida[["FLAG", "TITULO", "GRAVIDADE", "O_QUE_E", "POR_QUE_IMPORTA", "COMO_TRATAMOS",
                  "FICA_DE_FORA_DE", "APARECE_COM_AVISO_EM", "O_QUE_FAZER", "ONDE_LER_MAIS",
                  "NIVEL", "GRAO", "FONTE", "DESCRICAO_TECNICA"]]


def montar_dim_uso(usos, matriz, efeitos):
    """Aviso que todo grafico de uma analise deve exibir, derivado da matriz."""
    linhas = []
    for _, uso in usos.iterrows():
        u = uso["USO"]
        fora = [efeitos.loc[f, "TITULO"] for f in matriz.index if matriz.loc[f, u] == "excluir"]
        aviso = [efeitos.loc[f, "TITULO"] for f in matriz.index if matriz.loc[f, u] == "sinalizar"]
        partes = []
        partes.append("Fica de fora deste gráfico: " + "; ".join(fora) + "." if fora
                      else "Nenhum registro fica de fora deste gráfico por regra.")
        if aviso:
            partes.append("Aparece com aviso: " + "; ".join(aviso) + ".")
        linha = uso.to_dict()
        linha["FICA_DE_FORA_DESTE_GRAFICO"] = "; ".join(fora)
        linha["COM_AVISO_NESTE_GRAFICO"] = "; ".join(aviso)
        linha["AVISO_DO_GRAFICO"] = " ".join(partes)
        linhas.append(linha)
    return pd.DataFrame(linhas)


def validar_config(flags, usos, matriz, decisoes):
    """Falha cedo quando a configuracao editada a mao esta inconsistente."""
    if flags["FLAG"].duplicated().any():
        raise ErroConfiguracao("flags.csv tem FLAG repetida")
    if not set(flags["NIVEL"]) <= set(NIVEIS):
        raise ErroConfiguracao(f"NIVEL invalido em flags.csv: {set(flags['NIVEL']) - set(NIVEIS)}")
    if not set(flags["GRAO"]) <= GRAOS:
        raise ErroConfiguracao("GRAO invalido em flags.csv")
    if not set(usos["GRAO"]) <= GRAOS:
        raise ErroConfiguracao("GRAO invalido em usos.csv")
    if not set(usos["PUBLICAR"]) <= PUBLICAR:
        raise ErroConfiguracao("PUBLICAR invalido em usos.csv")
    if (usos["NOME_AMIGAVEL"].str.strip() == "").any():
        raise ErroConfiguracao("NOME_AMIGAVEL vazio em usos.csv")
    if set(matriz["FLAG"]) != set(flags["FLAG"]):
        dif = set(matriz["FLAG"]) ^ set(flags["FLAG"])
        raise ErroConfiguracao(f"flags.csv e matriz_flag_uso.csv divergem em {sorted(dif)}")
    colunas_uso = [c for c in matriz.columns if c not in ("FLAG", "DECISAO")]
    if set(colunas_uso) != set(usos["USO"]):
        raise ErroConfiguracao("colunas da matriz nao batem com usos.csv")
    for coluna in colunas_uso:
        invalidos = set(matriz[coluna]) - TRATAMENTOS
        if invalidos:
            raise ErroConfiguracao(f"tratamento invalido na matriz, coluna {coluna}: {invalidos}")
    usos_validos = set(usos["USO"]) | {"*"}
    for i, d in decisoes.iterrows():
        linha = i + 2
        if not (d["CO_IES"] or d["CO_CURSO"]):
            raise ErroConfiguracao(f"decisoes_manuais.csv linha {linha}: informe CO_IES ou CO_CURSO")
        if d["USO"] not in usos_validos:
            raise ErroConfiguracao(f"decisoes_manuais.csv linha {linha}: USO invalido {d['USO']!r}")
        if d["ACAO"] not in ("excluir", "manter"):
            raise ErroConfiguracao(f"decisoes_manuais.csv linha {linha}: ACAO deve ser excluir ou manter")
        if not d["JUSTIFICATIVA"].strip() or not d["DATA"].strip():
            raise ErroConfiguracao(f"decisoes_manuais.csv linha {linha}: JUSTIFICATIVA e DATA sao obrigatorias")


# ------------------------------------------------------------------ flags

def chaves_marcadas(df, chaves, colunas=CHAVE):
    """Booleano por linha de df: a chave aparece em `chaves`."""
    if chaves.empty:
        return np.zeros(len(df), dtype=bool)
    alvo = pd.MultiIndex.from_frame(chaves[colunas].astype(str).drop_duplicates())
    return pd.MultiIndex.from_frame(df[colunas].astype(str)).isin(alvo)


def divergencia_nome_rotulo(P):
    """Nome x rotulo: descarta o que a curadoria julgou compativel (nome composto ou historico)."""
    e01 = ler(CURADORIA / "01_nome_curso_x_rotulo_divergente.csv")
    reais = e01[~e01["RESULTADO_CURADORIA"].str.startswith("compativel")]
    chave = ["CO_IES", "CO_CURSO", "NO_CURSO", "NO_ROTULO_AREA"]
    base = P[chave + ["NU_ANO_CENSO"]].assign(POS=np.arange(len(P)))
    casados = base.merge(reais[chave + ["ANO_INICIAL", "ANO_FINAL"]], on=chave)
    ano = casados["NU_ANO_CENSO"].astype(int)
    dentro = casados[(ano >= casados["ANO_INICIAL"].astype(int)) & (ano <= casados["ANO_FINAL"].astype(int))]
    esperado = int(reais["QT_ANOS"].astype(int).sum())
    if len(dentro) != esperado:
        raise ErroConfiguracao(f"divergencia nome x rotulo: {len(dentro)} linhas contra {esperado} do extrato 01")
    return np.isin(np.arange(len(P)), dentro["POS"].to_numpy())


def calcular_flags_curso(P, E):
    """Flags de nivel curso e ano. Devolve DataFrame booleano alinhado a P."""
    F = pd.DataFrame(index=P.index)
    vistoria = ler(CURADORIA / "13_vistoria_casos.csv")
    for regra, flag in REGRAS_VISTORIA.items():
        marcado = chaves_marcadas(P, vistoria[vistoria["REGRA"] == regra])
        F[flag] = F[flag] | marcado if flag in F else marcado

    F["FL_NOME_ROTULO_DIVERGENTE"] = divergencia_nome_rotulo(P)
    F["FL_INSCRITO_ZERO"] = chaves_marcadas(P, ler(CURADORIA / "18_inscritos_zerados.csv"))
    F["FL_INSCRITO_IGUAL"] = chaves_marcadas(P, ler(CURADORIA / "05_igualdades_inscritos.csv"))
    F["FL_BAIXA_ATIVIDADE"] = chaves_marcadas(P, ler(CURADORIA / "08_series_baixa_atividade.csv"))
    F["FL_INTERDISCIPLINAR"] = chaves_marcadas(P, ler(CURADORIA / "09_cursos_interdisciplinares.csv"))
    F["FL_PROXY_OCDE_2017"] = chaves_marcadas(P, ler(CURADORIA / "12_proxy_ocde_2017.csv"))
    F["FL_EAD_DISTRIB_ATIPICA"] = chaves_marcadas(
        P, ler(CURADORIA / "10_ead_distribuicao_municipal_atipica.csv")
    )

    repetidas = ler(CURADORIA / "04_vagas_repetidas_por_ies_ano.csv")
    F["FL_VAGAS_IES_ANO_SUSPEITO"] = chaves_marcadas(
        P, repetidas, ["NU_ANO_CENSO", "CO_IES"]
    )
    valor = repetidas[["NU_ANO_CENSO", "CO_IES", "VALOR_VAGAS"]].copy()
    valor["VALOR_VAGAS"] = numerico(valor["VALOR_VAGAS"])
    com_valor = P[["NU_ANO_CENSO", "CO_IES"]].assign(
        VAGAS=numerico(P["QT_VG_TOTAL"]), POS=np.arange(len(P))
    ).merge(valor, on=["NU_ANO_CENSO", "CO_IES"], how="inner")
    iguais = com_valor.loc[com_valor["VAGAS"] == com_valor["VALOR_VAGAS"], "POS"]
    F["FL_VAGAS_REPETIDAS"] = np.isin(np.arange(len(P)), iguais.to_numpy())

    serie = ler(CURADORIA / "02_co_curso_rotulo_muda_na_serie.csv")
    F["FL_ROTULO_MUDA_NA_SERIE"] = chaves_marcadas(P, serie, ["CO_IES", "CO_CURSO"])
    varias_ies = set(ler(CURADORIA / "03_co_curso_em_varias_ies.csv")["CO_CURSO"])
    F["FL_CO_CURSO_EM_VARIAS_IES"] = P["CO_CURSO"].isin(varias_ies).to_numpy()

    com_municipio = E[E["IN_USAR_MAPA_MUNICIPAL"].str.lower() == "true"]
    tem_territorio = chaves_marcadas(P, com_municipio[CHAVE])
    F["FL_EAD_SEM_TERRITORIO"] = (P["DS_TP_MODALIDADE_ENSINO"] == "EaD").to_numpy() & ~tem_territorio
    return F.astype(bool)


def calcular_flag_municipal(M):
    """Sequencias de tres anos ou mais com matricula zero no municipio (extrato 16)."""
    execucoes = ler(CURADORIA / "16_zeros_municipais_persistentes.csv")
    linhas = []
    for _, e in execucoes.iterrows():
        for ano in range(int(e["ANO_INICIAL"]), int(e["ANO_FINAL"]) + 1):
            linhas.append((str(ano), e["CO_IES"], e["CO_CURSO"], e["CO_MUNICIPIO"]))
    cols = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO", "CO_MUNICIPIO"]
    marcadas = pd.DataFrame(linhas, columns=cols)
    return pd.DataFrame({"FL_MUN_ZERO_3_ANOS": chaves_marcadas(M, marcadas, cols)}, index=M.index)


def resumo_observacoes(F, efeitos):
    """NV_ATENCAO (0 a 3), quantidade, codigos e titulos das flags de cada linha, do mais grave ao menos."""
    colunas = list(F.columns)
    nv_flag = efeitos.loc[colunas, "NV"].to_numpy()
    ordem = np.argsort(-nv_flag, kind="stable")
    valores = F.to_numpy(dtype=bool)
    nv = (valores * nv_flag).max(axis=1) if len(colunas) else np.zeros(len(F), dtype=int)
    codigos = np.array([c.removeprefix("FL_") for c in colunas], dtype=object)[ordem]
    titulos = efeitos.loc[colunas, "TITULO"].to_numpy(dtype=object)[ordem]
    ordenados = valores[:, ordem]
    ds_flags = ["|".join(codigos[linha]) for linha in ordenados]
    ds_obs = [" • ".join(titulos[linha]) for linha in ordenados]
    gravidade = np.array(GRAVIDADES, dtype=object)[nv]
    return nv.astype(int), valores.sum(axis=1).astype(int), ds_flags, ds_obs, gravidade


# ---------------------------------------------------------- regras de uso

def flags_que_excluem(matriz, uso, flags_disponiveis):
    ativas = matriz.index[matriz[uso] == "excluir"]
    return [f for f in ativas if f in flags_disponiveis]


def excluir_por_flags(F, flags):
    if not flags:
        return pd.Series(False, index=F.index)
    return F[flags].any(axis=1)


def classificar(base_ok, excluir):
    """usada, sem_dado (nao atende ao requisito da analise) ou excluida."""
    valores = np.where(~base_ok, "sem_dado", np.where(excluir, "excluida", "usada"))
    return pd.Series(valores, index=base_ok.index)


def casar_decisao(df, d):
    mascara = pd.Series(True, index=df.index)
    for coluna in ("CO_IES", "CO_CURSO", "NU_ANO_CENSO"):
        if d[coluna]:
            mascara &= df[coluna].astype(str) == str(d[coluna])
    return mascara


def aplicar_decisoes(df, status, uso, decisoes):
    """Aplica excecoes manuais em ordem. `manter` nao recupera linha sem_dado."""
    status = status.copy()
    registro = []
    for i, d in decisoes.iterrows():
        if d["USO"] not in ("*", uso):
            continue
        casadas = casar_decisao(df, d)
        if d["ACAO"] == "excluir":
            alterar = casadas & (status == "usada")
            status[alterar] = "excluida"
        else:
            alterar = casadas & (status == "excluida")
            status[alterar] = "usada"
        registro.append(
            {
                "DECISAO_LINHA": i + 2,
                "USO": uso,
                "ACAO": d["ACAO"],
                "CO_IES": d["CO_IES"],
                "CO_CURSO": d["CO_CURSO"],
                "NU_ANO_CENSO": d["NU_ANO_CENSO"],
                "DECISAO": d["DECISAO"],
                "LINHAS_CASADAS": int(casadas.sum()),
                "LINHAS_ALTERADAS": int(alterar.sum()),
            }
        )
    return status, registro


def base_disponivel(df, uso_cfg):
    """Requisito minimo da analise: metrica de referencia preenchida e, se exigido, matricula positiva."""
    ok = pd.Series(True, index=df.index)
    metrica = uso_cfg["METRICA_REF"]
    if metrica.startswith("QT_"):
        ok &= numerico(df[metrica]).notna()
    if uso_cfg["EXIGE_MAT_POSITIVA"] == "sim":
        ok &= numerico(df["QT_MAT"]) > 0
    return ok


def volume(df, uso_cfg):
    metrica = uso_cfg["METRICA_REF"]
    if metrica.startswith("QT_"):
        return numerico(df[metrica]).fillna(0)
    return pd.Series(1.0, index=df.index)


# -------------------------------------------------------------- cobertura

def tabela_cobertura(df, status, uso_cfg, sem_territorio):
    v = volume(df, uso_cfg)
    base = pd.DataFrame(
        {
            "NU_ANO_CENSO": df["NU_ANO_CENSO"].to_numpy(),
            "DS_TP_MODALIDADE_ENSINO": df["DS_TP_MODALIDADE_ENSINO"].to_numpy(),
            "STATUS": status.to_numpy(),
            "VOL": v.to_numpy(),
        }
    )
    grupos = base.groupby(["NU_ANO_CENSO", "DS_TP_MODALIDADE_ENSINO", "STATUS"])
    linhas = grupos.size().unstack("STATUS", fill_value=0)
    vols = grupos["VOL"].sum().unstack("STATUS", fill_value=0)
    for tabela in (linhas, vols):
        for coluna in ("usada", "excluida", "sem_dado"):
            if coluna not in tabela:
                tabela[coluna] = 0
    saida = pd.DataFrame(index=linhas.index)
    saida["LINHAS_USADAS"] = linhas["usada"]
    saida["LINHAS_EXCLUIDAS"] = linhas["excluida"]
    saida["LINHAS_SEM_DADO"] = linhas["sem_dado"]
    saida["VOLUME_USADO"] = vols["usada"]
    saida["VOLUME_EXCLUIDO"] = vols["excluida"]
    saida["VOLUME_SEM_DADO"] = vols["sem_dado"]
    saida["VOLUME_SEM_TERRITORIO"] = 0.0
    if sem_territorio is not None:
        # anos sem nenhuma linha municipal (EaD 2017-2019) so existem em sem_territorio
        saida = saida.reindex(saida.index.union(sem_territorio.index)).fillna(0)
        saida["VOLUME_SEM_TERRITORIO"] = sem_territorio.reindex(saida.index).fillna(0)
        colunas_linhas = ["LINHAS_USADAS", "LINHAS_EXCLUIDAS", "LINHAS_SEM_DADO"]
        saida[colunas_linhas] = saida[colunas_linhas].astype(int)
    total_linhas = saida["LINHAS_USADAS"] + saida["LINHAS_EXCLUIDAS"] + saida["LINHAS_SEM_DADO"]
    saida["PCT_LINHAS_USADAS"] = (100 * saida["LINHAS_USADAS"] / total_linhas.replace(0, np.nan)).round(2)
    total = (
        saida["VOLUME_USADO"]
        + saida["VOLUME_EXCLUIDO"]
        + saida["VOLUME_SEM_DADO"]
        + saida["VOLUME_SEM_TERRITORIO"]
    )
    saida["PCT_VOLUME_USADO"] = (100 * saida["VOLUME_USADO"] / total.replace(0, np.nan)).round(2)
    saida["PCT_VOLUME_EXCLUIDO"] = (100 * saida["VOLUME_EXCLUIDO"] / total.replace(0, np.nan)).round(2)
    saida = saida.reset_index()
    saida.insert(0, "USO", uso_cfg["USO"])
    saida.insert(1, "METRICA_REF", uso_cfg["METRICA_REF"])
    return saida


# ------------------------------------------------------------ conferencias

def conferir_contra_curadoria(F):
    """As flags devem reproduzir as quantidades registradas na cobertura da vistoria."""
    cobertura = ler(CURADORIA / "14_vistoria_cobertura.csv").set_index("REGRA")["QUANTIDADE"].astype(int)
    esperado = {}
    for regra, flag in REGRAS_VISTORIA.items():
        esperado[flag] = esperado.get(flag, 0) + int(cobertura[regra])
    divergencias = [
        f"{flag}: flag={int(F[flag].sum())} curadoria={qt}"
        for flag, qt in esperado.items()
        if int(F[flag].sum()) != qt
    ]
    if divergencias:
        raise ErroConfiguracao("flags nao reproduzem a curadoria: " + "; ".join(divergencias))


# ------------------------------------------------------------------- main

def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    flags_cfg, usos_cfg, matriz, decisoes = carregar_config()
    textos, portal = carregar_textos(flags_cfg)
    efeitos = derivar_efeitos(flags_cfg, textos, matriz, usos_cfg, portal)

    P = ler(OFICIAL / "planilha_oficial_computacao.csv")
    E = ler(OFICIAL / "planilha_oficial_computacao_expandida.csv")
    P["CH_CURSO_ANO"] = P["NU_ANO_CENSO"] + "|" + P["CO_IES"] + "|" + P["CO_CURSO"]
    P["CH_SERIE_CURSO"] = P["CO_IES"] + "|" + P["CO_CURSO"]
    if P["CH_CURSO_ANO"].duplicated().any():
        raise ErroConfiguracao("chave ano + IES + curso duplicada na principal")

    F = calcular_flags_curso(P, E)
    conferir_contra_curadoria(F)
    flags_curso = flags_cfg.loc[flags_cfg["GRAO"] == "curso_ano", "FLAG"].tolist()
    if set(flags_curso) != set(F.columns):
        raise ErroConfiguracao(f"flags calculadas divergem de flags.csv: {set(flags_curso) ^ set(F.columns)}")
    F = F[flags_curso]
    nv, qt, lista, obs, gravidade = resumo_observacoes(F, efeitos)

    # municipal
    mapeavel = E["IN_USAR_MAPA_MUNICIPAL"].str.lower() == "true"
    M = E[mapeavel].copy().reset_index(drop=True)
    M["CH_CURSO_ANO"] = M["NU_ANO_CENSO"] + "|" + M["CO_IES"] + "|" + M["CO_CURSO"]
    posicao = pd.Series(np.arange(len(P)), index=P["CH_CURSO_ANO"])
    pos_m = posicao.reindex(M["CH_CURSO_ANO"]).to_numpy()
    if np.isnan(pos_m).any():
        raise ErroConfiguracao("linha municipal sem curso correspondente na principal")
    pos_m = pos_m.astype(int)
    FM = calcular_flag_municipal(M)
    ead_m = M["TP_MODALIDADE_ENSINO"] == "2"
    for coluna in ("QT_VG_TOTAL", "QT_INSCRITO_TOTAL"):
        M.loc[ead_m, coluna] = ""  # em EaD o zero municipal significa "nao se aplica"

    P_out = P.copy()
    for flag in flags_curso:
        P_out[flag] = F[flag].astype(int).to_numpy()
    P_out["QT_FLAGS"] = qt
    P_out["NV_ATENCAO"] = nv
    P_out["GRAVIDADE"] = gravidade
    P_out["DS_FLAGS"] = lista
    P_out["DS_OBSERVACOES"] = obs

    registros_manuais, coberturas = [], []
    M_out = M[
        ["CH_CURSO_ANO", "NU_ANO_CENSO", "CO_IES", "CO_CURSO", "TP_MODALIDADE_ENSINO",
         "DS_TP_MODALIDADE_ENSINO", "TP_DIMENSAO", "DS_TP_DIMENSAO", "CO_UF", "SG_UF",
         "CO_MUNICIPIO", "NO_MUNICIPIO", "QT_VG_TOTAL", "QT_INSCRITO_TOTAL", "QT_ING",
         "QT_MAT", "QT_CONC", "QT_SIT_TRANCADA", "QT_SIT_DESVINCULADO",
         "QT_SIT_TRANSFERIDO", "QT_SIT_FALECIDO"]
    ].copy()
    mun = FM["FL_MUN_ZERO_3_ANOS"].to_numpy()
    nv_mun = int(efeitos.loc["FL_MUN_ZERO_3_ANOS", "NV"])
    titulo_mun = efeitos.loc["FL_MUN_ZERO_3_ANOS", "TITULO"]
    nv_m = np.maximum(nv[pos_m], np.where(mun, nv_mun, 0))
    ds_flags_m = np.array(lista, dtype=object)[pos_m]
    obs_m = np.array(obs, dtype=object)[pos_m]
    M_out["NV_ATENCAO"] = nv_m
    M_out["GRAVIDADE"] = np.array(GRAVIDADES, dtype=object)[nv_m]
    M_out["DS_FLAGS"] = np.where(mun, np.where(ds_flags_m == "", "MUN_ZERO_3_ANOS", ds_flags_m + "|MUN_ZERO_3_ANOS"), ds_flags_m)
    M_out["DS_OBSERVACOES"] = np.where(mun, np.where(obs_m == "", titulo_mun, obs_m + " • " + titulo_mun), obs_m)
    M_out["FL_MUN_ZERO_3_ANOS"] = mun.astype(int)

    # matricula sem territorio (estrutural) por ano e modalidade, para a cobertura municipal
    fora = E[~mapeavel]
    sem_terr = numerico(fora["QT_MAT"]).groupby(
        [fora["NU_ANO_CENSO"], fora["DS_TP_MODALIDADE_ENSINO"]]
    ).sum()

    for _, uso in usos_cfg.iterrows():
        nome = uso["USO"]
        excluem = flags_que_excluem(matriz, nome, set(flags_cfg["FLAG"]))
        if uso["GRAO"] == "curso_ano":
            df = P
            excl = excluir_por_flags(F, [f for f in excluem if f in F.columns])
        else:
            df = M
            curso_flags = [f for f in excluem if f in F.columns]
            excl_curso = excluir_por_flags(F, curso_flags).to_numpy()[pos_m]
            excl_mun = excluir_por_flags(FM, [f for f in excluem if f in FM.columns]).to_numpy()
            excl = pd.Series(excl_curso | excl_mun, index=M.index)
        status = classificar(base_disponivel(df, uso), excl)
        status, registro = aplicar_decisoes(df, status, nome, decisoes)
        registros_manuais.extend(registro)
        coluna = f"IN_USO_{nome}"
        destino = P_out if uso["GRAO"] == "curso_ano" else M_out
        destino[coluna] = (status == "usada").astype(int).to_numpy()
        terr = sem_terr if (uso["GRAO"] == "municipio_ano" and uso["METRICA_REF"].startswith("QT_")) else None
        coberturas.append(tabela_cobertura(df, status, uso, terr))

    # conferencias finais
    mat_p = numerico(P["QT_MAT"]).sum()
    mat_m = numerico(M["QT_MAT"]).sum()
    mat_fora = numerico(fora["QT_MAT"]).sum()
    if mat_p != mat_m + mat_fora:
        raise ErroConfiguracao(f"matriculas nao reconciliam: principal={mat_p} municipal+fora={mat_m + mat_fora}")

    cobertura_mapa = pd.concat([c for c in coberturas if c["USO"].iloc[0] == "MAPA_MUN"])
    soma_mapa = cobertura_mapa[["VOLUME_USADO", "VOLUME_EXCLUIDO", "VOLUME_SEM_TERRITORIO"]].to_numpy().sum()
    if not np.isclose(soma_mapa, mat_p):
        raise ErroConfiguracao(f"cobertura do mapa nao fecha com a principal: {soma_mapa} contra {mat_p}")

    # saidas
    P_out.to_csv(SAIDA / "fato_curso_ano.csv", sep=";", index=False, encoding="utf-8-sig")
    M_out.to_csv(SAIDA / "fato_municipio_ano.csv", sep=";", index=False, encoding="utf-8-sig")
    montar_dim_flag(flags_cfg, textos, efeitos).to_csv(
        SAIDA / "dim_flag.csv", sep=";", index=False, encoding="utf-8-sig"
    )
    montar_dim_uso(usos_cfg, matriz, efeitos).to_csv(
        SAIDA / "dim_uso.csv", sep=";", index=False, encoding="utf-8-sig"
    )
    longa = matriz.reset_index().melt(
        id_vars=["FLAG", "DECISAO"], var_name="USO", value_name="TRATAMENTO"
    )
    longa[["FLAG", "USO", "TRATAMENTO", "DECISAO"]].to_csv(
        SAIDA / "matriz_flag_uso.csv", sep=";", index=False, encoding="utf-8-sig"
    )
    pd.concat(coberturas, ignore_index=True).to_csv(
        SAIDA / "cobertura_uso.csv", sep=";", index=False, encoding="utf-8-sig"
    )
    cols_manuais = ["DECISAO_LINHA", "USO", "ACAO", "CO_IES", "CO_CURSO", "NU_ANO_CENSO",
                    "DECISAO", "LINHAS_CASADAS", "LINHAS_ALTERADAS"]
    pd.DataFrame(registros_manuais, columns=cols_manuais).to_csv(
        SAIDA / "decisoes_manuais_aplicadas.csv", sep=";", index=False, encoding="utf-8-sig"
    )

    print(f"fato_curso_ano: {len(P_out)} linhas, {len(flags_curso)} flags")
    print(f"fato_municipio_ano: {len(M_out)} linhas")
    for _, uso in usos_cfg.iterrows():
        col = f"IN_USO_{uso['USO']}"
        destino = P_out if uso["GRAO"] == "curso_ano" else M_out
        usadas = int(destino[col].sum())
        print(f"  {uso['USO']:12s} usadas {usadas:7d} de {len(destino):7d}")
    print(f"decisoes manuais: {len(decisoes)}")
    print(f"Saidas em {SAIDA}")


if __name__ == "__main__":
    main()
