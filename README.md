# Evasão em Cursos de Computação no Brasil

Este projeto organiza dados de cursos superiores de Computação/TIC no Brasil para estudar
instituições, distribuição territorial e indicadores acadêmicos. O produto previsto é um
painel no Power BI, acompanhado do registro do que pode e do que não pode ser afirmado com
esses dados, de um jeito que a própria instituição consiga entender.

A fonte é o **Censo da Educação Superior do INEP**, de **2009 a 2024**. Não há extração própria
do cadastro e-MEC nem cruzamento independente com tabelas do IBGE no processamento documentado.
O projeto foi feito para **receber os próximos anos do Censo**, não é uma fotografia fixa.

## O fluxo em quatro etapas

| Etapa | O que faz | Saída | Documento |
| --- | --- | --- | --- |
| 1. Recorte | Seleciona os cursos de Computação/TIC nos microdados do INEP e valida a estrutura | `data/processed/oficial/` | [01_recorte.md](docs/01_recorte.md) |
| 2. Curadoria | Examina o recorte em busca de valores, classificações e distribuições suspeitos | `data/processed/curadoria/` | [02_curadoria.md](docs/02_curadoria.md) |
| 3. Manual de uso | Decide como cada achado afeta cada análise e explica cada registro em português simples | `data/processed/analise/` e `config/` | [03_manual_de_uso.md](docs/03_manual_de_uso.md) |
| 4. Novos anos | Traz cada novo Censo do INEP para dentro de tudo isso, com checagens automáticas | `config/anos.csv` | [04_novos_anos.md](docs/04_novos_anos.md) |

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
   Computação/TIC. Gera duas planilhas: **43.477 linhas** por curso e ano, e **315.410 linhas**
   territoriais. A validação estrutural fecha em **0 erros e 0 alertas**.
2. **Curadoria de conteúdo.** Passou pelas 43.477 linhas, conferiu 51 curso-anos direto no
   arquivo bruto e catalogou os pontos que merecem atenção antes de aparecer num gráfico.
3. **Manual de uso e transparência.** Cada achado vira uma marca no registro e uma explicação em
   português simples, com os números do próprio caso. Toda decisão sobre o que aparece, o que
   fica de fora e o que aparece com aviso está escrita, com o motivo e o modo de reverter. Uma
   instituição consegue abrir o painel e entender o que foi observado nos seus cursos.
4. **Projeto vivo.** Trazer o Censo de um ano novo é um comando, com checagem prévia do layout do
   INEP e checagem de continuidade entre anos, para que uma mudança silenciosa não passe.

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

**Tabelas prontas para o Power BI**, em `data/processed/analise/`:

| Arquivo | Finalidade |
| --- | --- |
| [fato_curso_ano.csv](data/processed/analise/fato_curso_ano.csv) | contagem, séries, vagas, inscritos e situações, com flags e gravidade |
| [fato_municipio_ano.csv](data/processed/analise/fato_municipio_ano.csv) | mapas e presença territorial |
| [ocorrencias.csv](data/processed/analise/ocorrencias.csv) | cada observação de cada registro, com a explicação do caso, para o "entenda os dados" |
| [resumo_ies_ano.csv](data/processed/analise/resumo_ies_ano.csv) | resumo em texto por instituição e ano |
| [cobertura_uso.csv](data/processed/analise/cobertura_uso.csv) | quanto cada análise usa e deixa de fora |
| dim_flag, dim_uso, matriz_flag_uso | catálogo de flags e análises, com os avisos de cada gráfico |

As decisões ficam em [`config/`](config/), editáveis à mão e versionadas. Os brutos ficam em
`data/raw/` e não são versionados, por ocuparem cerca de 11 GB.

## Uso no Power BI

Relacione as tabelas por `CH_CURSO_ANO`, conte cursos sempre pela `fato_curso_ano` e filtre cada
visual pela coluna `IN_USO_` da análise que ele representa. O
[manual de uso](docs/03_manual_de_uso.md) traz o passo a passo, as medidas prontas e um passeio
com um caso real, mostrando o que a instituição vê no painel.

## Reproduzir e alimentar

Com o ambiente configurado, o pipeline completo é:

```bash
.venv/bin/python scripts/executar_pipeline.py
```

Para trazer o Censo de um ano novo:

```bash
.venv/bin/python scripts/adicionar_ano.py 2025 --zip ~/Downloads/microdados_2025.zip
```

O primeiro está na [etapa 1](docs/01_recorte.md) e o segundo na [etapa 4](docs/04_novos_anos.md).

## Documentação

- [Etapa 1: recorte](docs/01_recorte.md): fontes, regras do recorte, planilhas, validação estrutural e reprodução.
- [Etapa 2: curadoria](docs/02_curadoria.md): achados classificados em estrutural, suspeito e baixo impacto, com exemplos.
- [Etapa 3: manual de uso](docs/03_manual_de_uso.md): tabelas prontas, transparência, matriz de tratamento, Power BI e registro de decisões.
- [Etapa 4: novos anos](docs/04_novos_anos.md): como trazer cada novo Censo, o que é automático e o que fazer se o INEP mudar algo.
