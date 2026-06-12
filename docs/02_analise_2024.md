# Síntese da análise de 2024

## Base final analisada

A base final analisada foi:

```text
data/processed/computacao_2024_tratada.csv
```

Ela foi gerada a partir dos Microdados do Censo da Educação Superior 2024 do INEP, cruzando a base de cursos com a base de IES por `NU_ANO_CENSO` e `CO_IES`.

## Recorte usado

O recorte provisório de Computação/TIC inclui:

1. cursos na área geral CINE de Computação e Tecnologias da Informação e Comunicação (TIC);
2. cursos com rótulo CINE `Computação formação de professor`;
3. cursos identificados por nome ou rótulo como `Engenharia de Computação`.

## Números principais

```text
Registros analisados: 78.657
Cursos distintos: 3.987
IES distintas: 977
Registros com uso em mapa municipal: 77.266
Registros sem uso em mapa municipal: 1.391
```

Indicadores agregados:

```text
Vagas: 2.776.208
Inscritos: 1.532.590
Ingressantes: 514.619
Matriculados: 871.845
Concluintes: 107.078
Matrículas trancadas: 190.893
Desvinculados: 320.211
Transferidos: 23.433
Falecidos: 85
Desvinculados/matriculados: 36,73%
```

O indicador `Desvinculados/matriculados` deve ser tratado como medida exploratória, não como taxa final de evasão, porque a metodologia definitiva ainda depende da modelagem histórica e da validação conceitual do projeto.

## Distribuição por dimensão territorial

| TP_DIMENSAO | DS_TP_DIMENSAO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- | --- |
| 2 | EaD no Brasil | 74.614 | 1.330 | 509.339 | 238.604 |
| 1 | Presencial no Brasil | 2.652 | 2.652 | 362.068 | 81.496 |
| 4 | EaD exterior | 56 | 56 | 438 | 111 |
| 3 | EaD somente nível Brasil | 1.335 | 1.335 | 0 | 0 |

## Distribuição por modalidade

| DS_TP_MODALIDADE_ENSINO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| EaD | 76.005 | 1.335 | 509.777 | 238.715 |
| Presencial | 2.652 | 2.652 | 362.068 | 81.496 |

## Principais rótulos CINE por matrículas

| NO_CINE_ROTULO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| Sistemas de informação | 20.334 | 1.500 | 420.479 | 160.022 |
| Ciência da computação | 5.695 | 507 | 127.190 | 33.253 |
| Engenharia de software | 7.807 | 213 | 69.832 | 24.063 |
| Engenharia de computação | 3.731 | 354 | 60.569 | 13.225 |
| Gestão da tecnologia da informação | 9.178 | 330 | 59.647 | 34.546 |
| Ciência de dados | 5.005 | 130 | 28.189 | 10.937 |
| Redes de computadores | 5.125 | 198 | 20.661 | 9.949 |
| Sistemas para internet | 3.740 | 165 | 15.718 | 6.949 |
| Programas interdisciplinares abrangendo computação e Tecnologias da Informação e Comunicação (TIC) | 899 | 53 | 14.735 | 2.364 |
| Computação formação de professor | 1.792 | 93 | 11.054 | 4.373 |
| Defesa cibernética | 3.895 | 54 | 10.547 | 5.306 |
| Segurança da informação | 2.419 | 73 | 10.028 | 3.902 |
| Jogos digitais | 2.982 | 141 | 8.466 | 4.101 |
| Banco de dados | 2.817 | 75 | 7.270 | 4.045 |
| Inteligência artificial | 1.222 | 31 | 3.250 | 1.132 |

## Principais UFs para mapa municipal

Esta tabela considera apenas registros com `IN_USAR_MAPA_MUNICIPAL = True`.

| SG_UF | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| SP | 18.896 | 1.600 | 290.330 | 106.723 |
| MG | 8.408 | 896 | 72.753 | 25.911 |
| RJ | 4.779 | 736 | 72.218 | 28.184 |
| PR | 5.745 | 750 | 60.411 | 22.230 |
| RS | 6.106 | 759 | 48.189 | 18.225 |
| DF | 530 | 530 | 37.193 | 12.382 |
| SC | 4.448 | 658 | 35.987 | 14.871 |
| PE | 2.662 | 537 | 34.711 | 10.850 |
| CE | 2.532 | 534 | 31.747 | 10.842 |
| BA | 4.097 | 612 | 28.423 | 10.966 |
| GO | 2.722 | 549 | 22.297 | 9.212 |
| PB | 1.216 | 399 | 16.491 | 4.713 |
| PA | 2.556 | 477 | 15.656 | 6.231 |
| ES | 1.689 | 415 | 14.688 | 5.804 |
| AM | 885 | 411 | 14.167 | 5.475 |

## Tabelas geradas

* `data/processed/resumos_2024/resumo_geral_2024.csv`
* `data/processed/resumos_2024/resumo_por_dimensao_2024.csv`
* `data/processed/resumos_2024/resumo_por_modalidade_2024.csv`
* `data/processed/resumos_2024/resumo_por_criterio_escopo_2024.csv`
* `data/processed/resumos_2024/resumo_por_cine_rotulo_2024.csv`
* `data/processed/resumos_2024/resumo_por_cine_area_geral_2024.csv`
* `data/processed/resumos_2024/resumo_por_cine_area_especifica_2024.csv`
* `data/processed/resumos_2024/resumo_por_cine_area_detalhada_2024.csv`
* `data/processed/resumos_2024/resumo_por_rede_categoria_2024.csv`
* `data/processed/resumos_2024/resumo_por_uf_curso_mapa_2024.csv`
* `data/processed/resumos_2024/resumo_por_municipio_curso_mapa_2024.csv`
* `data/processed/resumos_2024/resumo_por_ies_2024.csv`
* `data/processed/resumos_2024/resumo_por_curso_2024.csv`

## Próximo avanço

Com 2024 fechado, o próximo passo é repetir a mesma estrutura para os anos anteriores disponíveis e depois padronizar os campos para construir uma base histórica. Em paralelo, já é possível começar a mapear quais campos devem vir da SBC, do e-MEC e de coleta complementar por scraper.
