from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "data" / "processed" / ".pipeline"
OFICIAL = ROOT / "data" / "processed" / "oficial"

BASE_CURSOS = PIPELINE / "cursos_comparavel.csv"
BASE_EXPANDIDA = PIPELINE / "cursos_expandida.csv"
BASE_SITUACAO = PIPELINE / "situacao_academica.csv"

SAIDA_PRINCIPAL = OFICIAL / "planilha_oficial_computacao.csv"
SAIDA_EXPANDIDA = OFICIAL / "planilha_oficial_computacao_expandida.csv"
SAIDA_DICIONARIO = OFICIAL / "dicionario_planilha_oficial.csv"

CHAVE = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]

MAPA_PREENCHIMENTO = {
    "QT_SIT_TRANCADA": "QT_ALUNO_TRANCADA",
    "QT_SIT_DESVINCULADO": "QT_ALUNO_DESVINCULADO",
    "QT_SIT_TRANSFERIDO": "QT_ALUNO_TRANSFERIDO",
    "QT_SIT_FALECIDO": "QT_ALUNO_FALECIDO",
}

COLUNAS_ALUNO = [
    "QT_ALUNO_CURSANDO",
    "QT_ALUNO_TRANCADA",
    "QT_ALUNO_DESVINCULADO",
    "QT_ALUNO_TRANSFERIDO",
    "QT_ALUNO_FORMADO",
    "QT_ALUNO_FALECIDO",
    "QT_ALUNO_TOTAL_VINCULOS",
]

COLUNAS_PRINCIPAL = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "SG_IES",
    "CO_CURSO",
    "NO_CURSO",
    "NO_CURSO_NORMALIZADO",
    "DS_MODELO_DADOS",
    "DS_CRITERIO_ESCOPO",
    "DS_CLASSIFICACAO_AREA",
    "DS_NIVEL_COMPARABILIDADE",
    "DS_OBSERVACAO_COMPARABILIDADE",
    "DS_ORIGEM_SITUACAO_ACADEMICA",
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
]

COLUNAS_EXPANDIDA = [
    "NU_ANO_CENSO",
    "CO_IES",
    "NO_IES",
    "CO_CURSO",
    "NO_CURSO",
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

DESCRICOES = {
    "NU_ANO_CENSO": "Ano do Censo da Educação Superior.",
    "CO_IES": "Código da instituição no INEP.",
    "NO_IES": "Nome da instituição.",
    "SG_IES": "Sigla da instituição, quando disponível.",
    "CO_CURSO": "Código do curso no INEP.",
    "NO_CURSO": "Nome do curso.",
    "NO_CURSO_NORMALIZADO": "Nome do curso normalizado para comparação textual.",
    "DS_MODELO_DADOS": "Estrutura de arquivo utilizada no ano.",
    "DS_CRITERIO_ESCOPO": "Regra que incluiu o curso no recorte oficial.",
    "DS_CLASSIFICACAO_AREA": "Classificação usada no ano: CINE, CINE Brasil ou OCDE.",
    "DS_NIVEL_COMPARABILIDADE": "Nível metodológico de comparabilidade do ano.",
    "DS_OBSERVACAO_COMPARABILIDADE": "Limitação ou adaptação aplicada ao ano.",
    "DS_ORIGEM_SITUACAO_ACADEMICA": "Fonte dos indicadores de situação acadêmica.",
    "CO_AREA_GERAL": "Código da área geral na classificação disponível.",
    "NO_AREA_GERAL": "Nome da área geral na classificação disponível.",
    "CO_AREA_ESPECIFICA": "Código da área específica.",
    "NO_AREA_ESPECIFICA": "Nome da área específica.",
    "CO_AREA_DETALHADA": "Código da área detalhada.",
    "NO_AREA_DETALHADA": "Nome da área detalhada.",
    "CO_ROTULO_AREA": "Código do rótulo CINE/OCDE.",
    "NO_ROTULO_AREA": "Nome do rótulo CINE/OCDE.",
    "TP_GRAU_ACADEMICO": "Código do grau acadêmico.",
    "DS_TP_GRAU_ACADEMICO": "Descrição do grau acadêmico.",
    "TP_MODALIDADE_ENSINO": "Código da modalidade de ensino.",
    "DS_TP_MODALIDADE_ENSINO": "Modalidade presencial ou EaD.",
    "TP_CATEGORIA_ADMINISTRATIVA": "Código da categoria administrativa da IES.",
    "DS_TP_CATEGORIA_ADMINISTRATIVA": "Descrição da categoria administrativa.",
    "TP_REDE": "Código da rede pública ou privada.",
    "DS_TP_REDE": "Descrição da rede.",
    "TP_ORGANIZACAO_ACADEMICA": "Código da organização acadêmica.",
    "DS_TP_ORGANIZACAO_ACADEMICA": "Descrição da organização acadêmica.",
    "QT_LINHAS_EXPANDIDAS": "Quantidade de linhas territoriais do curso.",
    "IN_TEM_MULTIPLAS_LINHAS": "Indica se o curso possui mais de uma linha territorial.",
    "QT_UFS_DISTINTAS": "Quantidade de UFs associadas ao curso.",
    "SG_UF_LISTA": "Lista de UFs associadas ao curso.",
    "QT_MUNICIPIOS_DISTINTOS": "Quantidade de municípios associados ao curso.",
    "TP_DIMENSAO_LISTA": "Dimensões territoriais presentes no curso.",
    "DS_TP_DIMENSAO_LISTA": "Descrição das dimensões territoriais presentes.",
    "IN_USAR_MAPA_MUNICIPAL": "Indica se a linha pode ser usada em mapa municipal.",
    "TP_DIMENSAO": "Código da dimensão territorial do registro.",
    "DS_TP_DIMENSAO": "Descrição da dimensão territorial.",
    "DS_NIVEL_GEOGRAFICO": "Nível geográfico disponível no registro.",
    "CO_UF": "Código da unidade federativa.",
    "SG_UF": "Sigla da unidade federativa.",
    "CO_MUNICIPIO": "Código do município.",
    "NO_MUNICIPIO": "Nome do município.",
    "QT_VG_TOTAL": "Quantidade de vagas.",
    "QT_INSCRITO_TOTAL": "Quantidade de inscritos, quando disponível.",
    "QT_ING": "Quantidade de ingressantes.",
    "QT_MAT": "Quantidade de matrículas.",
    "QT_CONC": "Quantidade de concluintes.",
    "QT_SIT_TRANCADA": "Vínculos com situação trancada.",
    "QT_SIT_DESVINCULADO": "Vínculos com situação desvinculada.",
    "QT_SIT_TRANSFERIDO": "Vínculos com situação transferida.",
    "QT_SIT_FALECIDO": "Vínculos com situação falecido.",
}


def normalizar_chaves(df):
    for coluna in CHAVE:
        df[coluna] = (
            df[coluna].astype(str).str.replace('"', "", regex=False).str.strip()
        )
    return df


def selecionar(df, colunas):
    ausentes = [coluna for coluna in colunas if coluna not in df.columns]
    if ausentes:
        raise KeyError(f"Colunas ausentes: {', '.join(ausentes)}")
    return df[colunas].copy()


def integrar_situacao(cursos):
    cursos = normalizar_chaves(cursos)
    cursos["DS_ORIGEM_SITUACAO_ACADEMICA"] = "cadastro de cursos"

    if not BASE_SITUACAO.exists():
        return cursos

    alunos = pd.read_csv(
        BASE_SITUACAO,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
    )
    alunos = normalizar_chaves(alunos)
    for coluna in COLUNAS_ALUNO:
        alunos[coluna] = pd.to_numeric(alunos[coluna], errors="coerce")

    cursos = cursos.merge(alunos, on=CHAVE, how="left")
    preenchida_por_aluno = pd.Series(False, index=cursos.index)

    for coluna_curso, coluna_aluno in MAPA_PREENCHIMENTO.items():
        cursos[coluna_curso] = pd.to_numeric(
            cursos[coluna_curso],
            errors="coerce",
        )
        preencher = cursos[coluna_curso].isna() & cursos[coluna_aluno].notna()
        cursos.loc[preencher, coluna_curso] = cursos.loc[preencher, coluna_aluno]
        preenchida_por_aluno |= preencher

    cursos.loc[
        preenchida_por_aluno,
        "DS_ORIGEM_SITUACAO_ACADEMICA",
    ] = "arquivo de aluno"
    return cursos


def gerar_dicionario():
    arquivos = {}
    for coluna in COLUNAS_PRINCIPAL:
        arquivos.setdefault(coluna, []).append(SAIDA_PRINCIPAL.name)
    for coluna in COLUNAS_EXPANDIDA:
        arquivos.setdefault(coluna, []).append(SAIDA_EXPANDIDA.name)

    return pd.DataFrame(
        [
            {
                "COLUNA": coluna,
                "DESCRICAO": DESCRICOES[coluna],
                "ARQUIVOS": " | ".join(nomes),
            }
            for coluna, nomes in arquivos.items()
        ]
    )


def main():
    if not BASE_CURSOS.exists() or not BASE_EXPANDIDA.exists():
        raise FileNotFoundError(
            "Bases temporarias ausentes. Execute a pipeline completa."
        )

    OFICIAL.mkdir(parents=True, exist_ok=True)
    cursos = pd.read_csv(
        BASE_CURSOS,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        low_memory=False,
    )
    expandida = pd.read_csv(
        BASE_EXPANDIDA,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        low_memory=False,
    )

    principal = selecionar(integrar_situacao(cursos), COLUNAS_PRINCIPAL)
    expandida = selecionar(expandida, COLUNAS_EXPANDIDA)

    principal.to_csv(
        SAIDA_PRINCIPAL,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    expandida.to_csv(
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
    print(f"{SAIDA_PRINCIPAL} {principal.shape}")
    print(f"{SAIDA_EXPANDIDA} {expandida.shape}")
    print(SAIDA_DICIONARIO)


if __name__ == "__main__":
    main()
