"""Baixa os microdados brutos do INEP a partir do Google Drive do projeto.

Este script existe para que qualquer colaborador consiga popular a pasta ``data/raw/``
sem precisar de autenticação OAuth ou chaves de API restritas.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import gdown
except ImportError as exc:
    raise SystemExit(
        "O pacote 'gdown' não está instalado.\n"
        "Rode primeiro:\n"
        "    .venv/bin/pip install -r requirements.txt"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Mapeamento atualizado com os IDs corretos das PASTAS do Google Drive do projeto
FONTES_DRIVE: dict[str, dict] = {
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


def listar_fontes() -> None:
    print("Anos mapeados em FONTES_DRIVE:\n")
    for ano, fonte in sorted(FONTES_DRIVE.items()):
        print(f"  {ano}: pasta do Drive (id={fonte['id']})")


def pasta_tem_arquivos(pasta_ano: Path) -> bool:
    return pasta_ano.exists() and any(pasta_ano.rglob("*.[cC][sS][vV]"))


def organizar_apenas_csv(ano: str, pasta_ano: Path) -> None:
    """Move todo .csv encontrado (em qualquer subpasta) para a raiz de
    data/raw/<ano>/ e depois apaga tudo que não for CSV (pdf, xlsx, Thumbs.db,
    arquivos temporários do Office, txt de hash etc.)."""
    csv_files = [f for f in pasta_ano.rglob("*.[cC][sS][vV]") if f.is_file()]
    if csv_files:
        print(f"[{ano}] organizando {len(csv_files)} arquivo(s) CSV na raiz de data/raw/{ano}/...")
    for f in csv_files:
        dest = pasta_ano / f.name
        if f.resolve() == dest.resolve():
            continue
        if dest.exists():
            print(f"[{ano}] aviso: '{f.name}' já existe na raiz (nome duplicado no Drive) — mantendo o primeiro.")
            continue
        f.rename(dest)

    for item in pasta_ano.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        elif item.suffix.lower() != ".csv":
            try:
                item.unlink()
            except OSError:
                pass


# Uma pasta de ano "completa" (com anexos, dicionários, docente, local de
# oferta etc.) costuma passar de 15-20 GB, mesmo a pipeline só usando uma
# fração disso (DM_ALUNO/DM_CURSO/DM_IES/TB_AUX_CINE_BRASIL). Este número é
# só um alerta antes de começar, não uma garantia de que vai caber.
ESPACO_MINIMO_PASTA_GB = 20


def espaco_livre_gb(caminho: Path) -> float:
    caminho.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(caminho).free / (1024 ** 3)


def espaco_suficiente(pasta_ano: Path, minimo_gb: float, descricao: str) -> bool:
    livre = espaco_livre_gb(pasta_ano)
    if livre >= minimo_gb:
        return True
    print(
        f"[aviso] só há {livre:.1f} GB livres em {pasta_ano.drive or pasta_ano.anchor} "
        f"e {descricao} costuma precisar de pelo menos {minimo_gb:.0f} GB. "
        "Libere espaço (ou baixe para outro disco) antes de continuar."
    )
    resposta = input("Continuar mesmo assim? [s/N] ").strip().lower()
    return resposta == "s"


def baixar_pasta(ano: str, id_pasta: str, forcar: bool) -> bool:
    pasta_ano = RAW / ano
    if pasta_tem_arquivos(pasta_ano) and not forcar:
        print(f"[{ano}] já existem CSVs em data/raw/{ano}/ — pulando (use --forcar para baixar de novo).")
        return True

    if not espaco_suficiente(pasta_ano, ESPACO_MINIMO_PASTA_GB, f"a pasta completa de {ano}"):
        print(f"[{ano}] download cancelado por falta de espaço.")
        return False

    pasta_ano.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.google.com/drive/folders/{id_pasta}"
    print(f"[{ano}] baixando pasta completa do Drive para data/raw/{ano}/ ...")
    erro: Exception | None = None
    try:
        # A remoção do use_cookies e a inclusão do quiet=False ajudam a monitorar o progresso de arquivos grandes
        gdown.download_folder(url=url, output=str(pasta_ano), quiet=False, use_cookies=False)
    except Exception as exc:
        # Não retorna ainda: a pasta pode ter falhado só num PDF/xlsx não
        # essencial (ex: leia-me sem permissão) depois de já ter baixado
        # todos os CSVs. A checagem real de sucesso é a de baixo.
        erro = exc

    print(f"[{ano}] organizando o que foi baixado (só ficam os .csv)...")
    organizar_apenas_csv(ano, pasta_ano)

    if not pasta_tem_arquivos(pasta_ano):
        print(f"[{ano}] erro: a pasta foi processada, mas nenhum arquivo CSV foi encontrado.")
        if erro is not None:
            print(f"[{ano}] detalhe do erro do gdown: {erro}")
        return False

    if erro is not None:
        print(
            f"[{ano}] aviso: um arquivo não essencial (pdf/xlsx/leia-me/filtros) não pôde "
            f"ser baixado ({erro}), mas os CSVs já tinham sido obtidos antes disso."
        )

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa os microdados brutos do Google Drive do projeto.")
    parser.add_argument(
        "--ano",
        nargs="+",
        default=None,
        help="Baixar apenas os anos informados (ex: --ano 2022 2024). Por padrão baixa todos os mapeados.",
    )
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="Baixar de novo mesmo que os arquivos já existam localmente.",
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Só mostra o que está mapeado em FONTES_DRIVE, sem baixar nada.",
    )
    args = parser.parse_args()

    if args.listar:
        listar_fontes()
        return

    anos = args.ano if args.ano else sorted(FONTES_DRIVE.keys())
    anos_invalidos = [ano for ano in anos if ano not in FONTES_DRIVE]
    if anos_invalidos:
        print(f"Anos não mapeados em FONTES_DRIVE: {', '.join(anos_invalidos)}")
        print("Rode com --listar para ver os anos disponíveis.")
        sys.exit(1)

    sucesso: list[str] = []
    falha: list[str] = []

    for ano in anos:
        fonte = FONTES_DRIVE[ano]
        ok = baixar_pasta(ano, fonte["id"], args.forcar)
        (sucesso if ok else falha).append(ano)

    print("\n=== Resumo ===")
    print(f"Anos baixados com sucesso: {', '.join(sucesso) if sucesso else '-'}")
    if falha:
        print(f"Anos com falha: {', '.join(falha)}")
        print(
            "Verifique se as pastas no Drive estão com o compartilhamento configurado como "
            "'Qualquer pessoa com o link pode visualizar'."
        )
        sys.exit(1)

    print("\nArquivos disponíveis em data/raw/<ano>/. Para rodar a pipeline completa:")
    print("    .venv/bin/python scripts/executar_pipeline.py")


if __name__ == "__main__":
    main()