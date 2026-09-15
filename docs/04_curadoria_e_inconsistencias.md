# Curadoria e inconsistências

Guia prático para quem vai montar uma consulta, um gráfico ou um filtro em cima
das planilhas oficiais. Cada item abaixo diz o que foi encontrado, mostra um
exemplo real (sem precisar abrir a planilha) e recomenda o que fazer. O recorte
e os valores oficiais não foram alterados por esta curadoria; toda observação
fica registrada como nota, não como correção.

A chave de identificação usada em todo o documento é **ano + IES + curso**
(`CO_CURSO` sozinho não identifica uma categoria — é só o código de uma oferta
específica; duas ofertas completamente diferentes podem reutilizar o mesmo
número em anos que não se sobrepõem, como no item 3.2).

## Classificação usada

| Nível | Significa | O que fazer |
| --- | --- | --- |
| **Estrutural** | Não é erro de preenchimento. É assim que o Censo organiza o dado, e ignorar isso produz número errado ou sem sentido. | Aplicar a regra sempre, antes de qualquer análise no tema. |
| **Suspeito** | O valor declarado parece estranho (repetido, copiado, zerado, concentrado), mas não há confirmação externa de erro. | Decidir caso a caso; documentar quando um registro específico for excluído ou ressalvado. |
| **Baixo impacto** | Foi encontrado e catalogado, mas não muda contagens nem exige tratamento especial na maioria das análises. | Ciente; sem ação obrigatória. |

## Resumo por tema

| Tema | Nível | Onde afeta |
| --- | --- | --- |
| Vagas/inscritos de EaD só na linha nacional | Estrutural | Mapas de vagas/inscritos por município |
| "Taxa de evasão" pronta não existe | Estrutural | Qualquer indicador de evasão |
| Grão diferente entre principal e expandida | Estrutural | Contagem de cursos vs. mapas |
| Vagas repetidas entre cursos da mesma IES | Suspeito | Somas/comparações de `QT_VG_TOTAL` |
| Inscritos idênticos a vagas ou a ingressantes | Suspeito | Qualquer uso de `QT_INSCRITO_TOTAL` |
| Matrícula cai a zero, ou zerada com ingresso positivo | Suspeito | Séries históricas por curso |
| Concentração ou vazio territorial atípico em EaD | Suspeito | Mapas municipais |
| Nome do curso não bate com o rótulo de área | Suspeito | Agrupamento por tipo de curso |
| Rótulo "em processo de definição" (2024) | Suspeito | Classificação de cursos de 2024 |
| Grafia do nome muda ao longo dos anos | Baixo impacto | Nenhuma, se usar `CO_CURSO` para juntar anos |
| Código de curso reaparece em outra IES | Baixo impacto | Histórico de série ligado só por `CO_CURSO` |
| Rótulo de área muda de descrição entre anos | Baixo impacto | Agrupamento por rótulo em janelas longas |
| Sigla da IES ausente | Baixo impacto | Nenhuma; `CO_IES`/`NO_IES` já identificam a instituição |

---

## 1. Estrutural — considerar sempre

### 1.1 Vagas e inscritos de EaD só existem numa linha nacional, sem cidade

Nos cursos a distância, o Censo pede vaga e inscrito **uma vez por curso**, não
por polo. Na planilha expandida isso aparece como uma linha "EaD somente nível
Brasil" (`TP_DIMENSAO = 3`), sem UF nem município. Ingressante, matrícula e
concluinte, ao contrário, são declarados por município e por isso aparecem
zerados nessa linha nacional.

**Exemplo:** no curso de ADS EaD da Unifecaf (`CO_IES` 17.854, `CO_CURSO`
1.454.503) em 2024, o município de Taboão da Serra aparece com 1.508
matrículas e 1.854 ingressantes, mas vagas e inscritos zerados. A linha
nacional do mesmo curso/ano mostra 6.700 vagas e 3.461 inscritos, com 0
matrícula. Os dois pedaços são o mesmo curso — nenhum dos dois está "errado".

**Observação prática:** um mapa de matrícula ou ingressante por município é
confiável. Um mapa de vaga ou inscrito por município fica sempre zerado ou
incompleto, porque esse dado nunca teve endereço no Censo. Use `TP_DIMENSAO`
para separar as duas coisas, ou filtre por `IN_USAR_MAPA_MUNICIPAL = True` e
mapeie apenas `QT_ING`, `QT_MAT` e `QT_CONC`.

### 1.2 Não existe uma "taxa de evasão" pronta na base

`QT_SIT_DESVINCULADO` é um número de alunos que saíram **naquele ano**
(fluxo). `QT_MAT` é quantos alunos estão matriculados **naquele ano**
(estoque, incluindo quem entrou havia anos). Dividir um pelo outro não mede a
evasão de uma turma que entrou junto — mede duas fotografias diferentes do
mesmo curso.

**Exemplo:** eram 2.482 curso-anos com `QT_SIT_DESVINCULADO / QT_MAT` maior
que 1 — ou seja, mais gente "saiu" no ano do que o total de matriculados
naquele mesmo ano. Isso não é impossível nem é erro: mostra que as duas
grandezas contam populações diferentes.

**Observação prática:** por isso a razão foi retirada das planilhas oficiais
(detalhes em [Validação e qualidade](03_validacao_qualidade.md)). Os campos
`QT_SIT_DESVINCULADO`, `QT_SIT_TRANCADA` e `QT_MAT` continuam disponíveis
separadamente; qualquer indicador de evasão precisa de uma definição de
coorte (acompanhar quem entrou junto ao longo dos anos), que ainda não foi
feita.

### 1.3 A planilha principal e a expandida contam coisas diferentes

A principal tem uma linha por curso (ano + IES + curso). A expandida tem uma
linha por curso **e** território — um curso EaD grande pode ter centenas de
linhas territoriais para um único curso na principal.

**Exemplo:** o ADS EaD do Leonardo da Vinci (`CO_CURSO` 1.266.797) é **1**
linha na principal em 2024, com 13.896 matrículas. Na expandida, o mesmo
curso/ano tem **933** linhas municipais.

**Observação prática:** conte cursos e IES pela principal. Use a expandida só
para distribuir uma métrica já territorializável (`QT_ING`, `QT_MAT`,
`QT_CONC`) num mapa, relacionando as duas por `NU_ANO_CENSO + CO_IES +
CO_CURSO`. Contar linhas da expandida infla artificialmente o número de
cursos.

---

## 2. Suspeito — decidir caso a caso

### 2.1 Vagas repetidas entre vários cursos da mesma IES

Quando uma IES declara o **mesmo número exato** de vagas em quatro ou mais
cursos de Computação no mesmo ano, é provável que o número represente uma
capacidade institucional (ex.: "vagas do processo seletivo geral"), e não uma
vaga pensada curso a curso.

**Exemplo:** em 2013, a UNIP declarou `QT_VG_TOTAL = 230` em **52** dos seus
97 cursos de Computação. Em 2011, declarou `QT_VG_TOTAL = 460` em 31 cursos.

**Observação prática:** isso é relativamente inconsistente porque infla a
soma nacional/regional de vagas sem que exista 52 processos seletivos
distintos de 230 vagas cada — a repetição não prova duplicidade, mas também
não é uma vaga real por curso. Evite somar `QT_VG_TOTAL` entre cursos de uma
mesma IES para estimar "capacidade de oferta"; lista completa em
[`04_vagas_repetidas_por_ies_ano.csv`](../data/processed/curadoria/04_vagas_repetidas_por_ies_ano.csv)
(326 grupos IES/ano).

### 2.2 Inscritos idênticos a vagas ou a ingressantes

`QT_INSCRITO_TOTAL` deveria vir de um processo seletivo (gente que se
candidatou, nem todos entram). Quando esse número é **exatamente igual** à
vaga ofertada ou ao número de ingressantes, é provável que o campo tenha sido
preenchido por cópia, não por contagem de candidatos.

**Exemplo:** em 2024, os cinco cursos de Computação da Uniasselvi (unidades
de Blumenau e Brusque) têm inscrito igual à vaga, ao ingressante, ou aos dois
ao mesmo tempo (ex.: Engenharia de Software de Blumenau — vaga 25, inscrito
25, ingressante 25).

**Observação prática:** isso é relativamente inconsistente porque um
processo seletivo real quase nunca tem exatamente zero desistência entre
inscrito e ingressante, curso após curso. Ainda assim, a igualdade isolada
não prova erro (pode ser vaga única sem concorrência). Não use
`QT_INSCRITO_TOTAL` como medida de demanda sem checar o registro; lista
completa (3.457 curso-anos) em
[`05_igualdades_inscritos.csv`](../data/processed/curadoria/05_igualdades_inscritos.csv).

### 2.3 Matrícula que cai a zero, ou fica zerada com ingresso positivo

Um curso pode aparecer com `QT_MAT = 0` num ano e voltar a ter matrícula no
ano seguinte, às vezes com ingressante, trancamento ou desvinculação positivos
no mesmo ano zerado — sinal de que o curso continuou existindo administrativamente,
mesmo sem estoque de matrícula declarado.

**Exemplos (matrícula no ano anterior / no ano zerado / no ano seguinte):**

| IES / curso | Sequência de MAT | O que mais aparece no ano zerado |
| --- | --- | --- |
| UFRPE, Engenharia de Computação | 178 → 0 → 198 (2023) | 33 ingressantes, 193 trancados, 10 desvinculados |
| Universidade Salvador, Sistemas de Informação | 113 → 0 → 100 (2021) | 95 desvinculados |
| UNIP, ADS | 108 → 0 → 51 (2022) | 17 ingressantes, 5 trancados, 63 desvinculados |
| Cândido Mendes, Redes de Computadores | 76 → 0 → 60 (2023) | 4 ingressantes, 92 desvinculados |
| Leonardo da Vinci, Telemedicina | 55 → 47 → 0 (2024, fim da série até aqui) | 6 ingressantes, 51 desvinculados |

**Observação prática:** isso é relativamente inconsistente porque não dá para
saber, só com esse dado, se é um erro de preenchimento num ano específico, uma
pausa real na oferta, ou uma migração de alunos para outro código de curso —
as três hipóteses são compatíveis com os números. **1.098** curso-anos têm
essa queda para zero entre anos consecutivos, e **371** têm matrícula zero com
ingressante positivo (356 deles com 1 a 19 ingressantes). Não trate o ano
zerado como ausência de dado nem preencha por média dos vizinhos — mantenha o
zero e, se a análise for sensível a isso, exclua o curso-ano específico com
nota. Casos completos em
[`13_vistoria_casos.csv`](../data/processed/curadoria/13_vistoria_casos.csv)
(regras `matriculas_caem_a_zero`, `zero_matriculas_com_ingresso*`).

### 2.4 Concentração ou vazio territorial atípico em EaD

Em cursos EaD com muitos municípios cadastrados, a distribuição pode virar de
um ano para o outro de forma abrupta, ou ficar concentrada quase toda num
único município, sem que o total do curso mude na mesma proporção.

**Exemplos:**

- **Unifecaf, ADS** (`CO_CURSO` 1.454.503): em 2023, 792 matrículas em 72
  municípios (17 zerados), 622 delas em Taboão da Serra. Em 2024, **todas**
  as 1.508 matrículas do curso aparecem em Taboão da Serra, entre 28
  municípios cadastrados (27 zerados).
- **Leonardo da Vinci, Agrocomputação** (`CO_CURSO` 1.551.528): cai de 733
  matrículas (2023) para 311 (2024); em 2024 são 361 municípios cadastrados,
  188 zerados, o maior com só 27 matrículas e 534 desvinculados no curso.
- **Ampli, Desenvolvimento Web** (`CO_CURSO` 1.582.601): cresce de 153 para
  180 matrículas entre 2023 e 2024, mas os municípios caem de 95 para 60; os
  que somem detinham 51,6% da matrícula de 2023.
- Por outro lado, o ADS do **Leonardo da Vinci** (`CO_CURSO` 1.266.797), com
  868–933 municípios e 13,9–14,9 mil matrículas em 2023–2024, tem só ~4% da
  matrícula no maior município — isso é distribuição ampla normal, não
  concentração.

**Observação prática:** isso é relativamente inconsistente porque uma IES às
vezes lança a matrícula real só no polo-sede e mantém os demais municípios
"cadastrados" sem atualizar, ou reorganiza os polos de um ano para o outro
sem que o Censo distinga reorganização de erro de preenchimento. O total do
curso (declarado na principal) continua confiável; **a distribuição
municipal, não**, nesses casos específicos. Evite comparações município a
município aqui sem checar o padrão primeiro; os critérios usados para marcar
esses casos estão na seção 4. Lista completa (79 casos de concentração, 560
de muitos municípios zerados, 34 mudanças bruscas de distribuição) nos
extratos
[`10`](../data/processed/curadoria/10_ead_distribuicao_municipal_atipica.csv),
[`13`](../data/processed/curadoria/13_vistoria_casos.csv) e
[`17`](../data/processed/curadoria/17_mudancas_distribuicao.csv).

### 2.5 Nome do curso não bate com o rótulo de área

O rótulo CINE/OCDE (`NO_ROTULO_AREA`) é uma classificação que o INEP atribui
ao curso; o nome (`NO_CURSO`) é como a instituição chama o curso. Às vezes os
dois divergem — uma Engenharia de Software rotulada como Sistemas de
Informação, por exemplo.

**Exemplos (2024):**

- UFAM, `CO_CURSO` 122.634: nome "Engenharia De Software", rótulo "Sistemas
  de informação" (`0613S01`).
- UFRA (`CO_IES` 590), `CO_CURSO` 1.110.857: nome "Sistemas De Informação",
  rótulo "Ciência da computação" (`0613C01`) — inclusive já se chamou
  "Informática" entre 2010 e 2016, sempre com esse mesmo rótulo.
- Leonardo da Vinci, `CO_CURSO` 1.617.841 ("Desenvolvimento De Aplicativos
  Móveis"): rótulo "Sistemas para internet" em 2023, e "em processo de
  definição" em 2024 (ver item 2.6). Matrícula cai de 188 para 91 no mesmo
  intervalo.

**Observação prática:** isso é relativamente inconsistente porque não dá para
saber, só com o dado, se o nome está errado, se o rótulo está errado, ou se
os dois estão certos e é o INEP tratando o curso como equivalente a outra
categoria por causa do projeto pedagógico. Todos os três continuam dentro do
recorte oficial (área geral de Computação/TIC). Para tipo de curso, use
`NO_CURSO`; para agrupar por área, use `NO_ROTULO_AREA`, sabendo que os dois
podem discordar. 21 códigos com esse padrão (34 combinações ano/rótulo) em
[`01_nome_curso_x_rotulo_divergente.csv`](../data/processed/curadoria/01_nome_curso_x_rotulo_divergente.csv).

### 2.6 Rótulo declarado "em processo de definição" (18 casos, todos em 2024)

Em 2024, 18 curso-anos receberam o rótulo `0619P01` — "Programas abrangendo
Computação e TIC em processo de definição da classificação". Todos são cursos
de "Desenvolvimento Mobile" ou "Desenvolvimento de Aplicativos Móveis", em 17
instituições diferentes (Positivo, Cesumar, Leonardo da Vinci, grupo
Anhanguera/Pitágoras/Unopar, entre outras).

**Observação prática:** isso é relativamente inconsistente porque a própria
fonte (INEP) ainda não decidiu em qual categoria esses cursos entram — não é
um erro do curso nem da instituição, é uma classificação provisória. Continue
tratando esses cursos como Computação/TIC (é por isso que entram no recorte),
mas não os agrupe com convicção dentro de uma subárea específica em 2024.
Lista completa nos casos `classificacao_em_definicao` de
[`13_vistoria_casos.csv`](../data/processed/curadoria/13_vistoria_casos.csv).

---

## 3. Baixo impacto — encontrado, catalogado, sem tratamento necessário

### 3.1 A grafia do nome do curso muda ao longo dos anos

1.885 códigos de curso têm mais de uma grafia de nome na série: sem acento
até 2009, com acento a partir de 2010, "Title Case" a partir de 2021 (ex.:
"CIENCIA DA COMPUTACAO" → "CIÊNCIA DA COMPUTAÇÃO" → "Ciência Da
Computação"). **Isso não afeta nada** se a análise agrupar por `CO_CURSO` em
vez de pelo texto do nome.

### 3.2 O mesmo código de curso reaparece em outra IES, sem sobreposição de anos

124 códigos de curso (`CO_CURSO`) aparecem sob mais de um `CO_IES` ao longo da
série — mas nunca no mesmo ano. Em alguns casos é claramente a mesma
linhagem institucional: o curso 107.964 esteve na Faculdade de Tecnologia
Empresarial em 2009 (`CO_IES` 1.228) e, a partir de 2010, na Faculdade Ruy
Barbosa, depois renomeada Centro Universitário Ruy Barbosa Wyden (`CO_IES`
396, mesmo código o tempo todo). Em outros casos a ligação é menos óbvia e a
base não tem como confirmar se é continuidade da mesma oferta ou
reaproveitamento do número do código pelo INEP para um curso novo e não
relacionado.

**Observação prática:** isso não muda nenhum total (nunca há duas linhas com
o mesmo ano + IES + curso), mas **não** dá para montar uma série histórica
confiável de um curso encadeando anos só por `CO_CURSO` quando o `CO_IES`
muda no meio — trate a mudança de `CO_IES` como um possível corte na série,
não como continuidade automática. Lista completa em
[`03_co_curso_em_varias_ies.csv`](../data/processed/curadoria/03_co_curso_em_varias_ies.csv).

### 3.3 O rótulo de área muda de descrição de um ano para o outro

402 códigos de curso trocam de rótulo CINE ao longo da série, sem que o nome
do curso mude. A maior parte é o próprio INEP reetiquetando a categoria (por
exemplo "Engenharia de computação" e "Engenharia de computação (DCN
Engenharia)" são a mesma coisa, com texto diferente). Em alguns casos raros o
rótulo muda de fato de categoria: o curso 1.292.285 (Ciência da Computação,
Escola de Engenharia/EMGE, depois Escola Superior Dom Helder Câmara) tinha
rótulo de Engenharia de Computação em 2019 e passou a ter rótulo de Ciência
da Computação — igual ao próprio nome do curso — a partir de 2020.

**Observação prática:** isso não afeta contagens de matrícula/ingressante,
só agrupamentos feitos exclusivamente pelo texto do rótulo em janelas de
vários anos. Lista completa em
[`02_co_curso_rotulo_muda_na_serie.csv`](../data/processed/curadoria/02_co_curso_rotulo_muda_na_serie.csv).

### 3.4 Sigla da instituição ausente

3.942 linhas não têm `SG_IES` preenchida (9 a 13% por ano). Isso não impede
identificar a instituição, porque `CO_IES` e `NO_IES` estão sempre presentes;
a sigla é um campo opcional do Censo.

---

## 4. O que já foi conferido e está limpo

Estas checagens rodam a cada execução da pipeline e não encontraram nenhum
caso — servem como garantia de que o problema descrito não é maior do que o
registrado acima.

| Verificação | Resultado |
| --- | --- |
| Negativos, fracionários ou textos inválidos nas nove métricas | 0 nas duas planilhas |
| Repetição de ano + IES + curso + município nas linhas de mapa | 0 |
| Prefixo municipal diferente do código de UF nas linhas de mapa | 0 |
| Concluinte acima de matrícula, ou ingressante acima da soma de matrícula e situações | 0 |
| Total da planilha principal diferente da soma da expandida, para qualquer métrica | 0 |
| Curso presente em só uma das duas planilhas | 0 |
| Duplicata na chave ano + IES + curso | 0 |
| Vaga/inscrito de EaD fora da linha nacional, ou indicador acadêmico de EaD só na linha nacional | 0 |

Além disso, **51 curso-anos de 2020 a 2024** foram comparados diretamente com
o arquivo bruto do INEP (não com um intermediário do pipeline): matrícula,
ingressante, concluinte, trancado, desvinculado, transferido e falecido
batem, município a município, com o que a instituição declarou originalmente.
Essa comparação confirma que a transformação dos dados está correta nesses
casos — não confirma que a instituição preencheu o Censo sem erro. Lista em
[`15_conferencia_fonte.csv`](../data/processed/curadoria/15_conferencia_fonte.csv).

A checagem de texto e os limiares numéricos usados nas seções 2 e 3 não
cobrem toda inconsistência possível: um caso pode ser suspeito mesmo sem
cruzar o limiar de uma regra (a concentração da Unifecaf em 2023, por
exemplo, já era alta antes de disparar a regra de mudança brusca), e a
checagem de prefixo município/UF não confere a tabela do IBGE nem confirma
vínculo físico de um curso a um endereço.

---

## 5. Evidências completas e como reproduzir

Todo achado acima tem um extrato correspondente em
`data/processed/curadoria/`, gerado por dois scripts que não alteram as
planilhas oficiais:

```bash
.venv/bin/python scripts/gerar_extratos_curadoria.py
.venv/bin/python scripts/vistoriar_conteudo.py
```

| Arquivo | Conteúdo |
| --- | --- |
| `01` a `12` | Nomes/rótulos, mudanças históricas, códigos/IES, valores repetidos, contradições estruturais, zeros, baixa atividade, interdisciplinaridade, distribuição EaD, disponibilidade e proxy OCDE de 2017 |
| [`13_vistoria_casos.csv`](../data/processed/curadoria/13_vistoria_casos.csv) | Cada ocorrência com chave, regra, evidência e status |
| [`14_vistoria_cobertura.csv`](../data/processed/curadoria/14_vistoria_cobertura.csv) | Quantidade por regra, incluindo as regras sem nenhuma ocorrência (seção 4) |
| [`15_conferencia_fonte.csv`](../data/processed/curadoria/15_conferencia_fonte.csv) | Comparação com o arquivo bruto do INEP, por município/dimensão |
| [`16_zeros_municipais_persistentes.csv`](../data/processed/curadoria/16_zeros_municipais_persistentes.csv) | Sequências de município com matrícula zero por 3 anos ou mais |
| [`17_mudancas_distribuicao.csv`](../data/processed/curadoria/17_mudancas_distribuicao.csv) | Mudanças bruscas de distribuição municipal entre anos consecutivos |

No total, a triagem passou pelas **43.477 linhas** da principal e **315.410**
da expandida (2009–2024) e registrou **4.919 ocorrências em 2.463 chaves**
ano + IES + curso — a maioria concentrada nas categorias já descritas nas
seções 2 e 3. São indícios para revisão, não erros comprovados; a checagem
por regra não substitui uma conferência manual de todas as linhas.

Os CSVs são recriados a cada execução; o texto deste documento é mantido à
parte e só muda quando alguém o edita. Passo a passo completo em
[Pipeline e reprodução](02_pipeline_e_reproducao.md).
