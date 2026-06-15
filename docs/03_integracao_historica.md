# Estratégia de integração histórica

## Objetivo

Construir uma base histórica de cursos de Computação/TIC a partir dos microdados do INEP, começando por 2017, 2018, 2019, 2022 e 2024.

O objetivo imediato é padronizar um panorama comparável por ano, curso, IES, modalidade, localização e classificação de área. A análise de evasão mais detalhada deve ser tratada em uma segunda camada, especialmente para os anos antigos.

## Inventário atual

| Ano | Arquivos principais disponíveis | Estrutura | Delimitador observado | Classificação |
| --- | --- | --- | --- | --- |
| 2017 | `DM_CURSO`, `DM_IES`, `DM_LOCAL_OFERTA`, `TB_AUX_AREA_OCDE` | Modelo antigo, várias tabelas | `DM_CURSO` com `,`; demais arquivos com `|` | OCDE |
| 2018 | `DM_CURSO`, `DM_IES`, `DM_LOCAL_OFERTA`, `TB_AUX_CINE_BRASIL` | Modelo antigo, várias tabelas | `|` | CINE Brasil |
| 2019 | `SUP_CURSO`, `SUP_IES`, `SUP_LOCAL_OFERTA`, `TB_AUX_CINE_BRASIL` | Modelo antigo, várias tabelas | `|` | CINE Brasil |
| 2022 | `MICRODADOS_CADASTRO_CURSOS`, `MICRODADOS_ED_SUP_IES` | Modelo novo, duas tabelas principais | `;` | CINE |
| 2024 | `MICRODADOS_CADASTRO_CURSOS`, `MICRODADOS_ED_SUP_IES` | Modelo novo, duas tabelas principais | `;` | CINE |

O inventário automático é gerado por:

```bash
.venv/bin/python scripts/06_inventariar_bases.py
```

Saídas:

```text
data/processed/inventario_bases_raw.csv
data/processed/comparacao_colunas_raw.csv
```

## Base histórica expandida inicial

Foi criado um primeiro pipeline histórico:

```bash
.venv/bin/python scripts/07_consolidar_historico_cursos.py
```

Arquivos gerados:

```text
data/processed/historico/computacao_historico_cursos.csv
data/processed/historico/resumo_historico_por_ano.csv
```

A base histórica atual contém:

```text
135.273 registros
45 colunas padronizadas
5 anos integrados: 2017, 2018, 2019, 2022 e 2024
```

Essa é a **base expandida**. Ela é adequada para mapas, filtros geográficos, modalidade, `TP_DIMENSAO`, IES, curso e análises dinâmicas no Power BI. Ela ainda não deve ser tratada como base final de evasão, porque 2017-2019 não trazem desvinculação/trancamento nos arquivos de curso.

## Base comparável por curso

Como 2022 e 2024 possuem múltiplas linhas por curso por causa de dimensão/localização, também foi criada uma base com uma linha por curso lógico:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

Script:

```bash
.venv/bin/python scripts/08_validar_historico.py
```

Arquivo principal gerado:

```text
data/processed/historico/computacao_historico_cursos_comparavel.csv
```

Uso recomendado:

| Base | Uso principal | Cuidado |
| --- | --- | --- |
| `computacao_historico_cursos.csv` | mapa, dimensão geográfica, filtros de UF/município, análise expandida | não usar contagem de linhas como contagem de cursos |
| `computacao_historico_cursos_comparavel.csv` | série histórica, comparação entre anos, análise por curso/IES | indicadores numéricos foram agregados por soma das linhas expandidas |

## Validação de duplicidade lógica

O script `08_validar_historico.py` também gera arquivos de validação:

```text
data/processed/historico/validacao_historico_por_ano.csv
data/processed/historico/validacao_historico_metricas.csv
data/processed/historico/validacao_historico_dimensao_metricas.csv
data/processed/historico/validacao_linhas_por_curso.csv
data/processed/historico/validacao_top_cursos_multilinhas.csv
```

Resultado principal:

| Ano | Linhas na base expandida | Curso-IES distintos | Média de linhas por curso | Máximo de linhas por curso | Cursos com múltiplas linhas | Soma `QT_MAT` expandida | Soma `QT_MAT` agregada por curso | Soma do máximo de `QT_MAT` por curso | Razão expandida/máximo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.023 | 2.023 | 1,00 | 1 | 0 | 270.959 | 270.959 | 270.959 | 1,00 |
| 2018 | 2.480 | 2.480 | 1,00 | 1 | 0 | 333.996 | 333.996 | 333.996 | 1,00 |
| 2019 | 2.629 | 2.629 | 1,00 | 1 | 0 | 354.139 | 354.139 | 354.139 | 1,00 |
| 2022 | 55.007 | 3.341 | 16,46 | 1.112 | 956 | 594.580 | 594.580 | 351.167 | 1,69 |
| 2024 | 73.134 | 3.540 | 20,66 | 1.111 | 1.234 | 800.222 | 800.222 | 460.511 | 1,74 |

Interpretação:

* a soma expandida e a soma agregada por curso batem exatamente, porque a agregação por curso foi feita somando as linhas;
* 2017, 2018 e 2019 têm uma linha por curso no arquivo de curso;
* 2022 e 2024 têm muitos cursos com múltiplas linhas, principalmente por causa dos cursos EaD;
* a diferença entre a soma expandida e a soma do máximo por curso não prova duplicidade indevida. Ela mostra que indicadores como matrículas, ingressantes, concluintes e situações acadêmicas estão distribuídos em várias linhas territoriais;
* para `QT_VG_TOTAL` e `QT_INSCRITO_TOTAL`, a validação mostra razão 1,00 entre expandida e máximo por curso em todos os anos disponíveis. Em 2022/2024, isso acontece porque vagas e inscritos EaD aparecem principalmente em `TP_DIMENSAO = 3`, nível Brasil;
* para mapas, a base expandida é a correta. Para contagem de cursos e série histórica por curso/IES, usar a base comparável ou `distinct count` pela chave lógica.

## Diferenças metodológicas importantes

### 2017

O ano de 2017 usa classificação OCDE. O recorte de Computação não deve depender de `CO_CINE_ROTULO`, pois essa variável não existe na estrutura de 2017.

Regra aplicada:

* usar `CO_OCDE_AREA_ESPECIFICA = 48` para Computação;
* aplicar `TP_NIVEL_ACADEMICO = 1`;
* aplicar `TP_ATRIBUTO_INGRESSO <> 1`, preservando valores ausentes, para evitar Área Básica de Ingresso (ABI) nas estatísticas por área.

Como 2017 não tem CINE Brasil, `CO_OCDE_AREA_ESPECIFICA = 48` é tratado como aproximação histórica da área de Computação.

### 2018 e 2019

Os anos de 2018 e 2019 usam CINE Brasil, mas ainda no modelo antigo.

Regra aplicada:

* cruzar `DM_CURSO`/`SUP_CURSO` com `TB_AUX_CINE_BRASIL` por `CO_CINE_ROTULO`;
* usar a área geral 6 da CINE Brasil: Computação e Tecnologias da Informação e Comunicação;
* aplicar `TP_NIVEL_ACADEMICO = 1`;
* aplicar `TP_ATRIBUTO_INGRESSO <> 1`, preservando valores ausentes, para evitar ABI.

### 2022 e 2024

Os anos de 2022 e 2024 usam o modelo novo, com os arquivos de cursos e IES em formato `;`.

Regra aplicada:

* área geral 6 da CINE: Computação e Tecnologias da Informação e Comunicação;
* separação geográfica por `TP_DIMENSAO`.

A variável `TP_DIMENSAO` foi criada para identificar a dimensão geográfica dos cursos presenciais e EaD:

```text
1 = Cursos presenciais ofertados no Brasil
2 = Cursos a distância ofertados no Brasil
3 = Cursos a distância com dimensão de dados somente em nível Brasil
4 = Cursos a distância ofertados por instituições brasileiras no exterior
```

## Comparabilidade dos indicadores

### Indicadores comparáveis em todos os anos disponíveis

Com os arquivos atuais, é possível montar uma série histórica inicial com:

```text
ano
curso
IES
classificação de área
modalidade
grau acadêmico
categoria administrativa
organização acadêmica
matrículas
ingressantes
concluintes
vagas
inscritos, exceto 2017 no arquivo de curso atual
```

Nos anos antigos, os nomes das variáveis agregadas são diferentes:

| Conceito padronizado | 2017-2019 | 2022-2024 |
| --- | --- | --- |
| Matrículas | `QT_MATRICULA_TOTAL` | `QT_MAT` |
| Ingressantes | `QT_INGRESSO_TOTAL` | `QT_ING` |
| Concluintes | `QT_CONCLUINTE_TOTAL` | `QT_CONC` |
| Vagas | `QT_VAGA_TOTAL` | `QT_VG_TOTAL` |
| Inscritos | `QT_INSCRITO_TOTAL` em 2018/2019 | `QT_INSCRITO_TOTAL` |

### Indicadores de evasão/desvinculação

Nos anos de 2022 e 2024, a base de cursos já traz:

```text
QT_SIT_TRANCADA
QT_SIT_DESVINCULADO
QT_SIT_TRANSFERIDO
QT_SIT_FALECIDO
```

Nos anos de 2017, 2018 e 2019, os arquivos de curso disponíveis não trazem essas variáveis agregadas. Para analisar situação de vínculo nesses anos, é necessário processar os arquivos grandes de aluno:

```text
2017: DM_ALUNO.CSV, processado
2018: DM_ALUNO.CSV, processado
2019: SUP_ALUNO_2019.CSV, processado
```

O fluxo técnico está preparado e já foi executado para 2017, 2018 e 2019:

```bash
.venv/bin/python scripts/09_consolidar_alunos_quantitativo.py
.venv/bin/python scripts/10_mesclar_evasao_historico.py
```

Enquanto um arquivo de aluno não estiver em `data/raw/ANO/`, ou estiver vazio, esses scripts apenas sinalizam que a etapa daquele ano permanece pendente.

Validação atual da situação acadêmica:

| Ano | Origem da situação | Cursos com dado de aluno | Matrículas | Trancadas | Desvinculados | Transferidos | Falecidos | Desvinculados/matrículas |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | `DM_ALUNO.CSV` | 2.023 | 270.959 | 60.872 | 85.814 | 4.262 | 40 | 31,67% |
| 2018 | `DM_ALUNO.CSV` | 2.480 | 333.996 | 69.898 | 107.247 | 6.939 | 45 | 32,11% |
| 2019 | `SUP_ALUNO_2019.CSV` | 2.629 | 354.139 | 72.085 | 119.676 | 6.306 | 69 | 33,79% |
| 2022 | cadastro de cursos | 0 | 594.580 | 141.220 | 203.332 | 7.961 | 72 | 34,20% |
| 2024 | cadastro de cursos | 0 | 800.222 | 179.110 | 302.613 | 19.763 | 74 | 37,82% |

Em 2017, 2018 e 2019, `QT_MAT` bate com `QT_ALUNO_CURSANDO + QT_ALUNO_FORMADO`, e `QT_CONC` bate com `QT_ALUNO_FORMADO`, o que valida a agregação dos arquivos de aluno nesses anos.

## Auditoria do recorte de Computação/TIC

Para conferir se o filtro deixou cursos importantes para trás, foi criado:

```bash
.venv/bin/python scripts/11_auditar_recorte_computacao.py
```

O script procura, nos arquivos brutos de curso, registros que não estão na base comparável mas possuem termos de auditoria ligados a Computação/TIC em `NO_CURSO`, `NO_CINE_ROTULO`, `NO_CINE_AREA_DETALHADA`, `NO_OCDE` ou `NO_OCDE_AREA_DETALHADA`.

Saídas:

```text
data/processed/historico/auditoria_possiveis_cursos_fora_recorte.csv
data/processed/historico/auditoria_recorte_computacao_resumo.csv
```

Resumo atual:

| Ano | Candidatos fora do recorte | Cursos distintos | Nomes distintos |
| --- | ---: | ---: | ---: |
| 2017 | 576 | 576 | 36 |
| 2018 | 298 | 298 | 43 |
| 2019 | 326 | 326 | 43 |
| 2022 | 3.665 | 377 | 49 |
| 2024 | 5.578 | 502 | 54 |

Com o recorte oficial restrito à área geral 6 da CINE/CINE Brasil, a auditoria passa a listar cursos relacionados ou adjacentes que ficaram fora por pertencerem a outras áreas gerais, como Engenharia de Computação, Computação formação de professor, Matemática Computacional, Física Computacional, Informática em Saúde, Big Data no Agronegócio, áreas interdisciplinares e algumas engenharias com ênfase em computação.

## Prévia do recorte de Computação/TIC

Prévia calculada com os arquivos disponíveis e regras atuais:

| Ano | Registros no recorte expandido | Cursos distintos | IES distintas | Matrículas | Ingressantes | Concluintes | Vagas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.023 | 2.023 | 914 | 270.959 | 126.604 | 35.841 | 535.798 |
| 2018 | 2.480 | 2.480 | 985 | 333.996 | 163.672 | 43.562 | 790.522 |
| 2019 | 2.629 | 2.629 | 961 | 354.139 | 183.883 | 44.890 | 1.025.967 |
| 2022 | 55.007 | 3.341 | 942 | 594.580 | 410.454 | 61.760 | 2.298.785 |
| 2024 | 73.134 | 3.540 | 943 | 800.222 | 489.067 | 100.488 | 2.641.395 |

A diferença brusca de registros entre 2019 e 2022 não deve ser interpretada automaticamente como crescimento real de cursos. Ela reflete principalmente a mudança de estrutura dos microdados, especialmente na representação dos cursos EaD e na criação de `TP_DIMENSAO`.

Resumo histórico gerado pelo pipeline:

```text
data/processed/historico/resumo_historico_por_ano.csv
```

Nos arquivos de curso de 2017, 2018 e 2019, os campos `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO` e `QT_SIT_FALECIDO` não existem. Eles foram reconstruídos a partir dos arquivos de aluno e incorporados na base final `computacao_historico_com_evasao.csv`.

## Organização recomendada dos dados

Manter localmente:

```text
data/raw/ANO/
data/reference/inep/ANO/
```

Versionar no Git, se desejado:

```text
data/reference/inep/ANO/dicionario*
data/reference/inep/ANO/leia_me*
data/reference/inep/ANO/nota_informativa*
data/reference/inep/ANO/filtros*
```

Não versionar:

```text
data/raw/
data/processed/
data/reference/**/questionarios/
```

Os questionários podem ser descartados do projeto por enquanto. Eles ajudam a entender o preenchimento do Censo, mas não são necessários para o pipeline atual de microdados agregados por curso e IES.

## Próximas etapas técnicas

1. Usar a base expandida para desenhar os mapas e filtros geográficos no Power BI.
2. Usar a base comparável por curso para gráficos de série histórica e comparação entre anos.
3. Revisar os candidatos da auditoria apenas se o orientador quiser uma visão ampliada separada do recorte oficial.
4. Definir quais indicadores de evasão podem ser comparados apenas com curso/IES e quais exigem arquivos de aluno.
5. Decidir se os arquivos de docente entram como enriquecimento posterior.
