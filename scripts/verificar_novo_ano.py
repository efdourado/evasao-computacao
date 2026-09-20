"""Checagem previa de um ano novo do Censo, antes de rodar o pipeline.

O leitor de cursos preenche com vazio qualquer coluna que sumir, entao uma
mudanca de layout do INEP pode produzir um ano quase vazio sem nenhum erro.
Esta checagem pega isso antes: confere se os arquivos existem, se as colunas
que o pipeline usa continuam la, se o recorte nao ficou vazio ou muito
diferente do ano anterior e se apareceram rotulos de classificacao novos.

Uso:
    .venv/bin/python scripts/verificar_novo_ano.py 2025
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anos import ROOT, anos_todos, ano_de_referencia  # noqa: E402
from consolidar_cursos import (  # noqa: E402
    COLUNAS_CURSOS_LEITURA, colunas_csv, limpar_codigo, read_csv,
)

RAW = ROOT / "data" / "raw"
ESQUEMA = ROOT / "config" / "esquema_cadastro_cursos.csv"
LIMITES = ROOT / "config" / "limites_continuidade.csv"
PRINCIPAL = ROOT / "data" / "processed" / "oficial" / "planilha_oficial_computacao.csv"
ROTULO_ENGENHARIA = "0714E04"
SIMBOLOS = {"ERRO": "x", "ALERTA": "!", "OK": "v", "INFO": "-"}


def resultado(nivel, verificacao, detalhe):
    return {"NIVEL": nivel, "VERIFICACAO": verificacao, "DETALHE": detalhe}


def localizar(raw, ano, nomes):
    pasta = Path(raw) / str(ano)
    if not pasta.exists():
        return None
    alvo = {n.upper() for n in nomes}
    for caminho in sorted(pasta.rglob("*")):
        if caminho.is_file() and caminho.name.upper() in alvo:
            return caminho
    return None


def carregar_limites(caminho=LIMITES):
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig", dtype=str)
    return {l["METRICA"]: (float(l["ALERTA_PCT"]), float(l["ERRO_PCT"])) for l in df.to_dict("records")}


def classificar_variacao(variacao, limite):
    alerta, erro = limite
    if abs(variacao) >= erro:
        return "ERRO"
    if abs(variacao) >= alerta:
        return "ALERTA"
    return "OK"


def verificar(ano, raw=RAW, esquema=ESQUEMA, principal=None, limites=None, anos_registrados=None):
    """Devolve a lista de resultados. Qualquer NIVEL igual a ERRO impede seguir."""
    ano = str(ano)
    limites = limites or carregar_limites()
    esquema = pd.read_csv(esquema, sep=";", encoding="utf-8-sig", dtype=str)
    saida = []

    cursos = localizar(raw, ano, [f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV"])
    ies = localizar(raw, ano, [f"MICRODADOS_ED_SUP_IES_{ano}.CSV", f"MICRODADOS_CADASTRO_IES_{ano}.CSV"])
    dica = (f"Coloque os arquivos em data/raw/{ano}/dados/ ou use --zip com o arquivo baixado do INEP.")
    saida.append(resultado("OK", "arquivo de cursos", str(cursos)) if cursos
                 else resultado("ERRO", "arquivo de cursos", f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV nao encontrado. {dica}"))
    saida.append(resultado("OK", "arquivo de IES", str(ies)) if ies
                 else resultado("ERRO", "arquivo de IES", f"arquivo de IES de {ano} nao encontrado. {dica}"))
    if not cursos:
        return saida

    # 1. esquema
    colunas = colunas_csv(cursos)
    obrigatorias = [c for c in esquema.loc[esquema["OBRIGATORIA"] == "sim", "COLUNA"]]
    faltando = [c for c in obrigatorias if c not in colunas]
    if "CO_CINE_ROTULO" in faltando and "CO_CINE_ROTULO2" in colunas:
        faltando.remove("CO_CINE_ROTULO")
    if faltando:
        saida.append(resultado("ERRO", "colunas obrigatorias",
                               f"faltam {len(faltando)} colunas que o pipeline usa: {', '.join(faltando[:12])}. "
                               "O INEP provavelmente mudou o layout. Ajuste COLUNAS_CURSOS_LEITURA em consolidar_cursos.py."))
    else:
        saida.append(resultado("OK", "colunas obrigatorias", f"as {len(obrigatorias)} colunas usadas pelo pipeline estao presentes"))
    conhecidas = set(esquema["COLUNA"])
    novas = [c for c in colunas if c not in conhecidas]
    sumidas = [c for c in conhecidas if c not in colunas and c not in obrigatorias]
    saida.append(resultado("INFO", "layout", f"{len(novas)} colunas novas e {len(sumidas)} ausentes em relacao ao layout de referencia; nenhuma delas e usada pelo pipeline"))

    # 2. conteudo
    desejadas = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO", "CO_CINE_AREA_GERAL", "CO_CINE_ROTULO", "CO_CINE_ROTULO2", "TP_NIVEL_ACADEMICO"]
    df = read_csv(cursos, usecols=[c for c in desejadas if c in colunas])
    anos_no_arquivo = set(df["NU_ANO_CENSO"].dropna().astype(str).str.strip()) if "NU_ANO_CENSO" in df else set()
    if anos_no_arquivo and anos_no_arquivo != {ano}:
        saida.append(resultado("ERRO", "ano do arquivo", f"o arquivo traz NU_ANO_CENSO {sorted(anos_no_arquivo)}, esperado {ano}. Arquivo de outro ano?"))
    else:
        saida.append(resultado("OK", "ano do arquivo", f"NU_ANO_CENSO igual a {ano}"))

    rotulo = limpar_codigo(df["CO_CINE_ROTULO"]) if "CO_CINE_ROTULO" in df else pd.Series("", index=df.index)
    if "CO_CINE_ROTULO2" in df:
        vazio = rotulo.isna() | rotulo.eq("")
        rotulo = rotulo.mask(vazio, limpar_codigo(df["CO_CINE_ROTULO2"]))
    area = limpar_codigo(df["CO_CINE_AREA_GERAL"]) if "CO_CINE_AREA_GERAL" in df else pd.Series("", index=df.index)
    graduacao = df["TP_NIVEL_ACADEMICO"].astype(str).str.strip().isin(["1", "1.0"]) if "TP_NIVEL_ACADEMICO" in df else True
    no_recorte = (area.isin(["6", "06"]) | rotulo.eq(ROTULO_ENGENHARIA)) & graduacao
    cursos_recorte = df.loc[no_recorte, ["CO_IES", "CO_CURSO"]].drop_duplicates()
    if cursos_recorte.empty:
        saida.append(resultado("ERRO", "recorte", "o recorte de Computacao/TIC ficou vazio. Provavel mudanca no nome da coluna de area ou no codigo da classificacao."))
        return saida

    # 3. comparacao com o ano anterior
    if principal is None and PRINCIPAL.exists():
        principal = pd.read_csv(PRINCIPAL, sep=";", encoding="utf-8-sig", dtype=str, usecols=["NU_ANO_CENSO", "CO_ROTULO_AREA", "DS_CLASSIFICACAO_AREA"], keep_default_na=False)
    anos = anos_registrados if anos_registrados is not None else anos_todos()
    anteriores = [a for a in anos if a < ano]
    if principal is not None and anteriores:
        anterior = anteriores[-1]
        base = int((principal["NU_ANO_CENSO"] == anterior).sum())
        if base:
            variacao = 100 * (len(cursos_recorte) - base) / base
            nivel = classificar_variacao(variacao, limites["LINHAS"])
            saida.append(resultado(nivel, "cursos no recorte",
                                   f"{len(cursos_recorte)} cursos contra {base} em {anterior} ({variacao:+.1f}%)"))
        else:
            saida.append(resultado("ALERTA", "cursos no recorte",
                                   f"{anterior} esta registrado mas nao tem linhas na planilha oficial; comparacao pulada. "
                                   "Rode o pipeline para o ano anterior antes de trazer este."))
        conhecidos = set(principal.loc[principal["DS_CLASSIFICACAO_AREA"] != "OCDE", "CO_ROTULO_AREA"])
        novos = sorted(set(rotulo[no_recorte].dropna()) - conhecidos - {""})
        if novos:
            saida.append(resultado("ALERTA", "rotulos novos", f"{len(novos)} rotulos CINE nunca vistos: {', '.join(novos[:10])}. Pode ser nova versao da classificacao."))
        else:
            saida.append(resultado("OK", "rotulos", "nenhum rotulo CINE novo"))
    else:
        saida.append(resultado("INFO", "comparacao", "sem ano anterior na base para comparar"))
    saida.append(resultado("INFO", "recorte", f"{len(cursos_recorte)} cursos de graduacao em Computacao/TIC"))
    return saida


def imprimir(resultados):
    for r in resultados:
        print(f"  [{SIMBOLOS[r['NIVEL']]}] {r['VERIFICACAO']}: {r['DETALHE']}")
    erros = sum(r["NIVEL"] == "ERRO" for r in resultados)
    alertas = sum(r["NIVEL"] == "ALERTA" for r in resultados)
    print(f"  Erros: {erros} | Alertas: {alertas}")
    return erros


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("ano")
    args = parser.parse_args(argv)
    print(f"Checagem previa de {args.ano} (referencia: {ano_de_referencia()})")
    sys.exit(1 if imprimir(verificar(args.ano)) else 0)


if __name__ == "__main__":
    main()
