# Evasão em Cursos de Computação no Brasil

Este repositório transforma os Microdados do Censo da Educação Superior do INEP em uma base histórica de cursos superiores de Computação/TIC no Brasil.

O objetivo desta etapa é simples: partir dos arquivos originais, aplicar um recorte metodológico reproduzível e gerar planilhas prontas para análise e Power BI.

## Base oficial

A série atual cobre **2009 a 2024**. Nos anos classificados por CINE/CINE Brasil, entram:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

A área geral 6 corresponde a Computação e Tecnologias da Informação e Comunicação. O rótulo `0714E04` acrescenta Engenharia de Computação. Em 2017, que usa OCDE, foi aplicada uma aproximação equivalente documentada em [docs/01_visao_geral.md](docs/01_visao_geral.md).

## Resultados

As três planilhas finais ficam em `data/processed/oficial/`:

| Arquivo | Finalidade |
| --- | --- |
| `planilha_oficial_computacao.csv` | base principal, com uma linha por ano + IES + curso |
| `planilha_oficial_computacao_expandida.csv` | localizações e dimensões territoriais para mapas |
| `dicionario_planilha_oficial.csv` | descrição das colunas e dos arquivos em que aparecem |

Os arquivos brutos permanecem localmente em `data/raw/`. Eles somam aproximadamente 11 GB e incluem arquivos individuais acima do limite comum do GitHub, por isso não são versionados. As planilhas finais e a validação são versionadas.

## Reproduzir

Com o ambiente configurado:

```bash
.venv/bin/python scripts/executar_pipeline.py
```

Esse comando gera as três planilhas, executa as validações e remove os arquivos intermediários.

## Documentação

- [Visão geral e metodologia](docs/01_visao_geral.md)
- [Pipeline e reprodução](docs/02_pipeline_e_reproducao.md)
- [Validação e qualidade](docs/03_validacao_qualidade.md)
