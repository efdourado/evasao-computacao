# Evasão em Cursos de Computação no Brasil

Este projeto organiza dados de cursos superiores de Computação/TIC no Brasil
para estudar instituições, distribuição territorial e indicadores acadêmicos.
O produto previsto é um painel no Power BI, acompanhado das observações sobre
a qualidade e os limites dos dados.

A fonte é o **Censo da Educação Superior do INEP**, de **2009 a 2024**. Não há
extração própria do cadastro e-MEC ou cruzamento independente com tabelas do
IBGE no processamento documentado.

## De onde saímos

O INEP publica um arquivo bruto por ano desde 2009, mas não existe uma tabela
pronta de "cursos de Computação": era preciso filtrar e juntar 16 anos de
arquivos em três formatos diferentes, três sistemas de classificação de área
que mudam ao longo do tempo (CINE até 2016, aproximação OCDE em 2017, CINE
Brasil em 2018–2019, CINE novamente de 2020 em diante) e uma origem de
situação acadêmica (trancado, desvinculado etc.) que varia entre o cadastro
de cursos e o arquivo de aluno dependendo do ano.

Além da complexidade de formato, os números que cada instituição declara nem
sempre são confiáveis: vaga e inscrito às vezes parecem copiados de um curso
para outro, um curso EaD pode aparecer com toda a matrícula concentrada num
único polo mesmo tendo centenas de municípios cadastrados, e o mesmo código
de curso pode reaparecer anos depois em outra instituição. Não dava para
publicar um painel confiável sem antes entender e documentar essas
particularidades.

## Onde chegamos

1. **Pipeline reprodutível** que organiza os 16 anos brutos, aplica um
   recorte único e documentado de Computação/TIC (com tratamento específico
   para 2017 e para cursos de ingresso por Área Básica) e gera duas
   planilhas versionadas: **43.477 linhas** por curso (histórico e
   institucional) e **315.410 linhas** territoriais (base dos mapas).
2. **Validação estrutural automática**, hoje em **0 erros e 0 alertas**:
   nenhuma chave duplicada, nenhum curso fora do recorte, nenhuma métrica
   negativa, e o total de cada curso na planilha principal batendo com a
   soma das suas linhas territoriais.
3. **Curadoria de conteúdo**, feita manualmente com apoio de scripts: passou
   pelas 43.477 linhas, conferiu 51 curso-anos direto contra o arquivo bruto
   do INEP e catalogou **4.919 pontos de atenção em 2.463 combinações**
   ano + IES + curso — desde regras estruturais que sempre importam (como
   vaga/inscrito de EaD só existir numa linha nacional) até valores isolados
   apenas suspeitos. Tudo com exemplo concreto e recomendação de uso na
   [curadoria e inconsistências](docs/04_curadoria_e_inconsistencias.md).
4. **Testes automatizados** para as regras de curadoria mais sensíveis a
   erro de lógica (sequências de zero territorial, mudança de distribuição
   entre anos).

Nenhuma dessas etapas altera os valores declarados pelas instituições: elas
organizam, verificam e documentam a base, sem corrigir ou excluir dado de
origem automaticamente.

## O que vem a seguir

O painel de Power BI é construído em cima das duas planilhas oficiais,
aplicando as ressalvas da curadoria conforme a pergunta de cada análise (por
exemplo: usar `QT_MAT` para mapa municipal, mas nunca `QT_VG_TOTAL`; nunca
apresentar uma "taxa de evasão" pronta sem qualificar o que ela mede).

## Recorte e preservação da base

Nos anos classificados por CINE/CINE Brasil, entram:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

A área geral 6 corresponde a Computação e Tecnologias da Informação e
Comunicação. O rótulo `0714E04` acrescenta Engenharia de Computação. O
tratamento de graduação/ABI e a aproximação OCDE de 2017 estão descritos na
[metodologia](docs/01_visao_geral.md).

A curadoria preserva o recorte e os valores oficiais. Possíveis problemas na
declaração de origem, inclusive classificações incompatíveis com o curso,
ficam documentados sem correção ou exclusão automática.

## Arquivos para análise

As três planilhas finais ficam em `data/processed/oficial/`:

| Arquivo | Finalidade |
| --- | --- |
| [planilha_oficial_computacao.csv](data/processed/oficial/planilha_oficial_computacao.csv) | **43.477 linhas**, uma por ano + IES + curso; totais e séries históricas |
| [planilha_oficial_computacao_expandida.csv](data/processed/oficial/planilha_oficial_computacao_expandida.csv) | **315.410 linhas** territoriais e dimensionais; base dos mapas |
| [dicionario_planilha_oficial.csv](data/processed/oficial/dicionario_planilha_oficial.csv) | descrição das colunas e das planilhas em que aparecem |

Os brutos ficam em `data/raw/` e não são versionados devido ao volume,
aproximadamente 11 GB. As planilhas finais e a validação são versionadas.

## Uso no Power BI

A relação entre principal e expandida usa **ano + IES + curso**, sem repetir
totais pelas linhas municipais. Os mapas usam `IN_USAR_MAPA_MUNICIPAL =
True`; município associado não comprova campus/polo físico ou presença de
alunos.

Uma localização duvidosa pode comprometer a análise municipal sem invalidar o
total declarado. Antes de montar uma consulta, visite a
[curadoria](docs/04_curadoria_e_inconsistencias.md): ela classifica cada
achado em estrutural (sempre considerar), suspeito (decidir caso a caso) ou
baixo impacto (ciente, sem ação), sempre com um exemplo real.

## Reproduzir

Com o ambiente configurado:

```bash
.venv/bin/python scripts/executar_pipeline.py
```

Esse comando gera as três planilhas, executa a validação e a vistoria, recria
os extratos de curadoria e remove os arquivos intermediários. Ambiente,
obtenção das fontes e execução isolada estão em
[Pipeline e reprodução](docs/02_pipeline_e_reproducao.md).

## Documentação

- [Visão geral e metodologia](docs/01_visao_geral.md): fontes, recorte e comparabilidade histórica.
- [Pipeline e reprodução](docs/02_pipeline_e_reproducao.md): entradas, comandos e saídas.
- [Validação e qualidade](docs/03_validacao_qualidade.md): verificações estruturais e decisões sobre indicadores.
- [Curadoria e inconsistências](docs/04_curadoria_e_inconsistencias.md): o que validar antes de consultar, ranqueado por nível de atenção, com exemplos.
