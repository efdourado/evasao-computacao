# Validação e qualidade

A validação é executada no final da pipeline ou isoladamente com:

```bash
.venv/bin/python scripts/validar_planilhas_oficiais.py
```

## Saídas

| Arquivo | Conteúdo |
| --- | --- |
| `resumo_validacao.csv` | status geral, dimensões das bases e contagens principais |
| `ocorrencias_validacao.csv` | cada erro ou alerta com ano, IES, curso e descrição |

Não é mais gerado um relatório Markdown automático. Este documento concentra a interpretação; os CSVs guardam o resultado executado.

## O que é verificado

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
```

São alertas:

```text
mesmo código de IES com nomes diferentes no mesmo ano
mesmo código de curso com nomes diferentes no mesmo ano
```

## O que aconteceu com os 2.483 alertas antigos

Os alertas anteriores não representavam 2.483 erros de dados.

### Razão desvinculados/matrículas

Havia 2.482 linhas com `QT_SIT_DESVINCULADO / QT_MAT > 1`. Isso acontece porque:

```text
QT_SIT_DESVINCULADO = fluxo/situação observado no ano
QT_MAT = estoque de matrículas usado como denominador
```

As grandezas não formam automaticamente uma taxa de evasão da mesma coorte. Em vez de alterar os valores originais, o indicador derivado foi removido das planilhas oficiais. Os campos `QT_SIT_DESVINCULADO` e `QT_MAT` continuam disponíveis separadamente.

### Sigla de IES ausente

Existem 3.942 linhas sem `SG_IES`. Isso não impede a identificação da instituição porque `CO_IES` e `NO_IES` estão preenchidos. A sigla é opcional e agora aparece no resumo como informação, não como alerta.

## Resultado esperado

Após essas decisões, uma base íntegra deve apresentar:

```text
Total de Erros Críticos: 0
Alertas: 0
```

Além disso:

```text
Planilha Principal (Curso Único por Ano): 43.304 chaves distintas.
Planilha Expandida (Polos Geográficos): 315.237 linhas territoriais.
2009 a 2024 presentes
nenhuma linha fora do recorte oficial
nenhuma coluna individual de aluno ou docente
```

Se surgirem ocorrências futuras, elas devem ser analisadas em `ocorrencias_validacao.csv`. O script encerra com erro quando encontra qualquer problema bloqueante.
