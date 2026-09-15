# Pipeline e reprodução

## Arquivos de entrada

Os arquivos originais ficam em:

```text
data/raw/ANO/dados/
data/raw/ANO/referencia/
```

`dados/` contém cursos, IES, arquivos de aluno e tabelas auxiliares usadas pela pipeline. `referencia/` contém dicionários, leia-me, notas informativas e filtros do INEP.

Os dados brutos não são versionados: a pasta local tem aproximadamente 11 GB e contém arquivos individuais de 2 a 3 GB.

## Baixar os dados brutos

Se os arquivos brutos não estiverem disponíveis localmente, baixar do Drive compartilhado do projeto:

```bash
.venv/bin/python scripts/baixar_dados_drive.py
```

Opções úteis:

```bash
.venv/bin/python scripts/baixar_dados_drive.py --listar
.venv/bin/python scripts/baixar_dados_drive.py --ano 2022 2024
.venv/bin/python scripts/baixar_dados_drive.py --forcar
```

O script organiza cada ano em `data/raw/ANO/dados/` e `data/raw/ANO/referencia/`, preservando CSVs de dados e materiais de referência úteis. Questionários e arquivos auxiliares sem uso direto são descartados durante essa organização.

## Ambiente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Gerar tudo

Na raiz do repositório:

```bash
.venv/bin/python scripts/executar_pipeline.py
```

O comando executa:

1. leitura e padronização dos arquivos de curso e IES;
2. aplicação do recorte CINE/OCDE;
3. criação da camada comparável por ano + IES + curso;
4. integração dos arquivos de aluno de 2017-2019;
5. geração das três planilhas oficiais;
6. validação de qualidade;
7. geração dos extratos de curadoria;
8. vistoria de conteúdo, sequências territoriais e conferência de casos selecionados no bruto.

Os intermediários ficam temporariamente em `data/processed/.pipeline/` e são removidos ao término da execução, inclusive em caso de falha. O comando completo reconstrói as planilhas oficiais; os comandos isolados de curadoria abaixo apenas as leem.

## Saídas permanentes

```text
data/processed/oficial/planilha_oficial_computacao.csv
data/processed/oficial/planilha_oficial_computacao_expandida.csv
data/processed/oficial/dicionario_planilha_oficial.csv

data/processed/validacao/resumo_validacao.csv
data/processed/validacao/ocorrencias_validacao.csv
data/processed/curadoria/*.csv
```

## Abrir no Data Wrangler ou Pandas

Copiar e executar:

```python
from pathlib import Path
import pandas as pd

arquivo = (
    Path.cwd()
    / "data"
    / "processed"
    / "oficial"
    / "planilha_oficial_computacao.csv"
)

df = pd.read_csv(
    arquivo,
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
    low_memory=False,
)
```

Para abrir a expandida, trocar apenas o nome do arquivo.

O `sep=";"` é necessário porque as planilhas usam ponto e vírgula. `dtype=str` evita que códigos de curso, IES ou classificação sejam convertidos automaticamente para números.

Para analisar métricas:

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

## Conferência rápida

```bash
.venv/bin/python scripts/validar_planilhas_oficiais.py
```

Uma execução pronta para uso deve terminar com `Erros: 0`. Qualquer detalhe fica em `data/processed/validacao/ocorrencias_validacao.csv`.

## Curadoria de conteúdo

A validação bloqueante acima não decide casos que exigem interpretação
(repetição de valores, nome e rótulo diferentes, séries de baixa atividade e
distribuição municipal EaD atípica). Para gerar as listas de conferência:

```bash
.venv/bin/python scripts/gerar_extratos_curadoria.py
.venv/bin/python scripts/vistoriar_conteudo.py
```

Os extratos ficam em `data/processed/curadoria/` e a interpretação está em
[docs/04_curadoria_e_inconsistencias.md](04_curadoria_e_inconsistencias.md).

A vistoria acrescenta persistência de zeros, mudanças territoriais e comparação
de casos selecionados com os arquivos brutos. A execução não modifica as
planilhas oficiais. Os dois comandos recriam seus CSVs de saída e sobrescrevem
edições manuais nesses arquivos. As conclusões por caso ficam no documento de
curadoria; os status gerados nos CSVs não substituem decisões manuais de uso.

Os testes das regras temporais são executados com:

```bash
.venv/bin/python -m unittest discover -s tests -v
```
