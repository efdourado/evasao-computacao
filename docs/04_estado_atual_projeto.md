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

1. cursos na área geral CINE de Computação e Tecnologias da Informação e Comunicação;
2. cursos com rótulo CINE `Computação formação de professor`;
3. cursos identificados por nome/rótulo como `Engenharia de Computação`.

### 2018 e 2019

Regra aplicada:

1. cruzamento com `TB_AUX_CINE_BRASIL` por `CO_CINE_ROTULO`;
2. área geral CINE Brasil de Computação/TIC;
3. inclusão de `Computação formação de professor`;
4. inclusão de `Engenharia de Computação`;
5. filtro `TP_NIVEL_ACADEMICO = 1`;
6. exclusão de ABI por `TP_ATRIBUTO_INGRESSO <> 1`, preservando ausentes.

### 2017

2017 usa classificação OCDE, não CINE. Regra aplicada:

1. `CO_OCDE_AREA_ESPECIFICA = 48`;
2. inclusão complementar por nomes relacionados a Computação, como Engenharia de Computação, Redes de Computadores, Sistemas de Informação, Segurança da Informação e Informática;
3. filtro `TP_NIVEL_ACADEMICO = 1`;
4. exclusão de ABI por `TP_ATRIBUTO_INGRESSO <> 1`, preservando ausentes.

Ponto de atenção: 2017 é o ano metodologicamente menos comparável, porque usa OCDE enquanto os anos seguintes usam CINE/CINE Brasil.

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

A chave lógica de curso usada na validação é:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

## Resultados consolidados

| Ano | Registros no recorte expandido | Cursos distintos | IES distintas | Matrículas | Ingressantes | Concluintes | Vagas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.316 | 2.316 | 946 | 313.984 | 146.319 | 38.672 | 584.567 |
| 2018 | 2.734 | 2.734 | 1.006 | 374.469 | 182.866 | 46.106 | 839.556 |
| 2019 | 2.909 | 2.909 | 984 | 392.777 | 195.425 | 47.426 | 1.066.460 |
| 2022 | 58.623 | 3.669 | 970 | 645.320 | 429.865 | 65.480 | 2.373.648 |
| 2024 | 78.657 | 3.987 | 977 | 871.845 | 514.619 | 107.078 | 2.776.208 |

Em 2022 e 2024, os registros aumentam muito porque os microdados passam a representar cursos EaD por dimensão/localização. Esse aumento não deve ser lido como crescimento equivalente no número real de cursos.

## Validação da base expandida

| Ano | Linhas na base expandida | Cursos lógicos | Média de linhas por curso | Máximo de linhas por curso | Cursos com múltiplas linhas |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.316 | 2.316 | 1,00 | 1 | 0 |
| 2018 | 2.734 | 2.734 | 1,00 | 1 | 0 |
| 2019 | 2.909 | 2.909 | 1,00 | 1 | 0 |
| 2022 | 58.623 | 3.669 | 15,98 | 1.112 | 1.030 |
| 2024 | 78.657 | 3.987 | 19,73 | 1.111 | 1.330 |

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
| 1 - Presencial no Brasil | 2.652 | 2.652 | 362.068 | 81.496 |
| 2 - EaD no Brasil | 74.614 | 1.330 | 509.339 | 238.604 |
| 3 - EaD somente nível Brasil | 1.335 | 1.335 | 0 | 0 |
| 4 - EaD exterior | 56 | 56 | 438 | 111 |

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
Matrículas: 871.845
Trancadas: 190.893
Desvinculados: 320.211
Transferidos: 23.433
Falecidos: 85
Desvinculados/matrículas: 36,73%
```

Esse percentual é exploratório. Ele não deve ser apresentado como taxa final de evasão sem uma definição metodológica mais forte.

Para 2017, 2018 e 2019, os arquivos de curso disponíveis não possuem os indicadores agregados de situação de vínculo. Por isso, a situação acadêmica desses anos depende dos arquivos grandes de aluno.

O fluxo já foi executado para 2017, 2018 e 2019.

Validação atual:

| Ano | Origem da situação acadêmica | Cursos com dado de aluno | Matrículas | Concluintes/Formados | Trancadas | Desvinculados | Transferidos | Falecidos | Desvinculados/matrículas |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | `DM_ALUNO.CSV` | 2.316 | 313.984 | 38.672 | 66.421 | 94.303 | 5.043 | 43 | 30,03% |
| 2018 | `DM_ALUNO.CSV` | 2.734 | 374.469 | 46.106 | 76.198 | 118.756 | 7.621 | 48 | 31,71% |
| 2019 | `SUP_ALUNO_2019.CSV` | 2.909 | 392.777 | 47.426 | 79.540 | 130.125 | 6.850 | 75 | 33,13% |
| 2022 | cadastro de cursos | 0 | 645.320 | 65.480 | 150.770 | 214.515 | 8.769 | 80 | 33,24% |
| 2024 | cadastro de cursos | 0 | 871.845 | 107.078 | 190.893 | 320.211 | 23.433 | 85 | 36,73% |

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

1. se o recorte de Computação/TIC deve continuar combinando CINE/OCDE com exceções por nome;
2. como apresentar 2017, já que usa OCDE e é menos comparável;
3. se a taxa exploratória `desvinculados/matrículas` é suficiente para a primeira visualização ou se o professor prefere outra definição de evasão;
4. se os arquivos de docente entram como enriquecimento ou ficam fora da primeira entrega;
5. quais fontes externas entram primeiro: SBC, e-MEC ou coleta por scraper.

## Próximas decisões práticas

1. Gerar um primeiro Power BI com as bases atuais.
2. Definir se a próxima etapa será integração com SBC/e-MEC ou refinamento metodológico da métrica de evasão.
3. Padronizar medidas no Power BI para evitar contagem indevida de linhas como cursos.
4. Se necessário, criar um script específico para preparar tabelas finais já no formato esperado pelo Power BI.
