# Pipeline e reprodução

Este documento mostra como reproduzir a geração da planilha oficial.

## Onde colocar os arquivos brutos

Os microdados ficam localmente em:

```text
data/raw/
```

Na etapa atual, `data/raw/` deve conter apenas:

```text
2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
2017, 2018, 2019,
2020, 2021, 2022, 2023, 2024
```

A pasta `data/raw/` não é versionada.

Dentro de cada ano, o padrão é:

```text
data/raw/ANO/dados/
data/raw/ANO/referencia/
```

`dados/` contém apenas os arquivos usados pelo pipeline, como cursos, IES, aluno e tabelas auxiliares de classificação.

`referencia/` contém apenas materiais úteis para consulta, como dicionário de dados, leia-me, nota informativa, filtros e código de país. Questionários, arquivos MD5, temporários e tabelas não usadas no fluxo atual ficam fora.

## Ambiente

Criar e ativar o ambiente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Comandos principais

Rodar nesta ordem:

```bash
.venv/bin/python scripts/07_consolidar_historico_cursos.py
.venv/bin/python scripts/08_validar_historico.py
.venv/bin/python scripts/09_consolidar_alunos_quantitativo.py
.venv/bin/python scripts/10_mesclar_evasao_historico.py
.venv/bin/python scripts/11_auditar_recorte_computacao.py
.venv/bin/python scripts/12_gerar_planilha_oficial.py
.venv/bin/python scripts/14_validar_planilha_oficial.py
```

## Saídas esperadas

Planilhas finais:

```text
data/processed/oficial/planilha_oficial_computacao.csv
data/processed/oficial/planilha_oficial_computacao_expandida.csv
data/processed/oficial/dicionario_planilha_oficial.csv
```

Validação final:

```text
data/processed/validacao_oficial/
```

## Como saber se deu certo

A validação final deve mostrar:

```text
Erros: 0
```

Alertas podem existir. Eles indicam pontos para revisão, mas não bloqueiam o uso da planilha.

## Como abrir no Pandas

As planilhas usam `;` como separador e `utf-8-sig` como encoding.

```python
import pandas as pd

df = pd.read_csv(
    "data/processed/oficial/planilha_oficial_computacao.csv",
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
    low_memory=False,
)
```

Para converter métricas:

```python
metricas = [
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "QT_SIT_TRANCADA",
    "QT_SIT_DESVINCULADO",
    "QT_SIT_TRANSFERIDO",
    "QT_SIT_FALECIDO",
]

df[metricas] = df[metricas].apply(pd.to_numeric, errors="coerce")
```

## Checagens antes de push

```bash
git status
git ls-files data/raw data/processed
find data -type f -size +50M
```

O comando abaixo não deve retornar arquivos brutos ou processados versionados:

```bash
git ls-files data/raw data/processed
```
