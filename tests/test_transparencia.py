"""Verifica as frases e os resumos que a instituicao le no painel."""
import importlib.util
from pathlib import Path
import unittest

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("transp", RAIZ / "scripts/gerar_transparencia.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class Contexto:
    ultimo_ano = 2024
    mat = {("1", "10", 2022): 178.0, ("1", "10", 2024): 198.0, ("1", "11", 2023): 47.0}
    vagas = {("2013", "322"): {"VALOR_VAGAS": "230", "N_CURSOS_COM_ESSE_VALOR": "52", "N_CURSOS_COMPUTACAO": "97"}}
    municipios = {"2024|1|10": {"MUN": 10, "ZERO": 4}}


class Formatos(unittest.TestCase):
    def test_numeros_no_padrao_brasileiro(self):
        self.assertEqual(MOD.n("13896"), "13.896")
        self.assertEqual(MOD.n(""), "sem dado")
        self.assertEqual(MOD.pct("0.516"), "52%")

    def test_concordancia_singular_e_plural(self):
        self.assertEqual(MOD.plural("1", "ingressante", "ingressantes"), "1 ingressante")
        self.assertEqual(MOD.plural("6", "ingressante", "ingressantes"), "6 ingressantes")

    def test_lista_em_portugues(self):
        self.assertEqual(MOD.lista_pt(["a", "b", "c"]), "a, b e c")


class Frases(unittest.TestCase):
    def test_vagas_repetidas_cita_os_numeros_do_caso(self):
        r = {"NU_ANO_CENSO": "2013", "CO_IES": "322", "QT_VG_TOTAL": "230"}
        texto = MOD.ev_vagas_repetidas(r, Contexto())
        for trecho in ("230 vagas", "52 dos seus 97 cursos"):
            self.assertIn(trecho, texto)

    def test_matricula_que_cai_a_zero_informa_o_que_veio_depois(self):
        r = {"NU_ANO_CENSO": "2023", "CO_IES": "1", "CO_CURSO": "10"}
        c = Contexto()
        c.mat = {("1", "10", 2022): 178.0, ("1", "10", 2024): 198.0}
        self.assertIn("em 2024, 198", MOD.ev_mat_cai_a_zero(r, c))
        ultimo = {"NU_ANO_CENSO": "2024", "CO_IES": "1", "CO_CURSO": "11"}
        self.assertIn("2025 ainda não está na base", MOD.ev_mat_cai_a_zero(ultimo, c))

    def test_inscrito_zero_nao_diz_zero_vagas_quando_nao_ha(self):
        r = {"QT_ING": "237", "QT_VG_TOTAL": "0"}
        texto = MOD.ev_inscrito_zero(r, Contexto())
        self.assertIn("237 ingressantes", texto)
        self.assertNotIn("vagas", texto)

    def test_matricula_zero_com_ingresso_concorda_no_singular(self):
        r = {"NU_ANO_CENSO": "2017", "QT_ING": "1", "QT_SIT_TRANCADA": "0", "QT_SIT_DESVINCULADO": "1"}
        self.assertIn("1 ingressante e 1 desvinculado", MOD.ev_mat_zero_com_ing(r, Contexto()))

    def test_flag_sem_frase_propria_usa_o_texto_do_catalogo(self):
        dim = pd.DataFrame({"O_QUE_E": ["texto geral"]}, index=["FL_NOVA"])
        self.assertEqual(MOD.evidencia("FL_NOVA", {}, Contexto(), dim), "texto geral")


class Cobertura(unittest.TestCase):
    def test_toda_flag_do_catalogo_tem_frase_propria(self):
        """Uma flag nova sem frase cai no texto geral. Este teste avisa para escrever a frase."""
        catalogo = pd.read_csv(RAIZ / "config/flags.csv", sep=";", encoding="utf-8-sig", dtype=str)
        sem_frase = set(catalogo["FLAG"]) - set(MOD.EVIDENCIAS) - MOD.FLAGS_MUNICIPAIS
        self.assertEqual(sem_frase, set())


if __name__ == "__main__":
    unittest.main()
