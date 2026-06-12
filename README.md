# Evasão em Cursos de Computação no Brasil

Este repositório reúne scripts, anotações e bases tratadas para o projeto **“Uma análise multifatorial e multi-institucional das causas de evasão nos cursos de Computação no Brasil”**.

O objetivo inicial é construir uma base consolidada sobre instituições brasileiras que ofertam cursos superiores de Computação, a partir dos Microdados do Censo da Educação Superior do INEP e, posteriormente, cruzar esses dados com fontes complementares, como dados da SBC, e-MEC e sites institucionais. O scraper previsto no plano de trabalho deve entrar como apoio para automatizar parte da coleta pública e complementar lacunas que não estejam estruturadas nas bases principais.

## Objetivo da etapa atual

A etapa atual consiste em entender, carregar, cruzar e validar os dados de 2024 dos Microdados do Censo da Educação Superior.

Foram utilizados inicialmente dois arquivos principais:

* `MICRODADOS_CADASTRO_CURSOS_2024.CSV`: base de cursos superiores;
* `MICRODADOS_ED_SUP_IES_2024.CSV`: base de Instituições de Ensino Superior (IES).

Segundo o manual dos microdados, esses arquivos são disponibilizados em formato CSV, delimitados por ponto e vírgula (`;`), sendo um arquivo em nível de IES e outro em nível de curso.

## Estrutura do projeto

```text
evasao-computacao/
├── data/
│   ├── raw/
│   │   └── 2024/
│   │       ├── MICRODADOS_CADASTRO_CURSOS_2024.CSV
│   │       ├── MICRODADOS_ED_SUP_IES_2024.CSV
│   │       └── MICRODADOS_LICENCIATURA.xlsx
│   └── processed/
├── docs/
│   ├── 01_entendimento_dados.md
│   └── 02_analise_2024.md
├── scripts/
│   ├── 01_entender_2024.py
│   ├── 02_abrir_base.py
│   ├── 03_diagnostico_2024.py
│   ├── 04_limpar_2024.py
│   ├── 05_resumir_2024.py
│   └── 06_inventariar_bases.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Configuração do ambiente

Criar ambiente virtual:

```bash
python -m venv .venv
```

Ativar o ambiente virtual no Linux/macOS:

```bash
source .venv/bin/activate
```

Ativar o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

Instalar dependências:

```bash
pip install pandas openpyxl
```

Salvar dependências:

```bash
pip freeze > requirements.txt
```

## Scripts

### `01_entender_2024.py`

Carrega os arquivos de cursos e IES de 2024, cruza as bases por `NU_ANO_CENSO` e `CO_IES`, aplica um recorte provisório de Computação/TIC e gera arquivos em `data/processed/`.

O recorte atual inclui:

* cursos na área geral CINE de Computação e Tecnologias da Informação e Comunicação (TIC), registrada como `6` no arquivo do INEP;
* cursos com rótulo CINE `Computação formação de professor`;
* cursos identificados por nome/rótulo como `Engenharia de Computação`.

Arquivo principal gerado:

```text
data/processed/computacao_2024_preliminar.csv
```

### `02_abrir_base.py`

Abre a base preliminar gerada e imprime informações iniciais, como tamanho da tabela, colunas e primeiras linhas.

Resultado obtido até o momento:

```text
78657 linhas x 37 colunas
```

### `03_diagnostico_2024.py`

Gera diagnósticos sobre a base preliminar, incluindo:

* valores ausentes por coluna;
* distribuição por `TP_DIMENSAO`;
* distribuição por UF;
* distribuição por modalidade;
* distribuição por grau acadêmico;
* principais nomes de curso;
* principais rótulos CINE;
* verificação de duplicados.

Arquivos gerados:

```text
data/processed/diagnostico_ausentes.csv
data/processed/diagnostico_tp_dimensao.csv
data/processed/diagnostico_top_cursos.csv
data/processed/diagnostico_top_cine.csv
```

### `04_limpar_2024.py`

Gera uma versão tratada da base preliminar, com ajustes como:

* remoção de espaços extras;
* limpeza de aspas literais em códigos CINE;
* conversão de indicadores numéricos;
* preservação da hierarquia CINE;
* criação de colunas de escopo e critério de entrada;
* inclusão de indicadores de situação acadêmica, como trancados e desvinculados;
* criação de rótulos para `TP_DIMENSAO`;
* criação de colunas indicando se o registro possui localização do curso e se pode ser usado em mapa municipal;
* reorganização das colunas principais.

Arquivo esperado:

```text
data/processed/computacao_2024_tratada.csv
```

### `05_resumir_2024.py`

Gera tabelas-resumo finais de 2024 e um relatório curto da análise.

Arquivos principais gerados:

```text
data/processed/resumos_2024/resumo_geral_2024.csv
data/processed/resumos_2024/resumo_por_dimensao_2024.csv
data/processed/resumos_2024/resumo_por_modalidade_2024.csv
data/processed/resumos_2024/resumo_por_cine_rotulo_2024.csv
data/processed/resumos_2024/resumo_por_uf_curso_mapa_2024.csv
data/processed/resumos_2024/resumo_por_ies_2024.csv
docs/02_analise_2024.md
```

### `06_inventariar_bases.py`

Inventaria os arquivos disponíveis em `data/raw/`, contando linhas e colunas, e compara as colunas de cada ano com a estrutura de 2024.

Arquivos gerados:

```text
data/processed/inventario_bases_raw.csv
data/processed/comparacao_colunas_raw.csv
```

## Resultados preliminares de 2024

A execução atual gerou uma base preliminar com:

```text
78657 registros
37 colunas
```

E uma base tratada com:

```text
78657 registros
44 colunas
3987 cursos distintos
977 IES distintas
```

Distribuição por `TP_DIMENSAO`:

```text
2    74614
1     2652
3     1335
4       56
```

Distribuição por modalidade:

```text
TP_MODALIDADE_ENSINO = 2    76005
TP_MODALIDADE_ENSINO = 1     2652
```

Critérios de entrada no recorte:

```text
CINE área geral Computação/TIC                  73134
Nome/rótulo Engenharia de Computação             3731
CINE rótulo Computação formação de professor     1792
```

Indicadores agregados na base tratada:

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

Principais nomes de curso identificados:

```text
Análise E Desenvolvimento De Sistemas         14013
Gestão Da Tecnologia Da Informação             8597
Engenharia De Software                         7119
Redes De Computadores                          5125
Sistemas De Informação                         4909
Ciência Da Computação                          4019
Engenharia De Computação                       3651
Sistemas Para Internet                          3037
Jogos Digitais                                  2855
Ciência De Dados                                2813
Segurança Da Informação                         2417
Banco De Dados                                 1950
Ciências Da Computação                         1908
Segurança Cibernética                          1152
Defesa Cibernética                             1074
Cibersegurança                                 1072
```

Principais rótulos CINE identificados:

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
```

## Pontos de atenção

A variável `CO_CINE_ROTULO` deve ser tratada como texto, pois pode ser interpretada incorretamente por planilhas eletrônicas, especialmente quando contém a letra `E`. A base tratada já remove aspas literais dos códigos CINE, mantendo valores como `0613S01`.

A variável `TP_DIMENSAO` precisa ser considerada com cuidado nas análises geográficas, pois cursos EaD podem aparecer com diferentes níveis de agregação territorial. Em especial, registros com `TP_DIMENSAO = 3` representam cursos EaD com dados somente em nível Brasil, sem detalhamento por UF ou município.

Os registros com `IN_USAR_MAPA_MUNICIPAL = True` podem alimentar mapas municipais. Registros nacionais ou no exterior devem ser usados em indicadores agregados, sem forçar localização municipal.

Os indicadores `QT_SIT_DESVINCULADO` e `QT_SIT_TRANCADA` já foram incorporados, mas a razão `desvinculados/matriculados` deve ser tratada como indicador exploratório, não como taxa final de evasão. A taxa final depende da modelagem histórica e da definição metodológica que será adotada no projeto.

## Próximos passos

1. Repetir o pipeline para 2022, 2019, 2018 e 2017.
2. Padronizar as colunas entre os anos.
3. Construir a base histórica consolidada.
4. Preparar a estrutura de cruzamento com dados da SBC e do e-MEC.
5. Identificar quais campos precisarão de scraper ou coleta complementar.
6. Preparar indicadores e filtros para visualização dinâmica em BI.
