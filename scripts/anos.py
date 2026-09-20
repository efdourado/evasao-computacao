"""Registro dos anos do Censo processados (config/anos.csv).

E a fonte unica sobre quais anos existem e qual modelo de arquivo cada um usa.
Consolidador, validador e scripts de novo ano leem daqui, entao adicionar um
ano nao exige editar codigo.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ARQUIVO = ROOT / "config" / "anos.csv"
COLUNAS = ["ANO", "MODELO", "CLASSIFICACAO", "SITUACAO", "OBSERVACAO"]

MODELO_ATUAL = "cadastro_cursos"
# 2017 a 2019 usam leitores proprios, escritos para o layout daqueles arquivos.
# Qualquer outro ano tem de usar o modelo atual do cadastro de cursos.
ANOS_MODELO_ANTIGO = {
    "2017": "antigo_ocde",
    "2018": "antigo_cine_brasil",
    "2019": "antigo_cine_brasil",
}


class ErroRegistroAnos(Exception):
    pass


def validar_anos(df):
    if list(df.columns) != COLUNAS:
        raise ErroRegistroAnos(f"anos.csv deve ter as colunas {COLUNAS}")
    if df["ANO"].duplicated().any():
        raise ErroRegistroAnos("anos.csv tem ano repetido")
    for _, linha in df.iterrows():
        ano, modelo = linha["ANO"], linha["MODELO"]
        if not (ano.isdigit() and len(ano) == 4):
            raise ErroRegistroAnos(f"ano invalido em anos.csv: {ano!r}")
        esperado = ANOS_MODELO_ANTIGO.get(ano, MODELO_ATUAL)
        if modelo != esperado:
            raise ErroRegistroAnos(
                f"{ano}: modelo {modelo!r}, esperado {esperado!r}. Anos novos usam {MODELO_ATUAL!r}."
            )
    return df


def carregar_anos(caminho=ARQUIVO):
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    return validar_anos(df).sort_values("ANO").reset_index(drop=True)


def anos_todos(caminho=ARQUIVO):
    return carregar_anos(caminho)["ANO"].tolist()


def anos_cadastro_cursos(caminho=ARQUIVO):
    df = carregar_anos(caminho)
    return df.loc[df["MODELO"] == MODELO_ATUAL, "ANO"].tolist()


def ano_de_referencia(caminho=ARQUIVO):
    """Ultimo ano no modelo atual do cadastro, usado como base de comparacao."""
    return anos_cadastro_cursos(caminho)[-1]


def registrar_ano(ano, caminho=ARQUIVO, observacao=""):
    """Acrescenta o ano no modelo atual. Devolve False se ja estava registrado."""
    ano = str(ano)
    df = carregar_anos(caminho)
    if ano in set(df["ANO"]):
        return False
    nova = pd.DataFrame([[ano, MODELO_ATUAL, "CINE", "cadastro_cursos", observacao]], columns=COLUNAS)
    validar_anos(nova)
    pd.concat([df, nova]).sort_values("ANO").to_csv(
        caminho, sep=";", index=False, encoding="utf-8-sig", lineterminator="\n"
    )
    return True
