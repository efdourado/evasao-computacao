# Integração histórica

Este documento registra as decisões técnicas da integração dos microdados do INEP.

## Início oficial em 2009

A planilha oficial inicia em 2009 porque esse é o primeiro período em que a integração histórica se torna metodologicamente mais compatível com o recorte oficial de Computação/TIC.

O recorte oficial dos anos com CINE/CINE Brasil depende de:

```text
CO_CINE_AREA_GERAL = 6
OU
CO_CINE_ROTULO = 0714E04
```

Os microdados de 1995 a 2008 existem, mas usam estruturas antigas, códigos próprios e dicionários anteriores à padronização atual baseada em CINE. Integrar esses anos exigiria uma etapa específica de equivalência entre classificações antigas e o recorte atual.

Decisão atual: 1995-2008 não entram na planilha oficial. Esses dados foram removidos da pasta local `data/raw/` e só devem voltar se o projeto decidir fazer uma etapa histórica anterior a 2009.

## Regra de recorte

Para anos com CINE/CINE Brasil:

```text
CO_CINE_AREA_GERAL = 6
OU
CO_CINE_ROTULO = 0714E04
```

Essa regra inclui Computação/TIC pela área geral 6 e adiciona Engenharia de Computação pelo rótulo `0714E04`.

Para 2017:

```text
CO_OCDE_AREA_ESPECIFICA = 48
OU
CO_OCDE = 5.23E+06
```

2017 usa OCDE, então esse ano entra como aproximação histórica. A planilha oficial carrega `DS_NIVEL_COMPARABILIDADE` e `DS_OBSERVACAO_COMPARABILIDADE` para deixar isso explícito.

## Blocos de anos

| Período | Estrutura | Classificação | Status |
| --- | --- | --- | --- |
| 1995-1996 | `GRADUACAO_PRESENCIAL` + `INSTITUICAO` | área antiga | fora da base oficial atual |
| 1997-1999 | `GRADUACAO_PRESENCIAL` + `INSTITUICAO` | área antiga/campos codificados | fora da base oficial atual |
| 2000-2008 | `GRADUACAO_PRESENCIAL`, `GRADUACAO_DISTANCIA`, `FORME`, `SECOMPLE`, `INSTITUICAO` | área antiga/campos codificados | fora da base oficial atual |
| 2009-2016 | `MICRODADOS_CADASTRO_CURSOS` + `MICRODADOS_CADASTRO_IES` | CINE | integrado |
| 2017 | `DM_CURSO`, `DM_IES`, `TB_AUX_AREA_OCDE` | OCDE | integrado com proxy |
| 2018-2019 | `DM_CURSO`/`SUP_CURSO`, `DM_IES`/`SUP_IES`, `TB_AUX_CINE_BRASIL` | CINE Brasil | integrado |
| 2020-2024 | `MICRODADOS_CADASTRO_CURSOS` + IES | CINE | integrado |

## Bases geradas

### Base expandida

```text
data/processed/historico/computacao_historico_cursos.csv
```

Uso: mapas, UF, município, modalidade, `TP_DIMENSAO` e análises territoriais.

Tamanho atual:

```text
315.414 linhas
16 anos integrados: 2009-2024
```

### Base comparável

```text
data/processed/historico/computacao_historico_cursos_comparavel.csv
```

Uso: série histórica, contagem de cursos, comparação por IES/curso.

Chave lógica:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

Tamanho atual:

```text
43.481 linhas
```

## Duplicidade lógica

A partir de 2020, e principalmente em 2022-2024, o mesmo curso pode aparecer em várias linhas por dimensão/localização. Por isso existem duas camadas:

| Camada | Uso | Cuidado |
| --- | --- | --- |
| expandida | mapa e filtros territoriais | não contar linhas como cursos |
| comparável | série histórica por curso/IES | métricas somadas por chave lógica |

A validação fica em:

```text
data/processed/historico/validacao_historico_por_ano.csv
data/processed/historico/validacao_historico_metricas.csv
data/processed/historico/validacao_linhas_por_curso.csv
```

## Situação acadêmica

O projeto não mede evasão definitiva ainda. Ele organiza situação acadêmica:

```text
QT_SIT_TRANCADA
QT_SIT_DESVINCULADO
QT_SIT_TRANSFERIDO
QT_SIT_FALECIDO
```

Origem:

| Anos | Origem |
| --- | --- |
| 2009-2016 | cadastro de cursos |
| 2017-2019 | arquivos grandes de aluno (`DM_ALUNO`, `SUP_ALUNO_2019`) |
| 2020-2024 | cadastro de cursos |

O indicador `QT_SIT_DESVINCULADO / QT_MAT` é exploratório. Ele não deve ser apresentado como taxa final de evasão sem uma definição posterior.

## Anos 1995-2008

O script abaixo fica disponível apenas como utilitário opcional para o caso de recolocarmos os arquivos antigos em `data/raw/`:

```bash
.venv/bin/python scripts/13_inventariar_anos_antigos.py
```

Decisão atual:

* 1995-1996 têm campos explícitos de trancamento/abandono, mas exigem mapear a área antiga para Computação;
* 1997-1999 têm estrutura mais antiga/codificada;
* 2000-2008 têm presencial/EaD e tabelas complementares, mas precisam de dicionário para mapear os campos numéricos;
* nenhum desses anos entra na planilha oficial antes dessa etapa de mapeamento.

## Scripts principais

```bash
.venv/bin/python scripts/07_consolidar_historico_cursos.py
.venv/bin/python scripts/08_validar_historico.py
.venv/bin/python scripts/09_consolidar_alunos_quantitativo.py
.venv/bin/python scripts/10_mesclar_evasao_historico.py
.venv/bin/python scripts/11_auditar_recorte_computacao.py
.venv/bin/python scripts/12_gerar_planilha_oficial.py
```
