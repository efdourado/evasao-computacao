# Entendimento inicial das bases do INEP

## Contexto

O projeto utiliza os Microdados do Censo da Educação Superior para mapear cursos superiores de Computação no Brasil. A primeira etapa está focada no ano de 2024, com posterior expansão para anos anteriores.

O professor compartilhou pastas com dados de diferentes anos, incluindo 2017, 2018, 2019, 2022 e 2024. Cada pasta contém, em geral:

* dados;
* leia-me;
* anexos;
* dicionário de dados;
* questionários do Censo da Educação Superior.

## Fontes usadas em 2024

Foram usados dois arquivos principais dos microdados do INEP:

```text
MICRODADOS_CADASTRO_CURSOS_2024.CSV
MICRODADOS_ED_SUP_IES_2024.CSV
```

Os arquivos CSV são delimitados por ponto e vírgula (`;`) e foram carregados no Pandas com `encoding="latin1"` e `dtype=str`, para evitar perda de códigos identificadores.

## Chaves principais

O cruzamento inicial entre cursos e IES foi feito por:

```text
NU_ANO_CENSO
CO_IES
```

A variável `CO_IES` identifica a instituição e permite conectar a base de cursos com a base de IES.

## Recorte provisório de Computação

O filtro inicial por termos no nome do curso foi substituído por uma regra mais estável, baseada principalmente na classificação CINE:

1. cursos na área geral CINE de Computação e Tecnologias da Informação e Comunicação (TIC), registrada como `6` no arquivo do INEP;
2. cursos com rótulo CINE `Computação formação de professor`;
3. cursos identificados por nome ou rótulo como `Engenharia de Computação`.

Essa regra é provisória, mas é mais defensável que uma busca ampla por palavras, pois inclui cursos como Ciência de Dados, Sistemas para Internet, Jogos Digitais, Segurança da Informação e Inteligência Artificial.

## Bases geradas

A base preliminar atual foi gerada em:

```text
data/processed/computacao_2024_preliminar.csv
```

Resultado:

```text
78657 linhas
37 colunas
3987 cursos distintos
977 IES distintas
```

A base tratada foi gerada em:

```text
data/processed/computacao_2024_tratada.csv
```

Resultado:

```text
78657 linhas
44 colunas
```

## Colunas principais da base tratada

```text
NU_ANO_CENSO
CO_IES
NO_IES
SG_IES
TP_REDE
TP_CATEGORIA_ADMINISTRATIVA
TP_ORGANIZACAO_ACADEMICA
CO_CURSO
NO_CURSO
NO_CURSO_NORMALIZADO
IN_ESCOPO_COMPUTACAO
DS_CRITERIO_ESCOPO
CO_CINE_ROTULO
NO_CINE_ROTULO
NO_CINE_ROTULO_NORMALIZADO
CO_CINE_AREA_GERAL
NO_CINE_AREA_GERAL
CO_CINE_AREA_ESPECIFICA
NO_CINE_AREA_ESPECIFICA
CO_CINE_AREA_DETALHADA
NO_CINE_AREA_DETALHADA
TP_GRAU_ACADEMICO
TP_MODALIDADE_ENSINO
DS_TP_MODALIDADE_ENSINO
TP_DIMENSAO
DS_TP_DIMENSAO
DS_NIVEL_GEOGRAFICO
IN_TEM_LOCALIZACAO_CURSO
IN_USAR_MAPA_MUNICIPAL
NO_REGIAO
SG_UF
NO_MUNICIPIO
NO_REGIAO_IES
SG_UF_IES
NO_MUNICIPIO_IES
QT_VG_TOTAL
QT_INSCRITO_TOTAL
QT_ING
QT_MAT
QT_CONC
QT_SIT_TRANCADA
QT_SIT_DESVINCULADO
QT_SIT_TRANSFERIDO
QT_SIT_FALECIDO
```

## Diagnóstico inicial

### Critério de entrada no recorte

```text
CINE área geral Computação/TIC                  73134
Nome/rótulo Engenharia de Computação             3731
CINE rótulo Computação formação de professor     1792
```

### Valores ausentes

A coluna com maior quantidade de valores ausentes foi:

```text
SG_IES: 7912 ausentes
```

As colunas de localização do curso apresentaram valores ausentes em 1391 registros:

```text
NO_MUNICIPIO
SG_UF
NO_REGIAO
```

Esses valores ausentes estão relacionados principalmente à forma como cursos EaD nacionais e cursos no exterior são representados nos microdados.

### Distribuição por TP_DIMENSAO

```text
2    74614
1     2652
3     1335
4       56
```

Interpretação usada na base tratada:

* `1`: curso presencial com localização municipal;
* `2`: curso EaD com localização municipal/polo;
* `3`: curso EaD com informação apenas nacional;
* `4`: curso EaD no exterior.

### Modalidade

```text
2    76005
1     2652
```

A base é majoritariamente composta por registros EaD.

### Grau acadêmico

```text
3    54339
1    22526
2     1792
```

Esses códigos ainda podem receber rótulos descritivos com apoio do dicionário de dados.

### Indicadores agregados

```text
Vagas: 2.776.208
Inscritos: 1.532.590
Ingressantes: 514.619
Matriculados: 871.845
Concluintes: 107.078
Matrículas trancadas: 190.893
Desvinculados: 320.211
Transferidos: 23.433
Falecidos: 85
```

A razão `desvinculados/matriculados` em 2024 fica em aproximadamente 36,73%. Esse valor deve ser tratado como indicador exploratório, não como taxa final de evasão, porque a metodologia definitiva depende da modelagem histórica e da validação conceitual do projeto.

## Principais cursos capturados

```text
Análise E Desenvolvimento De Sistemas           14013
Gestão Da Tecnologia Da Informação               8597
Engenharia De Software                           7119
Redes De Computadores                            5125
Sistemas De Informação                           4909
Ciência Da Computação                            4019
Engenharia De Computação                         3651
Sistemas Para Internet                           3037
Jogos Digitais                                   2855
Ciência De Dados                                 2813
Segurança Da Informação                          2417
Banco De Dados                                   1950
Ciências Da Computação                           1908
Segurança Cibernética                            1152
Defesa Cibernética                               1074
Cibersegurança                                   1072
```

## Principais CINEs capturados

```text
Sistemas de informação                    20334
Gestão da tecnologia da informação         9178
Engenharia de software                     7807
Ciência da computação                      5695
Redes de computadores                      5125
Ciência de dados                           5005
Defesa cibernética                         3895
Sistemas para internet                     3740
Engenharia de computação                   3731
Jogos digitais                             2982
Banco de dados                             2817
Segurança da informação                    2419
Computação formação de professor           1792
Inteligência artificial                    1222
```

## Pontos de atenção

### 1. Unidade de análise

Os registros dos microdados não devem ser interpretados automaticamente como uma linha por curso único. O mesmo `CO_CURSO` pode aparecer em diferentes recortes territoriais, especialmente no EaD. Para contar cursos distintos, deve-se usar `CO_CURSO` ou `CO_IES + CO_CURSO`, conforme o indicador desejado.

### 2. Cursos EaD e localização

Registros com `TP_DIMENSAO = 1` ou `TP_DIMENSAO = 2` possuem localização do curso e podem alimentar mapas municipais.

Registros com `TP_DIMENSAO = 3` têm informação apenas nacional e devem ser usados em indicadores agregados. Eles não devem ser forçados para UF ou município.

Registros com `TP_DIMENSAO = 4` representam EaD no exterior e também devem ser tratados separadamente.

### 3. Códigos CINE

A variável `CO_CINE_ROTULO` deve permanecer como texto para evitar erros de interpretação em planilhas eletrônicas. A base tratada já remove aspas literais dos códigos, mantendo valores como `0613S01`.

### 4. Indicadores de evasão

As colunas `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO` e `QT_SIT_FALECIDO` foram incorporadas à base tratada. Elas permitem uma primeira leitura sobre permanência e desligamento, mas ainda precisam ser analisadas com cuidado antes de virar um indicador final de evasão.

### 5. Cruzamentos externos

A leitura atual é que os dados do INEP serão usados como base estruturada inicial e depois cruzados com SBC, e-MEC e outras fontes quando necessário. O scraper entra como apoio para automatizar parte da coleta pública e complementar campos que não estiverem estruturados.

## Próxima etapa prática

As próximas tarefas são:

* preparar dimensões de curso, IES, localização, modalidade e CINE;
* usar as tabelas-resumo de `data/processed/resumos_2024/` como base inicial para Power BI;
* levantar quais campos virão da SBC, do e-MEC e de coleta complementar;
* repetir o pipeline para os anos anteriores disponíveis;
* documentar decisões de modelagem para a base histórica.
