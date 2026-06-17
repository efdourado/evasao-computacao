# Anos antigos: 1995-2008

Os anos 1995-2008 existem nos microdados do INEP, mas não entram na planilha oficial atual.

## Motivo

Esses anos usam estruturas anteriores ao recorte CINE/CINE Brasil adotado no projeto.

Enquanto a regra oficial atual é:

```text
CO_CINE_AREA_GERAL = 6
ou
CO_CINE_ROTULO = 0714E04
```

os anos antigos usam arquivos e campos como:

```text
GRADUACAO_PRESENCIAL.CSV
GRADUACAO_DISTANCIA.CSV
FORME_PRESENCIAL.CSV
SECOMPLE_PRESENCIAL.CSV
INSTITUICAO.CSV
AREACURSO
NO_AREA_CONHE
NO_CURSO_HABILITACAO
QT_AFAST_1SEM_ABANDONO
QT_AFAST_2SEM_TRANCA
```

## Problema prático

Não existe uma equivalência direta e validada entre esses campos antigos e:

```text
área geral CINE 6
rótulo CINE 0714E04
situação acadêmica atual
TP_DIMENSAO
```

Para usar 1995-2008, seria necessário criar uma etapa própria:

1. localizar e interpretar todos os dicionários antigos;
2. mapear as áreas antigas para Computação/TIC;
3. revisar nomes históricos de cursos;
4. entender a separação entre presencial e EaD;
5. validar se abandono/trancamento antigo é comparável aos campos recentes;
6. documentar a equivalência antes de juntar com 2009-2024.

## Decisão atual

1995-2008 ficam fora da primeira planilha oficial.

Esses anos só devem voltar ao `data/raw/` se o projeto decidir criar uma etapa histórica anterior a 2009.
