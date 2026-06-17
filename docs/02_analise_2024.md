# Síntese da análise de 2024

## Base final analisada

A base final analisada foi:

```text
data/processed/computacao_2024_tratada.csv
```

Ela foi gerada a partir dos Microdados do Censo da Educação Superior 2024 do INEP, cruzando a base de cursos com a base de IES por `NU_ANO_CENSO` e `CO_IES`.

## Recorte usado

O recorte oficial inclui:

1. cursos na área geral 6 da CINE, isto é, Computação e Tecnologias da Informação e Comunicação (TIC);
2. cursos com `CO_CINE_ROTULO = 0714E04`, rótulo de Engenharia de Computação.

Cursos relacionados fora desses critérios, como Matemática Computacional, Física Computacional e Informática em Saúde, ficam para revisão na auditoria do recorte.

## Números principais

```text
Registros analisados: 76.865
Cursos distintos: 3.894
IES distintas: 977
Registros com uso em mapa municipal: 75.509
Registros sem uso em mapa municipal: 1.356
```

Indicadores agregados:

```text
Vagas: 2.739.900
Inscritos: 1.513.815
Ingressantes: 509.828
Matriculados: 860.791
Concluintes: 106.157
Matrículas trancadas: 188.392
Desvinculados: 315.838
Transferidos: 23.294
Falecidos: 84
Desvinculados/matriculados: 36,69%
```

O indicador `Desvinculados/matriculados` deve ser tratado como medida exploratória, não como taxa final de evasão, porque a metodologia definitiva ainda depende da modelagem histórica e da validação conceitual do projeto.

## Distribuição por dimensão territorial

| TP_DIMENSAO | DS_TP_DIMENSAO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- | --- |
| 2 | EaD no Brasil | 72.915 | 1.295 | 503.197 | 235.305 |
| 1 | Presencial no Brasil | 2.594 | 2.594 | 357.156 | 80.422 |
| 4 | EaD exterior | 56 | 56 | 438 | 111 |
| 3 | EaD somente nível Brasil | 1.300 | 1.300 | 0 | 0 |

## Distribuição por modalidade

| DS_TP_MODALIDADE_ENSINO | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| EaD | 74.271 | 1.300 | 503.635 | 235.416 |
| Presencial | 2.594 | 2.594 | 357.156 | 80.422 |

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
| Defesa cibernética | 3.895 | 54 | 10.547 | 5.306 |
| Segurança da informação | 2.419 | 73 | 10.028 | 3.902 |
| Jogos digitais | 2.982 | 141 | 8.466 | 4.101 |
| Banco de dados | 2.817 | 75 | 7.270 | 4.045 |
| Inteligência artificial | 1.222 | 31 | 3.250 | 1.132 |
| Criação digital | 7 | 7 | 1.286 | 233 |

## Principais UFs para mapa municipal

Esta tabela considera apenas registros com `IN_USAR_MAPA_MUNICIPAL = True`.

| SG_UF | QT_REGISTROS | QT_CURSOS_DISTINTOS | QT_MAT | QT_SIT_DESVINCULADO |
| --- | --- | --- | --- | --- |
| SP | 18.688 | 1.589 | 290.048 | 106.466 |
| MG | 8.248 | 881 | 72.189 | 25.615 |
| RJ | 4.691 | 724 | 71.831 | 27.929 |
| PR | 5.602 | 735 | 59.150 | 21.589 |
| RS | 5.959 | 741 | 47.659 | 17.946 |
| DF | 520 | 520 | 36.701 | 12.278 |
| SC | 4.323 | 640 | 35.486 | 14.661 |
| PE | 2.591 | 524 | 33.732 | 10.463 |
| CE | 2.432 | 521 | 31.325 | 10.711 |
| BA | 3.975 | 590 | 27.560 | 10.608 |
| GO | 2.679 | 541 | 22.261 | 9.150 |
| PB | 1.172 | 389 | 16.057 | 4.602 |
| PA | 2.465 | 463 | 14.944 | 6.013 |
| ES | 1.646 | 407 | 14.615 | 5.764 |
| AM | 843 | 399 | 13.676 | 5.270 |

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
