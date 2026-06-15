# Estado atual do projeto

Este documento resume a etapa atual do projeto para consulta rápida antes de reuniões. Os detalhes técnicos continuam nos documentos anteriores:

```text
docs/01_entendimento_dados.md
docs/02_analise_2024.md
docs/03_integracao_historica.md
```

## Objetivo da etapa

Construir uma base consolidada de cursos superiores de Computação/TIC no Brasil, a partir dos microdados do Censo da Educação Superior do INEP, com duas finalidades imediatas:

1. gerar um panorama histórico por curso, IES, modalidade, localização e classificação de área;
2. preparar bases confiáveis para visualização dinâmica em Power BI.

A análise de evasão/situação acadêmica já foi aprofundada para 2017, 2018 e 2019 a partir dos arquivos grandes de aluno. Para 2022 e 2024, os indicadores de situação acadêmica já vêm agregados no cadastro de cursos.

## Fontes recebidas e usadas

| Ano | Arquivos brutos disponíveis | Referências disponíveis | Situação |
| --- | --- | --- | --- |
| 2017 | `DM_CURSO`, `DM_IES`, `DM_LOCAL_OFERTA`, `DM_ALUNO`, `DM_DOCENTE`, `TB_AUX_AREA_OCDE` | dicionário, leia-me, filtros, código de país | curso integrado; aluno processado |
| 2018 | `DM_CURSO`, `DM_IES`, `DM_LOCAL_OFERTA`, `DM_ALUNO`, `DM_DOCENTE`, `TB_AUX_CINE_BRASIL` | dicionário, leia-me, filtros, nota, código de país | curso integrado; aluno processado |
| 2019 | `SUP_CURSO`, `SUP_IES`, `SUP_LOCAL_OFERTA`, `SUP_ALUNO_2019`, `SUP_DOCENTE_2019`, `TB_AUX_CINE_BRASIL` | dicionário, leia-me, filtros, código de país | curso integrado; aluno processado |
| 2022 | `MICRODADOS_CADASTRO_CURSOS`, `MICRODADOS_ED_SUP_IES` | dicionário, leia-me, nota informativa | integrado na base histórica |
| 2024 | `MICRODADOS_CADASTRO_CURSOS`, `MICRODADOS_ED_SUP_IES`, `MICRODADOS_LICENCIATURA` | dicionário, leia-me, nota informativa | integrado na base histórica e analisado em detalhe |

Arquivos brutos e processados não devem ser versionados no Git:

```text
data/raw/
data/processed/
```

Referências oficiais podem ser versionadas:

```text
data/reference/inep/
```

## Recorte de Computação/TIC

O recorte atual usa a classificação oficial sempre que possível, evitando depender apenas do nome do curso.

### 2022 e 2024

Regra aplicada:

1. cursos na área geral 6 da CINE: Computação e Tecnologias da Informação e Comunicação.

Cursos relacionados que estejam em outras áreas gerais, como Engenharia de Computação, Computação formação de professor, Matemática Computacional, Física Computacional e Informática em Saúde, não entram automaticamente no recorte oficial. Eles ficam na auditoria para revisão.

### 2018 e 2019

Regra aplicada:

1. cruzamento com `TB_AUX_CINE_BRASIL` por `CO_CINE_ROTULO`;
2. área geral 6 da CINE Brasil: Computação e Tecnologias da Informação e Comunicação;
3. filtro `TP_NIVEL_ACADEMICO = 1`;
4. exclusão de ABI por `TP_ATRIBUTO_INGRESSO <> 1`, preservando ausentes.

### 2017

2017 usa classificação OCDE, não CINE. Regra aplicada:

1. `CO_OCDE_AREA_ESPECIFICA = 48`, usado como aproximação histórica da área de Computação;
2. filtro `TP_NIVEL_ACADEMICO = 1`;
3. exclusão de ABI por `TP_ATRIBUTO_INGRESSO <> 1`, preservando ausentes.

Termos como `Análise e Desenvolvimento`, `Banco de Dados`, `Ciência de Dados`, `Engenharia de Computação`, `Engenharia de Software`, `Gestão da Tecnologia da Informação`, `Redes de Computadores`, `Sistemas de Informação`, `Tecnologia da Informação` e `Informática` não entram automaticamente no recorte oficial quando estão fora da área/classificação oficial, mas são monitorados pela auditoria.

Ponto de atenção: 2017 é o ano metodologicamente menos comparável, porque usa OCDE enquanto os anos seguintes usam CINE/CINE Brasil.

## Auditoria do recorte

Para reduzir o risco de deixar cursos de Computação/TIC fora do recorte, foi criada uma auditoria específica:

```bash
.venv/bin/python scripts/11_auditar_recorte_computacao.py
```

Ela procura, nos arquivos brutos de curso, nomes/rótulos com termos de auditoria ligados a Computação/TIC que **não** entraram na base comparável atual. A auditoria não altera o recorte automaticamente; ela gera uma lista para revisão manual.

Arquivos gerados:

```text
data/processed/historico/auditoria_possiveis_cursos_fora_recorte.csv
data/processed/historico/auditoria_recorte_computacao_resumo.csv
```

Resultado da auditoria após o alinhamento do recorte oficial à área geral 6 da CINE/CINE Brasil:

| Ano | Candidatos fora do recorte | Cursos distintos | Nomes distintos |
| --- | ---: | ---: | ---: |
| 2017 | 576 | 576 | 36 |
| 2018 | 298 | 298 | 43 |
| 2019 | 326 | 326 | 43 |
| 2022 | 3.665 | 377 | 49 |
| 2024 | 5.578 | 502 | 54 |

Os candidatos fora do recorte são cursos relacionados ou adjacentes que não pertencem à área geral 6, como Engenharia de Computação, Computação formação de professor, Matemática Computacional, Física Computacional, Informática em Saúde, Big Data no Agronegócio, áreas interdisciplinares e algumas engenharias com ênfase em computação. Eles devem ser tratados como lista de revisão metodológica, não como erro automático.

## Pipeline atual

| Script | Função |
| --- | --- |
| `01_entender_2024.py` | carrega 2024, cruza cursos e IES e aplica recorte preliminar |
| `02_abrir_base.py` | abre a base preliminar e imprime diagnóstico inicial |
| `03_diagnostico_2024.py` | gera diagnósticos de 2024 |
| `04_limpar_2024.py` | gera a base 2024 tratada |
| `05_resumir_2024.py` | gera resumos finais e relatório de 2024 |
| `06_inventariar_bases.py` | inventaria os arquivos brutos por ano |
| `07_consolidar_historico_cursos.py` | consolida a base histórica expandida |
| `08_validar_historico.py` | valida duplicidade lógica e gera base comparável por curso |
| `09_consolidar_alunos_quantitativo.py` | prepara agregação de situação de vínculo a partir dos arquivos grandes de aluno |
| `10_mesclar_evasao_historico.py` | mescla a base comparável com quantitativos derivados dos arquivos de aluno |
| `11_auditar_recorte_computacao.py` | lista possíveis cursos de Computação/TIC que ficaram fora do recorte |

Ordem recomendada para reproduzir a etapa histórica:

```bash
.venv/bin/python scripts/06_inventariar_bases.py
.venv/bin/python scripts/07_consolidar_historico_cursos.py
.venv/bin/python scripts/08_validar_historico.py
```

Ordem para atualizar evasão quando arquivos de aluno forem adicionados ou corrigidos:

```bash
.venv/bin/python scripts/09_consolidar_alunos_quantitativo.py
.venv/bin/python scripts/10_mesclar_evasao_historico.py
.venv/bin/python scripts/11_auditar_recorte_computacao.py
```

## Bases processadas principais

| Arquivo | Uso recomendado |
| --- | --- |
| `data/processed/computacao_2024_tratada.csv` | análise detalhada de 2024 |
| `data/processed/resumos_2024/` | tabelas-resumo de 2024 |
| `data/processed/historico/computacao_historico_cursos.csv` | base expandida para mapas, filtros geográficos e Power BI |
| `data/processed/historico/computacao_historico_cursos_comparavel.csv` | base com uma linha por curso lógico, indicada para série histórica e comparação entre anos |
| `data/processed/historico/validacao_historico_por_ano.csv` | validação da quantidade de linhas por curso/ano |
| `data/processed/historico/validacao_historico_metricas.csv` | validação por métrica numérica |
| `data/processed/historico/validacao_historico_dimensao_metricas.csv` | distribuição por `TP_DIMENSAO` |
| `data/processed/historico/alunos_computacao_quantitativo.csv` | quantitativos de aluno para 2017, 2018 e 2019 |
| `data/processed/historico/computacao_historico_com_evasao.csv` | base comparável com situação acadêmica preenchida por alunos quando disponível |
| `data/processed/historico/validacao_evasao_alunos_vs_cursos.csv` | validação entre quantitativos de aluno e agregados de curso |
| `data/processed/historico/auditoria_possiveis_cursos_fora_recorte.csv` | lista de candidatos que parecem Computação/TIC mas ficaram fora do recorte |
| `data/processed/historico/auditoria_recorte_computacao_resumo.csv` | resumo anual da auditoria do recorte |

A chave lógica de curso usada na validação é:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

## Resultados consolidados

| Ano | Registros no recorte expandido | Cursos distintos | IES distintas | Matrículas | Ingressantes | Concluintes | Vagas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.023 | 2.023 | 914 | 270.959 | 126.604 | 35.841 | 535.798 |
| 2018 | 2.480 | 2.480 | 985 | 333.996 | 163.672 | 43.562 | 790.522 |
| 2019 | 2.629 | 2.629 | 961 | 354.139 | 183.883 | 44.890 | 1.025.967 |
| 2022 | 55.007 | 3.341 | 942 | 594.580 | 410.454 | 61.760 | 2.298.785 |
| 2024 | 73.134 | 3.540 | 943 | 800.222 | 489.067 | 100.488 | 2.641.395 |

Em 2022 e 2024, os registros aumentam muito porque os microdados passam a representar cursos EaD por dimensão/localização. Esse aumento não deve ser lido como crescimento equivalente no número real de cursos.

## Validação da base expandida

| Ano | Linhas na base expandida | Cursos lógicos | Média de linhas por curso | Máximo de linhas por curso | Cursos com múltiplas linhas |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.023 | 2.023 | 1,00 | 1 | 0 |
| 2018 | 2.480 | 2.480 | 1,00 | 1 | 0 |
| 2019 | 2.629 | 2.629 | 1,00 | 1 | 0 |
| 2022 | 55.007 | 3.341 | 16,46 | 1.112 | 956 |
| 2024 | 73.134 | 3.540 | 20,66 | 1.111 | 1.234 |

Interpretação:

* 2017, 2018 e 2019 possuem uma linha por curso no arquivo de curso;
* 2022 e 2024 possuem múltiplas linhas por curso, principalmente por causa de EaD e `TP_DIMENSAO`;
* a base expandida é adequada para mapas e filtros territoriais;
* a base comparável é mais adequada para série histórica e contagem de cursos;
* no Power BI, não usar contagem de linhas como contagem de cursos.

## Leitura de `TP_DIMENSAO`

| Código | Interpretação | Uso |
| --- | --- | --- |
| 1 | Presencial no Brasil | pode entrar em mapa municipal |
| 2 | EaD no Brasil | pode entrar em mapa municipal/polos |
| 3 | EaD somente nível Brasil | usar apenas em indicadores nacionais |
| 4 | EaD exterior | tratar separadamente |

Em 2024:

| TP_DIMENSAO | Registros | Cursos distintos | Matrículas | Desvinculados |
| --- | ---: | ---: | ---: | ---: |
| 1 - Presencial no Brasil | 2.301 | 2.301 | 315.965 | 73.202 |
| 2 - EaD no Brasil | 69.541 | 1.234 | 483.835 | 229.305 |
| 3 - EaD somente nível Brasil | 1.239 | 1.239 | 0 | 0 |
| 4 - EaD exterior | 53 | 53 | 422 | 106 |

Vagas e inscritos EaD aparecem principalmente em `TP_DIMENSAO = 3`, enquanto matrículas, ingressantes, concluintes e situações acadêmicas aparecem distribuídos nas linhas territoriais.

## Indicadores de evasão e situação acadêmica

Nos anos de 2022 e 2024, os arquivos de curso já trazem:

```text
QT_SIT_TRANCADA
QT_SIT_DESVINCULADO
QT_SIT_TRANSFERIDO
QT_SIT_FALECIDO
```

Em 2024, no recorte de Computação/TIC:

```text
Matrículas: 800.222
Trancadas: 179.110
Desvinculados: 302.613
Transferidos: 19.763
Falecidos: 74
Desvinculados/matrículas: 37,82%
```

Esse percentual é exploratório. Ele não deve ser apresentado como taxa final de evasão sem uma definição metodológica mais forte.

Para 2017, 2018 e 2019, os arquivos de curso disponíveis não possuem os indicadores agregados de situação de vínculo. Por isso, a situação acadêmica desses anos depende dos arquivos grandes de aluno.

O fluxo já foi executado para 2017, 2018 e 2019.

Validação atual:

| Ano | Origem da situação acadêmica | Cursos com dado de aluno | Matrículas | Concluintes/Formados | Trancadas | Desvinculados | Transferidos | Falecidos | Desvinculados/matrículas |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | `DM_ALUNO.CSV` | 2.023 | 270.959 | 35.841 | 60.872 | 85.814 | 4.262 | 40 | 31,67% |
| 2018 | `DM_ALUNO.CSV` | 2.480 | 333.996 | 43.562 | 69.898 | 107.247 | 6.939 | 45 | 32,11% |
| 2019 | `SUP_ALUNO_2019.CSV` | 2.629 | 354.139 | 44.890 | 72.085 | 119.676 | 6.306 | 69 | 33,79% |
| 2022 | cadastro de cursos | 0 | 594.580 | 61.760 | 141.220 | 203.332 | 7.961 | 72 | 34,20% |
| 2024 | cadastro de cursos | 0 | 800.222 | 100.488 | 179.110 | 302.613 | 19.763 | 74 | 37,82% |

Checagem de consistência:

* em 2017, 2018 e 2019, `QT_MAT` bate exatamente com `QT_ALUNO_CURSANDO + QT_ALUNO_FORMADO`;
* em 2017, 2018 e 2019, `QT_CONC` bate exatamente com `QT_ALUNO_FORMADO`;
* isso indica que a agregação dos arquivos de aluno está coerente com os agregados oficiais de curso nesses três anos.

## Arquivos grandes e próximos usos

Arquivos de aluno:

```text
2017: DM_ALUNO.CSV, processado
2018: DM_ALUNO.CSV, processado
2019: SUP_ALUNO_2019.CSV, processado
```

Situação: **processado para 2017, 2018 e 2019**.

Motivo:

* 2017, 2018 e 2019 já permitem reconstruir situação de vínculo/evasão exploratória;
* 2022 e 2024 já têm situação acadêmica agregada no cadastro de cursos.

Fluxo preparado:

```text
09_consolidar_alunos_quantitativo.py
10_mesclar_evasao_historico.py
```

O script 09 usa a chave completa `NU_ANO_CENSO + CO_IES + CO_CURSO`, evitando depender apenas de `CO_CURSO`. O script 10 gera uma validação específica para comparar os quantitativos derivados dos alunos com os agregados já existentes na base de cursos.

Arquivos de docente:

```text
2017: DM_DOCENTE.CSV
2018: DM_DOCENTE.CSV
2019: SUP_DOCENTE_2019.CSV
```

Situação: **opcional**.

Motivo:

* podem enriquecer análises com perfil docente, titulação e regime de trabalho;
* não são centrais para fechar a primeira entrega de panorama de cursos e evasão exploratória.

## O que já dá para entregar

Com o estado atual, já é possível montar uma primeira entrega em Power BI com:

1. panorama histórico de cursos de Computação/TIC;
2. evolução de matrículas, ingressantes, concluintes e vagas;
3. comparação por modalidade, rede, categoria administrativa, grau acadêmico e CINE;
4. mapa municipal/UF com a base expandida;
5. visão de situação acadêmica/evasão exploratória para 2017, 2018, 2019, 2022 e 2024;
6. página metodológica explicando a diferença entre base expandida e base comparável.

Sugestão de páginas no Power BI:

| Página | Base principal | Conteúdo |
| --- | --- | --- |
| Visão geral histórica | comparável | série por ano, cursos, IES, matrículas, ingressantes, concluintes |
| Mapa | expandida | distribuição por UF/município, modalidade e `TP_DIMENSAO` |
| Cursos e áreas | comparável | CINE, nomes de curso, grau acadêmico, modalidade |
| IES | comparável | ranking e perfil das instituições |
| Situação acadêmica | final com evasão | trancados, desvinculados, transferidos e indicador exploratório para 2017, 2018, 2019, 2022 e 2024 |
| Metodologia | validações | recortes, limitações, chaves e cuidados |

## Pontos para discutir com o orientador

Não são bloqueios para continuar, mas são decisões metodológicas importantes:

1. como apresentar 2017, já que usa OCDE e é menos comparável;
2. se algum curso adjacente listado na auditoria deve aparecer em uma visão ampliada, separada do recorte oficial;
3. se a taxa exploratória `desvinculados/matrículas` é suficiente para a primeira visualização ou se o professor prefere outra definição de evasão;
4. se os arquivos de docente entram como enriquecimento ou ficam fora da primeira entrega;
5. quais fontes externas entram primeiro: SBC, e-MEC ou coleta por scraper.

## Próximas decisões práticas

1. Gerar um primeiro Power BI com as bases atuais.
2. Definir se a próxima etapa será integração com SBC/e-MEC ou refinamento metodológico da métrica de evasão.
3. Padronizar medidas no Power BI para evitar contagem indevida de linhas como cursos.
4. Se necessário, criar um script específico para preparar tabelas finais já no formato esperado pelo Power BI.
