# Visão geral

Este projeto organiza os Microdados do Censo da Educação Superior do INEP para analisar cursos superiores de Computação/TIC no Brasil.

## Base oficial atual

A base oficial cobre:

```text
2009 a 2024
```

Ela começa em 2009 porque esse é o primeiro período em que o recorte histórico fica compatível com a regra oficial baseada em CINE/CINE Brasil.

## Recorte de Computação/TIC

Nos anos com CINE/CINE Brasil, entram:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

Interpretação:

* área geral 6: Computação e Tecnologias da Informação e Comunicação;
* rótulo `0714E04`: Engenharia de Computação.

Em 2017, como o ano usa OCDE, foi usada uma aproximação histórica:

```text
CO_OCDE_AREA_ESPECIFICA = 48
ou
CO_OCDE = 5.23E+06
```

## Planilhas finais

As planilhas finais ficam em:

```text
data/processed/oficial/
```

| Arquivo | Uso |
| --- | --- |
| `planilha_oficial_computacao.csv` | base principal para Power BI, séries históricas e contagem de cursos |
| `planilha_oficial_computacao_expandida.csv` | mapas, UF, município, EaD e dimensão territorial |
| `dicionario_planilha_oficial.csv` | descrição das colunas principais |

## O que temos

A planilha principal tem uma linha por:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

Ela reúne:

```text
ano
instituição
curso
classificação de área
critério de entrada no recorte
modalidade
grau acadêmico
categoria administrativa
rede pública/privada
organização acadêmica
vagas
inscritos
ingressantes
matrículas
concluintes
trancados
desvinculados
transferidos
falecidos
```

## Cuidado com evasão

O projeto ainda não mede evasão definitiva. A base organiza situação acadêmica e permite indicadores exploratórios, como:

```text
QT_SIT_DESVINCULADO / QT_MAT
```

Esse indicador ajuda a observar padrões, mas não deve ser apresentado como taxa final de evasão sem definição metodológica posterior.

## Próximos passos

1. Usar `planilha_oficial_computacao.csv` como base principal no Power BI.
2. Usar `planilha_oficial_computacao_expandida.csv` apenas para mapas e filtros territoriais.
3. Integrar fontes externas como e-MEC, SBC e dados coletados por scraper.
4. Retomar 1995-2008 apenas se o projeto decidir ampliar a série histórica para antes de 2009.
