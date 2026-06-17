from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
HISTORICO = ROOT / "data" / "processed" / "historico"
SAIDA = HISTORICO / "inventario_anos_antigos_1995_2008.csv"

ANOS = [str(ano) for ano in range(1995, 2009)]
DELIMITADORES_CANDIDATOS = [";", "|", ",", "\t"]

TERMOS_ARQUIVO_CURSO = ["GRADUACAO"]
TERMOS_ARQUIVO_IES = ["INSTITUICAO"]
TERMOS_ARQUIVO_COMPLEMENTAR = ["FORME", "SECOMPLE"]

TERMOS_AREA = ["AREA", "AREACURSO", "CODAREA", "OCDE", "CINE"]
TERMOS_CURSO = ["CURSO"]
TERMOS_METRICAS_BASICAS = [
    "VAGA",
    "INSCR",
    "INGRESS",
    "MATRIC",
    "MATRI",
    "CONC",
    "DIPLOM",
]
TERMOS_SITUACAO = [
    "AFAST",
    "ABAND",
    "TRANC",
    "DESV",
    "SITUAC",
    "TRANSF",
    "FALEC",
]


def detectar_delimitador(caminho):
    with caminho.open("rb") as arquivo:
        primeira_linha = arquivo.readline().decode("latin1", errors="replace")
    return max(DELIMITADORES_CANDIDATOS, key=primeira_linha.count)


def colunas_csv(caminho):
    return pd.read_csv(
        caminho,
        sep=detectar_delimitador(caminho),
        encoding="latin1",
        dtype=str,
        nrows=0,
    ).columns.tolist()


def nomes_csv(pasta_ano):
    return sorted(
        [
            caminho
            for caminho in pasta_ano.rglob("*")
            if caminho.is_file() and caminho.suffix.lower() == ".csv"
        ]
    )


def nomes_com_termo(arquivos, termos):
    termos = tuple(termo.upper() for termo in termos)
    return [arquivo for arquivo in arquivos if any(termo in arquivo.name.upper() for termo in termos)]


def filtrar_colunas(colunas, termos):
    termos = tuple(termo.upper() for termo in termos)
    return sorted({coluna for coluna in colunas if any(termo in coluna.upper() for termo in termos)})


def juntar(valores):
    valores = [str(valor) for valor in valores if str(valor)]
    return " | ".join(valores)


def status_ano(ano):
    if ano in ["1995", "1996"]:
        return (
            "pendente_recorte_area_antiga",
            "Ha campos explicitos de afastamento/trancamento/abandono no presencial, "
            "mas falta mapear a classificacao antiga AREACURSO para Computacao e "
            "validar a cobertura de modalidade.",
        )
    if ano in ["1997", "1998", "1999"]:
        return (
            "pendente_dicionario_metricas",
            "A estrutura e mais antiga/codificada; nao integrar antes de mapear "
            "dicionario, recorte de area e significado dos campos numericos.",
        )
    return (
        "pendente_mapeamento_modelo_2000_2008",
        "Ha arquivos de graduacao presencial/EaD e classificacao por area antiga, "
        "mas as metricas principais aparecem em campos codificados; precisa "
        "mapeamento antes de comparar com CINE.",
    )


def inventariar_ano(ano):
    pasta_ano = RAW / ano
    if not pasta_ano.exists():
        status, observacao = "nao_disponivel", "Pasta do ano nao encontrada em data/raw."
        return {
            "NU_ANO_CENSO": ano,
            "QT_ARQUIVOS_CSV": 0,
            "ARQUIVOS_CURSO_CANDIDATOS": "",
            "ARQUIVOS_IES_CANDIDATOS": "",
            "ARQUIVOS_COMPLEMENTARES": "",
            "TEM_CINE": False,
            "TEM_OCDE": False,
            "TEM_AREA_ANTIGA": False,
            "COLUNAS_AREA": "",
            "COLUNAS_CURSO": "",
            "COLUNAS_METRICAS_BASICAS": "",
            "COLUNAS_SITUACAO_EVADIDA": "",
            "DS_STATUS_INTEGRACAO": status,
            "DS_OBSERVACAO": observacao,
        }

    arquivos = nomes_csv(pasta_ano)
    arquivos_curso = nomes_com_termo(arquivos, TERMOS_ARQUIVO_CURSO)
    arquivos_ies = nomes_com_termo(arquivos, TERMOS_ARQUIVO_IES)
    arquivos_complementares = nomes_com_termo(arquivos, TERMOS_ARQUIVO_COMPLEMENTAR)

    colunas = []
    for arquivo in arquivos_curso:
        try:
            colunas.extend(colunas_csv(arquivo))
        except Exception as exc:
            colunas.append(f"ERRO_AO_LER_{arquivo.name}:{exc}")

    colunas_area = filtrar_colunas(colunas, TERMOS_AREA)
    colunas_curso = filtrar_colunas(colunas, TERMOS_CURSO)
    colunas_metricas = filtrar_colunas(colunas, TERMOS_METRICAS_BASICAS)
    colunas_situacao = filtrar_colunas(colunas, TERMOS_SITUACAO)
    status, observacao = status_ano(ano)

    return {
        "NU_ANO_CENSO": ano,
        "QT_ARQUIVOS_CSV": len(arquivos),
        "ARQUIVOS_CURSO_CANDIDATOS": juntar(arquivo.name for arquivo in arquivos_curso),
        "ARQUIVOS_IES_CANDIDATOS": juntar(arquivo.name for arquivo in arquivos_ies),
        "ARQUIVOS_COMPLEMENTARES": juntar(arquivo.name for arquivo in arquivos_complementares),
        "TEM_CINE": any("CINE" in coluna.upper() for coluna in colunas),
        "TEM_OCDE": any("OCDE" in coluna.upper() for coluna in colunas),
        "TEM_AREA_ANTIGA": bool(colunas_area),
        "COLUNAS_AREA": juntar(colunas_area),
        "COLUNAS_CURSO": juntar(colunas_curso),
        "COLUNAS_METRICAS_BASICAS": juntar(colunas_metricas),
        "COLUNAS_SITUACAO_EVADIDA": juntar(colunas_situacao),
        "DS_STATUS_INTEGRACAO": status,
        "DS_OBSERVACAO": observacao,
    }


def main():
    HISTORICO.mkdir(parents=True, exist_ok=True)
    inventario = pd.DataFrame([inventariar_ano(ano) for ano in ANOS])
    inventario.to_csv(SAIDA, sep=";", index=False, encoding="utf-8-sig")
    print("Inventario de anos antigos gerado:")
    print(SAIDA)
    print(inventario[["NU_ANO_CENSO", "DS_STATUS_INTEGRACAO", "DS_OBSERVACAO"]])


if __name__ == "__main__":
    main()
