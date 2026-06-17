# Estado atual do projeto

Este é o documento principal da etapa atual. A base oficial agora cobre os anos **2009 a 2024**, com cuidado separado para os anos muito antigos, **1995 a 2008**.

## Objetivo atual

Construir uma planilha oficial por:

```text
ano + instituição + curso
```

com cursos de Computação/TIC definidos pela classificação do INEP, IES associadas e indicadores acadêmicos disponíveis em cada ano.

## Recorte oficial

Para anos com CINE/CINE Brasil, entram:

```text
CO_CINE_AREA_GERAL = 6
CO_CINE_ROTULO = 0714E04
```

Interpretação:

* `CO_CINE_AREA_GERAL = 6`: Computação e Tecnologias da Informação e Comunicação;
* `CO_CINE_ROTULO = 0714E04`: Engenharia de Computação.

Para 2017, que usa OCDE e não CINE, usamos uma aproximação histórica:

```text
CO_OCDE_AREA_ESPECIFICA = 48
CO_OCDE = 5.23E+06
```

Esse é o principal cuidado metodológico de 2017: ele não é CINE, mas foi trazido para manter a série histórica com o melhor recorte equivalente disponível.

## Cobertura atual

| Período | Situação | Uso recomendado |
| --- | --- | --- |
| 2009-2016 | Integrado por CINE no cadastro de cursos | Série histórica e Power BI |
| 2017 | Integrado por OCDE/proxy histórico | Série histórica com observação metodológica |
| 2018-2019 | Integrado por CINE Brasil no modelo antigo | Série histórica e Power BI |
| 2020-2024 | Integrado por CINE no cadastro de cursos | Série histórica, Power BI e mapas |
| 1995-2008 | Inventariado, ainda não integrado | Stand-by até mapear dicionários antigos |

Os anos 1995-2008 ficaram fora da planilha oficial por enquanto porque usam estruturas anteriores ao modelo CINE atual. O inventário está em:

```text
data/processed/historico/inventario_anos_antigos_1995_2008.csv
```

Resumo desse inventário:

| Período | Observação |
| --- | --- |
| 1995-1996 | Há campos explícitos de trancamento/abandono, mas falta mapear o recorte antigo de área para Computação. |
| 1997-1999 | Estrutura mais antiga/codificada; precisa dicionário antes de integrar. |
| 2000-2008 | Há graduação presencial/EaD e áreas antigas, mas as métricas estão em campos codificados; precisa mapeamento. |

## Planilhas oficiais

Geradas por:

```bash
.venv/bin/python scripts/12_gerar_planilha_oficial.py
```

Saídas:

```text
data/processed/oficial/planilha_oficial_computacao.csv
data/processed/oficial/planilha_oficial_computacao_expandida.csv
data/processed/oficial/dicionario_planilha_oficial.csv
```

Uso recomendado:

| Arquivo | Tamanho atual | Uso |
| --- | ---: | --- |
| `planilha_oficial_computacao.csv` | 43.481 linhas | análise principal por ano, IES e curso |
| `planilha_oficial_computacao_expandida.csv` | 315.414 linhas | mapas, UF, município, EaD e `TP_DIMENSAO` |
| `dicionario_planilha_oficial.csv` |  | descrição das colunas principais |

Para contar cursos, usar a chave:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

Não usar contagem simples de linhas da base expandida como contagem de cursos, principalmente em anos com EaD.

## Totais atuais

| Ano | Registros expandidos | Curso-IES distintos | IES distintas | Matrículas | Ingressantes | Concluintes | Desvinculados |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2009 | 3.077 | 1.967 | 886 | 284.863 | 116.880 | 42.422 | 33.054 |
| 2010 | 3.072 | 2.064 | 920 | 304.968 | 121.409 | 41.566 | 72.446 |
| 2011 | 3.539 | 2.176 | 951 | 320.827 | 129.178 | 41.797 | 83.812 |
| 2012 | 4.213 | 2.310 | 987 | 323.071 | 146.978 | 42.638 | 90.263 |
| 2013 | 4.258 | 2.357 | 986 | 332.197 | 143.122 | 41.421 | 91.106 |
| 2014 | 4.714 | 2.403 | 988 | 339.266 | 152.501 | 42.988 | 102.954 |
| 2015 | 5.607 | 2.439 | 979 | 338.413 | 148.737 | 45.255 | 103.810 |
| 2016 | 6.273 | 2.470 | 987 | 330.538 | 147.757 | 45.415 | 121.551 |
| 2017 | 2.292 | 2.292 | 949 | 314.020 | 144.190 | 38.403 | 93.925 |
| 2018 | 2.641 | 2.641 | 1.006 | 362.762 | 178.985 | 45.124 | 115.356 |
| 2019 | 2.816 | 2.816 | 984 | 381.845 | 192.362 | 46.640 | 126.740 |
| 2020 | 28.096 | 3.063 | 959 | 430.414 | 240.844 | 53.291 | 123.384 |
| 2021 | 40.977 | 3.228 | 949 | 499.839 | 284.526 | 56.552 | 142.315 |
| 2022 | 57.197 | 3.564 | 970 | 633.688 | 425.216 | 64.486 | 211.057 |
| 2023 | 69.777 | 3.797 | 974 | 767.713 | 489.263 | 84.164 | 264.156 |
| 2024 | 76.865 | 3.894 | 977 | 860.791 | 509.828 | 106.157 | 315.838 |

## Situação acadêmica

O projeto ainda não mede evasão definitiva. O que temos é situação acadêmica:

```text
trancados
desvinculados
transferidos
formados/concluintes
falecidos
```

Origem dos dados:

| Anos | Origem da situação acadêmica |
| --- | --- |
| 2009-2016 | agregados no cadastro de cursos |
| 2017-2019 | reconstruído a partir dos arquivos grandes de aluno |
| 2020-2024 | agregados no cadastro de cursos |

Indicador exploratório atual:

```text
QT_SIT_DESVINCULADO / QT_MAT
```

Não chamar esse indicador de taxa final de evasão sem definição metodológica posterior.

## Auditoria do recorte

Cursos relacionados, mas fora da regra oficial, não entram automaticamente. Exemplos:

```text
Matemática Computacional
Física Computacional
Informática em Saúde
Big Data no Agronegócio
áreas interdisciplinares
```

Eles aparecem na auditoria:

```text
data/processed/historico/auditoria_possiveis_cursos_fora_recorte.csv
data/processed/historico/auditoria_recorte_computacao_resumo.csv
```

Essa auditoria serve para transparência metodológica. Ela não altera a planilha oficial automaticamente.

## Pipeline principal

Ordem para reproduzir a etapa histórica:

```bash
.venv/bin/python scripts/07_consolidar_historico_cursos.py
.venv/bin/python scripts/08_validar_historico.py
.venv/bin/python scripts/09_consolidar_alunos_quantitativo.py
.venv/bin/python scripts/10_mesclar_evasao_historico.py
.venv/bin/python scripts/11_auditar_recorte_computacao.py
.venv/bin/python scripts/12_gerar_planilha_oficial.py
.venv/bin/python scripts/13_inventariar_anos_antigos.py
```

## Próximos passos

1. Começar o Power BI pela planilha oficial comparável.
2. Usar a planilha expandida para mapas e filtros territoriais.
3. Decidir se vale mapear 1995-2008 agora ou deixar como etapa histórica posterior.
4. Integrar fontes externas como e-MEC, SBC e scraper.
