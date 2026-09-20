"""Verifica a etapa 4: registro de anos, checagem previa e continuidade entre anos."""
import importlib.util
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def carregar(nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "scripts" / f"{nome}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


ANOS = carregar("anos")
VERIFICAR = carregar("verificar_novo_ano")
VALIDAR = carregar("validar_planilhas_oficiais")
ADICIONAR = carregar("adicionar_ano")
CONSOLIDAR = carregar("consolidar_cursos")

LIMITES = {"LINHAS": (20.0, 40.0), "MATRICULAS": (35.0, 60.0), "IES": (15.0, 30.0)}
COLUNAS_ESQUEMA = ["NU_ANO_CENSO", "CO_IES", "CO_CURSO", "CO_CINE_AREA_GERAL", "CO_CINE_ROTULO",
                   "TP_NIVEL_ACADEMICO", "QT_MAT"]


class Registro(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.arquivo = self.tmp / "anos.csv"
        shutil.copy(RAIZ / "config" / "anos.csv", self.arquivo)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_lista_de_anos_do_consolidador_nao_mudou(self):
        self.assertEqual(
            CONSOLIDAR.ANOS_CADASTRO_CINE,
            ["2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016",
             "2020", "2021", "2022", "2023", "2024"])

    def test_registrar_ano_novo_e_idempotente(self):
        self.assertTrue(ANOS.registrar_ano("2025", self.arquivo))
        self.assertFalse(ANOS.registrar_ano("2025", self.arquivo))
        self.assertEqual(ANOS.ano_de_referencia(self.arquivo), "2025")
        self.assertIn("2025", ANOS.anos_cadastro_cursos(self.arquivo))

    def test_modelo_errado_para_ano_antigo_e_recusado(self):
        df = pd.read_csv(self.arquivo, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
        df.loc[df["ANO"] == "2018", "MODELO"] = "cadastro_cursos"
        with self.assertRaises(ANOS.ErroRegistroAnos):
            ANOS.validar_anos(df)


class ChecagemPrevia(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.esquema = self.tmp / "esquema.csv"
        pd.DataFrame({"COLUNA": COLUNAS_ESQUEMA, "OBRIGATORIA": ["sim"] * len(COLUNAS_ESQUEMA)}).to_csv(
            self.esquema, sep=";", index=False)
        self.principal = pd.DataFrame({"NU_ANO_CENSO": ["2024"] * 100, "CO_ROTULO_AREA": ["0613C01"] * 100,
                                       "DS_CLASSIFICACAO_AREA": ["CINE"] * 100})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def arquivos(self, ano="2025", cursos=100, ano_no_arquivo=None, rotulo="0613C01", area="6", coluna_area="CO_CINE_AREA_GERAL"):
        pasta = self.tmp / ano / "dados"
        pasta.mkdir(parents=True, exist_ok=True)
        linhas = pd.DataFrame({
            "NU_ANO_CENSO": ano_no_arquivo or ano, "CO_IES": "1", "CO_CURSO": [str(i) for i in range(cursos)],
            coluna_area: area, "CO_CINE_ROTULO": rotulo, "TP_NIVEL_ACADEMICO": "1", "QT_MAT": "10",
        })
        linhas.to_csv(pasta / f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV", sep=";", index=False, encoding="latin1")
        pd.DataFrame({"NU_ANO_CENSO": [ano], "CO_IES": ["1"]}).to_csv(
            pasta / f"MICRODADOS_ED_SUP_IES_{ano}.CSV", sep=";", index=False, encoding="latin1")

    def rodar(self):
        return VERIFICAR.verificar("2025", raw=self.tmp, esquema=self.esquema, principal=self.principal,
                                   limites=LIMITES, anos_registrados=["2024"])

    def niveis(self, resultados):
        return {r["VERIFICACAO"]: r["NIVEL"] for r in resultados}

    def test_ano_coerente_passa(self):
        self.arquivos()
        niveis = self.niveis(self.rodar())
        self.assertNotIn("ERRO", niveis.values())
        self.assertEqual(niveis["cursos no recorte"], "OK")

    def test_arquivo_ausente_diz_onde_colocar(self):
        resultados = self.rodar()
        self.assertEqual(resultados[0]["NIVEL"], "ERRO")
        self.assertIn("data/raw/2025/dados", resultados[0]["DETALHE"])

    def test_coluna_renomeada_pelo_inep_e_barrada(self):
        """O leitor preencheria a coluna com vazio e o ano entraria quase sem cursos."""
        self.arquivos(coluna_area="CO_CINE_AREA_GERAL_NOVA")
        niveis = self.niveis(self.rodar())
        self.assertEqual(niveis["colunas obrigatorias"], "ERRO")
        self.assertEqual(niveis["recorte"], "ERRO")

    def test_arquivo_de_outro_ano_e_barrado(self):
        self.arquivos(ano_no_arquivo="2024")
        self.assertEqual(self.niveis(self.rodar())["ano do arquivo"], "ERRO")

    def test_queda_brusca_de_cursos_e_barrada(self):
        self.arquivos(cursos=30)
        self.assertEqual(self.niveis(self.rodar())["cursos no recorte"], "ERRO")

    def test_variacao_moderada_so_alerta(self):
        self.arquivos(cursos=75)
        self.assertEqual(self.niveis(self.rodar())["cursos no recorte"], "ALERTA")

    def test_ano_anterior_sem_linhas_avisa_em_vez_de_pular_em_silencio(self):
        self.arquivos()
        resultados = VERIFICAR.verificar("2025", raw=self.tmp, esquema=self.esquema, principal=self.principal,
                                         limites=LIMITES, anos_registrados=["2023"])
        self.assertEqual(self.niveis(resultados)["cursos no recorte"], "ALERTA")

    def test_rotulo_novo_gera_alerta(self):
        self.arquivos(rotulo="0619X99")
        resultados = self.rodar()
        self.assertEqual(self.niveis(resultados)["rotulos novos"], "ALERTA")
        self.assertIn("0619X99", [r for r in resultados if r["VERIFICACAO"] == "rotulos novos"][0]["DETALHE"])


class Zip(unittest.TestCase):
    def test_zip_do_inep_vai_para_dados_e_referencia(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            zip_path = tmp / "microdados.zip"
            with zipfile.ZipFile(zip_path, "w") as z:
                z.writestr("Microdados 2025/dados/MICRODADOS_CADASTRO_CURSOS_2025.CSV", "a;b\n1;2\n")
                z.writestr("Microdados 2025/Dicionario.xlsx", "x")
                z.writestr("Microdados 2025/anotacao.bin", "x")
            raw = tmp / "raw"
            dados, referencia = ADICIONAR.organizar_zip("2025", zip_path, raw=raw)
            self.assertEqual((dados, referencia), (1, 1))
            self.assertTrue((raw / "2025/dados/MICRODADOS_CADASTRO_CURSOS_2025.CSV").exists())
            self.assertTrue((raw / "2025/referencia/Dicionario.xlsx").exists())
            self.assertFalse((raw / ".staging_2025").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Continuidade(unittest.TestCase):
    @staticmethod
    def principal(por_ano):
        linhas = []
        for ano, (cursos, mat) in por_ano.items():
            for i in range(cursos):
                linhas.append({"NU_ANO_CENSO": ano, "CO_IES": str(i % 10), "CO_CURSO": str(i),
                               "QT_MAT": str(mat), "DS_TP_MODALIDADE_ENSINO": "Presencial"})
        return pd.DataFrame(linhas)

    def rodar(self, por_ano, anos):
        return VALIDAR.validar_continuidade(self.principal(por_ano), anos=anos, limites=LIMITES)

    def test_evolucao_normal_nao_gera_ocorrencia(self):
        ocorrencias, tabela = self.rodar({"2023": (100, 10), "2024": (108, 11)}, ["2023", "2024"])
        self.assertTrue(ocorrencias.empty)
        self.assertEqual(tabela["STATUS"].tolist(), ["OK", "OK"])

    def test_ano_registrado_sem_linhas_e_erro(self):
        """Foi registrado em config/anos.csv, mas o pipeline nao produziu nada."""
        ocorrencias, tabela = self.rodar({"2024": (100, 10)}, ["2024", "2025"])
        self.assertIn("ano_registrado_sem_linhas", set(ocorrencias["VALIDACAO"]))
        self.assertEqual(tabela.set_index("NU_ANO_CENSO").loc["2025", "STATUS"], "ERRO")

    def test_queda_a_metade_e_erro_e_variacao_moderada_e_alerta(self):
        _, tabela = self.rodar({"2023": (100, 10), "2024": (50, 10)}, ["2023", "2024"])
        self.assertEqual(tabela["STATUS"].tolist(), ["OK", "ERRO"])
        ocorrencias, tabela = self.rodar({"2023": (100, 10), "2024": (125, 10)}, ["2023", "2024"])
        self.assertEqual(tabela["STATUS"].tolist(), ["OK", "ALERTA"])
        self.assertEqual(set(ocorrencias["NIVEL"]), {"ALERTA"})


if __name__ == "__main__":
    unittest.main()
