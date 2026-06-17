# Evasão em Cursos de Computação no Brasil

Este repositório reúne scripts, anotações e bases tratadas para o projeto **“Uma análise multifatorial e multi-institucional das causas de evasão nos cursos de Computação no Brasil”**.

O objetivo inicial é construir uma base consolidada sobre instituições brasileiras que ofertam cursos superiores de Computação, a partir dos Microdados do Censo da Educação Superior do INEP e, posteriormente, cruzar esses dados com fontes complementares, como dados da SBC, e-MEC e sites institucionais. O scraper previsto no plano de trabalho deve entrar como apoio para automatizar parte da coleta pública e complementar lacunas que não estejam estruturadas nas bases principais.

## Objetivo da etapa atual

A etapa atual consiste em entender, carregar, cruzar e validar os dados dos Microdados do Censo da Educação Superior, com análise detalhada de 2024 e integração histórica oficial para 2009 a 2024.

A planilha oficial começa em 2009 porque é o primeiro período em que a integração histórica fica metodologicamente compatível com o recorte adotado para Computação/TIC. Os microdados de 1995 a 2008 existem, mas usam estruturas e classificações antigas; por isso ficaram fora da base oficial atual.

Foram utilizados inicialmente dois arquivos principais:

* `MICRODADOS_CADASTRO_CURSOS_2024.CSV`: base de cursos superiores;
* `MICRODADOS_ED_SUP_IES_2024.CSV`: base de Instituições de Ensino Superior (IES).

Segundo o manual dos microdados de 2024, esses arquivos são disponibilizados em formato CSV, delimitados por ponto e vírgula (`;`), sendo um arquivo em nível de IES e outro em nível de curso. Os anos antigos usam estruturas diferentes, documentadas em `docs/02_decisoes_metodologicas.md`.

## Estrutura do projeto

```text
evasao-computacao/
├── data/
│   ├── raw/
│   │   ├── 2009/
│   │   ├── ...
│   │   └── 2024/
│   ├── processed/
│   │   ├── historico/
│   │   └── oficial/
│   └── reference/
├── docs/
│   ├── 01_visao_geral.md
│   ├── 02_decisoes_metodologicas.md
│   ├── 03_pipeline_e_reproducao.md
│   ├── 04_validacao_qualidade.md
│   ├── 05_dicionario_planilhas_finais.md
│   └── tecnico/
├── scripts/
│   ├── 01_entender_2024.py
│   ├── 02_abrir_base.py
│   ├── 03_diagnostico_2024.py
│   ├── 04_limpar_2024.py
│   ├── 05_resumir_2024.py
│   ├── 06_inventariar_bases.py
│   ├── 07_consolidar_historico_cursos.py
│   ├── 08_validar_historico.py
│   ├── 09_consolidar_alunos_quantitativo.py
│   ├── 10_mesclar_evasao_historico.py
│   ├── 11_auditar_recorte_computacao.py
│   ├── 12_gerar_planilha_oficial.py
│   ├── 13_inventariar_anos_antigos.py
│   └── 14_validar_planilha_oficial.py
├── requirements.txt
├── .gitignore
└── README.md
```

`data/raw/` guarda localmente os microdados e documentos de apoio baixados do INEP. A pasta não é versionada e, nesta etapa, deve conter apenas os anos usados na base oficial: 2009 a 2024.

`data/reference/` guarda dicionários, leia-me, filtros e notas informativas pequenos que ajudam a justificar decisões metodológicas. Esses arquivos são apoio documental, não entrada direta do pipeline.

`data/processed/oficial/` guarda as planilhas finais para análise e Power BI:

```text
planilha_oficial_computacao.csv
planilha_oficial_computacao_expandida.csv
dicionario_planilha_oficial.csv
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
pip install -r .\requirements.txt
```

Salvar dependências:

```bash
pip freeze > requirements.txt
```

## Scripts

### `01_entender_2024.py`

Carrega os arquivos de cursos e IES de 2024, cruza as bases por `NU_ANO_CENSO` e `CO_IES`, aplica o recorte oficial de Computação/TIC e gera arquivos em `data/processed/`.

O recorte atual inclui:

* cursos na área geral CINE de Computação e Tecnologias da Informação e Comunicação (TIC), registrada como `6` no arquivo do INEP;
* cursos com `CO_CINE_ROTULO = 0714E04`, rótulo de Engenharia de Computação.

Arquivo principal gerado:

```text
data/processed/computacao_2024_preliminar.csv
```

### `02_abrir_base.py`

Abre a base preliminar gerada e imprime informações iniciais, como tamanho da tabela, colunas e primeiras linhas.

Resultado obtido até o momento:

```text
76865 linhas x 37 colunas
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
docs/tecnico/analise_2024.md
```

### `06_inventariar_bases.py`

Inventaria os arquivos disponíveis em `data/raw/`, contando linhas e colunas, detectando delimitadores e comparando as colunas de cada ano com a estrutura de 2024. O script reconhece tanto o modelo novo (`MICRODADOS_CADASTRO_CURSOS` e `MICRODADOS_ED_SUP_IES`) quanto o modelo antigo (`DM_CURSO`, `SUP_CURSO`, `DM_IES`, `SUP_IES`, `DM_LOCAL_OFERTA`, `SUP_LOCAL_OFERTA`, tabelas CINE e OCDE).

Arquivos gerados:

```text
data/processed/inventario_bases_raw.csv
data/processed/comparacao_colunas_raw.csv
```

### `07_consolidar_historico_cursos.py`

Gera a base histórica expandida de cursos de Computação/TIC usando os anos disponíveis em `data/raw/`.

O recorte oficial inclui:

* `CO_CINE_AREA_GERAL = 6` nos anos com CINE/CINE Brasil;
* `CO_CINE_ROTULO = 0714E04` para incluir Engenharia de Computação;
* em 2017, `CO_OCDE_AREA_ESPECIFICA = 48` e `CO_OCDE = 5.23E+06` como aproximação histórica.

Arquivos gerados:

```text
data/processed/historico/computacao_historico_cursos.csv
data/processed/historico/resumo_historico_por_ano.csv
```

Essa base é indicada para mapa, dimensão geográfica, filtros e análises dinâmicas. Nos anos 2017-2019, os indicadores de desvinculação/trancamento são reconstruídos a partir dos arquivos de aluno pelos scripts `09` e `10`.

### `08_validar_historico.py`

Valida a duplicidade lógica da base histórica usando a chave `NU_ANO_CENSO + CO_IES + CO_CURSO`, cria uma base comparável com uma linha por curso e gera diagnósticos para evitar inflar contagens no Power BI.

Arquivos gerados:

```text
data/processed/historico/computacao_historico_cursos_comparavel.csv
data/processed/historico/validacao_historico_por_ano.csv
data/processed/historico/validacao_historico_metricas.csv
data/processed/historico/validacao_historico_dimensao_metricas.csv
data/processed/historico/validacao_linhas_por_curso.csv
data/processed/historico/validacao_top_cursos_multilinhas.csv
```

Uso recomendado:

```text
Base expandida: mapas, filtros geográficos e TP_DIMENSAO.
Base comparável: série histórica, contagem de cursos e comparação por curso/IES.
```

### `09_consolidar_alunos_quantitativo.py`

Processa os arquivos grandes de aluno quando eles existem em `data/raw/ANO/`.

O script procura arquivos como `DM_ALUNO.CSV`, `SUP_ALUNO_2019.CSV` ou `MICRODADOS_CADASTRO_ALUNOS_ANO.CSV`, filtra apenas cursos de Computação/TIC pela chave `NU_ANO_CENSO + CO_IES + CO_CURSO` e agrega as situações de vínculo.

Arquivo gerado:

```text
data/processed/historico/alunos_computacao_quantitativo.csv
```

### `10_mesclar_evasao_historico.py`

Mescla a base comparável de cursos com os quantitativos derivados dos arquivos de aluno. A ideia é preencher situação acadêmica de 2017-2019 quando os arquivos de aluno forem processados, mantendo os agregados oficiais já existentes nos cadastros de curso dos demais anos.

Arquivos gerados:

```text
data/processed/historico/computacao_historico_com_evasao.csv
data/processed/historico/validacao_evasao_alunos_vs_cursos.csv
```

Atualmente, 2017, 2018 e 2019 já foram processados a partir dos arquivos de aluno.

### `11_auditar_recorte_computacao.py`

Audita o recorte de Computação/TIC procurando, nos arquivos brutos de curso, registros com termos ligados a Computação/TIC que não entraram na base comparável.

Arquivos gerados:

```text
data/processed/historico/auditoria_possiveis_cursos_fora_recorte.csv
data/processed/historico/auditoria_recorte_computacao_resumo.csv
```

Essa auditoria não altera a base automaticamente. Ela serve para revisar possíveis cursos deixados fora do recorte e documentar decisões metodológicas.

### `12_gerar_planilha_oficial.py`

Gera as planilhas oficiais a partir das bases histórica, comparável e com situação acadêmica.

Arquivos gerados:

```text
data/processed/oficial/planilha_oficial_computacao.csv
data/processed/oficial/planilha_oficial_computacao_expandida.csv
data/processed/oficial/dicionario_planilha_oficial.csv
```

### `13_inventariar_anos_antigos.py`

Utilitário opcional para inventariar os anos 1995-2008, caso esses microdados sejam recolocados em `data/raw/` no futuro. Esses anos usam estruturas anteriores ao recorte CINE atual e não fazem parte da planilha oficial.

Arquivo gerado:

```text
data/processed/historico/inventario_anos_antigos_1995_2008.csv
```

### `14_validar_planilha_oficial.py`

Valida a planilha oficial antes do Power BI. O script checa duplicatas, nulos críticos, recorte oficial, métricas negativas, colunas sensíveis e consistência entre a planilha comparável e a expandida.

Arquivos gerados:

```text
data/processed/validacao_oficial/01_resumo_geral.csv
data/processed/validacao_oficial/02_duplicatas_chave.csv
data/processed/validacao_oficial/03_nulos_colunas_criticas.csv
data/processed/validacao_oficial/04_instituicoes_nomes_conflitantes.csv
data/processed/validacao_oficial/05_cursos_nomes_conflitantes.csv
data/processed/validacao_oficial/06_recorte_cine_invalido.csv
data/processed/validacao_oficial/07_metricas_negativas_ou_estranhas.csv
data/processed/validacao_oficial/08_colunas_sensiveis_detectadas.csv
data/processed/validacao_oficial/09_comparacao_oficial_vs_expandida.csv
data/processed/validacao_oficial/relatorio_validacao_oficial.md
```

## Integração histórica

Além da análise de 2024, o projeto já integra oficialmente os anos 2009 a 2024.

Documentos principais:

```text
docs/01_visao_geral.md
docs/02_decisoes_metodologicas.md
docs/03_pipeline_e_reproducao.md
docs/04_validacao_qualidade.md
docs/05_dicionario_planilhas_finais.md
```

Resumo das estruturas atuais:

```text
1995-2008: fora da planilha oficial atual
2009-2016: cadastro de cursos + cadastro de IES, CINE
2017: modelo antigo, OCDE/proxy histórico
2018-2019: modelo antigo, CINE Brasil
2020-2024: cadastro de cursos + IES, CINE
```

Os arquivos de aluno (`DM_ALUNO`/`SUP_ALUNO_2019`) não são necessários para montar o panorama histórico por curso e IES, mas são importantes para aprofundar a análise de situação de vínculo/evasão nos anos antigos. Os scripts `09` e `10` já processaram 2017, 2018 e 2019.

Após a consolidação, o projeto separa duas bases:

```text
data/processed/historico/computacao_historico_cursos.csv
data/processed/historico/computacao_historico_cursos_comparavel.csv
```

A primeira é expandida por localização/dimensão e deve alimentar mapas. A segunda possui uma linha por `NU_ANO_CENSO + CO_IES + CO_CURSO` e deve ser usada para comparação histórica por curso/IES.

## Recorte de Computação/TIC

O filtro principal usa a classificação oficial CINE/CINE Brasil.

```text
2009-2016 e 2020-2024: CO_CINE_AREA_GERAL = 6 ou CO_CINE_ROTULO = 0714E04.
2018/2019: CO_CINE_AREA_GERAL = 06 ou CO_CINE_ROTULO = 0714E04.
2017: CO_OCDE_AREA_ESPECIFICA = 48 ou CO_OCDE = 5.23E+06.
```

Nos anos com a coluna disponível, o pipeline filtra graduação por `TP_NIVEL_ACADEMICO = 1` e exclui ABI por `TP_ATRIBUTO_INGRESSO <> 1`, preservando valores ausentes.

`0714E04` é o rótulo CINE de Engenharia de Computação. Em 2017, `5.23E+06` funciona como aproximação histórica no padrão OCDE.

A lista detalhada de validações e candidatos fora do recorte oficial está documentada em:

```text
docs/02_decisoes_metodologicas.md
docs/04_validacao_qualidade.md
```

## Resultados preliminares de 2024

A execução atual gerou uma base preliminar com:

```text
76865 registros
37 colunas
```

E uma base tratada com:

```text
76865 registros
44 colunas
3894 cursos distintos
977 IES distintas
```

Distribuição por `TP_DIMENSAO`:

```text
2    72915
1     2594
3     1300
4       56
```

Distribuição por modalidade:

```text
TP_MODALIDADE_ENSINO = 2    74271
TP_MODALIDADE_ENSINO = 1     2594
```

Critérios de entrada no recorte:

```text
CINE área geral 6 Computação/TIC                73134
CINE rótulo 0714E04 Engenharia de Computação     3731
```

Indicadores agregados na base tratada:

```text
Vagas: 2.739.900
Inscritos: 1.513.815
Ingressantes: 509.828
Matriculados: 860.791
Concluintes: 106.157
Matrículas trancadas: 188.392
Desvinculados: 315.838
Transferidos: 23.294
Falecidos: 84
```

Principais nomes de curso identificados:

```text
Análise E Desenvolvimento De Sistemas         14013
Gestão Da Tecnologia Da Informação             8597
Engenharia De Software                         7119
Redes De Computadores                          5125
Sistemas De Informação                         4909
Ciência Da Computação                          3781
Engenharia De Computação                       3651
Sistemas Para Internet                          3037
Jogos Digitais                                  2855
Ciência De Dados                                2813
Segurança Da Informação                         2417
Banco De Dados                                 1950
Ciências Da Computação                         1906
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
Inteligência artificial                    1222
```

## Pontos de atenção

A variável `CO_CINE_ROTULO` deve ser tratada como texto, pois pode ser interpretada incorretamente por planilhas eletrônicas, especialmente quando contém a letra `E`. A base tratada já remove aspas literais dos códigos CINE, mantendo valores como `0613S01`.

A variável `TP_DIMENSAO` precisa ser considerada com cuidado nas análises geográficas, pois cursos EaD podem aparecer com diferentes níveis de agregação territorial. Em especial, registros com `TP_DIMENSAO = 3` representam cursos EaD com dados somente em nível Brasil, sem detalhamento por UF ou município.

Os registros com `IN_USAR_MAPA_MUNICIPAL = True` podem alimentar mapas municipais. Registros nacionais ou no exterior devem ser usados em indicadores agregados, sem forçar localização municipal.

Os indicadores `QT_SIT_DESVINCULADO` e `QT_SIT_TRANCADA` já foram incorporados, mas a razão `desvinculados/matriculados` deve ser tratada como indicador exploratório, não como taxa final de evasão. A taxa final depende da modelagem histórica e da definição metodológica que será adotada no projeto.

## Próximos passos

1. Preparar tabelas e medidas no Power BI usando a base correta para cada visual.
2. Revisar candidatos ambíguos da auditoria do recorte, se o orientador quiser ajustar o escopo.
3. Preparar a estrutura de cruzamento com dados da SBC e do e-MEC.
4. Identificar quais campos precisarão de scraper ou coleta complementar.
5. Decidir se os arquivos de docente entram como enriquecimento posterior.
