# Evasão em Cursos de Computação no Brasil

Este projeto organiza dados de cursos superiores de Computação/TIC no Brasil para estudar
instituições, distribuição territorial e indicadores acadêmicos. O produto previsto é um
painel no Power BI, acompanhado do registro do que pode e do que não pode ser afirmado com
esses dados.

A fonte é o **Censo da Educação Superior do INEP**, de **2009 a 2024**. Não há extração própria
do cadastro e-MEC nem cruzamento independente com tabelas do IBGE no processamento documentado.

## O fluxo em três etapas

| Etapa | O que faz | Saída | Documento |
| --- | --- | --- | --- |
| 1. Recorte | Seleciona os cursos de Computação/TIC nos microdados do INEP e valida a estrutura | `data/processed/oficial/` | [01_recorte.md](docs/01_recorte.md) |
| 2. Curadoria | Examina o recorte em busca de valores, classificações e distribuições suspeitos | `data/processed/curadoria/` | [02_curadoria.md](docs/02_curadoria.md) |
| 3. Manual de uso | Decide como cada achado afeta cada análise e entrega tabelas prontas com flags | `data/processed/analise/` e `config/` | [03_manual_de_uso.md](docs/03_manual_de_uso.md) |

## De onde saímos

O INEP publica um arquivo bruto por ano desde 2009, mas não existe uma tabela pronta de
"cursos de Computação". Era preciso filtrar e juntar 16 anos de arquivos em formatos
diferentes, com três sistemas de classificação de área que mudam ao longo do tempo (CINE
até 2016, aproximação OCDE em 2017, CINE Brasil em 2018 e 2019, CINE de novo de 2020 em
diante) e com uma origem de situação acadêmica que varia entre o cadastro de cursos e o
arquivo de aluno.

Além do formato, os números que cada instituição declara nem sempre são confiáveis. Vaga e
inscrito às vezes parecem copiados de um curso para outro, um curso EaD pode ter toda a
matrícula num único município mesmo com centenas cadastrados, e o mesmo código de curso pode
reaparecer anos depois em outra instituição. Não dava para publicar um painel confiável sem
entender e documentar essas particularidades.

## Onde chegamos

1. **Recorte reprodutível.** Um pipeline organiza os 16 anos brutos e aplica uma regra única de
   Computação/TIC, com tratamento específico para 2017 e para cursos de ingresso por Área
   Básica. Gera duas planilhas: **43.477 linhas** por curso e ano, e **315.410 linhas**
   territoriais. A validação estrutural fecha em **0 erros e 0 alertas**.
2. **Curadoria de conteúdo.** Passou pelas 43.477 linhas, conferiu 51 curso-anos direto no
   arquivo bruto e catalogou os pontos que merecem atenção antes de aparecer num gráfico, do
   que é estrutural do Censo ao que é só um valor estranho isolado, cada um com exemplo real.
3. **Manual de uso.** Transforma cada achado em flag e decide, análise por análise, quando um
   registro é apenas sinalizado e quando sai daquela análise. Todas as decisões estão
   escritas, com o motivo e o modo de reverter, e as tabelas saem prontas para o Power BI.

Nenhuma etapa altera os valores declarados pelas instituições. As planilhas oficiais guardam
todo o recorte, e qualquer decisão da etapa 3 pode ser revista sem refazer as anteriores.

## O recorte

Nos anos classificados por CINE ou CINE Brasil, entram os cursos que atendem a pelo menos uma
regra:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

A área geral 6 é Computação e Tecnologias da Informação e Comunicação. O rótulo `0714E04`
acrescenta Engenharia de Computação. O tratamento de ABI e a aproximação OCDE de 2017 estão na
[etapa 1](docs/01_recorte.md).

## Arquivos

**Base oficial**, o recorte completo e intocado, em `data/processed/oficial/`:

| Arquivo | Finalidade |
| --- | --- |
| [planilha_oficial_computacao.csv](data/processed/oficial/planilha_oficial_computacao.csv) | **43.477 linhas**, uma por ano, IES e curso |
| [planilha_oficial_computacao_expandida.csv](data/processed/oficial/planilha_oficial_computacao_expandida.csv) | **315.410 linhas** territoriais e dimensionais |
| [dicionario_planilha_oficial.csv](data/processed/oficial/dicionario_planilha_oficial.csv) | descrição das colunas |

**Tabelas prontas para o Power BI**, com flags e colunas de uso, em `data/processed/analise/`:

| Arquivo | Finalidade |
| --- | --- |
| [fato_curso_ano.csv](data/processed/analise/fato_curso_ano.csv) | contagem, séries, vagas, inscritos, situações e classificação |
| [fato_municipio_ano.csv](data/processed/analise/fato_municipio_ano.csv) | mapas e presença territorial |
| [cobertura_uso.csv](data/processed/analise/cobertura_uso.csv) | quanto cada análise usa e deixa de fora |
| dim_flag, dim_uso, matriz_flag_uso | catálogo de flags, catálogo de análises e tratamento de cada flag |

As decisões ficam em [`config/`](config/), editáveis à mão e versionadas. Os brutos ficam em
`data/raw/` e não são versionados, por ocuparem cerca de 11 GB.

## Uso no Power BI

Relacione a `fato_municipio_ano` à `fato_curso_ano` por `CH_CURSO_ANO`, muitos para um, e conte
cursos sempre pela `fato_curso_ano`. Filtre cada visual pela coluna `IN_USO_` da análise que ele
representa. Antes de montar uma consulta, leia o [manual de uso](docs/03_manual_de_uso.md): ele
diz o que cada análise exclui, o que apenas sinaliza e o que nunca deve ser calculado, como uma
taxa de evasão ou a concorrência.

## Reproduzir

Com o ambiente configurado:

```bash
.venv/bin/python scripts/executar_pipeline.py
```

O comando executa as três etapas em sequência e remove os arquivos intermediários. Ambiente,
obtenção das fontes e execução isolada de cada etapa estão na [etapa 1](docs/01_recorte.md).

## Documentação

- [Etapa 1: recorte](docs/01_recorte.md): fontes, regras do recorte, planilhas, validação estrutural e reprodução.
- [Etapa 2: curadoria](docs/02_curadoria.md): achados classificados em estrutural, suspeito e baixo impacto, com exemplos.
- [Etapa 3: manual de uso](docs/03_manual_de_uso.md): tabelas prontas, análises, matriz de tratamento e registro de decisões.
