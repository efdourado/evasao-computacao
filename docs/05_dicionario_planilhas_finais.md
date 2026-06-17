# Dicionário das planilhas finais

As planilhas finais ficam em:

```text
data/processed/oficial/
```

## 1. Planilha principal

Arquivo:

```text
planilha_oficial_computacao.csv
```

Uso:

```text
série histórica
contagem de cursos
comparação por instituição
comparação por curso
indicadores agregados
Power BI principal
```

Chave:

```text
NU_ANO_CENSO + CO_IES + CO_CURSO
```

Cada linha representa um curso em uma instituição em um ano.

## 2. Planilha expandida

Arquivo:

```text
planilha_oficial_computacao_expandida.csv
```

Uso:

```text
mapas
UF
município
dimensão territorial
EaD/polos/localizações
```

Ela pode ter várias linhas para o mesmo curso. Não usar contagem de linhas como contagem de cursos.

## 3. Dicionário

Arquivo:

```text
dicionario_planilha_oficial.csv
```

Uso:

```text
consultar significado das colunas principais
```

## Colunas principais

Identificação:

```text
NU_ANO_CENSO
CO_IES
NO_IES
SG_IES
CO_CURSO
NO_CURSO
```

Recorte:

```text
DS_CRITERIO_ESCOPO
DS_CLASSIFICACAO_AREA
DS_NIVEL_COMPARABILIDADE
DS_OBSERVACAO_COMPARABILIDADE
CO_AREA_GERAL
NO_AREA_GERAL
CO_ROTULO_AREA
NO_ROTULO_AREA
```

Curso e instituição:

```text
DS_TP_GRAU_ACADEMICO
DS_TP_MODALIDADE_ENSINO
DS_TP_CATEGORIA_ADMINISTRATIVA
DS_TP_REDE
DS_TP_ORGANIZACAO_ACADEMICA
```

Métricas:

```text
QT_VG_TOTAL
QT_INSCRITO_TOTAL
QT_ING
QT_MAT
QT_CONC
QT_SIT_TRANCADA
QT_SIT_DESVINCULADO
QT_SIT_TRANSFERIDO
QT_SIT_FALECIDO
TX_DESVINCULADO_SOBRE_MAT
```

## Exemplos de filtros no Power BI

Filtros recomendados:

```text
ano
UF
IES
modalidade
grau acadêmico
rede pública/privada
curso
critério de escopo
classificação de área
```

Medidas recomendadas:

```text
distinct count de CO_CURSO por ano/IES
soma de QT_MAT
soma de QT_ING
soma de QT_CONC
soma de QT_SIT_DESVINCULADO
razão exploratória QT_SIT_DESVINCULADO / QT_MAT
```

Evitar:

```text
contar linhas da planilha expandida como cursos
chamar TX_DESVINCULADO_SOBRE_MAT de taxa final de evasão
misturar comparável e expandida sem chave
```
