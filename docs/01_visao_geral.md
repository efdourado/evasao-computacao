# Visão geral da base oficial

## Objetivo

O projeto organiza os Microdados do Censo da Educação Superior do INEP em uma base histórica de cursos de Computação/TIC, instituições e indicadores acadêmicos.

As fontes efetivamente processadas são os arquivos do Censo e suas tabelas
auxiliares. Uma extração própria do cadastro e-MEC ou um cruzamento independente
com tabelas do IBGE não integra o processamento documentado nesta versão.

A planilha oficial atual cobre **2009 a 2024**. O resultado principal possui uma linha por:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

## Recorte de Computação/TIC

Nos anos com CINE ou CINE Brasil, o curso entra quando atende a pelo menos uma regra:

```text
CO_CINE_AREA_GERAL = 6
CO_CINE_ROTULO = 0714E04
```

A primeira regra seleciona a área geral **Computação e Tecnologias da Informação e Comunicação (TIC)**. A segunda inclui **Engenharia de Computação**, classificada fora da área geral 6.

O processamento também seleciona nível acadêmico de graduação e filtra ABI
(Área Básica de Ingresso) pelo atributo de ingresso ou pelo nome explícito.
Os 11 registros de cursos interdisciplinares foram mantidos. A retirada anterior
de quatro registros ABI e a ressalva sobre essa decisão estão registradas na
[curadoria](04_curadoria_e_inconsistencias.md). A vistoria atual preserva a base
recebida, sem ampliar ou reduzir novamente o recorte.

### Onde conferir

| Período | Arquivo de curso | Classificação consultada |
| --- | --- | --- |
| 2009-2016 | `data/raw/ANO/dados/MICRODADOS_CADASTRO_CURSOS_ANO.CSV` | campos CINE do próprio arquivo |
| 2017 | `DM_CURSO.CSV` | `TB_AUX_AREA_OCDE.CSV` |
| 2018 | `DM_CURSO.CSV` | `TB_AUX_CINE_BRASIL.CSV` |
| 2019 | `SUP_CURSO_2019.CSV` | `TB_AUX_CINE_BRASIL_2019.CSV` |
| 2020-2024 | `MICRODADOS_CADASTRO_CURSOS_ANO.CSV` | campos CINE do próprio arquivo |

Nos arquivos recentes, os campos principais para conferência são:

```text
CO_CINE_AREA_GERAL
NO_CINE_AREA_GERAL
CO_CINE_ROTULO
NO_CINE_ROTULO
```

### Rótulos da área geral 6 presentes na série

A base oficial contém os seguintes rótulos CINE associados à área geral 6. Alguns nomes aparecem em códigos diferentes porque a classificação foi atualizada ao longo dos anos.

| Código | Rótulo |
| --- | --- |
| `0612B01` | Banco de dados |
| `0612D01` | Defesa cibernética |
| `0612G01` | Gestão da tecnologia da informação |
| `0612R01` | Redes de computadores |
| `0612S01` | Segurança da informação |
| `0613C01` | Ciência da computação |
| `0613E01` | Engenharia de software |
| `0613I01` | Inteligência artificial |
| `0613I02` | Internet das coisas |
| `0613J01` | Jogos digitais |
| `0613S01` | Sistemas de informação |
| `0613S02` | Sistemas para internet |
| `0614C01` | Ciência da computação |
| `0614I01` | Inteligência artificial |
| `0615S01` | Segurança da informação |
| `0615S02` | Sistemas de informação |
| `0615S03` | Sistemas para internet |
| `0616E01` | Engenharia de computação (DCN Computação) |
| `0616I01` | Internet das coisas |
| `0616S01` | Sistemas embarcados |
| `0617A01` | Agrocomputação |
| `0617C01` | Ciência de dados |
| `0617C02` | Computação/TIC em biociências e saúde |
| `0617C03` | Criação digital |
| `0619P01` | Programas de Computação/TIC em definição de classificação |
| `0681A01` | Agrocomputação |
| `0681C01` | Ciência de dados |
| `0681C02` | Computação/TIC em biociências e saúde |
| `0681C03` | Criação digital |
| `0681J01` | Jogos digitais |
| `0688P01` | Programas interdisciplinares de Computação/TIC |

Essa lista registra os rótulos encontrados nos dados de 2009 a 2024. Ela não substitui o manual CINE Brasil.

### Engenharia de Computação

O rótulo adicional é:

```text
0714E04 - Engenharia de Computação
```

Ele é selecionado individualmente porque pertence à área geral 7, mas foi incluído no escopo por decisão metodológica do projeto.

## Aproximação de 2017

O ano de 2017 usa a classificação OCDE, não CINE. Para aproximar o mesmo universo, foram selecionados:

```text
CO_OCDE_AREA_ESPECIFICA = 48
ou
CO_OCDE = 5.23E+06
```

Na área específica 48 aparecem:

| Código | Rótulo OCDE |
| --- | --- |
| `481A01` | Administração de redes |
| `481B01` | Banco de dados |
| `481C01` | Ciência da computação |
| `481I01` | Informática (ciência da computação) |
| `481T01` | Tecnologia da informação |
| `481T02` | Tecnologia em desenvolvimento de softwares |
| `482U01` | Uso da internet |
| `483A01` | Análise de sistemas |
| `483A02` | Análise e Desenvolvimento de Sistemas |
| `483S01` | Segurança da informação |
| `483S02` | Sistemas de informação |

O valor bruto `5.23E+06` é a serialização de `523E04`, rótulo OCDE de
Engenharia de Computação. A planilha oficial expõe o código normalizado
`523E04`. Esse proxy recupera 269 linhas: 229 chamadas Engenharia de
Computação, 36 Engenharia de Software e 4 cursos relacionados.

Por isso, 2017 permanece na série, mas recebe:

```text
DS_CLASSIFICACAO_AREA = OCDE
DS_NIVEL_COMPARABILIDADE = media_ocde_proxy
```

Ele é comparável por aproximação, não por equivalência perfeita de classificação.

## Por que 1995-2008 ficaram fora

Os anos anteriores foram examinados, mas não possuem os campos usados na regra atual. Em vez de `CO_CINE_AREA_GERAL` e `CO_CINE_ROTULO`, aparecem estruturas como:

```text
GRADUACAO_PRESENCIAL.CSV
GRADUACAO_DISTANCIA.CSV
AREACURSO
NO_AREA_CONHE
NO_CURSO_HABILITACAO
```

Também aparecem nomenclaturas históricas como Informática, Processamento de Dados e Análise de Sistemas. Um filtro apenas por nome poderia incluir cursos indevidos ou deixar cursos válidos de fora.

Integrar 1995-2008 exigiria uma etapa própria:

1. interpretar os dicionários de cada estrutura;
2. mapear códigos antigos de área;
3. criar equivalências entre nomes históricos e a classificação atual;
4. validar presencial e EaD entre modelos diferentes;
5. documentar o grau de comparabilidade de cada ano.

Assim, 2009 é o início da série oficial atual. Os anos anteriores não foram considerados equivalentes automaticamente.

## As três planilhas finais

### Planilha principal

`planilha_oficial_computacao.csv` é a base recomendada para séries históricas, contagem de cursos e análises por instituição.

Ela possui **43.477 linhas** e uma única linha por ano + IES + curso. Quando o arquivo original traz o curso dividido por municípios ou localidades, as métricas são somadas nessa chave e as localizações são resumidas em colunas como `QT_UFS_DISTINTAS` e `SG_UF_LISTA`.

### Planilha expandida

`planilha_oficial_computacao_expandida.csv` possui **315.410 linhas** porque preserva as linhas territoriais dos arquivos originais.

Um curso EaD pode aparecer uma vez para cada município associado. A planilha
não possui identificador de polo físico. Um mesmo curso pode ter centenas de
linhas territoriais e continuar sendo apenas um curso na principal.

A expandida serve para:

```text
mapas por UF ou município
filtros por TP_DIMENSAO
análises territoriais de ingressantes, matrículas e concluintes
```

Em EaD, vagas e inscritos ficam na linha nacional e não podem ser distribuídos
por município.

Ela não deve ser usada para contar cursos pela quantidade de linhas. No Power BI, deve ser relacionada à principal por:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

### Dicionário

`dicionario_planilha_oficial.csv` descreve cada coluna e informa em qual planilha ela aparece.

## Informações acadêmicas

Dependendo do ano, a base contém vagas, inscritos, ingressantes, matrículas, concluintes, trancados, desvinculados, transferidos e falecidos.

As situações acadêmicas vêm de:

| Anos | Fonte |
| --- | --- |
| 2009-2016 | cadastro de cursos |
| 2017-2019 | arquivos grandes de aluno |
| 2020-2024 | cadastro de cursos |

Esses dados ainda não formam uma taxa definitiva de evasão. A antiga razão `desvinculados/matrículas` foi retirada da planilha oficial porque compara um fluxo anual com um estoque e pode produzir valores acima de 1. Permanecem os valores originais para uma definição metodológica posterior.
