# Etapa 4: alimentar o projeto com novos anos

Este projeto **não é estático**. Foi construído para receber cada novo Censo da Educação
Superior do INEP sem refazer o trabalho das etapas anteriores. Esta etapa descreve como
trazer um ano novo, o que é automático, o que ainda depende de uma pessoa e o que fazer
quando o INEP muda alguma coisa.

A regra de projeto é esta: quando o INEP mantém o layout do cadastro de cursos, adicionar um
ano **não exige editar nenhum código**. Quando ele muda, as checagens dizem exatamente o que
quebrou e onde corrigir, em vez de deixar o ano entrar quase vazio sem aviso.

## Em resumo

Baixe o arquivo de microdados do ano novo no site do INEP e rode um comando:

```bash
.venv/bin/python scripts/adicionar_ano.py 2025 --zip ~/Downloads/microdados_2025.zip
```

Se os arquivos já estiverem em `data/raw/2025/dados/`, omita o `--zip`. Para só testar, sem
registrar nem rodar nada, acrescente `--verificar`.

O comando faz, nesta ordem:

1. organiza o zip em `data/raw/2025/dados/` e `data/raw/2025/referencia/`;
2. faz a **checagem prévia** do ano e para se houver erro, sem alterar nada;
3. registra o ano em `config/anos.csv`;
4. roda o pipeline completo, que refaz recorte, validação, curadoria, flags e explicações;
5. mostra a linha do ano na tabela de continuidade e a lista do que revisar.

## O que é automático e o que é manual

| Passo | Quem faz | Como |
| --- | --- | --- |
| Organizar os arquivos do INEP | automático | `--zip` |
| Conferir arquivos, colunas e recorte do ano | automático | checagem prévia |
| Registrar o ano | automático | `config/anos.csv` |
| Recorte, validação estrutural e continuidade | automático | pipeline |
| Extratos da curadoria e flags | automático | pipeline |
| Textos e ocorrências por registro | automático | pipeline |
| Ler a checagem prévia e a continuidade | **pessoa** | poucos minutos |
| Decidir os casos "revisar em nova rodada" | **pessoa** | `config/curadoria_nome_rotulo.csv` |
| Registrar uma decisão nova, se surgiu um tipo novo de achado | **pessoa** | [manual de uso](03_manual_de_uso.md) |
| Atualizar os números de fotografia dos documentos e fazer o commit | **pessoa** | ver abaixo |

## A checagem prévia

O leitor de cursos foi escrito para tolerar colunas ausentes: se o INEP renomear um campo, o
pipeline preenche a coluna com vazio e segue. Sem a checagem prévia, um ano com a coluna de
área renomeada entraria na base com quase nenhum curso e sem erro algum. Ela existe para
impedir exatamente isso.

| Verificação | Erro quando |
| --- | --- |
| Arquivos de cursos e de IES | não existem em `data/raw/ANO`. A mensagem diz onde colocá-los |
| Colunas obrigatórias | falta qualquer coluna que o pipeline usa, comparada ao layout de referência em `config/esquema_cadastro_cursos.csv` |
| Ano do arquivo | `NU_ANO_CENSO` do arquivo não é o ano informado, ou seja, arquivo trocado |
| Recorte vazio | nenhum curso de Computação/TIC de graduação foi encontrado |
| Cursos no recorte | variação sobre o ano anterior acima do limite de erro |

E um alerta, sem parar nada, quando aparecem **rótulos CINE nunca vistos**, o que pode indicar
uma nova versão da classificação.

Como referência de que o método funciona: no arquivo real de 2024 a checagem conta 3.894 cursos no
recorte, exatamente as linhas de 2024 da planilha oficial.

## A continuidade entre anos

Depois do pipeline, a validação compara cada ano com o anterior e grava o resultado em
`data/processed/validacao/continuidade_anual.csv`. Os limites ficam em
`config/limites_continuidade.csv` e podem ser ajustados:

| Métrica | Alerta a partir de | Erro a partir de |
| --- | --- | --- |
| Cursos | 20% | 40% |
| Matrículas | 35% | 60% |
| Instituições | 15% | 30% |

Um ano registrado sem nenhuma linha é sempre erro. Erro bloqueia o uso, como qualquer erro da
validação estrutural. Alerta só pede revisão.

Os limites foram calibrados no histórico de 2009 a 2024, que passa sem nenhum alarme. As maiores
variações reais foram 15,2% em cursos em 2018, na troca de classificação, e 26,8% em
matrículas em 2022, no crescimento do EaD. Ficam abaixo dos limites de alerta, então um alarme
novo é sinal de que há algo diferente para olhar.

## O que cada etapa faz com o ano novo

- **Etapa 1, recorte.** Aplica as mesmas regras. Um ano novo precisa estar no modelo
  `cadastro_cursos`, que é o dos arquivos `MICRODADOS_CADASTRO_CURSOS_ANO.CSV`. Os modelos
  antigos de 2017 a 2019 são leitores próprios e não se repetem.
- **Etapa 2, curadoria.** Todos os extratos são refeitos com o ano incluído. Casos novos de nome
  contra rótulo aparecem como "revisar em nova rodada" até alguém classificá-los.
- **Etapa 3, manual de uso.** Flags, análises e explicações são refeitas. A matriz de tratamento
  vale para casos novos automaticamente. Só exige mexer na configuração se surgir um **tipo novo**
  de achado.

## Quando o INEP muda alguma coisa

| O que aparece | Causa provável | Onde corrigir |
| --- | --- | --- |
| Erro em "colunas obrigatórias" | O INEP renomeou ou removeu um campo | `COLUNAS_CURSOS_LEITURA` e `processar_ano_novo` em `consolidar_cursos.py`. Depois rode com `--atualizar-esquema` |
| Erro "recorte vazio" | Mudou o nome da coluna de área ou o código da classificação | Mesmo lugar, e a regra em [01_recorte.md](01_recorte.md) |
| Alerta "rótulos novos" | Nova versão da classificação CINE | Conferir os rótulos e atualizar a tabela de rótulos do documento de recorte |
| Erro em "cursos no recorte" | O recorte encolheu ou cresceu demais | Abrir o arquivo bruto e comparar com o ano anterior |
| Erro "arquivo de cursos não encontrado" | Nome de arquivo diferente do esperado | `localizar` em `verificar_novo_ano.py` e `processar_ano_novo` |
| Erro estrutural "oferta EaD fora da dimensão nacional" | O INEP mudou como informa vagas e inscritos do EaD | A regra estrutural do mapa, na etapa 3 |
| Um layout inteiramente diferente | Novo modelo de arquivos, como o de 2017 a 2019 | Escrever um leitor novo e registrar o modelo em `scripts/anos.py` |

## Como adicionar uma flag nova

Se um ano novo revelar um tipo de problema que ainda não existe:

1. detecte o caso no script de curadoria e gere um extrato;
2. acrescente a flag em `config/flags.csv`;
3. acrescente a linha dela em `config/matriz_flag_uso.csv`, dizendo em cada análise se exclui ou
   só sinaliza;
4. escreva o texto em `config/textos_flags.csv`, em português simples;
5. leia a flag em `calcular_flags_curso`, em `gerar_camada_analise.py`;
6. escreva a frase do caso em `gerar_transparencia.py`. Sem ela, a ocorrência usa o texto geral.

O script recusa configurações inconsistentes: flag sem texto, sem linha na matriz ou com
tratamento desconhecido. Um teste também avisa quando falta a frase própria de uma flag.

## Como manter os documentos honestos

Os números citados nos documentos, como o total de linhas ou as contagens por achado, são uma
**fotografia da versão de 2009 a 2024**. Não os corrija à mão a cada ano. Fonte da verdade para
qualquer número:

| Número | Onde ler o valor atual |
| --- | --- |
| Linhas, IES, anos | `data/processed/validacao/resumo_validacao.csv` |
| Evolução por ano | `data/processed/validacao/continuidade_anual.csv` |
| Achados por regra | `data/processed/curadoria/14_vistoria_cobertura.csv` |
| Quanto cada análise exclui | `data/processed/analise/cobertura_uso.csv` |

A cada ano acrescentado, registre uma linha abaixo e faça o commit da configuração junto com as
tabelas regeneradas.

## Histórico de versões dos dados

| Data | Anos cobertos | Linhas na planilha principal | Observação |
| --- | --- | --- | --- |
| 2026-09-20 | 2009 a 2024 | 43.477 | Versão inicial com as quatro etapas |

## O que esta etapa garante e o que não garante

**Garante:**

- há um único registro dos anos, em `config/anos.csv`, lido por todos os scripts;
- um ano com layout quebrado é barrado antes de entrar, e um ano vazio ou muito diferente do
  anterior é barrado depois;
- toda decisão sobre casos é um arquivo de configuração revisável, e nenhuma vive escondida no
  código;
- a base oficial é refeita do zero a cada execução e o resultado é determinístico;
- os testes cobrem os modos de falha acima.

**Não garante:**

- que o dado declarado pelas instituições esteja correto. Isso continua sendo o papel da
  curadoria e das flags;
- que o INEP não republique um ano antigo com retificações. Se acontecer, substitua os arquivos
  em `data/raw/ANO`, com `--forcar`, e rode o pipeline: todos os anos são refeitos juntos;
- anos anteriores a 2009, fora do escopo por decisão registrada na [etapa 1](01_recorte.md).
