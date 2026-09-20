"""Verifica as regras que transformam flags e decisoes em IN_USO."""
import importlib.util
from pathlib import Path
import unittest

import pandas as pd

SPEC = importlib.util.spec_from_file_location(
    "camada", Path(__file__).resolve().parents[1] / "scripts/gerar_camada_analise.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def decisoes(*linhas):
    colunas = ["CO_IES", "CO_CURSO", "NU_ANO_CENSO", "USO", "ACAO", "JUSTIFICATIVA", "DATA", "RESPONSAVEL", "DECISAO"]
    return pd.DataFrame(linhas, columns=colunas)


def frame():
    return pd.DataFrame({
        "NU_ANO_CENSO": ["2023", "2023", "2024", "2024"],
        "CO_IES": ["1", "1", "2", "2"],
        "CO_CURSO": ["10", "11", "20", "21"],
    })


class RegrasDeUso(unittest.TestCase):
    def test_apenas_flags_marcadas_como_excluir_removem_linha(self):
        matriz = pd.DataFrame(
            {"VAGAS": ["excluir", "sinalizar", "-"]}, index=["FL_A", "FL_B", "FL_C"])
        F = pd.DataFrame({"FL_A": [True, False, False], "FL_B": [False, True, False],
                          "FL_C": [False, False, True]})
        flags = MOD.flags_que_excluem(matriz, "VAGAS", set(F.columns))
        self.assertEqual(flags, ["FL_A"])
        self.assertEqual(MOD.excluir_por_flags(F, flags).tolist(), [True, False, False])

    def test_linha_sem_dado_nao_vira_excluida(self):
        base_ok = pd.Series([False, True, True])
        excluir = pd.Series([True, True, False])
        self.assertEqual(MOD.classificar(base_ok, excluir).tolist(), ["sem_dado", "excluida", "usada"])

    def test_decisao_manual_exclui_e_mantem_sem_recuperar_sem_dado(self):
        df = frame()
        status = pd.Series(["usada", "sem_dado", "excluida", "usada"])
        regras = decisoes(
            ["1", "", "", "VAGAS", "excluir", "teste", "2026-09-20", "x", "D99"],
            ["2", "20", "", "*", "manter", "teste", "2026-09-20", "x", "D99"],
            ["", "", "2023", "INSCRITOS", "excluir", "outra analise", "2026-09-20", "x", "D99"],
        )
        novo, registro = MOD.aplicar_decisoes(df, status, "VAGAS", regras)
        self.assertEqual(novo.tolist(), ["excluida", "sem_dado", "usada", "usada"])
        self.assertEqual(len(registro), 2)
        self.assertEqual(registro[0]["LINHAS_CASADAS"], 2)
        self.assertEqual(registro[0]["LINHAS_ALTERADAS"], 1)

    def test_base_exige_metrica_preenchida_e_matricula_positiva(self):
        df = pd.DataFrame({"QT_INSCRITO_TOTAL": ["10", "", "0"], "QT_MAT": ["5", "0", "3"]})
        inscritos = {"METRICA_REF": "QT_INSCRITO_TOTAL", "EXIGE_MAT_POSITIVA": "nao"}
        self.assertEqual(MOD.base_disponivel(df, inscritos).tolist(), [True, False, True])
        presenca = {"METRICA_REF": "linhas", "EXIGE_MAT_POSITIVA": "sim"}
        self.assertEqual(MOD.base_disponivel(df, presenca).tolist(), [True, False, True])


class Configuracao(unittest.TestCase):
    def test_config_versionada_e_consistente(self):
        flags, usos, matriz, manuais = MOD.carregar_config()
        self.assertEqual(set(matriz.index), set(flags["FLAG"]))
        self.assertEqual(set(matriz.columns) - {"DECISAO"}, set(usos["USO"]))

    def test_matriz_com_flag_desconhecida_e_rejeitada(self):
        flags, usos, matriz, manuais = MOD.carregar_config()
        quebrada = matriz.reset_index()
        quebrada.loc[0, "FLAG"] = "FL_INEXISTENTE"
        with self.assertRaises(MOD.ErroConfiguracao):
            MOD.validar_config(flags, usos, quebrada, manuais)

    def test_decisao_manual_exige_justificativa(self):
        flags, usos, matriz, manuais = MOD.carregar_config()
        sem_justificativa = decisoes(["1", "", "", "VAGAS", "excluir", "", "2026-09-20", "x", "D99"])
        with self.assertRaises(MOD.ErroConfiguracao):
            MOD.validar_config(flags, usos, matriz.reset_index(), sem_justificativa)

    def test_decisao_manual_nao_pode_excluir_tudo(self):
        flags, usos, matriz, manuais = MOD.carregar_config()
        curinga = decisoes(["", "", "", "*", "excluir", "erro", "2026-09-20", "x", "D99"])
        with self.assertRaises(MOD.ErroConfiguracao):
            MOD.validar_config(flags, usos, matriz.reset_index(), curinga)


if __name__ == "__main__":
    unittest.main()
