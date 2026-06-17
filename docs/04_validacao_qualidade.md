# Validação de qualidade

A validação final é gerada por:

```bash
.venv/bin/python scripts/14_validar_planilha_oficial.py
```

Saída:

```text
data/processed/validacao_oficial/
```

## Validações automáticas

| Arquivo | O que valida |
| --- | --- |
| `01_resumo_geral.csv` | resumo geral da planilha e das validações |
| `02_duplicatas_chave.csv` | duplicatas em `NU_ANO_CENSO + CO_IES + CO_CURSO` |
| `03_nulos_colunas_criticas.csv` | nulos em campos obrigatórios |
| `04_instituicoes_nomes_conflitantes.csv` | mesmo `CO_IES` com mais de um nome no mesmo ano |
| `05_cursos_nomes_conflitantes.csv` | mesmo `CO_CURSO` com mais de um nome no mesmo ano |
| `06_recorte_cine_invalido.csv` | linhas fora do recorte oficial |
| `07_metricas_negativas_ou_estranhas.csv` | métricas negativas ou razões que exigem revisão |
| `08_colunas_sensiveis_detectadas.csv` | colunas individuais/sensíveis indesejadas |
| `09_comparacao_oficial_vs_expandida.csv` | chaves presentes na comparável e na expandida |
| `relatorio_validacao_oficial.md` | relatório legível da validação |

## Regras que bloqueiam

São tratadas como `ERRO`:

```text
duplicata na chave oficial
CO_IES vazio
CO_CURSO vazio
NO_IES vazio
NO_CURSO vazio
ano fora de 2009-2024
métrica numérica negativa
colunas sensíveis ou individuais
linha fora do recorte oficial
chave existente na expandida e ausente na comparável, ou o inverso
```

Se houver qualquer `ERRO`, o script termina com código diferente de zero.

## Regras que alertam

São tratadas como `ALERTA`:

```text
IES sem sigla
mesmo código de IES com nomes diferentes no mesmo ano
mesmo código de curso com nomes diferentes no mesmo ano
desvinculados/matrículas acima de 1
```

Alertas não impedem o uso da base, mas devem ser mencionados em reunião se virarem ponto de discussão.

## Resultado atual

Na última execução:

```text
Status: APROVADO_COM_ALERTAS
Erros: 0
Alertas: 2483
```

Interpretação dos alertas atuais:

* `SG_IES` ausente em parte das linhas: não bloqueia, porque sigla de IES nem sempre está preenchida;
* `QT_SIT_DESVINCULADO / QT_MAT > 1` em algumas chaves: é alerta metodológico, pois desvinculados são situação/fluxo do ano e matrículas são estoque. Não usar essa razão como taxa final de evasão.

Pontos fortes da validação atual:

```text
0 duplicatas na chave oficial
0 linhas fora do recorte oficial
0 colunas sensíveis detectadas
0 perdas de chave entre planilha comparável e expandida
0 conflitos de nome de IES no mesmo ano
0 conflitos de nome de curso no mesmo ano
```
