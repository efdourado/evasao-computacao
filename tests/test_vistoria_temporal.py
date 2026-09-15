"""Verifica limites metodologicos das sequencias e da comparacao territorial."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import pandas as pd

SPEC = importlib.util.spec_from_file_location(
    'vistoria', Path(__file__).resolve().parents[1] / 'scripts/vistoriar_conteudo.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TemporalTests(unittest.TestCase):
    def run_audit(self, records):
        frame = pd.DataFrame(records, columns=['NU_ANO_CENSO', 'CO_MUNICIPIO', 'MAT', 'DS_MODELO_DADOS'])
        frame['CO_IES'] = '1'
        frame['CO_CURSO'] = '2'
        frame['NO_IES'] = 'IES'
        frame['NO_CURSO'] = 'Curso'
        frame['NO_MUNICIPIO'] = frame.CO_MUNICIPIO
        frame['TP_MODALIDADE_ENSINO'] = '2'
        p = frame[MOD.KEY + ['DS_MODELO_DADOS']].drop_duplicates()
        frame = frame.drop(columns='DS_MODELO_DADOS')
        results = {}
        def capture(df, mask, rule, evidence, impact):
            results[rule] = df.loc[mask]
        previous = MOD.OUT
        try:
            with tempfile.TemporaryDirectory() as directory:
                MOD.OUT = Path(directory)
                MOD.vistoria_temporal(frame, p, capture)
        finally:
            MOD.OUT = previous
        return results

    def test_zeros_require_consecutive_observations_and_same_model(self):
        records = [(str(y), 'A', 0, 'novo') for y in [2020, 2021, 2022]]
        records += [(str(y), 'B', 0, 'novo') for y in [2020, 2022, 2023]]
        records += [(str(y), 'C', v, 'novo') for y, v in [(2020, 0), (2021, float('nan')), (2022, 0)]]
        result = self.run_audit(records)['municipio_zero_3_anos_consecutivos']
        self.assertEqual(result.CO_MUNICIPIO.tolist(), ['A'])
        split = self.run_audit([('2020', 'A', 0, 'antigo'), ('2021', 'A', 0, 'novo'), ('2022', 'A', 0, 'novo')])
        self.assertTrue(split['municipio_zero_3_anos_consecutivos'].empty)

    def test_uniform_growth_does_not_change_distribution(self):
        records = [(str(y), str(m), n, 'novo') for y, n in [(2020, 20), (2021, 40)] for m in range(5)]
        self.assertTrue(self.run_audit(records)['mudanca_distribuicao_municipal'].empty)

    def test_disappearing_territory_is_recorded_separately(self):
        records = [('2020', str(m), 20, 'novo') for m in range(5)]
        records += [('2021', str(m), 20, 'novo') for m in range(5, 10)]
        result = self.run_audit(records)['mudanca_distribuicao_municipal']
        self.assertEqual(len(result), 1)
        self.assertEqual(result.VARIACAO_DISTRIBUICAO.iloc[0], 1)
        self.assertEqual(result.FRAC_MAT_EM_MUNICIPIOS_QUE_SOMEM.iloc[0], 1)
        # Ausencia do municipio nao produz sequencia de zeros.
        self.assertTrue(self.run_audit(records)['municipio_zero_3_anos_consecutivos'].empty)


if __name__ == '__main__':
    unittest.main()
