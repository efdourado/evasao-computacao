from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "data" / "processed" / ".pipeline"
BASE_EXPANDIDA = PIPELINE / "cursos_expandida.csv"
BASE_COMPARAVEL = PIPELINE / "cursos_comparavel.csv"

CHAVE_CURSO = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO"]

# Métricas originais do módulo de Curso (NÃO devem ser somadas no agrupamento geográfico)
METRICAS_CADASTRO = [
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC"
]

# Métricas de fluxo derivadas do Módulo Aluno (essas acumulam por polo/vínculo)
METRICAS_FLUXO_ALUNO = [
    "QT_SIT_TRANCADA",
    "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO",
    "QT_SIT_FALECIDO"
]

NUMERICAS = METRICAS_CADASTRO + METRICAS_FLUXO_ALUNO

COLUNAS_IDENTIFICACAO = [
    "DS_MODELO_DADOS",
    "DS_CLASSIFICACAO_AREA",
    "DS_NIVEL_COMPARABILIDADE",
    "DS_OBSERVACAO_COMPARABILIDADE",
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

def valores_unicos(serie):
    valores = {
        str(valor).strip()
        for valor in serie.dropna()
        if str(valor).strip() and str(valor).strip().lower() != "nan"
    }
    return "|".join(sorted(valores)) if valores else pd.NA

def contar_unicos(serie):
    return len({
        str(valor).strip()
        for valor in serie.dropna()
        if str(valor).strip() and str(valor).strip().lower() != "nan"
    })

def algum_verdadeiro(serie):
    if serie.dropna().empty:
        return False
    # Avaliação híbrida: aceita booleanos nativos, numéricos e strings textuais
    return serie.isin([True, 1, 1.0, "True", "true", "1", "Sim", "sim", "yes", "YES"]).any()

def carregar_base_expandida():
    if not BASE_EXPANDIDA.exists():
        raise FileNotFoundError(
            f"Cursos consolidados nao encontrados em {BASE_EXPANDIDA}. Execute consolidar_cursos.py."
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
            
    # Criação resiliente do ID do Município unificado
    codigo = base.get("CO_MUNICIPIO", pd.Series(pd.NA, index=base.index)).fillna("").astype(str).str.strip()
    nome = base.get("NO_MUNICIPIO", pd.Series(pd.NA, index=base.index)).fillna("").astype(str).str.strip()
    
    base["ID_MUNICIPIO"] = codigo.mask(
        codigo.eq("") | codigo.str.lower().eq("nan"),
        nome
    )
    return base

def gerar_base_comparavel(base):
    # Dicionário dinâmico de agregações cadastrais
    agregacoes = {
        coluna: (coluna, "first")
        for coluna in COLUNAS_IDENTIFICACAO
        if coluna in base.columns
    }
    
    # Adiciona metadados de controle geográfico da expansão
    agregacoes.update({
        "QT_LINHAS_EXPANDIDAS": ("CO_CURSO", "size"),
        "QT_UFS_DISTINTAS": ("SG_UF", contar_unicos),
        "SG_UF_LISTA": ("SG_UF", valores_unicos),
        "QT_MUNICIPIOS_DISTINTOS": ("ID_MUNICIPIO", contar_unicos),
        "TP_DIMENSAO_LISTA": ("TP_DIMENSAO", valores_unicos),
        "DS_TP_DIMENSAO_LISTA": ("DS_TP_DIMENSAO", valores_unicos),
        "IN_USAR_MAPA_MUNICIPAL": ("IN_USAR_MAPA_MUNICIPAL", algum_verdadeiro),
    })
    
    # Agrega metadados descritivos
    comparavel = base.groupby(CHAVE_CURSO, dropna=False).agg(**agregacoes).reset_index()
    
    # Agrega Métricas Cadastrais usando 'max' para evitar inflar duplicados geográficos
    metricas_cad_ativas = [c for c in METRICAS_CADASTRO if c in base.columns]
    if metricas_cad_ativas:
        somas_cad = base.groupby(CHAVE_CURSO, dropna=False)[metricas_cad_ativas].max().reset_index()
        comparavel = comparavel.merge(somas_cad, on=CHAVE_CURSO, how="left")
        
    # Agrega Métricas de Fluxo (Alunos) usando 'sum' para acumular ocorrências reais
    metricas_fluxo_ativas = [c for c in METRICAS_FLUXO_ALUNO if c in base.columns]
    if metricas_fluxo_ativas:
        somas_fluxo = base.groupby(CHAVE_CURSO, dropna=False)[metricas_fluxo_ativas].sum(min_count=1).reset_index()
        comparavel = comparavel.merge(somas_fluxo, on=CHAVE_CURSO, how="left")
        
    comparavel["IN_TEM_MULTIPLAS_LINHAS"] = comparavel["QT_LINHAS_EXPANDIDAS"] > 1
    
    # Ordenação lógica estrita das colunas de saída
    colunas_finais_existentes = [c for c in METRICAS_CADASTRO + METRICAS_FLUXO_ALUNO if c in comparavel.columns]
    ordem = (
        CHAVE_CURSO
        + [coluna for coluna in COLUNAS_IDENTIFICACAO if coluna in comparavel.columns]
        + [
            "QT_LINHAS_EXPANDIDAS",
            "IN_TEM_MULTIPLAS_LINHAS",
            "QT_UFS_DISTINTAS",
            "SG_UF_LISTA",
            "QT_MUNICIPIOS_DISTINTOS",
            "TP_DIMENSAO_LISTA",
            "DS_TP_DIMENSAO_LISTA",
            "IN_USAR_MAPA_MUNICIPAL",
        ]
        + colunas_finais_existentes
    )
    
    return comparavel[ordem].sort_values(CHAVE_CURSO)

def main():
    PIPELINE.mkdir(parents=True, exist_ok=True)
    
    print("Carregando e processando base unificada...")
    base_expandida = carregar_base_expandida()
    
    comparavel = gerar_base_comparavel(base_expandida)
    
    comparavel.to_csv(
        BASE_COMPARAVEL,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    
    print("\nBase comparavel (Curso Único por Ano) gerada com sucesso:")
    print(f"Destino: {BASE_COMPARAVEL}")
    print(f"Dimensões finais da tabela: {comparavel.shape[0]} cursos distintos x {comparavel.shape[1]} colunas.")

if __name__ == "__main__":
    main()