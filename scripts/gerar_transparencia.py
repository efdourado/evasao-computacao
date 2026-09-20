"""Etapa 3 (transparencia): explica cada registro em portugues simples.

Le as tabelas de analise ja geradas e os extratos da curadoria, e escreve em
data/processed/analise/:

    ocorrencias.csv     uma linha por registro e por observacao, com a evidencia
                        concreta do caso e o que o painel faz com ele
    resumo_ies_ano.csv  um resumo em texto por instituicao e ano

O objetivo e que qualquer pessoa, inclusive a propria instituicao, consiga
clicar em "entender" e ver o que foi observado, com os numeros do proprio caso,
sem abrir planilha. Nenhum valor da base oficial e alterado.

Documentacao: docs/03_manual_de_uso.md

Uso:
    .venv/bin/python scripts/gerar_transparencia.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_camada_analise import (  # noqa: E402
    CONFIG, CURADORIA, SAIDA, GRAVIDADES, ErroConfiguracao, ler, lista_pt,
)
from gerar_extratos_curadoria import normalizar_texto  # noqa: E402

CHAVE = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]
FLAGS_MUNICIPAIS = {"FL_MUN_ZERO_3_ANOS"}


# ---------------------------------------------------------------- formatos

def n(valor):
    """Numero inteiro no padrao brasileiro, ou 'sem dado'."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "sem dado"
    if np.isnan(numero):
        return "sem dado"
    return f"{int(round(numero)):,}".replace(",", ".")


def pct(fracao):
    try:
        return f"{float(fracao) * 100:.0f}%".replace(".", ",")
    except (TypeError, ValueError):
        return "sem dado"


def plural(valor, singular, plural_):
    """1 ingressante, 2 ingressantes."""
    try:
        um = float(valor) == 1
    except (TypeError, ValueError):
        um = False
    return f"{n(valor)} {singular if um else plural_}"


def num(r, coluna):
    try:
        valor = float(r.get(coluna, ""))
    except (TypeError, ValueError):
        return float("nan")
    return valor


# ---------------------------------------------------------------- contexto

class Contexto:
    """Tudo o que as frases precisam para citar numeros do proprio caso."""

    def __init__(self, fato, municipal):
        self.ultimo_ano = int(fato["NU_ANO_CENSO"].astype(int).max())
        mat = fato[["CO_IES", "CO_CURSO", "NU_ANO_CENSO", "QT_MAT"]]
        self.mat = {
            (i, c, int(a)): float(m) if m != "" else float("nan")
            for i, c, a, m in mat.itertuples(index=False)
        }
        total = fato.assign(M=pd.to_numeric(fato["QT_MAT"], errors="coerce").fillna(0))
        serie = total.groupby(["CO_IES", "CO_CURSO"]).agg(ANOS=("M", "size"), MAT=("M", "sum"))
        self.serie = serie.to_dict("index")
        muni = municipal.assign(M=pd.to_numeric(municipal["QT_MAT"], errors="coerce"))
        agg = muni.groupby("CH_CURSO_ANO").agg(
            MUN=("CO_MUNICIPIO", "nunique"), ZERO=("M", lambda s: int((s == 0).sum()))
        )
        self.municipios = agg.to_dict("index")
        self.vagas = self._indice("04_vagas_repetidas_por_ies_ano.csv", ["NU_ANO_CENSO", "CO_IES"])
        self.inscrito = self._indice("05_igualdades_inscritos.csv", CHAVE)
        self.ead = self._indice("10_ead_distribuicao_municipal_atipica.csv", CHAVE)
        self.mudanca = self._indice("17_mudancas_distribuicao.csv", CHAVE)
        self.rotulos = self._indice("02_co_curso_rotulo_muda_na_serie.csv", ["CO_IES", "CO_CURSO"])
        codigos = set(ler(CURADORIA / "03_co_curso_em_varias_ies.csv")["CO_CURSO"])
        sub = fato[fato["CO_CURSO"].isin(codigos)].assign(A=fato["NU_ANO_CENSO"].astype(int))
        por_ies = sub.groupby(["CO_CURSO", "CO_IES"]).agg(INI=("A", "min"), FIM=("A", "max"), NOME=("NO_IES", "last"))
        self.varias_ies = {}
        for (curso, _), l in por_ies.sort_values("INI").iterrows():
            self.varias_ies.setdefault(curso, []).append((l["INI"], l["FIM"], l["NOME"]))
        self.zeros = ler(CURADORIA / "16_zeros_municipais_persistentes.csv")
        self.rotulos_cron = self._rotulos_cronologicos(fato)

    def _rotulos_cronologicos(self, fato):
        """Para cursos cujo rotulo muda: sequencia (ano inicial, ano final, rotulo), sem contar variacoes triviais."""
        alvo = set(self.rotulos)
        sub = fato[[(i, c) in alvo for i, c in zip(fato["CO_IES"], fato["CO_CURSO"])]]
        sub = sub.assign(A=sub["NU_ANO_CENSO"].astype(int)).sort_values(["CO_IES", "CO_CURSO", "A"])
        saida = {}
        for (ies, curso), g in sub.groupby(["CO_IES", "CO_CURSO"]):
            corridas = []
            for a, rotulo in zip(g["A"], g["NO_ROTULO_AREA"]):
                canon = normalizar_texto(rotulo)
                if canon.startswith("ENGENHARIA DE COMPUTACAO"):
                    canon = "ENGENHARIA DE COMPUTACAO"
                if corridas and corridas[-1][2] == canon:
                    corridas[-1][1] = a
                else:
                    corridas.append([a, a, canon, rotulo])
            saida[(ies, curso)] = [(i, f, r) for i, f, _, r in corridas]
        return saida

    @staticmethod
    def _indice(arquivo, chave):
        df = ler(CURADORIA / arquivo)
        return {tuple(l[c] for c in chave): l for l in df.to_dict("records")}


# ------------------------------------------------------- frases por flag

def ev_vagas_repetidas(r, c):
    x = c.vagas.get((r["NU_ANO_CENSO"], r["CO_IES"]))
    if not x:
        return "Este curso declarou o mesmo número de vagas que outros cursos da instituição no ano."
    return (f"Em {r['NU_ANO_CENSO']}, a instituição declarou {n(x['VALOR_VAGAS'])} vagas em "
            f"{x['N_CURSOS_COM_ESSE_VALOR']} dos seus {x['N_CURSOS_COMPUTACAO']} cursos de Computação. "
            f"Este curso declarou {n(r['QT_VG_TOTAL'])} vagas.")


def ev_vagas_ies_ano(r, c):
    x = c.vagas.get((r["NU_ANO_CENSO"], r["CO_IES"]))
    base = ("Por isso as vagas de todos os cursos da instituição nesse ano ficam fora do gráfico de vagas. "
            f"Este curso declarou {n(r['QT_VG_TOTAL'])} vagas.")
    if not x:
        return "Neste ano a instituição repetiu o mesmo número de vagas em vários cursos. " + base
    return (f"Em {r['NU_ANO_CENSO']}, a instituição repetiu {n(x['VALOR_VAGAS'])} vagas em "
            f"{x['N_CURSOS_COM_ESSE_VALOR']} dos seus {x['N_CURSOS_COMPUTACAO']} cursos de Computação. " + base)


def ev_inscrito_igual(r, c):
    x = c.inscrito.get(tuple(r[k] for k in CHAVE), {})
    igual = x.get("INSCRITO_IGUAL_A", "")
    i = n(r["QT_INSCRITO_TOTAL"])
    if igual == "VAGAS ING":
        alvo = f"ao de vagas e ao de ingressantes ({n(r['QT_VG_TOTAL'])})"
    elif igual == "ING":
        alvo = f"ao de ingressantes ({n(r['QT_ING'])})"
    else:
        alvo = f"ao de vagas ({n(r['QT_VG_TOTAL'])})"
    return f"Foram informados {i} inscritos, número idêntico {alvo}."


def ev_inscrito_zero(r, c):
    g, v = num(r, "QT_ING"), num(r, "QT_VG_TOTAL")
    if g > 0:
        extra = f" e {plural(v, 'vaga', 'vagas')}" if v > 0 else ""
        return f"Foram informados 0 inscritos, mas o curso teve {plural(g, 'ingressante', 'ingressantes')}{extra}."
    if v > 0:
        return f"Foram informados 0 inscritos para {n(v)} vagas e 0 ingressantes."
    return "Foram informados 0 inscritos, 0 vagas e 0 ingressantes."


def ev_mat_zero_com_ing(r, c):
    partes = [plural(r["QT_ING"], "ingressante", "ingressantes")]
    if num(r, "QT_SIT_TRANCADA") > 0:
        partes.append(plural(r["QT_SIT_TRANCADA"], "trancado", "trancados"))
    if num(r, "QT_SIT_DESVINCULADO") > 0:
        partes.append(plural(r["QT_SIT_DESVINCULADO"], "desvinculado", "desvinculados"))
    return (f"O curso informou 0 matrículas em {r['NU_ANO_CENSO']}, mas registrou "
            + lista_pt(partes) + " no mesmo ano.")


def _antes_depois(r, c):
    ano = int(r["NU_ANO_CENSO"])
    chave = (r["CO_IES"], r["CO_CURSO"])
    return ano, c.mat.get(chave + (ano - 1,)), c.mat.get(chave + (ano + 1,))


def ev_mat_cai_a_zero(r, c):
    ano, ant, dep = _antes_depois(r, c)
    if dep is not None:
        fim = f"em {ano + 1}, {n(dep)}."
    elif ano >= c.ultimo_ano:
        fim = f"{ano + 1} ainda não está na base."
    else:
        fim = f"o curso não aparece em {ano + 1}."
    return f"Em {ano - 1} o curso tinha {n(ant)} matrículas; em {ano}, informou 0; {fim}"


def ev_zero_lacuna(r, c):
    ano, ant, dep = _antes_depois(r, c)
    return (f"As matrículas foram de {n(ant)} em {ano - 1} para 0 em {ano} e voltaram a {n(dep)} "
            f"em {ano + 1}. É o padrão típico de um ano sem preenchimento.")


def ev_salto_mat(r, c):
    ano, ant, _ = _antes_depois(r, c)
    atual = num(r, "QT_MAT")
    if ant and ant > 0 and atual >= ant:
        razao = f", cerca de {atual / ant:.1f} vezes o valor anterior".replace(".", ",")
    elif ant and ant > 0:
        razao = f", {pct(atual / ant)} do valor anterior"
    else:
        razao = ""
    return f"As matrículas passaram de {n(ant)} em {ano - 1} para {n(atual)} em {ano}{razao}."


def ev_ead_atipica(r, c):
    x = c.ead.get(tuple(r[k] for k in CHAVE))
    if not x:
        return "Distribuição por município fora do padrão."
    partes = []
    if float(x["FRAC_MUNICIPIOS_ZERADOS"]) >= 0.6:
        partes.append(f"Dos {x['MUNICIPIOS']} municípios cadastrados, {x['MUNICIPIOS_SEM_MATRICULA']} "
                      f"({pct(x['FRAC_MUNICIPIOS_ZERADOS'])}) não têm nenhum aluno.")
    if float(x["FRAC_NO_MAIOR_MUNICIPIO"]) >= 0.9:
        partes.append(f"Entre {x['MUNICIPIOS']} municípios cadastrados, o maior concentra "
                      f"{pct(x['FRAC_NO_MAIOR_MUNICIPIO'])} das matrículas ({n(x['MAT_MAIOR_MUNICIPIO'])} "
                      f"de {n(x['MAT_TOTAL_MUNICIPAL'])}).")
    return " ".join(partes)


def ev_mudanca_distribuicao(r, c):
    x = c.mudanca.get(tuple(r[k] for k in CHAVE))
    if not x:
        return "A distribuição por município mudou muito em relação ao ano anterior."
    frase = (f"De {x['ANO_ANTERIOR']} para {r['NU_ANO_CENSO']}, a distribuição das matrículas entre os "
             f"municípios mudou muito: para ficar igual à do ano anterior, "
             f"{pct(x['VARIACAO_DISTRIBUICAO'])} das matrículas teriam de trocar de município.")
    if x["MUNICIPIOS_ANTES"] != x["MUNICIPIOS_DEPOIS"]:
        frase += f" Os municípios com registro foram de {x['MUNICIPIOS_ANTES']} para {x['MUNICIPIOS_DEPOIS']}."
    if float(x["FRAC_MAT_EM_MUNICIPIOS_QUE_SOMEM"]) > 0:
        frase += (f" Os que deixaram de aparecer reuniam {pct(x['FRAC_MAT_EM_MUNICIPIOS_QUE_SOMEM'])} "
                  "das matrículas do ano anterior.")
    return frase + f" As matrículas foram de {n(x['MAT_ANTES'])} para {n(x['MAT_DEPOIS'])}."


def ev_nome_rotulo(r, c):
    return (f"O curso se chama \"{r['NO_CURSO']}\", mas o INEP o classificou como "
            f"\"{r['NO_ROTULO_AREA']}\" (código {r['CO_ROTULO_AREA']}).")


def ev_rotulo_definicao(r, c):
    return f"O INEP marcou este curso com o código {r['CO_ROTULO_AREA']}: \"{r['NO_ROTULO_AREA']}\"."


def _municipios(r, c):
    return c.municipios.get(r["CH_CURSO_ANO"], {"MUN": 0, "ZERO": 0})


def ev_ead_zerados(r, c):
    m = _municipios(r, c)
    return f"{m['ZERO']} dos {m['MUN']} municípios cadastrados neste curso não têm nenhum aluno em {r['NU_ANO_CENSO']}."


def ev_ead_todos_zero(r, c):
    m = _municipios(r, c)
    return f"Os {m['MUN']} municípios cadastrados neste curso aparecem sem nenhum aluno em {r['NU_ANO_CENSO']}."


def ev_tudo_zero(r, c):
    return (f"Em {r['NU_ANO_CENSO']}, vagas, inscritos, ingressantes, matrículas, concluintes e situações "
            "acadêmicas vieram todos zerados.")


def ev_baixa_atividade(r, c):
    s = c.serie.get((r["CO_IES"], r["CO_CURSO"]), {"ANOS": 0, "MAT": 0})
    return (f"Em {s['ANOS']} anos na base, este curso somou {n(s['MAT'])} matrículas, "
            "com metade ou mais dos anos sem nenhuma.")


def ev_interdisciplinar(r, c):
    return (f"Curso interdisciplinar de graduação, classificado como \"{r['NO_ROTULO_AREA']}\", mantido no "
            "recorte por não ser de ingresso por área básica.")


def ev_rotulo_muda(r, c):
    corridas = c.rotulos_cron.get((r["CO_IES"], r["CO_CURSO"]))
    if not corridas:
        return "O INEP classificou este curso de formas diferentes ao longo dos anos."
    itens = [f"{ini} a {fim}: {rotulo}" if ini != fim else f"{ini}: {rotulo}" for ini, fim, rotulo in corridas]
    return "O INEP classificou este curso assim: " + "; ".join(itens) + "."


def ev_varias_ies(r, c):
    usos = c.varias_ies.get(r["CO_CURSO"])
    if not usos:
        return f"O código {r['CO_CURSO']} aparece também em outra instituição."
    itens = [f"{nome} ({ini} a {fim})" for ini, fim, nome in usos[:4]]
    resto = " e outras" if len(usos) > 4 else ""
    return (f"O código {r['CO_CURSO']} foi usado por {len(usos)} instituições diferentes ao longo dos anos: "
            + "; ".join(itens) + resto + ".")


def ev_proxy_ocde(r, c):
    return (f"Em 2017 o INEP usou a classificação OCDE. Este curso entrou na base pelo código "
            f"{r['CO_ROTULO_AREA']}, que nessa classificação é o de Engenharia de Computação.")


def ev_sem_territorio(r, c):
    return (f"O Censo de {r['NU_ANO_CENSO']} não informou os municípios deste curso a distância. "
            f"Só há o total nacional: {n(r['QT_MAT'])} matrículas.")


EVIDENCIAS = {
    "FL_VAGAS_REPETIDAS": ev_vagas_repetidas,
    "FL_VAGAS_IES_ANO_SUSPEITO": ev_vagas_ies_ano,
    "FL_INSCRITO_IGUAL": ev_inscrito_igual,
    "FL_INSCRITO_ZERO": ev_inscrito_zero,
    "FL_MAT_ZERO_COM_ING": ev_mat_zero_com_ing,
    "FL_MAT_CAI_A_ZERO": ev_mat_cai_a_zero,
    "FL_ZERO_LACUNA_50": ev_zero_lacuna,
    "FL_SALTO_MAT": ev_salto_mat,
    "FL_EAD_DISTRIB_ATIPICA": ev_ead_atipica,
    "FL_MUDANCA_DISTRIBUICAO": ev_mudanca_distribuicao,
    "FL_NOME_ROTULO_DIVERGENTE": ev_nome_rotulo,
    "FL_ROTULO_EM_DEFINICAO": ev_rotulo_definicao,
    "FL_EAD_MUNICIPIOS_ZERADOS_AMPLA": ev_ead_zerados,
    "FL_EAD_TODOS_MUN_ZERO": ev_ead_todos_zero,
    "FL_TUDO_ZERO": ev_tudo_zero,
    "FL_BAIXA_ATIVIDADE": ev_baixa_atividade,
    "FL_INTERDISCIPLINAR": ev_interdisciplinar,
    "FL_ROTULO_MUDA_NA_SERIE": ev_rotulo_muda,
    "FL_CO_CURSO_EM_VARIAS_IES": ev_varias_ies,
    "FL_PROXY_OCDE_2017": ev_proxy_ocde,
    "FL_EAD_SEM_TERRITORIO": ev_sem_territorio,
}


def evidencia(flag, r, contexto, dim):
    """Frase do caso. Flag nova sem frase propria cai no texto geral do catalogo."""
    funcao = EVIDENCIAS.get(flag)
    if funcao is None:
        return dim.loc[flag, "O_QUE_E"]
    return funcao(r, contexto)


# ------------------------------------------------------------ montagem

def ocorrencias_curso(fato, dim, contexto):
    linhas = []
    colunas_id = ["NU_ANO_CENSO", "CO_IES", "NO_IES", "CO_CURSO", "NO_CURSO",
                  "DS_TP_MODALIDADE_ENSINO", "CH_CURSO_ANO"]
    flags = [c for c in fato.columns if c.startswith("FL_")]
    for flag in flags:
        if flag in FLAGS_MUNICIPAIS or flag not in dim.index:
            continue
        marcados = fato[fato[flag] == "1"]
        for r in marcados.to_dict("records"):
            linhas.append({**{k: r[k] for k in colunas_id},
                           "CO_MUNICIPIO": "", "NO_MUNICIPIO": "", "SG_UF": "",
                           "FLAG": flag, "EVIDENCIA": evidencia(flag, r, contexto, dim)})
    return pd.DataFrame(linhas)


def ocorrencias_municipio(fato, municipal, contexto):
    """Sequencias de matricula zero, uma linha por ano da sequencia."""
    curso = fato.set_index(CHAVE)[["NO_IES", "NO_CURSO", "DS_TP_MODALIDADE_ENSINO", "CH_CURSO_ANO"]]
    nomes = municipal[["CO_MUNICIPIO", "NO_MUNICIPIO", "SG_UF"]].drop_duplicates("CO_MUNICIPIO").set_index("CO_MUNICIPIO")
    linhas = []
    for e in contexto.zeros.to_dict("records"):
        ini, fim, k = int(e["ANO_INICIAL"]), int(e["ANO_FINAL"]), e["ANOS_ZERO"]
        info = nomes.loc[e["CO_MUNICIPIO"]] if e["CO_MUNICIPIO"] in nomes.index else None
        nome = info["NO_MUNICIPIO"] if info is not None else e["NO_MUNICIPIO"]
        for ano in range(ini, fim + 1):
            chave = (str(ano), e["CO_IES"], e["CO_CURSO"])
            if chave not in curso.index:
                continue
            c = curso.loc[chave]
            linhas.append({
                "NU_ANO_CENSO": str(ano), "CO_IES": e["CO_IES"], "NO_IES": c["NO_IES"],
                "CO_CURSO": e["CO_CURSO"], "NO_CURSO": c["NO_CURSO"],
                "DS_TP_MODALIDADE_ENSINO": c["DS_TP_MODALIDADE_ENSINO"], "CH_CURSO_ANO": c["CH_CURSO_ANO"],
                "CO_MUNICIPIO": e["CO_MUNICIPIO"], "NO_MUNICIPIO": nome,
                "SG_UF": info["SG_UF"] if info is not None else "",
                "FLAG": "FL_MUN_ZERO_3_ANOS",
                "EVIDENCIA": f"{nome} aparece neste curso com 0 matrículas por {k} anos seguidos, de {ini} a {fim}.",
            })
    return pd.DataFrame(linhas)


def ocorrencias_manuais(fato, decisoes, usos):
    """Excecoes manuais tambem precisam aparecer: nada fica de fora sem explicacao."""
    if decisoes.empty:
        return pd.DataFrame()
    nome = usos.set_index("USO")["NOME_AMIGAVEL"].to_dict()
    linhas = []
    for d in decisoes.to_dict("records"):
        mascara = pd.Series(True, index=fato.index)
        for col in ("CO_IES", "CO_CURSO", "NU_ANO_CENSO"):
            if d[col]:
                mascara &= fato[col] == d[col]
        onde = "todos os gráficos" if d["USO"] == "*" else nome[d["USO"]]
        verbo = "Fica de fora de" if d["ACAO"] == "excluir" else "Volta a entrar em"
        for r in fato[mascara].to_dict("records"):
            linhas.append({
                **{k: r[k] for k in ["NU_ANO_CENSO", "CO_IES", "NO_IES", "CO_CURSO", "NO_CURSO",
                                     "DS_TP_MODALIDADE_ENSINO", "CH_CURSO_ANO"]},
                "CO_MUNICIPIO": "", "NO_MUNICIPIO": "", "SG_UF": "", "FLAG": "DECISAO_MANUAL",
                "EVIDENCIA": f"{verbo} {onde} por decisão da equipe do projeto em {d['DATA']}: {d['JUSTIFICATIVA']}",
            })
    return pd.DataFrame(linhas)


def resumo_ies_ano(fato, oc):
    fato = fato.copy()
    grupos = fato.groupby(["NU_ANO_CENSO", "CO_IES"])
    resumo = grupos.agg(NO_IES=("NO_IES", "last"), N_CURSOS=("CO_CURSO", "size")).reset_index()
    for grav, coluna in [("Alerta", "N_CURSOS_ALERTA"), ("Atenção", "N_CURSOS_ATENCAO"),
                         ("Informação", "N_CURSOS_INFORMACAO"), ("Sem observações", "N_CURSOS_SEM_OBSERVACOES")]:
        contagem = fato[fato["GRAVIDADE"] == grav].groupby(["NU_ANO_CENSO", "CO_IES"]).size().rename(coluna)
        resumo = resumo.merge(contagem, on=["NU_ANO_CENSO", "CO_IES"], how="left")
        resumo[coluna] = resumo[coluna].fillna(0).astype(int)
    resumo["PCT_CURSOS_COM_ALERTA"] = (100 * resumo["N_CURSOS_ALERTA"] / resumo["N_CURSOS"]).round(1)
    curso = oc[oc["CO_MUNICIPIO"] == ""]
    top = (curso.groupby(["NU_ANO_CENSO", "CO_IES", "TITULO", "NV"]).size().rename("QT").reset_index()
           .sort_values(["NU_ANO_CENSO", "CO_IES", "NV", "QT"], ascending=[True, True, False, False]))
    frases = {}
    for (ano, ies), g in top.groupby(["NU_ANO_CENSO", "CO_IES"]):
        frases[(ano, ies)] = "; ".join(f"{t} ({q} {'curso' if q == 1 else 'cursos'})" for t, q in zip(g["TITULO"][:3], g["QT"][:3]))
    resumo["PRINCIPAIS_OBSERVACOES"] = [frases.get((a, i), "") for a, i in zip(resumo["NU_ANO_CENSO"], resumo["CO_IES"])]

    def texto(r):
        base = f"Em {r['NU_ANO_CENSO']}, {r['NO_IES']} tem {r['N_CURSOS']} {'curso' if r['N_CURSOS'] == 1 else 'cursos'} de Computação na base."
        if r["N_CURSOS_SEM_OBSERVACOES"] == r["N_CURSOS"]:
            return base + " Nenhum tem observações."
        partes = []
        if r["N_CURSOS_ALERTA"]:
            um = r["N_CURSOS_ALERTA"] == 1
            partes.append(f"{r['N_CURSOS_ALERTA']} {'fica' if um else 'ficam'} de fora de algum gráfico")
        if r["N_CURSOS_ATENCAO"]:
            um = r["N_CURSOS_ATENCAO"] == 1
            partes.append(f"{r['N_CURSOS_ATENCAO']} {'aparece' if um else 'aparecem'} com aviso")
        if r["N_CURSOS_INFORMACAO"]:
            um = r["N_CURSOS_INFORMACAO"] == 1
            partes.append(f"{r['N_CURSOS_INFORMACAO']} {'tem' if um else 'têm'} só nota informativa")
        return base + " " + lista_pt(partes).capitalize() + ". Principais observações: " + r["PRINCIPAIS_OBSERVACOES"] + "."

    resumo["TEXTO_ENTENDA"] = resumo.apply(texto, axis=1)
    return resumo


def main():
    dim = ler(SAIDA / "dim_flag.csv").set_index("FLAG")
    usos = ler(SAIDA / "dim_uso.csv")
    fato = ler(SAIDA / "fato_curso_ano.csv")
    municipal = ler(SAIDA / "fato_municipio_ano.csv")
    decisoes = ler(CONFIG / "decisoes_manuais.csv")
    contexto = Contexto(fato, municipal)

    partes = [ocorrencias_curso(fato, dim, contexto), ocorrencias_municipio(fato, municipal, contexto),
              ocorrencias_manuais(fato, decisoes, usos)]
    oc = pd.concat([p for p in partes if not p.empty], ignore_index=True)

    manual = pd.DataFrame({"TITULO": ["Decisão da equipe do projeto"], "GRAVIDADE": ["Alerta"],
                           "COMO_TRATAMOS": ["Definido caso a caso pela equipe; veja o texto da ocorrência."]},
                          index=["DECISAO_MANUAL"])
    info = pd.concat([dim[["TITULO", "GRAVIDADE", "COMO_TRATAMOS"]], manual])
    oc = oc.join(info, on="FLAG")
    oc["NV"] = oc["GRAVIDADE"].map({g: i for i, g in enumerate(GRAVIDADES)})
    oc = oc.sort_values(["NU_ANO_CENSO", "CO_IES", "CO_CURSO", "NV", "FLAG", "CO_MUNICIPIO"],
                        ascending=[True, True, True, False, True, True]).reset_index(drop=True)
    ordem = ["NU_ANO_CENSO", "CO_IES", "NO_IES", "CO_CURSO", "NO_CURSO", "DS_TP_MODALIDADE_ENSINO",
             "CO_MUNICIPIO", "NO_MUNICIPIO", "SG_UF", "CH_CURSO_ANO", "FLAG", "TITULO", "GRAVIDADE", "NV",
             "EVIDENCIA", "COMO_TRATAMOS"]
    oc = oc[ordem]

    vazias = int((oc["EVIDENCIA"].str.strip() == "").sum())
    if vazias:
        raise ErroConfiguracao(f"{vazias} ocorrencias sem evidencia")
    esperado = int(sum((fato[c] == "1").sum() for c in fato.columns if c.startswith("FL_")
                       and c not in FLAGS_MUNICIPAIS))
    esperado += len(pd.concat([p for p in partes[1:2] if not p.empty], ignore_index=True)) if not partes[1].empty else 0
    esperado += len(partes[2]) if not partes[2].empty else 0
    if len(oc) != esperado:
        raise ErroConfiguracao(f"ocorrencias={len(oc)} contra {esperado} marcas nas tabelas")

    oc.to_csv(SAIDA / "ocorrencias.csv", sep=";", index=False, encoding="utf-8-sig")
    resumo = resumo_ies_ano(fato, oc)
    resumo.to_csv(SAIDA / "resumo_ies_ano.csv", sep=";", index=False, encoding="utf-8-sig")
    print(f"ocorrencias: {len(oc)} linhas")
    print(oc["GRAVIDADE"].value_counts().to_dict())
    print(f"resumo_ies_ano: {len(resumo)} linhas")


if __name__ == "__main__":
    main()
