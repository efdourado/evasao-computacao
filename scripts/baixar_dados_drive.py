"""Baixa os microdados brutos do Drive compartilhado do projeto.

O script organiza os arquivos no padrao esperado pela pipeline:

    data/raw/<ano>/dados/
    data/raw/<ano>/referencia/

CSVs vao para ``dados/``. Dicionarios, notas, leia-me e filtros vao para
``referencia/``. Questionarios e arquivos auxiliares sem uso direto sao
descartados durante a organizacao do download.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

FONTES_DRIVE: dict[str, dict[str, str]] = {
    "2017": {
        "tipo": "pasta",
        "id": "1cC89WLw4pkylaT2xlmkcXmrV1JKsggBN",
    },
    "2018": {
        "tipo": "pasta",
        "id": "1h3eq5NqKY3NaV2kGfGOnR3Y1oLkDPifa",
    },
    "2019": {
        "tipo": "pasta",
        "id": "1Pn2EFGR13z1mPpu5Sk8XLBunFoEOv_Vw",
    },
    "2022": {
        "tipo": "pasta",
        "id": "1A6GpXNSFY9Ji6JoLpAb7pNpHAev1oIFR",
    },
    "2024": {
        "tipo": "pasta",
        "id": "1Oz356C1kN1RYXajhNN9uaX_TgEg09oa2",
    },
}

EXTENSOES_REFERENCIA = {
    ".doc",
    ".docx",
    ".html",
    ".pdf",
    ".txt",
    ".xls",
    ".xlsx",
    ".zip",
}

ESPACO_MINIMO_POR_ANO_GB = 20


def importar_gdown():
    try:
        import gdown
    except ImportError as exc:
        raise SystemExit(
            "O pacote 'gdown' nao esta instalado.\n"
            "Rode primeiro:\n"
            "    .venv/bin/pip install -r requirements.txt"
        ) from exc
    return gdown


def nome_normalizado(caminho: Path) -> str:
    texto = unicodedata.normalize("NFKD", caminho.name)
    return texto.encode("ascii", "ignore").decode("ascii").upper()


def eh_questionario(caminho: Path) -> bool:
    nome = nome_normalizado(caminho)
    return "QUESTIONARIO" in nome or "QUESTIONARIOS" in nome


def listar_fontes() -> None:
    print("Anos mapeados em FONTES_DRIVE:\n")
    for ano, fonte in sorted(FONTES_DRIVE.items()):
        print(f"  {ano}: {fonte['tipo']} do Drive (id={fonte['id']})")


def pasta_tem_csv(pasta_ano: Path) -> bool:
    dados = pasta_ano / "dados"
    return dados.exists() and any(dados.rglob("*.[cC][sS][vV]"))


def espaco_livre_gb(caminho: Path) -> float:
    caminho.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(caminho).free / (1024**3)


def confirmar_espaco(pasta_ano: Path) -> bool:
    livre = espaco_livre_gb(pasta_ano)
    if livre >= ESPACO_MINIMO_POR_ANO_GB:
        return True

    print(
        f"[aviso] ha apenas {livre:.1f} GB livres. "
        f"Um ano completo pode precisar de {ESPACO_MINIMO_POR_ANO_GB} GB."
    )
    resposta = input("Continuar mesmo assim? [s/N] ").strip().lower()
    return resposta == "s"


def mover_arquivo(origem: Path, destino_dir: Path, forcar: bool) -> bool:
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / origem.name

    if destino.exists():
        if not forcar:
            print(f"[aviso] {destino.name} ja existe; mantendo arquivo atual.")
            return False
        destino.unlink()

    shutil.move(str(origem), str(destino))
    return True


def organizar_download(staging: Path, pasta_ano: Path, forcar: bool) -> tuple[int, int]:
    dados = pasta_ano / "dados"
    referencia = pasta_ano / "referencia"
    total_dados = 0
    total_referencia = 0

    arquivos = [caminho for caminho in staging.rglob("*") if caminho.is_file()]
    for caminho in arquivos:
        sufixo = caminho.suffix.lower()

        if sufixo == ".csv" and not eh_questionario(caminho):
            if mover_arquivo(caminho, dados, forcar):
                total_dados += 1
            continue

        if sufixo in EXTENSOES_REFERENCIA and not eh_questionario(caminho):
            if mover_arquivo(caminho, referencia, forcar):
                total_referencia += 1

    return total_dados, total_referencia


def baixar_pasta(ano: str, id_pasta: str, forcar: bool) -> bool:
    pasta_ano = RAW / ano
    staging = pasta_ano / ".download_tmp"

    if pasta_tem_csv(pasta_ano) and not forcar:
        print(f"[{ano}] CSVs ja existem em data/raw/{ano}/dados/; pulando.")
        return True

    if not confirmar_espaco(pasta_ano):
        print(f"[{ano}] download cancelado por falta de espaco.")
        return False

    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)

    gdown = importar_gdown()
    url = f"https://drive.google.com/drive/folders/{id_pasta}"
    print(f"[{ano}] baixando pasta do Drive...")

    erro: Exception | None = None
    try:
        gdown.download_folder(
            url=url,
            output=str(staging),
            quiet=False,
            use_cookies=False,
        )
    except Exception as exc:
        erro = exc

    total_dados, total_referencia = organizar_download(staging, pasta_ano, forcar)
    shutil.rmtree(staging, ignore_errors=True)

    if total_dados == 0:
        print(f"[{ano}] nenhum CSV util foi encontrado no download.")
        if erro is not None:
            print(f"[{ano}] erro do gdown: {erro}")
        return False

    print(
        f"[{ano}] organizado: {total_dados} arquivo(s) em dados/ "
        f"e {total_referencia} em referencia/."
    )
    if erro is not None:
        print(f"[{ano}] aviso: o Drive retornou erro apos baixar parte dos arquivos: {erro}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa e organiza os microdados brutos do Drive do projeto."
    )
    parser.add_argument(
        "--ano",
        nargs="+",
        default=None,
        help="Baixar apenas os anos informados. Exemplo: --ano 2022 2024.",
    )
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="Baixar de novo e sobrescrever arquivos com o mesmo nome.",
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Listar anos mapeados sem baixar nada.",
    )
    args = parser.parse_args()

    if args.listar:
        listar_fontes()
        return

    anos = args.ano if args.ano else sorted(FONTES_DRIVE)
    invalidos = [ano for ano in anos if ano not in FONTES_DRIVE]
    if invalidos:
        print(f"Anos nao mapeados: {', '.join(invalidos)}")
        print("Use --listar para ver os anos disponiveis.")
        sys.exit(1)

    sucesso: list[str] = []
    falha: list[str] = []
    for ano in anos:
        fonte = FONTES_DRIVE[ano]
        if fonte["tipo"] != "pasta":
            print(f"[{ano}] tipo de fonte ainda nao suportado: {fonte['tipo']}")
            falha.append(ano)
            continue
        ok = baixar_pasta(ano, fonte["id"], args.forcar)
        (sucesso if ok else falha).append(ano)

    print("\nResumo:")
    print(f"  sucesso: {', '.join(sucesso) if sucesso else '-'}")
    print(f"  falha: {', '.join(falha) if falha else '-'}")

    if falha:
        sys.exit(1)

    print("\nDepois do download, rode:")
    print("  .venv/bin/python scripts/executar_pipeline.py")


if __name__ == "__main__":
    main()
