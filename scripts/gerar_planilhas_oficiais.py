from pathlib import Path
import pandas as pd
import numpy as np

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
    "NU_ANO_CENSO", "CO_IES", "NO_IES", "SG_IES", "CO_CURSO", "NO_CURSO", "NO_CURSO_NORMALIZADO",
    "DS_MODELO_DADOS", "DS_CRITERIO_ESCOPO", "DS_CLASSIFICACAO_AREA", "DS_NIVEL_COMPARABILIDADE",
    "DS_OBSERVACAO_COMPARABILIDADE", "DS_ORIGEM_SITUACAO_ACADEMICA", "CO_AREA_GERAL", "NO_AREA_GERAL",
    "CO_AREA_ESPECIFICA", "NO_AREA_ESPECIFICA", "CO_AREA_DETALHADA", "NO_AREA_DETALHADA",
    "CO_ROTULO_AREA", "NO_ROTULO_AREA", "TP_GRAU_ACADEMICO", "DS_TP_GRAU_ACADEMICO",
    "TP_MODALIDADE_ENSINO", "DS_TP_MODALIDADE_ENSINO", "TP_CATEGORIA_ADMINISTRATIVA",
    "DS_TP_CATEGORIA_ADMINISTRATIVA", "TP_REDE", "DS_TP_REDE", "TP_ORGANIZACAO_ACADEMICA",
    "DS_TP_ORGANIZACAO_ACADEMICA", "QT_LINHAS_EXPANDIDAS", "IN_TEM_MULTIPLAS_LINHAS",
    "QT_UFS_DISTINTAS", "SG_UF_LISTA", "QT_MUNICIPIOS_DISTINTOS", "TP_DIMENSAO_LISTA",
    "DS_TP_DIMENSAO_LISTA", "IN_USAR_MAPA_MUNICIPAL", "QT_VG_TOTAL", "QT_INSCRITO_TOTAL",
    "QT_ING", "QT_MAT", "QT_CONC", "QT_SIT_TRANCADA", "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO", "QT_SIT_FALECIDO",
]

COLUNAS_EXPANDIDA = [
    "NU_ANO_CENSO", "CO_IES", "NO_IES", "CO_CURSO", "NO_CURSO", "TP_MODALIDADE_ENSINO",
    "DS_TP_MODALIDADE_ENSINO", "TP_DIMENSAO", "DS_TP_DIMENSAO", "DS_NIVEL_GEOGRAFICO",
    "IN_USAR_MAPA_MUNICIPAL", "CO_UF", "SG_UF", "CO_MUNICIPIO", "NO_MUNICIPIO", "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL", "QT_ING", "QT_MAT", "QT_CONC", "QT_SIT_TRANCADA", "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO", "QT_SIT_FALECIDO",
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
        if coluna in df.columns:
            df[coluna] = df[coluna].astype(str).str.replace('"', "", regex=False).str.strip()
    return df

def selecionar(df, colunas):
    for col in colunas:
        if col not in df.columns:
            df[col] = pd.NA
    return df[colunas].copy()

def integrar_situacao(cursos):
    cursos = normalizar_chaves(cursos)
    
    # Inicializa de forma segura como Não Disponível
    cursos["DS_ORIGEM_SITUACAO_ACADEMICA"] = "Não disponível (Sem dados)"

    # Marca registros onde o Módulo Curso já possui indicadores numéricos nativos válidos
    campos_originais_validos = (
        cursos["QT_SIT_DESVINCULADO"].notna() & 
        cursos["QT_SIT_DESVINCULADO"].ne("") & 
        cursos["QT_SIT_DESVINCULADO"].ne(0)
    )
    cursos.loc[campos_originais_validos, "DS_ORIGEM_SITUACAO_ACADEMICA"] = "cadastro de cursos"

    if not BASE_SITUACAO.exists():
        print("[Aviso] Base de situacao academica de alunos ausente. Usando apenas dados cadastrais de curso.")
        return cursos

    alunos = pd.read_csv(BASE_SITUACAO, sep=";", encoding="utf-8-sig", dtype=str)
    alunos = normalizar_chaves(alunos)
    
    for coluna in COLUNAS_ALUNO:
        if coluna in alunos.columns:
            alunos[coluna] = pd.to_numeric(alunos[coluna], errors="coerce").fillna(0)

    cursos = cursos.merge(alunos, on=CHAVE, how="left")
    preenchida_por_aluno = pd.Series(False, index=cursos.index)

    for coluna_curso, coluna_aluno in MAPA_PREENCHIMENTO.items():
        cursos[coluna_curso] = pd.to_numeric(cursos[coluna_curso], errors="coerce")
        if coluna_aluno in cursos.columns:
            # Substitui se o cadastro original for nulo e houver dado vindo do bloco de alunos
            preencher = cursos[coluna_curso].isna() & cursos[coluna_aluno].notna()
            cursos.loc[preencher, coluna_curso] = cursos.loc[preencher, coluna_aluno]
            preenchida_por_aluno |= preencher

    cursos.loc[preenchida_por_aluno, "DS_ORIGEM_SITUACAO_ACADEMICA"] = "arquivo de aluno"
    return cursos

def gerar_dicionario():
    arquivos = {}
    for coluna in COLUNAS_PRINCIPAL:
        arquivos.setdefault(coluna, []).append(SAIDA_PRINCIPAL.name)
    for coluna in COLUNAS_EXPANDIDA:
        arquivos.setdefault(coluna, []).append(SAIDA_EXPANDIDA.name)

    return pd.DataFrame([
        {
            "COLUNA": coluna,
            "DESCRICAO": DESCRICOES.get(coluna, "Sem descrição cadastrada."),
            "ARQUIVOS": " | ".join(nomes),
        }
        for coluna, nomes in arquivos.items()
    ])

def valor_para_texto(v):
    """Converte um valor para a mesma representação textual que ele teria
    se tivesse sido lido de um CSV já existente (evita '150' num bloco e
    '150.0' no outro, dentro da mesma coluna)."""
    if pd.isna(v):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)
 
 
def atualizar_planilha(nova_df, caminho_saida):
    if not caminho_saida.exists():
        nova_df.to_csv(caminho_saida, sep=";", index=False, encoding="utf-8-sig")
        return
 
    nova_df = nova_df.copy()
    nova_df["NU_ANO_CENSO"] = nova_df["NU_ANO_CENSO"].astype(str)
    anos_novos = nova_df["NU_ANO_CENSO"].unique()
 
    if len(anos_novos) > 1:
        raise ValueError("A planilha de entrada contém múltiplos anos.")
    ano_a_remover = anos_novos[0]
 
    existente_df = pd.read_csv(caminho_saida, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
    existente_df["NU_ANO_CENSO"] = existente_df["NU_ANO_CENSO"].astype(str)
 
    # Remove de forma limpa o ano sob processamento da planilha oficial acumulada
    existente_df = existente_df[existente_df["NU_ANO_CENSO"] != ano_a_remover]
 
    # Esquema final = colunas antigas (na mesma ordem) + qualquer coluna nova
    # que só exista no bloco atual. Antes isso era um reindex direto pro
    # schema antigo, que descartava silenciosamente colunas novas.
    colunas_antigas = existente_df.columns.tolist()
    colunas_novas_extra = [c for c in nova_df.columns if c not in colunas_antigas]
    if colunas_novas_extra:
        print(
            f"[aviso] a planilha nova traz {len(colunas_novas_extra)} coluna(s) que não existiam "
            f"no arquivo acumulado ({', '.join(colunas_novas_extra)}). Foram adicionadas ao final "
            "do esquema (ficam vazias nas linhas dos anos antigos)."
        )
    colunas_finais = colunas_antigas + colunas_novas_extra
 
    # Normaliza os dois lados para texto antes de concatenar, pra não
    # misturar "150" (lido como string do CSV antigo) com 150.0 (numérico
    # da execução atual) na mesma coluna.
    nova_df_alinhada = nova_df.reindex(columns=colunas_finais)
    for coluna in nova_df_alinhada.columns:
        nova_df_alinhada[coluna] = nova_df_alinhada[coluna].map(valor_para_texto)
 
    existente_df_alinhada = existente_df.reindex(columns=colunas_finais, fill_value="")
 
    combinado_df = pd.concat([existente_df_alinhada, nova_df_alinhada], ignore_index=True)
    combinado_df.to_csv(caminho_saida, sep=";", index=False, encoding="utf-8-sig")

def main():
    if not BASE_CURSOS.exists() or not BASE_EXPANDIDA.exists():
        raise FileNotFoundError("Bases temporarias intermediárias ausentes. Execute a pipeline completa.")

    OFICIAL.mkdir(parents=True, exist_ok=True)
    
    cursos = pd.read_csv(BASE_CURSOS, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
    expandida = pd.read_csv(BASE_EXPANDIDA, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)

    anos_a_processar = sorted(cursos["NU_ANO_CENSO"].unique())
    print(f"Anos a serem processados e atualizados nas planilhas oficiais: {anos_a_processar}")

    for ano in anos_a_processar:
        print(f"\nProcessando ano: {ano}")
        cursos_ano = cursos[cursos["NU_ANO_CENSO"] == ano]
        expandida_ano = expandida[expandida["NU_ANO_CENSO"] == ano]

        principal = selecionar(integrar_situacao(cursos_ano), COLUNAS_PRINCIPAL)
        expandida_ano = selecionar(expandida_ano, COLUNAS_EXPANDIDA)

        atualizar_planilha(principal, SAIDA_PRINCIPAL)
        atualizar_planilha(expandida_ano, SAIDA_EXPANDIDA)

    gerar_dicionario().to_csv(SAIDA_DICIONARIO, sep=";", index=False, encoding="utf-8-sig")

    print("\nPlanilhas oficiais geradas com sucesso:")
    print(f"Planilha Principal (Curso Único): {SAIDA_PRINCIPAL}")
    print(f"Planilha Expandida (Polos Geográficos): {SAIDA_EXPANDIDA}")
    print(f"Dicionário de Variáveis Técnico: {SAIDA_DICIONARIO}")

if __name__ == "__main__":
    main()