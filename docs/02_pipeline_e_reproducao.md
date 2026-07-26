# Pipeline e reprodução

## Arquivos de entrada

Os arquivos originais ficam em:

```text
data/raw/ANO/dados/
data/raw/ANO/referencia/
```

`dados/` contém cursos, IES, arquivos de aluno e tabelas auxiliares usadas pela pipeline. `referencia/` contém dicionários, leia-me, notas informativas e filtros do INEP.

Os dados brutos não são versionados: a pasta local tem aproximadamente 11 GB e contém arquivos individuais de 2 a 3 GB.

## Baixar os dados brutos (Google Drive)

Os arquivos brutos não ficam versionados no repositório (pesam ~11 GB no total). Eles estão hospedados em um Google Drive compartilhado do projeto e podem ser baixados por qualquer colaborador, sem autenticação, com:

```bash
.venv/bin/python scripts/baixar_dados_drive.py
```

O script usa o pacote `gdown` para baixar direto do Drive público (basta o link estar como "Qualquer pessoa com o link pode visualizar"), inclusive arquivos de 2-3 GB que passam pela tela de confirmação do Google. Cada ano cai em `data/raw/<ano>/`, no formato que os scripts da pipeline já esperam.

Opções úteis:

```bash
.venv/bin/python scripts/baixar_dados_drive.py --listar        # mostra o que está mapeado, sem baixar
.venv/bin/python scripts/baixar_dados_drive.py --ano 2022 2024 # baixa só alguns anos
.venv/bin/python scripts/baixar_dados_drive.py --forcar        # baixa de novo mesmo se já existir
```

Para adicionar um novo ano, ou corrigir/atualizar um ID do Drive, basta editar o dicionário `FONTES_DRIVE` no início do script — cada entrada aceita uma pasta inteira do Drive (quando os CSVs de um ano vêm todos juntos) ou uma lista de arquivos individuais com seus IDs. O próprio script explica esse formato em comentários.

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
6. validação de qualidade.

Os intermediários ficam temporariamente em `data/processed/.pipeline/` e são removidos após uma execução bem-sucedida.

## Saídas permanentes

```text
data/processed/oficial/planilha_oficial_computacao.csv
data/processed/oficial/planilha_oficial_computacao_expandida.csv
data/processed/oficial/dicionario_planilha_oficial.csv

data/processed/validacao/resumo_validacao.csv
data/processed/validacao/ocorrencias_validacao.csv
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