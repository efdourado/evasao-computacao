# Decisões metodológicas

Este documento explica as principais decisões da primeira planilha oficial.

## Por que começar em 2009

A planilha oficial inicia em 2009 porque esse é o primeiro período em que a integração histórica fica metodologicamente compatível com o recorte oficial de Computação/TIC.

O recorte oficial depende de:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

Antes de 2009, os microdados usam estruturas e classificações antigas. Integrar esses anos exigiria uma etapa própria para mapear códigos antigos para o recorte CINE moderno.

## Por que 1995-2008 ficaram fora

1995-2008 não foram descartados por falta de interesse. Eles ficaram fora porque exigem uma equivalência metodológica própria.

Exemplo prático: nos anos antigos aparecem arquivos e campos como:

```text
GRADUACAO_PRESENCIAL.CSV
GRADUACAO_DISTANCIA.CSV
INSTITUICAO.CSV
AREACURSO
NO_AREA_CONHE
NO_CURSO_HABILITACAO
QT_AFAST_1SEM_ABANDONO
QT_AFAST_2SEM_TRANCA
```

Esses campos não possuem uma regra direta equivalente a:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

Para usar 1995-2008, seria necessário:

1. entender os dicionários antigos;
2. mapear códigos antigos de área para Computação/TIC;
3. validar nomes históricos como Processamento de Dados, Informática e Análise de Sistemas;
4. decidir como comparar presencial/EaD entre estruturas antigas e recentes;
5. documentar a equivalência com o recorte CINE moderno.

Por isso esses anos são etapa futura, não entrada limpa para a primeira planilha oficial.

## Por que Engenharia de Computação entra separada

Engenharia de Computação não entra apenas pela área geral 6. Ela é incluída pelo rótulo específico:

```text
CO_CINE_ROTULO = 0714E04
```

Isso segue a decisão metodológica do projeto: usar área geral 6 para Computação/TIC e adicionar Engenharia de Computação por rótulo.

## Por que 2017 usa OCDE

2017 não usa CINE/CINE Brasil na mesma estrutura dos anos posteriores. Por isso foi usada uma aproximação histórica:

```text
CO_OCDE_AREA_ESPECIFICA = 48
ou
CO_OCDE = 5.23E+06
```

Na planilha, esse ano fica marcado com:

```text
DS_CLASSIFICACAO_AREA = OCDE
DS_NIVEL_COMPARABILIDADE = media_ocde_proxy
```

## Por que existem duas planilhas

Existem duas planilhas porque a mesma informação precisa servir a usos diferentes.

| Planilha | Uso |
| --- | --- |
| `planilha_oficial_computacao.csv` | série histórica e contagem de cursos |
| `planilha_oficial_computacao_expandida.csv` | mapas e dimensão territorial |

A planilha expandida pode ter várias linhas para o mesmo curso, especialmente em EaD. Para contar cursos, sempre usar a planilha principal ou a chave:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

## O que é indicador exploratório de desvinculação

O indicador:

```text
QT_SIT_DESVINCULADO / QT_MAT
```

é exploratório. Ele não deve ser chamado automaticamente de taxa de evasão, porque evasão exige definição metodológica própria.
