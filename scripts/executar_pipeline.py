from __future__ import annotations

import time
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TEMPORARIOS = ROOT / "data" / "processed" / ".pipeline"

# Sequência lógica e estrita de dependências da pipeline
ETAPAS = [
    "consolidar_cursos.py",
    "criar_base_comparavel.py",
    "consolidar_situacao_academica.py",
    "gerar_planilhas_oficiais.py",
    "validar_planilhas_oficiais.py",
]

def main() -> None:
    # Garante um estado limpo expurgando resquícios de execuções corrompidas anteriores
    if TEMPORARIOS.exists():
        print(f"Limpando diretório temporário de trabalho: {TEMPORARIOS.name}...")
        shutil.rmtree(TEMPORARIOS, ignore_errors=True)

    tempo_inicio_total = time.time()
    print(f"=== Iniciando Pipeline de Consolidação Histórica (2009-2024) ===")
    print(f"Raiz do projeto configurada em: {ROOT}\n")

    try:
        for i, etapa in enumerate(ETAPAS, start=1):
            script_caminho = SCRIPTS / etapa
            if not script_caminho.exists():
                raise FileNotFoundError(f"Script estrutural da etapa {i} não encontrado: {script_caminho}")

            print(f"[{i}/{len(ETAPAS)}] Executando sub-processo: {etapa}...", flush=True)
            tempo_inicio_etapa = time.time()

            # Execução controlada isolando o ambiente Python virtual atual (.venv)
            resultado = subprocess.run(
                [sys.executable, str(script_caminho)],
                cwd=str(ROOT),
                capture_output=False,  # Mantém os prints dos scripts visíveis no console
                text=True,
                check=False  # Tratamento manual para logs customizados antes do crash
            )

            duracao_etapa = time.time() - tempo_inicio_etapa

            if resultado.returncode != 0:
                print(f"\n[ERRO CRÍTICO] A etapa '{etapa}' falhou com código de saída {resultado.returncode}.", file=sys.stderr)
                print("Interrompendo a esteira de processamento para evitar corrupção na base histórica.", file=sys.stderr)
                sys.exit(resultado.returncode)

            print(f"[SUCESSO] Etapa '{etapa}' concluída em {duracao_etapa:.2f} segundos.\n")

        # Expurga os arquivos voláteis apenas se toda a esteira rodar com sucesso
        if TEMPORARIOS.exists():
            print(f"Finalizando esteira com sucesso. Limpando artefatos intermediários em {TEMPORARIOS.name}...")
            shutil.rmtree(TEMPORARIOS, ignore_errors=True)

    except Exception as exc:
        print(f"\n[FALHA INESPERADA NA PIPELINE]: {exc}", file=sys.stderr)
        sys.exit(1)

    tempo_total = time.time() - tempo_inicio_total
    print("\n=======================================================================")
    print(f"Pipeline concluída com paridade total em {tempo_total/60:.2f} minutos.")
    print("As planilhas finais tratadas estão consolidadas em: data/processed/oficial/")
    print("=======================================================================")

if __name__ == "__main__":
    main()