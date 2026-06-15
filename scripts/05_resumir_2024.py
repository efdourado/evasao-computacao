from pathlib import Path
from numbers import Number

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = PROCESSED / "resumos_2024"
DOCS = ROOT / "docs"

ENTRADA = PROCESSED / "computacao_2024_tratada.csv"
RELATORIO = DOCS / "02_analise_2024.md"

COLUNAS_NUMERICAS = [
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


def carregar_base():
    df = pd.read_csv(ENTRADA, sep=";", encoding="utf-8-sig", dtype=str)

    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    for col in ["IN_TEM_LOCALIZACAO_CURSO", "IN_USAR_MAPA_MUNICIPAL"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().eq("TRUE")

    return df


def resumir(df, colunas_grupo):
    resumo = (
        df.groupby(colunas_grupo, dropna=False)
        .agg(
            QT_REGISTROS=("CO_CURSO", "size"),
            QT_CURSOS_DISTINTOS=("CO_CURSO", "nunique"),
            QT_IES_DISTINTAS=("CO_IES", "nunique"),
            **{col: (col, "sum") for col in COLUNAS_NUMERICAS if col in df.columns},
        )
        .reset_index()
    )

    resumo["TX_DESVINCULADO_SOBRE_MAT"] = (
        resumo["QT_SIT_DESVINCULADO"] / resumo["QT_MAT"]
    ).where(resumo["QT_MAT"] > 0)

    resumo["TX_TRANCADA_SOBRE_MAT"] = (
        resumo["QT_SIT_TRANCADA"] / resumo["QT_MAT"]
    ).where(resumo["QT_MAT"] > 0)

    return resumo.sort_values(
        ["QT_MAT", "QT_CURSOS_DISTINTOS", "QT_REGISTROS"],
        ascending=False,
    )


def salvar(resumo, nome):
    caminho = OUT / nome
    resumo.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")
    return caminho


def formatar_inteiro(valor):
    return f"{int(valor):,}".replace(",", ".")


def formatar_percentual(valor):
    if pd.isna(valor):
        return "n/a"
    return f"{valor * 100:.2f}%".replace(".", ",")


def formatar_celula(valor):
    if pd.isna(valor):
        return ""
    if isinstance(valor, Number):
        if float(valor).is_integer():
            return formatar_inteiro(valor)
        return f"{valor:.4f}".replace(".", ",")
    return str(valor).replace("|", "/")


def tabela_markdown(df, colunas, limite=10):
    linhas = df.head(limite)[colunas].copy()
    cabecalho = "| " + " | ".join(colunas) + " |"
    separador = "| " + " | ".join(["---"] * len(colunas)) + " |"
    corpo = [
        "| " + " | ".join(formatar_celula(linha[col]) for col in colunas) + " |"
        for _, linha in linhas.iterrows()
    ]
    return "\n".join([cabecalho, separador, *corpo])


def gerar_relatorio(df, caminhos):
    totais = pd.DataFrame([{}])

    totais.loc[0, "QT_REGISTROS"] = len(df)
    totais.loc[0, "QT_CURSOS_DISTINTOS"] = df["CO_CURSO"].nunique()
    totais.loc[0, "QT_IES_DISTINTAS"] = df["CO_IES"].nunique()
    totais.loc[0, "QT_REGISTROS_MAPA_MUNICIPAL"] = df["IN_USAR_MAPA_MUNICIPAL"].sum()
    totais.loc[0, "QT_REGISTROS_SEM_MAPA_MUNICIPAL"] = (
        len(df) - df["IN_USAR_MAPA_MUNICIPAL"].sum()
    )

    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            totais.loc[0, col] = df[col].sum()

    total_matriculas = totais.loc[0, "QT_MAT"]
    total_desvinculados = totais.loc[0, "QT_SIT_DESVINCULADO"]
    taxa_desvinculado = total_desvinculados / total_matriculas

    por_dimensao = resumir(df, ["TP_DIMENSAO", "DS_TP_DIMENSAO"])
    por_modalidade = resumir(df, ["TP_MODALIDADE_ENSINO", "DS_TP_MODALIDADE_ENSINO"])
    por_cine = resumir(df, ["NO_CINE_ROTULO"])
    por_uf = resumir(df[df["IN_USAR_MAPA_MUNICIPAL"]], ["SG_UF"])

    conteudo = f"""# Síntese da análise de 2024

## Base final analisada

A base final analisada foi:

```text
data/processed/computacao_2024_tratada.csv
```

Ela foi gerada a partir dos Microdados do Censo da Educação Superior 2024 do INEP, cruzando a base de cursos com a base de IES por `NU_ANO_CENSO` e `CO_IES`.

## Recorte usado

O recorte oficial de Computação/TIC inclui cursos na área geral 6 da CINE, isto é, Computação e Tecnologias da Informação e Comunicação (TIC).

Cursos relacionados que estejam em outras áreas gerais, como Engenharia de Computação, Computação formação de professor, Matemática Computacional, Física Computacional e Informática em Saúde, não entram automaticamente nessa base. Eles ficam para revisão na auditoria do recorte.

## Números principais

```text
Registros analisados: {formatar_inteiro(totais.loc[0, "QT_REGISTROS"])}
Cursos distintos: {formatar_inteiro(totais.loc[0, "QT_CURSOS_DISTINTOS"])}
IES distintas: {formatar_inteiro(totais.loc[0, "QT_IES_DISTINTAS"])}
Registros com uso em mapa municipal: {formatar_inteiro(totais.loc[0, "QT_REGISTROS_MAPA_MUNICIPAL"])}
Registros sem uso em mapa municipal: {formatar_inteiro(totais.loc[0, "QT_REGISTROS_SEM_MAPA_MUNICIPAL"])}
```

Indicadores agregados:

```text
Vagas: {formatar_inteiro(totais.loc[0, "QT_VG_TOTAL"])}
Inscritos: {formatar_inteiro(totais.loc[0, "QT_INSCRITO_TOTAL"])}
Ingressantes: {formatar_inteiro(totais.loc[0, "QT_ING"])}
Matriculados: {formatar_inteiro(totais.loc[0, "QT_MAT"])}
Concluintes: {formatar_inteiro(totais.loc[0, "QT_CONC"])}
Matrículas trancadas: {formatar_inteiro(totais.loc[0, "QT_SIT_TRANCADA"])}
Desvinculados: {formatar_inteiro(totais.loc[0, "QT_SIT_DESVINCULADO"])}
Transferidos: {formatar_inteiro(totais.loc[0, "QT_SIT_TRANSFERIDO"])}
Falecidos: {formatar_inteiro(totais.loc[0, "QT_SIT_FALECIDO"])}
Desvinculados/matriculados: {formatar_percentual(taxa_desvinculado)}
```

O indicador `Desvinculados/matriculados` deve ser tratado como medida exploratória, não como taxa final de evasão, porque a metodologia definitiva ainda depende da modelagem histórica e da validação conceitual do projeto.

## Distribuição por dimensão territorial

{tabela_markdown(por_dimensao, ["TP_DIMENSAO", "DS_TP_DIMENSAO", "QT_REGISTROS", "QT_CURSOS_DISTINTOS", "QT_MAT", "QT_SIT_DESVINCULADO"])}

## Distribuição por modalidade

{tabela_markdown(por_modalidade, ["DS_TP_MODALIDADE_ENSINO", "QT_REGISTROS", "QT_CURSOS_DISTINTOS", "QT_MAT", "QT_SIT_DESVINCULADO"])}

## Principais rótulos CINE por matrículas

{tabela_markdown(por_cine, ["NO_CINE_ROTULO", "QT_REGISTROS", "QT_CURSOS_DISTINTOS", "QT_MAT", "QT_SIT_DESVINCULADO"], limite=15)}

## Principais UFs para mapa municipal

Esta tabela considera apenas registros com `IN_USAR_MAPA_MUNICIPAL = True`.

{tabela_markdown(por_uf, ["SG_UF", "QT_REGISTROS", "QT_CURSOS_DISTINTOS", "QT_MAT", "QT_SIT_DESVINCULADO"], limite=15)}

## Tabelas geradas

{chr(10).join(f"* `{caminho.relative_to(ROOT)}`" for caminho in caminhos)}

## Próximo avanço

Com 2024 fechado, o próximo passo é repetir a mesma estrutura para os anos anteriores disponíveis e depois padronizar os campos para construir uma base histórica. Em paralelo, já é possível começar a mapear quais campos devem vir da SBC, do e-MEC e de coleta complementar por scraper.
"""

    RELATORIO.write_text(conteudo, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    df = carregar_base()

    caminhos = []

    resumo_geral = pd.DataFrame(
        [
            {
                "NU_ANO_CENSO": "2024",
                "QT_REGISTROS": len(df),
                "QT_CURSOS_DISTINTOS": df["CO_CURSO"].nunique(),
                "QT_IES_DISTINTAS": df["CO_IES"].nunique(),
                "QT_REGISTROS_MAPA_MUNICIPAL": df["IN_USAR_MAPA_MUNICIPAL"].sum(),
                "QT_REGISTROS_SEM_MAPA_MUNICIPAL": (
                    len(df) - df["IN_USAR_MAPA_MUNICIPAL"].sum()
                ),
                **{col: df[col].sum() for col in COLUNAS_NUMERICAS if col in df.columns},
            }
        ]
    )
    resumo_geral["TX_DESVINCULADO_SOBRE_MAT"] = (
        resumo_geral["QT_SIT_DESVINCULADO"] / resumo_geral["QT_MAT"]
    )
    caminhos.append(salvar(resumo_geral, "resumo_geral_2024.csv"))

    tabelas = {
        "resumo_por_dimensao_2024.csv": ["TP_DIMENSAO", "DS_TP_DIMENSAO"],
        "resumo_por_modalidade_2024.csv": [
            "TP_MODALIDADE_ENSINO",
            "DS_TP_MODALIDADE_ENSINO",
        ],
        "resumo_por_criterio_escopo_2024.csv": ["DS_CRITERIO_ESCOPO"],
        "resumo_por_cine_rotulo_2024.csv": ["CO_CINE_ROTULO", "NO_CINE_ROTULO"],
        "resumo_por_cine_area_geral_2024.csv": [
            "CO_CINE_AREA_GERAL",
            "NO_CINE_AREA_GERAL",
        ],
        "resumo_por_cine_area_especifica_2024.csv": [
            "CO_CINE_AREA_ESPECIFICA",
            "NO_CINE_AREA_ESPECIFICA",
        ],
        "resumo_por_cine_area_detalhada_2024.csv": [
            "CO_CINE_AREA_DETALHADA",
            "NO_CINE_AREA_DETALHADA",
        ],
        "resumo_por_rede_categoria_2024.csv": [
            "TP_REDE",
            "TP_CATEGORIA_ADMINISTRATIVA",
            "TP_ORGANIZACAO_ACADEMICA",
        ],
        "resumo_por_uf_curso_mapa_2024.csv": ["SG_UF"],
        "resumo_por_municipio_curso_mapa_2024.csv": [
            "SG_UF",
            "NO_MUNICIPIO",
        ],
        "resumo_por_ies_2024.csv": [
            "CO_IES",
            "NO_IES",
            "SG_IES",
            "SG_UF_IES",
            "NO_MUNICIPIO_IES",
        ],
        "resumo_por_curso_2024.csv": [
            "CO_IES",
            "NO_IES",
            "CO_CURSO",
            "NO_CURSO",
            "CO_CINE_ROTULO",
            "NO_CINE_ROTULO",
        ],
    }

    for nome, colunas in tabelas.items():
        base = df
        if "mapa" in nome:
            base = df[df["IN_USAR_MAPA_MUNICIPAL"]]
        caminhos.append(salvar(resumir(base, colunas), nome))

    gerar_relatorio(df, caminhos)

    print("Resumos gerados em:", OUT)
    print("Relatório gerado em:", RELATORIO)
    print("Base analisada:", ENTRADA)
    print(df.shape)


if __name__ == "__main__":
    main()
