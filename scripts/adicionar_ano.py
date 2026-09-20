"""Adiciona um novo ano do Censo ao projeto, do arquivo do INEP ate as tabelas prontas.

    .venv/bin/python scripts/adicionar_ano.py 2025 --zip ~/Downloads/microdados_2025.zip
    .venv/bin/python scripts/adicionar_ano.py 2025            # arquivos ja em data/raw/2025
    .venv/bin/python scripts/adicionar_ano.py 2025 --verificar # so a checagem previa

Passos: organiza os arquivos, faz a checagem previa, registra o ano em
config/anos.csv, roda o pipeline completo e mostra o que revisar. Nenhum
codigo precisa ser editado quando o INEP mantem o layout do cadastro de cursos.
"""
import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_dados_drive  # noqa: E402
from anos import ROOT, registrar_ano  # noqa: E402
from consolidar_cursos import COLUNAS_CURSOS_LEITURA, colunas_csv  # noqa: E402
from verificar_novo_ano import ESQUEMA, RAW, imprimir, localizar, verificar  # noqa: E402

CONTINUIDADE = ROOT / "data" / "processed" / "validacao" / "continuidade_anual.csv"


def organizar_zip(ano, caminho_zip, raw=RAW, forcar=False):
    """Extrai o zip do INEP e coloca dados e referencia onde o pipeline espera."""
    staging = Path(raw) / f".staging_{ano}"
    shutil.rmtree(staging, ignore_errors=True)
    with zipfile.ZipFile(caminho_zip) as z:
        z.extractall(staging)
    try:
        return baixar_dados_drive.organizar_download(staging, Path(raw) / str(ano), forcar)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def atualizar_esquema(ano, raw=RAW, destino=ESQUEMA):
    arquivo = localizar(raw, ano, [f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV"])
    colunas = colunas_csv(arquivo)
    obrigatorias = set(COLUNAS_CURSOS_LEITURA) - {"CO_CINE_ROTULO2", "TP_ATRIBUTO_INGRESSO"}
    pd.DataFrame({"COLUNA": colunas, "OBRIGATORIA": ["sim" if c in obrigatorias else "nao" for c in colunas]}).to_csv(
        destino, sep=";", index=False, encoding="utf-8-sig", lineterminator="\n")


PROXIMOS_PASSOS = """
Proximos passos (manuais, nesta ordem):
  1. Leia acima o que a checagem previa e a validacao apontaram.
  2. Abra data/processed/validacao/continuidade_anual.csv e veja se {ano} esta coerente com o anterior.
  3. Revise os achados novos de {ano} em data/processed/curadoria/ e em analise/ocorrencias.csv.
     Casos "revisar em nova rodada" no extrato 01 precisam de decisao (config/curadoria_nome_rotulo.csv).
  4. Se surgiu um tipo novo de achado, registre uma decisao em docs/03_manual_de_uso.md.
  5. Atualize os numeros de fotografia dos documentos e faca o commit.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("ano")
    parser.add_argument("--zip", dest="zip_", help="zip de microdados baixado do INEP")
    parser.add_argument("--forcar", action="store_true", help="sobrescreve arquivos ja existentes em data/raw")
    parser.add_argument("--verificar", action="store_true", help="so a checagem previa; nao registra nem roda")
    parser.add_argument("--sem-pipeline", action="store_true", help="registra o ano mas nao roda o pipeline")
    parser.add_argument("--atualizar-esquema", action="store_true", help="passa a usar o layout deste ano como referencia")
    args = parser.parse_args(argv)
    ano = args.ano

    if args.zip_:
        print(f"[1] Organizando {args.zip_} em data/raw/{ano}")
        dados, referencia = organizar_zip(ano, args.zip_, forcar=args.forcar)
        print(f"    {dados} arquivos de dados e {referencia} de referencia")
    print(f"[2] Checagem previa de {ano}")
    if imprimir(verificar(ano)):
        print("\nParado: corrija os erros acima. Nada foi registrado nem alterado.")
        return 1
    if args.verificar:
        return 0

    print(f"[3] Registro em config/anos.csv: {'incluido' if registrar_ano(ano) else 'ja estava registrado'}")
    if args.sem_pipeline:
        return 0
    print(f"[4] Pipeline completo (pode levar varios minutos)")
    try:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "executar_pipeline.py")], cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        print(f"\nO pipeline falhou. {ano} continua registrado em config/anos.csv; para desfazer, apague a linha de {ano} nesse arquivo.")
        return 1
    if args.atualizar_esquema:
        atualizar_esquema(ano)
        print(f"[5] Layout de {ano} passou a ser a referencia em config/esquema_cadastro_cursos.csv")
    if CONTINUIDADE.exists():
        tabela = pd.read_csv(CONTINUIDADE, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
        print("\nContinuidade:")
        print(tabela[tabela["NU_ANO_CENSO"] == ano].to_string(index=False))
    print(PROXIMOS_PASSOS.format(ano=ano))
    return 0


if __name__ == "__main__":
    sys.exit(main())
