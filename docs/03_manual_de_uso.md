# Etapa 3: manual de uso

Terceira etapa do fluxo. Pega os achados da [curadoria](02_curadoria.md) e decide, caso a
caso, como cada um afeta cada análise. O resultado são tabelas prontas para o Power BI, com
flags e colunas de uso, e um registro escrito de todas as decisões, que pode ser revisto
a qualquer momento.

```text
dados do INEP  ->  1. recorte  ->  2. curadoria  ->  3. manual de uso  ->  Power BI
                   (01_recorte)     (02_curadoria)    (este documento)
```

## Princípios

1. **A base oficial nunca muda.** As planilhas oficiais guardam todo o recorte, com todos os
   valores declarados. Nada aqui apaga linha nem corrige valor.
2. **Exclusão é por análise, não global.** Uma flag só tira uma linha de uma análise quando a
   matriz diz "excluir" para aquele par. A mesma linha continua valendo nas outras análises.
3. **Todo achado da curadoria vira flag.** Se um registro é suspeito, ele carrega a marca, e
   qualquer visual pode mostrá-la.
4. **Excluir sempre informa a cobertura.** Cada análise diz quantas linhas e quanto volume
   deixou de fora, e nunca trata o excluído como zero.
5. **Toda decisão é escrita e pode ser revista.** O registro está na [seção 5](#5-registro-de-decisões),
   com o motivo, a alternativa descartada e como reverter.

## 1. As tabelas prontas

Ficam em `data/processed/analise/`, geradas por `scripts/gerar_camada_analise.py` a partir das
planilhas oficiais, dos extratos da curadoria e dos arquivos de `config/`.

| Arquivo | Grão | Para que serve |
| --- | --- | --- |
| `fato_curso_ano.csv` | um curso por ano, 43.477 linhas | Contagem, séries, vagas, inscritos, situações acadêmicas e classificação. É a planilha principal com flags |
| `fato_municipio_ano.csv` | um curso por ano e município, 309.291 linhas | Mapas e presença territorial. Só linhas municipais mapeáveis |
| `dim_flag.csv` | uma linha por flag | Catálogo: nível, fonte e descrição |
| `dim_uso.csv` | uma linha por análise | Catálogo das nove análises |
| `matriz_flag_uso.csv` | flag por análise | O tratamento de cada flag em cada análise, em formato longo |
| `cobertura_uso.csv` | análise, ano e modalidade | Quanto cada análise usa, exclui e não tem |
| `decisoes_manuais_aplicadas.csv` | uma linha por exceção manual e análise | Efeito das exceções de `config/decisoes_manuais.csv` |

**Colunas que importam:**

| Coluna | Como usar |
| --- | --- |
| `IN_USO_<ANÁLISE>` | 1 quando a linha pode entrar naquela análise. É o filtro principal |
| `FL_<ACHADO>` | 1 quando o achado se aplica ao registro |
| `DS_FLAGS` | Lista das flags do registro, separadas por barra vertical. Boa para tooltip |
| `NV_ATENCAO` | 0 sem nota, 1 só notas, 2 ao menos uma suspeita. Serve para destaque, não como filtro |
| `CH_CURSO_ANO` | Chave ano, IES e curso. Relaciona a municipal à `fato_curso_ano`, muitos para um |
| `CH_SERIE_CURSO` | Chave IES e curso. Usar para seguir um curso no tempo |

**Cinco regras práticas:**

- Conte cursos e IES pela `fato_curso_ano`. Nunca conte linhas da municipal.
- Filtre sempre pelo `IN_USO_` da análise que está fazendo. Usar o filtro de outra análise muda o sentido do número.
- Na municipal, vagas e inscritos ficam em branco para EaD. Branco significa "não se aplica", não zero.
- Para seguir um curso ao longo dos anos, use `CH_SERIE_CURSO`, nunca `CO_CURSO` sozinho.
- `NV_ATENCAO` igual a 2 cobre cerca de 30% das linhas, sobretudo por vagas e inscritos. Não o use como filtro.

## 2. As nove análises

| Análise | Pergunta que responde | Tabela | Publicar | Requisito além das flags |
| --- | --- | --- | --- | --- |
| `CONTAGEM` | Quantos cursos e IES existem por ano? | curso e ano | sim | Para cursos em atividade, acrescentar `QT_MAT` maior que zero |
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

## 3. Matriz de tratamento

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

A fonte da verdade é `config/matriz_flag_uso.csv`. Esta tabela é uma cópia para leitura. A matriz
inicial é uma proposta ([D10](#d10--matriz-inicial-de-tratamentos)): o modelo foi aprovado, mas as
células ainda precisam de revisão.

## 4. Impacto medido em 2026-09-20

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

Dois pontos de atenção. O volume de vagas é o que mais perde, e a razão está na decisão D03.
E os 3,7% de matrículas sem território no mapa são o EaD de 2017 a 2019, que o Censo não
detalha por município e não pode ser mapeado por nenhuma regra.

## 5. Registro de decisões

| ID | Decisão | Status | Data |
| --- | --- | --- | --- |
| [D01](#d01--a-base-oficial-não-muda-e-a-exclusão-é-por-análise) | A base oficial não muda; exclusão é por análise | Decidida | 2026-09-20 |
| [D02](#d02--ead-no-mapa-só-a-regra-estreita-exclui) | EaD no mapa: só a regra estreita exclui | Decidida | 2026-09-20 |
| [D03](#d03--vagas-excluir-o-ies-e-ano-inteiros) | Vagas: excluir a IES e o ano inteiros | Decidida, com alto impacto | 2026-09-20 |
| [D04](#d04--concorrência-não-é-publicada) | Concorrência (inscritos por vaga) não é publicada | Decidida | 2026-09-20 |
| [D05](#d05--as-tabelas-prontas-são-versionadas) | As tabelas prontas são versionadas | Decidida | 2026-09-20 |
| [D06](#d06--nenhuma-ies-é-removida-por-inteiro-por-padrão) | Nenhuma IES é removida por inteiro por padrão | Decidida | 2026-09-20 |
| [D07](#d07--inscritos-zerados-saem-da-análise-de-inscritos) | Inscritos zerados saem da análise de inscritos | Proposta, a confirmar | 2026-09-20 |
| [D08](#d08--presença-territorial-como-análise-própria) | Presença territorial como análise própria | Proposta, a confirmar | 2026-09-20 |
| [D09](#d09--evasão-só-contagens-absolutas) | Evasão: só contagens absolutas | Decidida, herdada | 2026-09-20 |
| [D10](#d10--matriz-inicial-de-tratamentos) | Matriz inicial de tratamentos | Proposta, revisar célula a célula | 2026-09-20 |

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
  curso mantido é problemático. Para casos isolados, usar uma exceção manual (seção 7).

### D03 — Vagas: excluir o IES e ano inteiros

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
  pipeline, que exige 11 GB de dados brutos. Ocupam 33 MB e 44 MB.
- **Descartado:** gerar só localmente. Cada pessoa teria de reconstruir tudo.
- **Como reverter:** apagar as duas linhas de `data/processed/analise` do `.gitignore` e
  remover a pasta do índice do git.

### D06 — Nenhuma IES é removida por inteiro por padrão

- **Decisão:** não há exclusão de instituição inteira. Se alguma for necessária, entra como
  exceção manual, com justificativa (seção 7).
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
- **Status:** proposta minha, ainda não confirmada.

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
- **Status:** proposta minha, ainda não confirmada.

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

- **Decisão:** a matriz da seção 3 é o ponto de partida. O modelo foi aprovado, mas as células
  foram propostas sem revisão individual.
- **Critério usado:** excluir só quando manter distorce o resultado da análise. Sinalizar quando
  o leitor precisa saber. Deixar vazio quando não há relação. Matrícula zero exclui em análises
  que dependem da matrícula do ano, como evasão e trajetória de curso, e só sinaliza em séries
  agregadas, onde o efeito é pequeno.
- **Como reverter:** editar a célula em `config/matriz_flag_uso.csv` e rodar o script.
- **Status:** proposta, revisar célula a célula.

## 6. Como rever uma decisão

1. Registre a discordância e o motivo, de preferência com um caso concreto.
2. Edite o arquivo certo em `config/`: a matriz para mudar o tratamento de uma flag, `usos.csv`
   para mudar uma análise, ou `decisoes_manuais.csv` para uma exceção pontual.
3. Rode `.venv/bin/python scripts/gerar_camada_analise.py`. O script valida a configuração e
   recusa flags, análises ou tratamentos desconhecidos.
4. Compare `cobertura_uso.csv` antes e depois. A mudança precisa caber no que se quer.
5. Atualize a decisão na seção 5, com o novo status e a data, e acrescente uma linha ao
   histórico da seção 9.
6. Faça o commit da configuração junto com as tabelas regeneradas.

Como a base oficial não muda, rever uma decisão nunca exige refazer o recorte nem a curadoria.

## 7. Exceções por instituição, curso ou ano

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
O arquivo `decisoes_manuais_aplicadas.csv` mostra quantas linhas cada exceção casou e alterou.

## 8. Limites

- As flags são indícios. Nenhum achado foi confirmado com o INEP ou com as instituições.
- Excluir de uma análise não corrige o valor: só evita apresentá-lo onde ele distorce.
- Nenhuma taxa de evasão ou de concorrência é calculada.
- O mapa de EaD não cobre 2017 a 2019, pois o Censo não traz o detalhe municipal.
- Município associado a um curso EaD não prova polo físico nem residência dos alunos.

## 9. Histórico e pendências

| Data | Alteração | Decisões |
| --- | --- | --- |
| 2026-09-20 | Criação da etapa 3 e do registro, com as regras iniciais | D01 a D10 |

**Pendências:**

- Revisar a matriz célula a célula e fechar a D10.
- Confirmar ou rejeitar D07 e D08.
- Revisar a D03 primeiro se houver discordância sobre publicar vagas.
- Definir a taxa de evasão de coorte, o que abre uma nova análise.
