# Etapa 1: dados do INEP e recorte

O projeto segue um fluxo em três etapas, cada uma com um documento:

| Etapa | O que faz | Documento |
| --- | --- | --- |
| 1. Recorte | Pega os microdados do INEP e seleciona os cursos de Computação/TIC | este documento |
| 2. Curadoria | Examina o recorte em busca de valores e classificações suspeitos | [02_curadoria.md](02_curadoria.md) |
| 3. Manual de uso | Decide como cada achado afeta cada análise e entrega tabelas prontas com flags | [03_manual_de_uso.md](03_manual_de_uso.md) |

Este documento cobre a etapa 1: de onde vêm os dados, quais regras definem o
recorte, como são as planilhas oficiais, como validá-las e como reproduzir tudo.

## Objetivo e fonte

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
(Área Básica de Ingresso) pelo atributo de ingresso ou pelo nome explícito. O
segundo critério existe porque o arquivo bruto do INEP nem sempre marca o
atributo de ingresso corretamente: em 2012–2014, o curso 5.000.758 (Faculdade
de Tecnologia de São Caetano do Sul) aparecia como "ABI - Sistemas de
Informação" sem esse atributo preenchido, e em 2023 o curso 50.017.083 (ITA)
aparecia como "Abi - Engenharia" do mesmo jeito. Os dois foram retirados do
recorte pelo filtro por nome. O primeiro volta a aparecer a partir de 2015,
quando a mesma instituição passa a declarar o mesmo código de curso como um
Tecnólogo comum em Sistemas de Informação, sem o prefixo ABI.

Os 11 registros de cursos interdisciplinares, por outro lado, foram mantidos:
eles têm área geral de Computação/TIC e nome próprio (não usam "ABI" nem
"Área Básica de Ingresso"), então não se encaixam na regra de exclusão. A
vistoria atual preserva essa decisão de escopo, sem ampliar ou reduzir
novamente o recorte; achados sobre a confiabilidade dos valores dentro do
recorte já definido estão na [curadoria](02_curadoria.md).

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

## As planilhas do recorte

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

Esses dados ainda não formam uma taxa definitiva de evasão. A antiga razão `desvinculados/matrículas` foi retirada da planilha oficial porque compara um fluxo anual com um estoque e pode produzir valores acima de 1. Permanecem os valores originais para uma definição metodológica posterior. O uso desses campos nas análises está fixado no [manual de uso](03_manual_de_uso.md).

## Validação estrutural

A validação estrutural é executada ao fim do recorte ou isoladamente com:

```bash
.venv/bin/python scripts/validar_planilhas_oficiais.py
```

### Saídas

| Arquivo | Conteúdo |
| --- | --- |
| `resumo_validacao.csv` | status geral, dimensões das bases e contagens principais |
| `ocorrencias_validacao.csv` | cada erro ou alerta com ano, IES, curso e descrição |

Não é mais gerado um relatório Markdown automático. Este documento concentra a interpretação; os CSVs guardam o resultado executado.

### O que é verificado

São erros bloqueantes:

```text
duplicata na chave ano + IES + curso da planilha principal
campo obrigatório vazio
ano fora de 2009-2024
curso fora do recorte CINE/OCDE
métrica quantitativa negativa
linha geográfica duplicada
curso presente em apenas uma das planilhas
coluna individual, sensível ou indicador metodologicamente removido
ABI identificado no nome do curso
total da principal diferente da soma da expandida
vagas/inscritos EaD fora da dimensão nacional
indicadores acadêmicos EaD na dimensão nacional
```

São alertas:

```text
mesmo código de IES com nomes diferentes no mesmo ano
mesmo código de curso com nomes diferentes no mesmo ano
```

`Erros: 0` e `Alertas: 0` significam que a estrutura produzida pela pipeline
está íntegra. Não significam que todo valor declarado pela fonte foi confirmado.
Nome e rótulo diferentes, valores repetidos e distribuição territorial atípica
são tratados separadamente no
[curadoria](02_curadoria.md).

### O que aconteceu com os 2.483 alertas antigos

Os alertas anteriores não representavam 2.483 erros de dados.

#### Razão desvinculados/matrículas

Havia 2.482 linhas com `QT_SIT_DESVINCULADO / QT_MAT > 1`. Isso acontece porque:

```text
QT_SIT_DESVINCULADO = fluxo/situação observado no ano
QT_MAT = estoque de matrículas usado como denominador
```

As grandezas não formam automaticamente uma taxa de evasão da mesma coorte. Em vez de alterar os valores originais, o indicador derivado foi removido das planilhas oficiais. Os campos `QT_SIT_DESVINCULADO` e `QT_MAT` continuam disponíveis separadamente.

#### Sigla de IES ausente

Existem 3.942 linhas sem `SG_IES`. Isso não impede a identificação da instituição porque `CO_IES` e `NO_IES` estão preenchidos. A sigla é opcional e agora aparece no resumo como informação, não como alerta.

### Resultado esperado

Após essas decisões, uma base íntegra deve apresentar:

```text
Erros: 0
Alertas: 0
```

Além disso:

```text
43.477 chaves distintas na planilha principal
315.410 linhas territoriais na planilha expandida
2009 a 2024 presentes
nenhuma linha fora do recorte oficial
nenhuma coluna individual de aluno ou docente
```

Se surgirem ocorrências futuras, elas devem ser analisadas em `ocorrencias_validacao.csv`. O script encerra com erro quando encontra qualquer problema bloqueante.

## Reproduzir

### Arquivos de entrada

Os arquivos originais ficam em:

```text
data/raw/ANO/dados/
data/raw/ANO/referencia/
```

`dados/` contém cursos, IES, arquivos de aluno e tabelas auxiliares usadas pela pipeline. `referencia/` contém dicionários, leia-me, notas informativas e filtros do INEP.

Os dados brutos não são versionados: a pasta local tem aproximadamente 11 GB e contém arquivos individuais de 2 a 3 GB.

### Baixar os dados brutos

Se os arquivos brutos não estiverem disponíveis localmente, baixar do Drive compartilhado do projeto:

```bash
.venv/bin/python scripts/baixar_dados_drive.py
```

Opções úteis:

```bash
.venv/bin/python scripts/baixar_dados_drive.py --listar
.venv/bin/python scripts/baixar_dados_drive.py --ano 2022 2024
.venv/bin/python scripts/baixar_dados_drive.py --forcar
```

O script organiza cada ano em `data/raw/ANO/dados/` e `data/raw/ANO/referencia/`, preservando CSVs de dados e materiais de referência úteis. Questionários e arquivos auxiliares sem uso direto são descartados durante essa organização.

### Ambiente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Gerar tudo

Na raiz do repositório:

```bash
.venv/bin/python scripts/executar_pipeline.py
```

O comando executa as três etapas em sequência:

| Etapa | Passos |
| --- | --- |
| 1. Recorte | leitura e padronização dos arquivos de curso e IES; recorte CINE/OCDE; camada comparável por ano + IES + curso; integração dos arquivos de aluno de 2017-2019; geração das planilhas oficiais; validação estrutural |
| 2. Curadoria | geração dos extratos de curadoria; vistoria de conteúdo, sequências territoriais e conferência de casos selecionados no bruto |
| 3. Manual de uso | camada de análise: flags, regras de uso por análise e tabelas prontas para o Power BI |

Cada etapa pode ser executada isoladamente (`scripts/validar_planilhas_oficiais.py`,
`scripts/gerar_extratos_curadoria.py`, `scripts/vistoriar_conteudo.py`,
`scripts/gerar_camada_analise.py`). A camada de análise só lê as planilhas oficiais e
os extratos da curadoria. Os intermediários ficam temporariamente em `data/processed/.pipeline/` e são removidos ao término da execução, inclusive em caso de falha. O comando completo reconstrói as planilhas oficiais; os comandos isolados das etapas 2 e 3 apenas as leem e recriam seus próprios CSVs, sobrescrevendo edições manuais feitas neles.

### Saídas permanentes

```text
data/processed/oficial/planilha_oficial_computacao.csv
data/processed/oficial/planilha_oficial_computacao_expandida.csv
data/processed/oficial/dicionario_planilha_oficial.csv

data/processed/validacao/resumo_validacao.csv
data/processed/validacao/ocorrencias_validacao.csv
data/processed/curadoria/*.csv
data/processed/analise/*.csv
```

`config/*.csv` não é saída: são as decisões da etapa 3, editadas à mão e versionadas.

### Abrir no Data Wrangler ou Pandas

Copiar e executar:

```python
from pathlib import Path
import pandas as pd

arquivo = (
    Path.cwd()
    / "data"
    / "processed"
    / "oficial"
    / "planilha_oficial_computacao.csv"
)

df = pd.read_csv(
    arquivo,
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
    low_memory=False,
)
```

Para abrir a expandida, trocar apenas o nome do arquivo.

O `sep=";"` é necessário porque as planilhas usam ponto e vírgula. `dtype=str` evita que códigos de curso, IES ou classificação sejam convertidos automaticamente para números.

Para analisar métricas:

```python
metricas = [
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "QT_SIT_TRANCADA",
    "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO",
    "QT_SIT_FALECIDO",
]

df[metricas] = df[metricas].apply(pd.to_numeric, errors="coerce")
```

### Testes

```bash
.venv/bin/python -m unittest discover -s tests -v
```
