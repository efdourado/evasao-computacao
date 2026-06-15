# Síntese da análise de 2024

## Base final analisada

A base final analisada foi:

```text
data/processed/computacao_2024_tratada.csv
```

Ela foi gerada a partir dos Microdados do Censo da Educação Superior 2024 do INEP, cruzando a base de cursos com a base de IES por `NU_ANO_CENSO` e `CO_IES`.

## Recorte usado

O recorte oficial de Computação/TIC inclui cursos na área geral 6 da CINE, isto é, Computação e Tecnologias da Informação e Comunicação (TIC).

Cursos relacionados que estejam em outras áreas gerais, como Engenharia de Computação, Computação formação de professor, Matemática Computacional, Física Computacional e Informática em Saúde, não entram automaticamente nessa base. Eles ficam para revisão na auditoria do recorte.

## Números principais

```text
Registros analisados: 73.134
Cursos distintos: 3.540
IES distintas: 943
Registros com uso em mapa municipal: 71.842
Registros sem uso em mapa municipal: 1.292
```

Indicadores agregados:

```text
Vagas: 2.641.395
Inscritos: 1.423.984
Ingressantes: 489.067
Matriculados: 800.222
Concluintes: 100.488
Matrículas trancadas: 179.110
Desvinculados: 302.613
Transferidos: 19.763
Falecidos: 74
Desvinculados/matriculados: 37,82%
```

O indicador `Desvinculados/matriculados` deve ser tratado como medida exploratória, não como taxa final de evasão, porque a metodologia definitiva ainda depende da modelagem histórica e da validação conceitual do projeto.

## Distribuição por dimensão territorial

| TP_DIMENSAO | DS_TP_DIMENSAO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- | --- |
| 2 | EaD no Brasil | 69.541 | 1.234 | 483.835 | 229.305 |
| 1 | Presencial no Brasil | 2.301 | 2.301 | 315.965 | 73.202 |
| 4 | EaD exterior | 53 | 53 | 422 | 106 |
| 3 | EaD somente nível Brasil | 1.239 | 1.239 | 0 | 0 |

## Distribuição por modalidade

| DS_TP_MODALIDADE_ENSINO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| EaD | 70.833 | 1.239 | 484.257 | 229.411 |
| Presencial | 2.301 | 2.301 | 315.965 | 73.202 |

## Principais rótulos CINE por matrículas

| NO_CINE_ROTULO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| Sistemas de informação | 20.334 | 1.500 | 420.479 | 160.022 |
| Ciência da computação | 5.695 | 507 | 127.190 | 33.253 |
| Engenharia de software | 7.807 | 213 | 69.832 | 24.063 |
| Gestão da tecnologia da informação | 9.178 | 330 | 59.647 | 34.546 |
| Ciência de dados | 5.005 | 130 | 28.189 | 10.937 |
| Redes de computadores | 5.125 | 198 | 20.661 | 9.949 |
| Sistemas para internet | 3.740 | 165 | 15.718 | 6.949 |
| Programas interdisciplinares abrangendo computação e Tecnologias da Informação e Comunicação (TIC) | 899 | 53 | 14.735 | 2.364 |
| Defesa cibernética | 3.895 | 54 | 10.547 | 5.306 |
| Segurança da informação | 2.419 | 73 | 10.028 | 3.902 |
| Jogos digitais | 2.982 | 141 | 8.466 | 4.101 |
| Banco de dados | 2.817 | 75 | 7.270 | 4.045 |
| Inteligência artificial | 1.222 | 31 | 3.250 | 1.132 |
| Criação digital | 7 | 7 | 1.286 | 233 |
| Agrocomputação | 542 | 12 | 1.269 | 679 |

## Principais UFs para mapa municipal

Esta tabela considera apenas registros com `IN_USAR_MAPA_MUNICIPAL = True`.

| SG_UF | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| SP | 17.447 | 1.450 | 265.694 | 101.421 |
| RJ | 4.483 | 681 | 67.908 | 27.014 |
| MG | 7.853 | 815 | 65.958 | 24.410 |
| PR | 5.241 | 693 | 55.298 | 20.563 |
| RS | 5.706 | 692 | 44.838 | 17.223 |
| DF | 501 | 501 | 35.704 | 12.088 |
| SC | 4.153 | 604 | 34.150 | 14.239 |
| PE | 2.517 | 502 | 32.079 | 10.169 |
| CE | 2.364 | 493 | 29.272 | 10.375 |
| BA | 3.814 | 549 | 25.238 | 9.953 |
| GO | 2.584 | 513 | 21.202 | 8.910 |
| PB | 1.138 | 376 | 15.235 | 4.492 |
| PA | 2.349 | 439 | 13.429 | 5.580 |
| ES | 1.576 | 381 | 13.409 | 5.447 |
| AM | 805 | 374 | 11.658 | 4.939 |

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
