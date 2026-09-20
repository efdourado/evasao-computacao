# Etapa 3: manual de uso

Terceira etapa do fluxo. Pega os achados da [curadoria](02_curadoria.md), decide caso a caso como
cada um afeta cada análise e **explica cada registro em português simples**. O resultado são
tabelas prontas para o Power BI, com flags, colunas de uso e textos, e um registro escrito de
todas as decisões, que pode ser revisto a qualquer momento.

```text
dados do INEP -> 1. recorte -> 2. curadoria -> 3. manual de uso -> Power BI
                                                     ^
                                  4. novos anos alimenta tudo, ano a ano
```

A ambição desta etapa é a de um **portal da transparência** para os dados: nada passa batido.
Tudo o que a curadoria apontou vira uma marca no registro, e a marca explica, com os números do
próprio caso, o que foi visto e o que o painel faz com aquilo. Uma pessoa da instituição consegue
abrir o painel, clicar em "entender" e ler o que foi observado nos seus cursos.

## Princípios

1. **A base oficial nunca muda.** As planilhas oficiais guardam todo o recorte, com todos os
   valores declarados. Nada aqui apaga linha nem corrige valor.
2. **Exclusão é por análise, não global.** Uma flag só tira uma linha de uma análise quando a
   matriz diz "excluir" para aquele par. A mesma linha continua valendo nas outras análises.
3. **Todo achado da curadoria vira flag, e toda flag explica a si mesma.** O texto que a
   instituição lê é gerado a partir da matriz, então nunca contradiz o que o painel faz.
4. **Excluir sempre informa a cobertura.** Cada análise diz quantas linhas e quanto volume
   deixou de fora, e nunca trata o excluído como zero.
5. **Toda decisão é escrita e pode ser revista.** O registro está na [seção 8](#8-registro-de-decisões),
   com o motivo, a alternativa descartada e como reverter.
6. **Os avisos são indícios, nunca acusação.** O painel diz onde o dado merece cuidado. Não afirma
   erro nem irregularidade da instituição.

## 1. As tabelas prontas

Ficam em `data/processed/analise/`, geradas por `scripts/gerar_camada_analise.py` e
`scripts/gerar_transparencia.py` a partir das planilhas oficiais, dos extratos da curadoria e dos
arquivos de `config/`.

| Arquivo | Grão | Para que serve |
| --- | --- | --- |
| `fato_curso_ano.csv` | um curso por ano, 43.477 linhas | Contagem, séries, vagas, inscritos, situações e classificação. É a planilha principal com flags, gravidade e colunas de uso |
| `fato_municipio_ano.csv` | um curso por ano e município, 309.291 linhas | Mapas e presença territorial. Só linhas municipais mapeáveis |
| `ocorrencias.csv` | um registro por observação, 29.274 linhas | A explicação de cada caso, com os números dele. Alimenta a página "entenda" |
| `resumo_ies_ano.csv` | uma instituição por ano, 15.452 linhas | Um parágrafo pronto por instituição e ano, mais as contagens por gravidade |
| `dim_flag.csv` | uma linha por flag | Catálogo: título, gravidade, o que é, por que importa, como tratamos e o que a instituição pode fazer |
| `dim_uso.csv` | uma linha por análise | Catálogo das nove análises, com o aviso que cada gráfico deve exibir |
| `matriz_flag_uso.csv` | flag por análise | O tratamento de cada flag em cada análise, em formato longo |
| `cobertura_uso.csv` | análise, ano e modalidade | Quanto cada análise usa, exclui e não tem |
| `decisoes_manuais_aplicadas.csv` | uma exceção manual por análise | Efeito das exceções de `config/decisoes_manuais.csv` |

**Colunas que importam nas duas tabelas de fatos:**

| Coluna | Como usar |
| --- | --- |
| `IN_USO_<ANÁLISE>` | 1 quando a linha pode entrar naquela análise. É o filtro principal |
| `GRAVIDADE` | Sem observações, Informação, Atenção ou Alerta. Para colorir e ordenar. Explicada na seção 2 |
| `NV_ATENCAO` | A gravidade em número, de 0 a 3, para ordenar |
| `DS_OBSERVACOES` | Os títulos das observações do registro, do mais grave ao menos, em português. Boa para tooltip |
| `DS_FLAGS` | Os códigos das flags, separados por barra vertical. Para quem prefere filtrar por código |
| `FL_<ACHADO>` | 1 quando o achado se aplica ao registro |
| `CH_CURSO_ANO` | Chave ano, IES e curso. Relaciona todas as tabelas |
| `CH_SERIE_CURSO` | Chave IES e curso. Usar para seguir um curso no tempo |

**Cinco regras práticas:**

- Conte cursos e IES pela `fato_curso_ano`. Nunca conte linhas da municipal.
- Filtre sempre pelo `IN_USO_` da análise que está fazendo. Usar o filtro de outra análise muda o sentido do número.
- Na municipal, vagas e inscritos ficam em branco para EaD. Branco significa "não se aplica", não zero.
- Para seguir um curso ao longo dos anos, use `CH_SERIE_CURSO`, nunca `CO_CURSO` sozinho.
- Use `GRAVIDADE` para destacar e `IN_USO_` para filtrar. Não filtre por gravidade.

## 2. Como cada registro se explica

Há duas escalas, que respondem a perguntas diferentes:

- **Nível** (`Suspeito`, `Baixo impacto`, `Estrutural`) descreve a natureza do achado, e fica no
  catálogo para quem analisa. Veio da [curadoria](02_curadoria.md).
- **Gravidade** descreve **o que o painel faz** com o registro, e é a que a instituição vê. É
  derivada da matriz de tratamento, então muda sozinha quando uma regra muda.

| Gravidade | Significa para quem lê | Quando |
| --- | --- | --- |
| **Alerta** | Este dado fica de fora de pelo menos um gráfico | A flag tem tratamento "excluir" em alguma análise |
| **Atenção** | Este dado aparece, mas com aviso, e merece cuidado | Achado suspeito que só sinaliza |
| **Informação** | Só uma nota de contexto. Não altera nenhum gráfico | Achado estrutural ou de baixo impacto |
| **Sem observações** | Nada a registrar | Nenhuma flag |

Hoje, dos 43.477 registros de curso e ano, 9.945 estão em Alerta, 2.990 em Atenção,
2.332 em Informação e 28.210 sem observações. Alerta é frequente sobretudo por causa de
vagas e de inscritos zerados, e diz apenas que o dado não entra em algum gráfico, não que a
instituição errou.

**Cada observação traz os campos abaixo.** `TITULO`, `EVIDENCIA` e `COMO_TRATAMOS` já vêm em `ocorrencias.csv`. Os demais vêm de `dim_flag.csv`, ligada pela coluna `FLAG`.

| Campo | O que responde |
| --- | --- |
| `TITULO` | O que foi observado, em uma frase curta |
| `EVIDENCIA` | O caso concreto, com os números do próprio registro |
| `O_QUE_E` | O que isso significa |
| `POR_QUE_IMPORTA` | Por que muda a leitura do dado |
| `COMO_TRATAMOS` | O que o painel faz: em quais gráficos o dado fica de fora e em quais aparece com aviso |
| `O_QUE_FAZER` | O que a instituição pode conferir |
| `ONDE_LER_MAIS` | O item da curadoria ou do manual que explica |

Os textos ficam em `config/textos_flags.csv`, em português simples, e podem ser editados sem
tocar em código. As frases com os números do caso são geradas pelo script. Cada gráfico também
recebe um aviso pronto em `dim_uso.csv`, listando o que fica de fora dele e o que aparece com aviso.

## 3. As nove análises

| Análise | Pergunta que responde | Tabela | Publicar | Requisito além das flags |
| --- | --- | --- | --- | --- |
| `CONTAGEM` | Quantos cursos e instituições existem por ano? | curso e ano | sim | Para cursos em atividade, acrescentar `QT_MAT` maior que zero |
| `SERIE_MAT` | Como evoluem matrículas, ingressantes e concluintes? | curso e ano | sim | `QT_MAT` preenchida |
| `MAPA_MUN` | Onde estão as matrículas? | município e ano | sim | `QT_MAT` preenchida |
| `PRESENCA` | Em quantos municípios há oferta? | município e ano | sim | `QT_MAT` maior que zero no município |
| `VAGAS` | Quantas vagas foram oferecidas? | curso e ano | sim | `QT_VG_TOTAL` preenchida |
| `INSCRITOS` | Quantos se inscreveram? | curso e ano | exploratório | `QT_INSCRITO_TOTAL` preenchida. 2017 fica de fora |
| `EVASAO_SIT` | Quantos alunos desvinculados e trancados? | curso e ano | sim, só contagens | `QT_SIT_DESVINCULADO` preenchida |
| `AREA_TIPO` | Como se distribuem por tipo de curso ou área? | curso e ano | sim | nenhum |
| `SERIE_CURSO` | Como um mesmo curso evolui no tempo? | curso e ano | sim | `QT_MAT` preenchida |

`Publicar` diz se o resultado pode aparecer como número oficial (`sim`), só como exploração
com ressalva (`exploratório`) ou não deve aparecer (`não`). Nenhuma análise calcula taxa de
evasão nem concorrência.

## 4. Matriz de tratamento

Cada célula diz o que uma flag faz em uma análise:

- **excluir** tira a linha da análise: `IN_USO_<ANÁLISE>` fica 0.
- **sinalizar** mantém a linha e deixa a flag visível.
- **vazio** significa que a flag não tem relação com a análise.

Uma linha que não atende ao requisito da análise, como a matrícula ausente, fica com
`IN_USO_<ANÁLISE>` 0 e aparece como "sem dado" na cobertura, separada das exclusões por flag.

| Flag | CONTAGEM | SERIE_MAT | MAPA_MUN | PRESENCA | VAGAS | INSCRITOS | EVASAO_SIT | AREA_TIPO | SERIE_CURSO | Decisão |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `FL_VAGAS_REPETIDAS` |  |  |  |  | sinalizar |  |  |  |  | D03 |
| `FL_VAGAS_IES_ANO_SUSPEITO` |  |  |  |  | **excluir** |  |  |  |  | D03 |
| `FL_INSCRITO_IGUAL` |  |  |  |  |  | sinalizar |  |  |  | D04 |
| `FL_INSCRITO_ZERO` |  |  |  |  |  | **excluir** |  |  |  | D07 |
| `FL_MAT_ZERO_COM_ING` |  | sinalizar |  |  |  |  | **excluir** |  | **excluir** | D10 |
| `FL_MAT_CAI_A_ZERO` |  | sinalizar |  |  |  |  | **excluir** |  | **excluir** | D10 |
| `FL_ZERO_LACUNA_50` |  | sinalizar |  |  |  |  | **excluir** |  | **excluir** | D10 |
| `FL_SALTO_MAT` |  | sinalizar |  |  |  |  | sinalizar |  | sinalizar | D10 |
| `FL_EAD_DISTRIB_ATIPICA` |  |  | **excluir** | **excluir** |  |  |  |  |  | D02 |
| `FL_MUDANCA_DISTRIBUICAO` |  |  | sinalizar | sinalizar |  |  |  |  |  | D10 |
| `FL_NOME_ROTULO_DIVERGENTE` |  |  |  |  |  |  |  | sinalizar |  | D10 |
| `FL_ROTULO_EM_DEFINICAO` |  |  |  |  |  |  |  | sinalizar |  | D10 |
| `FL_EAD_MUNICIPIOS_ZERADOS_AMPLA` |  |  | sinalizar | sinalizar |  |  |  |  |  | D02 |
| `FL_EAD_TODOS_MUN_ZERO` |  |  | sinalizar | sinalizar |  |  |  |  |  | D10 |
| `FL_TUDO_ZERO` | sinalizar | sinalizar |  |  |  |  | **excluir** |  | sinalizar | D10 |
| `FL_BAIXA_ATIVIDADE` | sinalizar |  |  |  |  |  |  |  | sinalizar | D10 |
| `FL_INTERDISCIPLINAR` | sinalizar |  |  |  |  |  |  | sinalizar |  | D10 |
| `FL_ROTULO_MUDA_NA_SERIE` |  |  |  |  |  |  |  | sinalizar | sinalizar | D10 |
| `FL_CO_CURSO_EM_VARIAS_IES` |  |  |  |  |  |  |  |  | sinalizar | D10 |
| `FL_MUN_ZERO_3_ANOS` |  |  | sinalizar | sinalizar |  |  |  |  |  | D10 |
| `FL_PROXY_OCDE_2017` | sinalizar | sinalizar |  |  |  |  |  | sinalizar |  | D10 |
| `FL_EAD_SEM_TERRITORIO` |  |  | sinalizar | sinalizar |  |  |  |  |  | D10 |

A fonte da verdade é `config/matriz_flag_uso.csv`. Esta tabela é uma cópia para leitura.

## 5. Impacto medido em 2026-09-20

Fotografia da `cobertura_uso.csv` na data. O valor vigente sempre está no arquivo.

| Análise | Linhas usadas | Excluídas por flag | Sem dado | Volume excluído |
| --- | --- | --- | --- | --- |
| `CONTAGEM` | 43.477 | 0 | 0 | 0% |
| `SERIE_MAT` | 43.477 | 0 | 0 | 0% |
| `MAPA_MUN` | 304.536 | 4.755 | 0 | 0,5% das matrículas, mais 3,7% sem território |
| `PRESENCA` | 248.678 | 1.367 | 59.246 | não se aplica |
| `VAGAS` | 37.943 | 5.534 | 0 | **28,3% das vagas** |
| `INSCRITOS` | 36.852 | 4.333 | 2.292 | 0%, pois zeros não somam |
| `EVASAO_SIT` | 42.116 | 1.361 | 0 | 0,5% dos desvinculados |
| `AREA_TIPO` | 43.477 | 0 | 0 | 0% |
| `SERIE_CURSO` | 42.152 | 1.325 | 0 | 0%, pois só saem pontos zerados |

Dois pontos de atenção. O volume de vagas é o que mais perde, e a razão está na decisão D03. E os
3,7% de matrículas sem território no mapa são o EaD de 2017 a 2019, que o Censo não detalha por
município e não pode ser mapeado por nenhuma regra.

## 6. Passeio guiado: o que a instituição vê

Vamos seguir um caso real, o **Centro Universitário Leonardo da Vinci em 2024**, do dado até o
que aparece no painel. Todos os números abaixo saem das tabelas prontas.

### Passo 1: o registro do curso

Na `fato_curso_ano`, o curso **Técnicas Para Telemedicina** em 2024 é uma linha com estes campos:

| Campo | Valor |
| --- | --- |
| `QT_VG_TOTAL`, `QT_INSCRITO_TOTAL` | 6 vagas, 6 inscritos |
| `QT_ING`, `QT_MAT` | 6 ingressantes, 0 matrículas |
| `QT_SIT_DESVINCULADO` | 51 |
| `GRAVIDADE` e `NV_ATENCAO` | Alerta e 3 |
| `DS_OBSERVACOES` | Zero matrículas, mas com ingressantes • Matrículas caíram a zero de um ano para o outro • Inscritos iguais às vagas ou aos ingressantes • Todos os municípios cadastrados sem aluno (EaD) |

### Passo 2: o que foi observado, com os números do caso

Estas são as linhas de `ocorrencias.csv` deste curso. É o que a instituição lê ao clicar em "entender":

| Gravidade | O que foi observado | O caso | O que o painel faz |
| --- | --- | --- | --- |
| Alerta | Matrículas caíram a zero de um ano para o outro | Em 2023 o curso tinha 47 matrículas; em 2024, informou 0; 2025 ainda não está na base. | Fica de fora de: Alunos desvinculados e trancados e Evolução de um mesmo curso. Aparece com aviso em: Matrículas, ingressantes e concluintes ao longo dos anos. |
| Alerta | Zero matrículas, mas com ingressantes | O curso informou 0 matrículas em 2024, mas registrou 6 ingressantes e 51 desvinculados no mesmo ano. | Fica de fora de: Alunos desvinculados e trancados e Evolução de um mesmo curso. Aparece com aviso em: Matrículas, ingressantes e concluintes ao longo dos anos. |
| Atenção | Inscritos iguais às vagas ou aos ingressantes | Foram informados 6 inscritos, número idêntico ao de vagas e ao de ingressantes (6). | Aparece com aviso em: Inscritos nos processos seletivos. |
| Informação | Todos os municípios cadastrados sem aluno (EaD) | Os 44 municípios cadastrados neste curso aparecem sem nenhum aluno em 2024. | Aparece com aviso em: Mapa de matrículas por município e Presença em municípios. |

Repare que nenhuma frase acusa a instituição. Elas descrevem o que os dados mostram e o que o
painel decide fazer com isso.

### Passo 3: o que acontece em cada gráfico

Para este mesmo curso, cada análise se comporta de um jeito, conforme a matriz:

| Gráfico | Coluna | O que acontece |
| --- | --- | --- |
| Quantidade de cursos e instituições | `IN_USO_CONTAGEM` = 1 | entra normalmente |
| Matrículas, ingressantes e concluintes ao longo dos anos | `IN_USO_SERIE_MAT` = 1 | entra com aviso |
| Vagas oferecidas | `IN_USO_VAGAS` = 1 | entra normalmente |
| Inscritos nos processos seletivos | `IN_USO_INSCRITOS` = 1 | entra com aviso |
| Alunos desvinculados e trancados | `IN_USO_EVASAO_SIT` = 0 | fica de fora |
| Distribuição por tipo de curso | `IN_USO_AREA_TIPO` = 1 | entra normalmente |
| Evolução de um mesmo curso | `IN_USO_SERIE_CURSO` = 0 | fica de fora |

Nenhum dado foi apagado. O curso continua inteiro na base oficial e na `fato_curso_ano`. Só
não entra, por exemplo, no gráfico de alunos desvinculados, porque o ano tem matrícula zero e
51 desvinculados, e qualquer conta com esses dois números ficaria sem sentido.

### Passo 4: o mapa

Na `fato_municipio_ano`, este curso tem 44 linhas de município em 2024. Todas com matrícula
zero: por isso o curso soma 0 no mapa de matrículas e **não conta** como presença em nenhum
município (44 linhas com `IN_USO_PRESENCA` igual a 0). Cadastrar um município não basta para
contar como oferta, e essa é a regra que impede que municípios apenas cadastrados inflem a presença.

### Passo 5: a instituição inteira

O `resumo_ies_ano.csv` já traz o parágrafo pronto para o cartão de abertura da página:

> Em 2024, CENTRO UNIVERSITÁRIO LEONARDO DA VINCI tem 17 cursos de Computação na base. 1 fica de fora de algum gráfico e 16 aparecem com aviso. Principais observações: Matrículas caíram a zero de um ano para o outro (1 curso); Zero matrículas, mas com ingressantes (1 curso); Inscritos iguais às vagas ou aos ingressantes (17 cursos).

### Passo 6: um caso em que o gráfico muda de verdade

No gráfico de **vagas**, o exemplo típico é a UNIP em 2013:

> Em 2013, a instituição repetiu 230 vagas em 52 dos seus 97 cursos de Computação. Por isso as vagas de todos os cursos da instituição nesse ano ficam fora do gráfico de vagas. Este curso declarou 230 vagas.

Repare que a regra não olha só os cursos com o número repetido. Outro curso da mesma instituição no mesmo ano,
Gestão de sistemas de informação (EaD), com 36.522 vagas declaradas, também fica de fora, porque não dá para saber quais vagas da instituição são reais. Todos os
cursos da UNIP nesse ano saem do gráfico de vagas, e o aviso do gráfico diz isso. Em 2013, 35,3% de todo o
volume de vagas declarado no país deixa de entrar por regras assim.

### Como a instituição lê tudo isso no painel

```text
+------------------------------------------------------------------+
|  ENTENDA OS DADOS      Instituição [ Leonardo da Vinci ]  Ano [2024]|
+------------------------------------------------------------------+
|  Em 2024, CENTRO UNIVERSITÁRIO LEONARDO DA VINCI tem 17 cursos de Computação na base. 1 fica de f...
+------------------------------------------------------------------+
|  Gravidade [Alerta v]    Curso [todos v]                          |
|                                                                  |
|  ALERTA   Matrículas caíram a zero de um ano para o outro        |
|           Em 2023 o curso tinha 47 matrículas; em 2024, informou 0.
|           Fica de fora de: Alunos desvinculados e trancados ...  |
|           [ O que é isso? ]  [ O que fazer? ]                    |
+------------------------------------------------------------------+
|  Estes avisos são indícios encontrados automaticamente...        |
+------------------------------------------------------------------+
```

## 7. Como montar no Power BI

### Importar

- Use **Obter dados, Texto/CSV**, com delimitador **ponto e vírgula** e origem **UTF-8**.
- As colunas numéricas (`QT_*`) usam **ponto decimal**. Converta com a cultura **inglês (Estados Unidos)**, senão o
  Power BI pode ler `1508.0` como 15080. No Power Query: `Table.TransformColumnTypes(Fonte, {"QT_MAT", type number}, "en-US")`.
- `CO_IES`, `CO_CURSO`, `CO_MUNICIPIO` e as chaves `CH_*` devem ficar como **texto**.

### Relacionamentos

| De | Para | Cardinalidade |
| --- | --- | --- |
| `fato_municipio_ano[CH_CURSO_ANO]` | `fato_curso_ano[CH_CURSO_ANO]` | muitos para um |
| `ocorrencias[CH_CURSO_ANO]` | `fato_curso_ano[CH_CURSO_ANO]` | muitos para um |
| `ocorrencias[FLAG]` | `dim_flag[FLAG]` | muitos para um |

`resumo_ies_ano`, `dim_uso` e `cobertura_uso` ficam sem relacionamento e são lidas por filtro
de ano e instituição ou por valor fixo.

### Medidas prontas

```text
Cursos = CALCULATE ( DISTINCTCOUNT ( fato_curso_ano[CH_CURSO_ANO] ), fato_curso_ano[IN_USO_CONTAGEM] = 1 )
Instituições = CALCULATE ( DISTINCTCOUNT ( fato_curso_ano[CO_IES] ), fato_curso_ano[IN_USO_CONTAGEM] = 1 )
Matrículas = CALCULATE ( SUM ( fato_curso_ano[QT_MAT] ), fato_curso_ano[IN_USO_SERIE_MAT] = 1 )
Vagas = CALCULATE ( SUM ( fato_curso_ano[QT_VG_TOTAL] ), fato_curso_ano[IN_USO_VAGAS] = 1 )
Matrículas no mapa = CALCULATE ( SUM ( fato_municipio_ano[QT_MAT] ), fato_municipio_ano[IN_USO_MAPA_MUN] = 1 )
Municípios com oferta = CALCULATE ( DISTINCTCOUNT ( fato_municipio_ano[CO_MUNICIPIO] ), fato_municipio_ano[IN_USO_PRESENCA] = 1 )
Registros com observação = DISTINCTCOUNT ( ocorrencias[CH_CURSO_ANO] )
Aviso do gráfico de vagas = LOOKUPVALUE ( dim_uso[AVISO_DO_GRAFICO], dim_uso[USO], "VAGAS" )
```

### Páginas sugeridas

| Página | Conteúdo | Aviso obrigatório |
| --- | --- | --- |
| Panorama | Cartões de cursos, instituições e matrículas. Linha de matrículas por ano | Aviso do gráfico de `SERIE_MAT` e um botão "entender" |
| Mapa | Mapa de matrículas por município e cartão de municípios com oferta | Que o EaD de 2017 a 2019 não tem detalhe por município |
| Vagas e inscritos | Vagas por ano e inscritos, este último com faixa "exploratório" | O aviso de `VAGAS` e a cobertura em `cobertura_uso` |
| **Entenda os dados** | Página de detalhamento (drill-through) por instituição, ano e curso. Cartão com `TEXTO_ENTENDA`, tabela de `ocorrencias` colorida pela gravidade e tooltip com `dim_flag` | O `AVISO_GERAL` de `config/portal.csv` |
| Sobre os dados | O catálogo de `dim_flag` inteiro, as etapas do projeto e o link para esta documentação | nenhum |

Use `DS_OBSERVACOES` como tooltip de cada barra ou ponto, para que a explicação apareça ao passar
o mouse. Deixe um botão de detalhamento em cada visual, levando para "Entenda os dados" com o
contexto de instituição e ano já filtrado. Assim nada passa batido: quem vê um número que foi
tratado de forma diferente tem, a um clique, a explicação dele.

## 8. Registro de decisões

| ID | Decisão | Status | Data |
| --- | --- | --- | --- |
| [D01](#d01--a-base-oficial-não-muda-e-a-exclusão-é-por-análise) | A base oficial não muda; exclusão é por análise | Decidida | 2026-09-20 |
| [D02](#d02--ead-no-mapa-só-a-regra-estreita-exclui) | EaD no mapa: só a regra estreita exclui | Decidida | 2026-09-20 |
| [D03](#d03--vagas-excluir-a-ies-e-o-ano-inteiros) | Vagas: excluir a IES e o ano inteiros | Decidida, com alto impacto | 2026-09-20 |
| [D04](#d04--concorrência-não-é-publicada) | Concorrência (inscritos por vaga) não é publicada | Decidida | 2026-09-20 |
| [D05](#d05--as-tabelas-prontas-são-versionadas) | As tabelas prontas são versionadas | Decidida | 2026-09-20 |
| [D06](#d06--nenhuma-ies-é-removida-por-inteiro-por-padrão) | Nenhuma IES é removida por inteiro por padrão | Decidida | 2026-09-20 |
| [D07](#d07--inscritos-zerados-saem-da-análise-de-inscritos) | Inscritos zerados saem da análise de inscritos | Proposta, a confirmar | 2026-09-20 |
| [D08](#d08--presença-territorial-como-análise-própria) | Presença territorial como análise própria | Proposta, a confirmar | 2026-09-20 |
| [D09](#d09--evasão-só-contagens-absolutas) | Evasão: só contagens absolutas | Decidida, herdada | 2026-09-20 |
| [D10](#d10--matriz-inicial-de-tratamentos) | Matriz inicial de tratamentos | Proposta, a confirmar | 2026-09-20 |
| [D11](#d11--transparência-por-registro) | Transparência por registro, com gravidade pelo efeito | Proposta, a confirmar | 2026-09-20 |
| [D12](#d12--nome-do-curso-contra-rótulo-só-os-casos-divergentes) | Nome contra rótulo: só os casos divergentes | Proposta, a confirmar | 2026-09-20 |
| [D13](#d13--o-projeto-é-alimentado-ao-longo-do-tempo) | O projeto é alimentado ao longo do tempo | Proposta, a confirmar | 2026-09-20 |

Cada decisão abaixo tem os mesmos campos: o que foi decidido, por quê, o que foi descartado,
como reverter e quando vale rever.

### D01 — A base oficial não muda e a exclusão é por análise

- **Decisão:** as planilhas oficiais seguem com todo o recorte. Achados viram flags, e exclusão
  é uma coluna `IN_USO_<ANÁLISE>`, nunca a remoção de linha.
- **Por quê:** a curadoria foi feita para decidir caso a caso como apresentar os dados. Como a
  base fica intacta, qualquer decisão pode ser revista rodando o script de novo, sem perda.
- **Descartado:** gerar planilhas já filtradas e apagar os registros suspeitos. Perde
  rastreabilidade e obriga a refazer tudo quando alguém discorda.
- **Como reverter:** não se aplica. É o princípio que torna as demais decisões reversíveis.

### D02 — EaD no mapa: só a regra estreita exclui

- **Decisão:** `FL_EAD_DISTRIB_ATIPICA`, com 220 curso-anos, exclui do mapa e da presença
  territorial. `FL_EAD_MUNICIPIOS_ZERADOS_AMPLA`, com 560, só sinaliza.
- **Por quê:** a regra ampla marca 9,7% das matrículas e pega cursos grandes e normais, como o
  ADS do Leonardo da Vinci em 2024, que a própria curadoria descreve como distribuição ampla
  normal. Dos 560 casos, 419 nem passam na regra estreita. A estreita marca 0,5% das matrículas.
  No mapa ela deixa de fora 4.755 linhas municipais e 32.575 matrículas.
- **Descartado:** excluir pela regra ampla, que tiraria do mapa quase 10% das matrículas,
  sobretudo de cursos legítimos.
- **Como reverter:** em `config/matriz_flag_uso.csv`, na linha `FL_EAD_MUNICIPIOS_ZERADOS_AMPLA`,
  trocar `sinalizar` por `excluir` nas colunas `MAPA_MUN` e `PRESENCA`. Para não excluir ninguém,
  na linha `FL_EAD_DISTRIB_ATIPICA` trocar `excluir` por `sinalizar`. Depois rodar o script.
- **Rever quando:** alguém mostrar que um curso excluído tem distribuição legítima, ou que um
  curso mantido é problemático. Para casos isolados, usar uma exceção manual (seção 10).

### D03 — Vagas: excluir a IES e o ano inteiros

- **Decisão:** na análise `VAGAS`, todos os cursos de uma IES num ano em que houve repetição de
  vagas ficam de fora (`FL_VAGAS_IES_ANO_SUSPEITO`). A flag por linha, `FL_VAGAS_REPETIDAS`,
  só sinaliza.
- **Por quê:** valor idêntico em quatro ou mais cursos indica capacidade institucional lançada
  em vários cursos. Os demais cursos da mesma IES no ano não têm por que ser mais confiáveis.
- **Impacto, o maior de todas as decisões:** saem 5.534 curso-anos, 12,7% das linhas, e
  **28,3% do volume declarado de vagas**, entre 21% e 44% conforme o ano. Do volume excluído,
  82% é EaD e 53% é só a UNIP.
- **Descartado:** excluir apenas as linhas com o valor repetido, 2.096 curso-anos e 6,0% do
  volume. Perde menos dado, mas deixa passar os outros cursos das mesmas IES.
- **Como reverter:** em `config/matriz_flag_uso.csv`, coluna `VAGAS`, trocar `excluir` por
  `sinalizar` na linha `FL_VAGAS_IES_ANO_SUSPEITO`. Para a alternativa por linha, trocar também
  `sinalizar` por `excluir` na linha `FL_VAGAS_REPETIDAS`.
- **Rever quando:** houver discordância sobre publicar vagas. **É a decisão a rever primeiro**,
  porque muda o resultado mais do que qualquer outra.

### D04 — Concorrência não é publicada

- **Decisão:** não publicar inscritos por vaga como indicador. `INSCRITOS` existe só como
  análise exploratória, com `FL_INSCRITO_IGUAL` sinalizando.
- **Por quê:** o numerador e o denominador têm problema. Há 3.457 curso-anos com inscritos
  iguais a vagas ou ingressantes, 6,9% das matrículas, 4.333 com inscritos zerados e vagas
  repetidas em 2.096. A razão herdaria todos os defeitos.
- **Descartado:** publicar a concorrência excluindo os registros flagrados. Sobraria uma
  amostra enviesada, que não representa o conjunto.
- **Como reverter:** mudar `PUBLICAR` em `config/usos.csv` e escrever a nova decisão aqui,
  definindo quais flags passam a excluir.

### D05 — As tabelas prontas são versionadas

- **Decisão:** `data/processed/analise/*.csv` entram no git, como as planilhas oficiais. A
  municipal usa colunas reduzidas: os nomes de IES e curso vêm da `fato_curso_ano` por
  `CH_CURSO_ANO`.
- **Por quê:** o Power BI puxa dos arquivos, e assim qualquer pessoa os obtém sem rodar o
  pipeline, que exige 11 GB de dados brutos.
- **Descartado:** gerar só localmente. Cada pessoa teria de reconstruir tudo.
- **Como reverter:** apagar as duas linhas de `data/processed/analise` do `.gitignore` e
  remover a pasta do índice do git.

### D06 — Nenhuma IES é removida por inteiro por padrão

- **Decisão:** não há exclusão de instituição inteira. Se alguma for necessária, entra como
  exceção manual, com justificativa (seção 10).
- **Por quê:** as maiores ocorrências, UNIP em vagas repetidas e Anhanguera em EaD atípico,
  respondem por cerca de um sexto do total de cada regra. As regras por linha e por IES e ano
  já tratam esses casos com mais precisão.
- **Descartado:** uma lista fixa de IES excluídas, que esconderia também os cursos corretos.
- **Como reverter:** adicionar uma linha em `config/decisoes_manuais.csv`.

### D07 — Inscritos zerados saem da análise de inscritos

- **Decisão:** `FL_INSCRITO_ZERO` exclui da análise `INSCRITOS`.
- **Por quê:** são 4.333 curso-anos, 10,5% das linhas fora de 2017, e em 389 há ingressantes
  positivos. Um zero pode ser campo não informado, e puxa médias de demanda para baixo.
- **Impacto:** 4.333 linhas e nenhum volume, pois zero não soma.
- **Descartado:** só sinalizar. Manteria os zeros nas médias.
- **Como reverter:** na linha `FL_INSCRITO_ZERO`, coluna `INSCRITOS`, trocar `excluir` por
  `sinalizar`.
- **Status:** proposta, ainda a confirmar.

### D08 — Presença territorial como análise própria

- **Decisão:** contar municípios com oferta é a análise `PRESENCA`. Só conta o município com
  matrícula positiva, e o EaD de distribuição atípica sai.
- **Por quê:** o problema de origem é a instituição lançar a matrícula num único polo e manter
  os demais municípios cadastrados sem alunos. Contar municípios cadastrados infla a presença.
  A regra tira 59.246 linhas municipais sem matrícula, 19% do total, e mais 1.367 por
  distribuição atípica.
- **Ressalva:** município associado não prova polo físico.
- **Como reverter:** em `config/usos.csv`, trocar `EXIGE_MAT_POSITIVA` por `nao`, ou remover a
  análise da configuração.
- **Status:** proposta, ainda a confirmar.

### D09 — Evasão: só contagens absolutas

- **Decisão:** `EVASAO_SIT` publica contagens absolutas de desvinculados e trancados e nunca
  uma razão com matrículas. Ficam de fora os curso-anos em que a matrícula não é confiável:
  zero, lacuna, ou zero com ingressantes. São 1.361 curso-anos e 0,5% dos desvinculados.
- **Por quê:** a razão desvinculados por matrículas passa de 1 em 2.482 curso-anos, pois compara
  um fluxo anual com um estoque. Uma taxa de coorte ainda não foi definida. Decisão herdada da
  [etapa 1](01_recorte.md), agora registrada aqui.
- **Como reverter:** quando a taxa de evasão for definida, registrar uma nova decisão e criar a
  análise correspondente.

### D10 — Matriz inicial de tratamentos

- **Decisão:** a matriz da seção 4 é a regra vigente. Foi proposta com um critério único, e o
  modelo foi aprovado, mas as células ainda não foram revistas uma a uma.
- **Critério usado:** excluir só quando manter distorce o resultado da análise. Sinalizar quando
  o leitor precisa saber. Deixar vazio quando não há relação. Matrícula zero exclui em análises
  que dependem da matrícula do ano, como evasão e trajetória de curso, e só sinaliza em séries
  agregadas, onde o efeito é pequeno.
- **Como reverter:** editar a célula em `config/matriz_flag_uso.csv` e rodar o script. Qualquer
  célula pode ser revista a qualquer momento.
- **Status:** proposta, revisar célula a célula.

### D11 — Transparência por registro

- **Decisão:** cada observação vira uma explicação em português simples, com os números do
  próprio caso, e nenhum registro tratado de forma diferente fica sem explicação. A gravidade é
  derivada do efeito real na matriz: Alerta quando o dado fica de fora de algum gráfico, Atenção
  quando aparece com aviso, Informação quando só contextualiza. Os textos ficam em
  `config/textos_flags.csv`. Exceções manuais também aparecem nas ocorrências.
- **Por quê:** o objetivo é que a própria instituição entenda o que foi observado e o que foi
  tratado de forma diferente no painel, sem acusação. Como o texto e a gravidade nascem da matriz,
  mudar uma regra atualiza a explicação sozinha e nunca há contradição entre o que o painel diz e
  o que faz.
- **Descartado:** escrever as explicações à mão por instituição, que envelheceria a cada ano,
  e usar só os códigos das flags, que ninguém de fora entende.
- **Como reverter:** editar o texto em `config/textos_flags.csv`. Para mudar a gravidade, mudar a
  matriz.
- **Status:** proposta, a confirmar.

### D12 — Nome do curso contra rótulo: só os casos divergentes

- **Decisão:** `FL_NOME_ROTULO_DIVERGENTE` marca os 36 curso-anos que a curadoria julgou
  divergentes, e não os 58 da triagem automática. Os 22 curso-anos que a curadoria considerou
  compatíveis, por nome composto ou histórico, ficam só no extrato.
- **Por quê:** marcar como divergente um curso que a própria curadoria julgou compatível
  seria acusar a instituição sem base, o que o painel não pode fazer.
- **Como reverter:** trocar o resultado do curso em `config/curadoria_nome_rotulo.csv`.
- **Status:** proposta, a confirmar.

### D13 — O projeto é alimentado ao longo do tempo

- **Decisão:** os anos processados ficam registrados em `config/anos.csv`, lidos por todos os
  scripts. Trazer um ano novo é o comando descrito na [etapa 4](04_novos_anos.md), com checagem
  prévia do layout do INEP e checagem de continuidade entre anos, que barram um ano quebrado.
- **Por quê:** o projeto foi feito para receber cada novo Censo. Sem essas checagens, uma mudança
  de layout do INEP poderia produzir um ano quase vazio sem nenhum erro.
- **Descartado:** editar listas de anos no código a cada ano, o que exige programar e não avisa
  quando algo dá errado.
- **Como reverter:** apagar a linha do ano em `config/anos.csv`.
- **Status:** proposta, a confirmar.

## 9. Como rever uma decisão

1. Registre a discordância e o motivo, de preferência com um caso concreto.
2. Edite o arquivo certo em `config/`: a matriz para mudar o tratamento de uma flag, `usos.csv`
   para mudar uma análise, `textos_flags.csv` para mudar uma explicação, ou `decisoes_manuais.csv`
   para uma exceção pontual.
3. Rode `.venv/bin/python scripts/gerar_camada_analise.py` e depois
   `.venv/bin/python scripts/gerar_transparencia.py`. O script valida a configuração e recusa
   flags, análises ou tratamentos desconhecidos.
4. Compare `cobertura_uso.csv` antes e depois. A mudança precisa caber no que se quer.
5. Atualize a decisão na seção 8, com o novo status e a data, e acrescente uma linha ao
   histórico da seção 12.
6. Faça o commit da configuração junto com as tabelas regeneradas.

Como a base oficial não muda, rever uma decisão nunca exige refazer o recorte nem a curadoria.

## 10. Exceções por instituição, curso ou ano

`config/decisoes_manuais.csv` guarda exceções pontuais, uma por linha:

| Coluna | Conteúdo |
| --- | --- |
| `CO_IES`, `CO_CURSO`, `NU_ANO_CENSO` | O que a exceção atinge. Vazio significa qualquer valor, mas ao menos `CO_IES` ou `CO_CURSO` é obrigatório |
| `USO` | A análise atingida, ou asterisco para todas |
| `ACAO` | `excluir` tira a linha da análise. `manter` traz de volta uma linha excluída por flag |
| `JUSTIFICATIVA`, `DATA`, `RESPONSAVEL` | Obrigatórias as duas primeiras |
| `DECISAO` | Referência opcional a uma decisão deste registro |

Exemplo ilustrativo, que não é uma decisão real, para tirar a UNIP do mapa em 2023:

```text
322;;2023;MAPA_MUN;excluir;Distribuição municipal não confirmada com a IES;2026-09-20;nome;D06
```

`manter` nunca recupera uma linha "sem dado", porque o requisito da análise não se cumpre.
O arquivo `decisoes_manuais_aplicadas.csv` mostra quantas linhas cada exceção casou e alterou, e
cada exceção também aparece como uma ocorrência explicada em `ocorrencias.csv`.

## 11. Limites

- As flags são indícios. Nenhum achado foi confirmado com o INEP ou com as instituições.
- Excluir de uma análise não corrige o valor: só evita apresentá-lo onde ele distorce.
- Nenhuma taxa de evasão ou de concorrência é calculada.
- O mapa de EaD não cobre 2017 a 2019, pois o Censo não traz o detalhe municipal.
- Município associado a um curso EaD não prova polo físico nem residência dos alunos.
- O canal de contato do projeto para as instituições ainda não está definido. Quando estiver, é
  só preencher `CONTATO_PROJETO` em `config/portal.csv` e ele passa a aparecer no "o que fazer"
  de cada observação.

## 12. Histórico e pendências

| Data | Alteração | Decisões |
| --- | --- | --- |
| 2026-09-20 | Criação da etapa 3 e do registro, com as regras iniciais | D01 a D10 |
| 2026-09-20 | Transparência por registro e gravidade pelo efeito. Colunas `NV_ATENCAO_CURSO` e `DS_FLAGS_CURSO` da municipal viraram `NV_ATENCAO` e `DS_FLAGS`. `NV_ATENCAO` passou a ir de 0 a 3 | D11 |
| 2026-09-20 | Flag de nome contra rótulo corrigida de 58 para 36 curso-anos | D12 |
| 2026-09-20 | Etapa 4: registro de anos, checagem prévia e continuidade | D13 |

**Pendências:**

- Confirmar ou rejeitar D07, D08, D10, D11, D12 e D13, hoje propostas.
- Revisar a matriz célula a célula e fechar a D10.
- Definir o canal de contato do projeto em `config/portal.csv`.
- Revisar a D03 primeiro se houver discordância sobre publicar vagas.
- Definir a taxa de evasão de coorte, o que abre uma nova análise.
