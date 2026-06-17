# Estado atual do projeto

Este é o documento principal da etapa atual. A direção agora é construir uma **planilha oficial** de cursos de Computação a partir dos microdados do INEP, começando pelos anos já disponíveis: 2017, 2018, 2019, 2022 e 2024.

## Objetivo atual

Gerar uma base consolidada por:

```text
ano + instituição + curso
```

com os cursos oficialmente definidos como Computação/TIC, IES associadas e indicadores acadêmicos disponíveis em cada ano.

## Recorte oficial

Para os anos com CINE/CINE Brasil, entram:

```text
CO_CINE_AREA_GERAL = 6
CO_CINE_ROTULO = 0714E04
```

Interpretação:

* `CO_CINE_AREA_GERAL = 6`: Computação e Tecnologias da Informação e Comunicação;
* `CO_CINE_ROTULO = 0714E04`: Engenharia de Computação.

Para 2017, que usa OCDE e não CINE Brasil, foi usado:

```text
CO_OCDE_AREA_ESPECIFICA = 48
CO_OCDE = 5.23E+06
```

O segundo código é uma aproximação histórica para capturar Engenharia/Computação no padrão antigo. Esse é o principal ponto metodológico a observar em 2017.

## O que fica fora

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

Resumo atual da auditoria:

| Ano | Candidatos fora do recorte | Cursos distintos | Nomes distintos |
| --- | ---: | ---: | ---: |
| 2017 | 310 | 310 | 30 |
| 2018 | 137 | 137 | 37 |
| 2019 | 139 | 139 | 37 |
| 2022 | 1.475 | 154 | 43 |
| 2024 | 1.847 | 148 | 46 |

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

| Arquivo | Uso |
| --- | --- |
| `planilha_oficial_computacao.csv` | análise principal por ano, IES e curso |
| `planilha_oficial_computacao_expandida.csv` | mapas, UF, município, EaD e `TP_DIMENSAO` |
| `dicionario_planilha_oficial.csv` | descrição das colunas principais |

## Totais atuais

| Ano | Registros expandidos | Cursos distintos | IES distintas | Matrículas | Ingressantes | Concluintes | Vagas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.292 | 2.292 | 949 | 314.020 | 144.190 | 38.403 | 589.585 |
| 2018 | 2.641 | 2.641 | 1.006 | 362.762 | 178.985 | 45.124 | 831.472 |
| 2019 | 2.816 | 2.816 | 984 | 381.845 | 192.362 | 46.640 | 1.059.141 |
| 2022 | 57.197 | 3.564 | 970 | 633.688 | 425.216 | 64.486 | 2.351.629 |
| 2024 | 76.865 | 3.894 | 977 | 860.791 | 509.828 | 106.157 | 2.739.900 |

Em 2022 e 2024 há muitas linhas por curso por causa de EaD, localização e `TP_DIMENSAO`. Para contar cursos, usar a chave:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

## Situação acadêmica

O projeto ainda não mede evasão definitiva. O que temos é situação acadêmica:

```text
trancados
desvinculados
transferidos
formados/concluintes
falecidos
```

Em 2022 e 2024 esses campos vêm no cadastro de cursos. Em 2017, 2018 e 2019 eles foram reconstruídos a partir dos arquivos grandes de aluno.

Indicador exploratório atual:

```text
QT_SIT_DESVINCULADO / QT_MAT
```

Não chamar isso de taxa final de evasão sem definição metodológica posterior.

## Pipeline principal

Ordem para reproduzir tudo:

```bash
.venv/bin/python scripts/01_entender_2024.py
.venv/bin/python scripts/03_diagnostico_2024.py
.venv/bin/python scripts/04_limpar_2024.py
.venv/bin/python scripts/05_resumir_2024.py
.venv/bin/python scripts/07_consolidar_historico_cursos.py
.venv/bin/python scripts/08_validar_historico.py
.venv/bin/python scripts/09_consolidar_alunos_quantitativo.py
.venv/bin/python scripts/10_mesclar_evasao_historico.py
.venv/bin/python scripts/11_auditar_recorte_computacao.py
.venv/bin/python scripts/12_gerar_planilha_oficial.py
```

## Próximos passos

1. Adicionar novos anos mantendo a regra de recorte.
2. Resolver diferenças de nomenclatura entre anos antigos e recentes.
3. Separar casos ambíguos em auditoria quando não houver correspondência clara.
4. Começar o Power BI pela planilha oficial comparável.
5. Usar a planilha expandida apenas para mapa e dimensão territorial.
6. Depois integrar fontes externas como e-MEC, SBC e scraper.
