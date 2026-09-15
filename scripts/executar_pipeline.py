from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TEMPORARIOS = ROOT / "data" / "processed" / ".pipeline"

ETAPAS = [
    "consolidar_cursos.py",
    "criar_base_comparavel.py",
    "consolidar_situacao_academica.py",
    "gerar_planilhas_oficiais.py",
    "validar_planilhas_oficiais.py",
    "gerar_extratos_curadoria.py",
    "vistoriar_conteudo.py",
]


def main():
    shutil.rmtree(TEMPORARIOS, ignore_errors=True)

    try:
        for etapa in ETAPAS:
            print(f"\n=== {etapa} ===", flush=True)
            subprocess.run(
                [sys.executable, str(SCRIPTS / etapa)],
                cwd=ROOT,
                check=True,
            )
    finally:
        shutil.rmtree(TEMPORARIOS, ignore_errors=True)

    print("\nPipeline concluida. As planilhas finais estao em data/processed/oficial/.")


if __name__ == "__main__":
    main()
