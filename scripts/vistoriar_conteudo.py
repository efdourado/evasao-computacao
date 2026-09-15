"""Triagem de conteudo sem alterar bases oficiais; evidencias para revisao humana."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/curadoria'
KEY = ['NU_ANO_CENSO', 'CO_IES', 'CO_CURSO']
MET = ['QT_VG_TOTAL', 'QT_INSCRITO_TOTAL', 'QT_ING', 'QT_MAT', 'QT_CONC',
       'QT_SIT_TRANCADA', 'QT_SIT_DESVINCULADO', 'QT_SIT_TRANSFERIDO', 'QT_SIT_FALECIDO']


def read(path):
    return pd.read_csv(path, sep=';', dtype=str, encoding='utf-8-sig')


def vistoria_temporal(municipal, p, add):
    """Anos ausentes interrompem sequencias; territorio ausente nao vira zero."""
    m = municipal.merge(p[KEY + ['DS_MODELO_DADOS']], on=KEY, validate='many_to_one')
    m['YEAR'] = m.NU_ANO_CENSO.astype(int)
    keys = ['CO_IES', 'CO_CURSO', 'CO_MUNICIPIO', 'DS_MODELO_DADOS', 'TP_MODALIDADE_ENSINO']
    m = m.sort_values(keys + ['YEAR'])
    g = m.groupby(keys, dropna=False)
    zero = m.MAT.eq(0)
    previous_zero = g.MAT.shift().eq(0)
    consecutive = m.YEAR.sub(g.YEAR.shift()).eq(1)
    m['RUN'] = (~(zero & previous_zero & consecutive)).cumsum()
    runs = m.loc[zero].groupby(keys + ['RUN'], dropna=False).agg(
        ANO_INICIAL=('YEAR', 'min'), ANO_FINAL=('YEAR', 'max'), ANOS_ZERO=('YEAR', 'size'),
        NO_IES=('NO_IES', 'last'), NO_CURSO=('NO_CURSO', 'last'), NO_MUNICIPIO=('NO_MUNICIPIO', 'last'),
    ).reset_index()
    runs = runs[runs.ANOS_ZERO.ge(3)].copy()
    runs['NU_ANO_CENSO'] = runs.ANO_FINAL.astype(str)
    runs.drop(columns='RUN').to_csv(OUT / '16_zeros_municipais_persistentes.csv', sep=';', index=False, encoding='utf-8-sig')
    add(runs, pd.Series(True, index=runs.index), 'municipio_zero_3_anos_consecutivos',
        lambda i, r: f"{r.ANO_INICIAL}-{r.ANO_FINAL}: {r.ANOS_ZERO} anos presentes com MAT=0; municipio={r.CO_MUNICIPIO}",
        'persistencia de oferta territorial sem matriculas declaradas')

    shifts = []
    grouped = m.groupby(['CO_IES', 'CO_CURSO', 'DS_MODELO_DADOS', 'TP_MODALIDADE_ENSINO'], dropna=False)
    for (ies, course, model, mode), group in grouped:
        years = {int(y): rows for y, rows in group.groupby('YEAR')}
        for year, b in years.items():
            if year - 1 not in years:
                continue
            a = years[year - 1]
            if min(a.CO_MUNICIPIO.nunique(), b.CO_MUNICIPIO.nunique()) < 5:
                continue
            if a.MAT.isna().any() or b.MAT.isna().any():
                continue
            av = a.groupby('CO_MUNICIPIO').MAT.sum()
            bv = b.groupby('CO_MUNICIPIO').MAT.sum()
            ta, tb = av.sum(), bv.sum()
            if min(ta, tb) < 100:
                continue
            shares = pd.concat([av / ta, bv / tb], axis=1, keys=['a', 'b'])
            # Zero aqui representa participacao ausente no vetor declarado,
            # nao imputacao de matricula na tabela oficial.
            tv = shares.fillna(0).diff(axis=1)['b'].abs().sum() / 2
            lost = av.index.difference(bv.index)
            lost_share = av.loc[lost].sum() / ta
            if tv < .5 and lost_share < .5:
                continue
            shifts.append(dict(NU_ANO_CENSO=str(year), ANO_ANTERIOR=year-1,
                CO_IES=ies, CO_CURSO=course, NO_IES=b.NO_IES.iloc[0], NO_CURSO=b.NO_CURSO.iloc[0],
                DS_MODELO_DADOS=model, TP_MODALIDADE_ENSINO=mode,
                MUNICIPIOS_ANTES=len(av), MUNICIPIOS_DEPOIS=len(bv),
                MAT_ANTES=ta, MAT_DEPOIS=tb, VARIACAO_DISTRIBUICAO=round(tv, 6),
                FRAC_MAT_EM_MUNICIPIOS_QUE_SOMEM=round(lost_share, 6),
                MAIOR_MUNICIPIO_ANTES=av.idxmax(), MAIOR_MUNICIPIO_DEPOIS=bv.idxmax()))
    changes = pd.DataFrame(shifts, columns=KEY + ['ANO_ANTERIOR', 'NO_IES', 'NO_CURSO',
        'DS_MODELO_DADOS', 'TP_MODALIDADE_ENSINO', 'MUNICIPIOS_ANTES', 'MUNICIPIOS_DEPOIS',
        'MAT_ANTES', 'MAT_DEPOIS', 'VARIACAO_DISTRIBUICAO', 'FRAC_MAT_EM_MUNICIPIOS_QUE_SOMEM',
        'MAIOR_MUNICIPIO_ANTES', 'MAIOR_MUNICIPIO_DEPOIS'])
    changes.to_csv(OUT / '17_mudancas_distribuicao.csv', sep=';', index=False, encoding='utf-8-sig')
    add(changes, pd.Series(True, index=changes.index), 'mudanca_distribuicao_municipal',
        lambda i, r: f"{r.ANO_ANTERIOR}-{r.NU_ANO_CENSO}: distancia={r.VARIACAO_DISTRIBUICAO}; fracao anterior em municipios ausentes={r.FRAC_MAT_EM_MUNICIPIOS_QUE_SOMEM}; MAT={r.MAT_ANTES}->{r.MAT_DEPOIS}",
        'ruptura territorial declarada; nao implica migracao individual dos estudantes')


def main():
    p = read(ROOT / 'data/processed/oficial/planilha_oficial_computacao.csv')
    e = read(ROOT / 'data/processed/oficial/planilha_oficial_computacao_expandida.csv')
    n = p[MET].apply(pd.to_numeric, errors='coerce')
    en = e[MET].apply(pd.to_numeric, errors='coerce')
    flags = []
    counts = []

    def add(frame, mask, rule, evidence, impact):
        sub = frame.loc[mask].copy()
        unit = {'municipio_zero_3_anos_consecutivos': 'sequencia municipal',
                'mudanca_distribuicao_municipal': 'transicao anual'}.get(rule, 'linha')
        counts.append({'REGRA': rule, 'UNIDADE': unit, 'QUANTIDADE': len(sub)})
        for idx, row in sub.iterrows():
            flags.append({**{c: row.get(c, '') for c in KEY + ['NO_IES', 'NO_CURSO', 'CO_MUNICIPIO', 'NO_MUNICIPIO']},
                          'REGRA': rule, 'EVIDENCIA': evidence(idx, row), 'IMPACTO': impact,
                          'STATUS': 'suspeita; sem erro de declaracao confirmado'})

    for frame, nums, label in [(p, n, 'principal'), (e, en, 'expandida')]:
        add(frame, nums.lt(0).any(axis=1), 'valor_negativo_' + label,
            lambda i, r, ns=nums: ns.loc[i][ns.loc[i].lt(0)].to_json(), 'contagens')
        add(frame, (nums.notna() & nums.mod(1).ne(0)).any(axis=1), 'contagem_fracionaria_' + label,
            lambda i, r, ns=nums: ns.loc[i].to_json(), 'contagens')
        invalid = frame[MET].notna() & nums.isna()
        add(frame, invalid.any(axis=1), 'valor_nao_numerico_' + label,
            lambda i, r: r[MET].to_json(), 'leitura das metricas')

    add(p, n.notna().all(axis=1) & n.eq(0).all(axis=1), 'todas_metricas_informadas_zero',
        lambda i, r: 'As nove metricas estao preenchidas com zero.', 'oferta sem atividade ou preenchimento')
    counts.append({'REGRA': 'principal_com_alguma_metrica_ausente', 'UNIDADE': 'linha', 'QUANTIDADE': int(n.isna().any(axis=1).sum())})
    add(p, n.QT_MAT.eq(0) & n.QT_ING.ge(20), 'zero_matriculas_com_ingresso',
        lambda i, r: f"MAT=0; ING={r.QT_ING}; DESV={r.QT_SIT_DESVINCULADO}; TRANC={r.QT_SIT_TRANCADA}",
        'pode refletir saida dos ingressantes durante o ano; conferir situacoes')
    add(p, n.QT_MAT.eq(0) & n.QT_CONC.gt(0), 'zero_matriculas_com_concluintes',
        lambda i, r: f"MAT=0; CONC={r.QT_CONC}", 'compatibilidade de conceitos e preenchimento')
    add(p, n.QT_MAT.eq(0) & n.QT_ING.between(1, 19), 'zero_matriculas_com_ingresso_1_a_19',
        lambda i, r: f"MAT=0; ING={r.QT_ING}; DESV={r.QT_SIT_DESVINCULADO}",
        'baixa escala tambem merece conferencia; nao e erro automatico')
    add(p, p.NO_ROTULO_AREA.fillna('').str.contains('processo de defini', case=False),
        'classificacao_em_definicao', lambda i, r: f"{r.CO_ROTULO_AREA}: {r.NO_ROTULO_AREA}",
        'classificacao declarada ainda em definicao; nao inferir categoria pelo nome')

    h = p.assign(MAT=n.QT_MAT, YEAR=p.NU_ANO_CENSO.astype(int)).sort_values(['CO_IES', 'CO_CURSO', 'YEAR'])
    g = h.groupby(['CO_IES', 'CO_CURSO'])
    h['ANTES'] = g.MAT.shift(1)
    h['DEPOIS'] = g.MAT.shift(-1)
    h['ANO_ANTES'] = g.YEAR.shift(1)
    h['ANO_DEPOIS'] = g.YEAR.shift(-1)
    adjacent = h.YEAR.sub(h.ANO_ANTES).eq(1)
    add(h, adjacent & h.MAT.eq(0) & h.ANTES.gt(0), 'matriculas_caem_a_zero',
        lambda i, r: f"{int(r.ANO_ANTES)}: {r.ANTES}; {r.YEAR}: 0; ING={r.QT_ING}; DESV={r.QT_SIT_DESVINCULADO}",
        'encerramento, interrupcao ou declaracao; inclui ultimo ano da serie')
    add(h, adjacent & h.ANO_DEPOIS.sub(h.YEAR).eq(1) & h.MAT.eq(0) & h.ANTES.ge(50) & h.DEPOIS.ge(50),
        'zero_entre_anos_com_50_ou_mais', lambda i, r: f"MAT: {r.ANTES} -> 0 -> {r.DEPOIS}", 'possivel lacuna anual')
    ratio = h.MAT.div(h.ANTES.replace(0, float('nan')))
    add(h, adjacent & h.MAT.sub(h.ANTES).abs().ge(500) & (ratio.ge(5) | ratio.le(0.2)),
        'salto_matriculas_5x_500', lambda i, r: f"{int(r.ANO_ANTES)}: {r.ANTES}; {r.YEAR}: {r.MAT}",
        'mudanca real ou ruptura de declaracao/modelo; exige contexto')

    municipal = e[e.IN_USAR_MAPA_MUNICIPAL.str.lower().eq('true')].copy()
    municipal['MAT'] = pd.to_numeric(municipal.QT_MAT, errors='coerce')
    vistoria_temporal(municipal, p, add)
    mk = KEY + ['CO_MUNICIPIO']
    counts.append({'REGRA': 'linhas_municipais_mesma_chave_e_municipio', 'UNIDADE': 'linha',
                   'QUANTIDADE': int(municipal.duplicated(mk, keep=False).sum())})
    muni = municipal.groupby(mk, dropna=False).agg(MAT=('MAT', lambda x: x.sum(min_count=1)),
        AUSENTES=('MAT', lambda x: x.isna().sum())).reset_index()
    geo = muni.groupby(KEY).agg(MUNICIPIOS=('CO_MUNICIPIO', 'nunique'),
        ZERADOS=('MAT', lambda x: x.eq(0).sum()), AUSENTES=('AUSENTES', 'sum'),
        TOTAL=('MAT', lambda x: x.sum(min_count=1)), MAIOR=('MAT', 'max')).reset_index()
    geo = geo.merge(p[KEY + ['NO_IES', 'NO_CURSO', 'TP_MODALIDADE_ENSINO']], on=KEY, validate='one_to_one')
    geo['FRAC_MAIOR'] = geo.MAIOR / geo.TOTAL.replace(0, float('nan'))
    ead = geo.TP_MODALIDADE_ENSINO.eq('2')
    add(geo, ead & geo.MUNICIPIOS.ge(2) & geo.AUSENTES.eq(0) & geo.ZERADOS.eq(geo.MUNICIPIOS),
        'ead_todos_municipios_zero', lambda i, r: f"{r.MUNICIPIOS} municipios; todos com MAT=0",
        'lista territorial sem matriculas; conferir atividade e situacoes')
    add(geo, ead & geo.MUNICIPIOS.ge(5) & geo.TOTAL.gt(0) & geo.ZERADOS.ge(1)
        & (geo.ZERADOS.div(geo.MUNICIPIOS).ge(.5) | geo.ZERADOS.ge(50)),
        'ead_muitos_zeros_sem_piso_matriculas',
        lambda i, r: f"{r.ZERADOS}/{r.MUNICIPIOS} municipios zerados; MAT total={r.TOTAL}; maior={r.MAIOR}; ausentes={r.AUSENTES}",
        'oferta territorial pode nao representar atividade; limite 50% ou 50 municipios')
    add(geo, geo.TP_MODALIDADE_ENSINO.eq('2') & geo.MUNICIPIOS.ge(5) & geo.TOTAL.ge(100)
        & (geo.FRAC_MAIOR.ge(.9) | geo.ZERADOS.div(geo.MUNICIPIOS).ge(.6)),
        'ead_concentracao_100_mais', lambda i, r: f"{r.MUNICIPIOS} municipios; {r.ZERADOS} zerados; {r.AUSENTES} valores ausentes; total {r.TOTAL}; maior {r.MAIOR}",
        'distribuicao municipal nao confirmada')
    add(e, e.IN_USAR_MAPA_MUNICIPAL.str.lower().eq('true') & e.CO_MUNICIPIO.str[:2].ne(e.CO_UF),
        'prefixo_municipio_diverge_uf', lambda i, r: f"municipio={r.CO_MUNICIPIO}; UF={r.CO_UF}", 'localizacao')

    names = read(OUT / '01_nome_curso_x_rotulo_divergente.csv')
    nk = names[['CO_IES', 'CO_CURSO', 'NO_CURSO', 'NO_ROTULO_AREA']].drop_duplicates()
    suspects = p.merge(nk, on=list(nk.columns), how='inner', validate='many_to_one')
    add(suspects, pd.Series(True, index=suspects.index), 'nome_rotulo_triagem_anterior',
        lambda i, r: f"nome={r.NO_CURSO}; rotulo={r.CO_ROTULO_AREA} {r.NO_ROTULO_AREA}",
        'classificacao por tipo de curso; nome sozinho nao determina rotulo correto')

    result = pd.DataFrame(flags).sort_values(['REGRA'] + KEY)
    result.to_csv(OUT / '13_vistoria_casos.csv', sep=';', index=False, encoding='utf-8-sig')
    pd.DataFrame(counts).to_csv(OUT / '14_vistoria_cobertura.csv', sep=';', index=False, encoding='utf-8-sig')

    # A selecao e deterministica e inclui casos solicitados e exemplos por regra.
    selected = result.sort_values('NU_ANO_CENSO', ascending=False).groupby('REGRA').head(2)[KEY]
    explicit = pd.DataFrame([
        ['2024', '17854', '1454503'], ['2023', '17854', '1454503'],
        ['2024', '4', '122634'], ['2024', '590', '1110857'],
        ['2023', '1472', '1266797'], ['2024', '1472', '1266797'],
        ['2024', '1472', '1572897'], ['2024', '1472', '1617841'],
        ['2024', '1472', '1551528'],
        ['2021', '1472', '1516785'], ['2022', '1472', '1516785'],
        ['2023', '1472', '1516785'], ['2024', '1472', '1516785'],
    ], columns=KEY)
    gaps = result[result.REGRA.eq('zero_entre_anos_com_50_ou_mais')][KEY]
    neighbors = [gaps.assign(NU_ANO_CENSO=(gaps.NU_ANO_CENSO.astype(int) + offset).astype(str))
                 for offset in [-1, 0, 1]]
    selected = pd.concat([selected, explicit, *neighbors]).drop_duplicates()
    transitions = result[result.REGRA.eq('mudanca_distribuicao_municipal')].sort_values(
        'NU_ANO_CENSO', ascending=False).head(3)[KEY]
    selected = pd.concat([selected, transitions,
        transitions.assign(NU_ANO_CENSO=(transitions.NU_ANO_CENSO.astype(int)-1).astype(str))]).drop_duplicates()
    evidence = []
    for year, keys in selected.groupby('NU_ANO_CENSO'):
        files = list((ROOT / 'data/raw' / year / 'dados').glob('*CADASTRO_CURSOS*'))
        if not files:
            for _, key in keys.iterrows():
                evidence.append({**key.to_dict(), 'STATUS': 'nao conferido; modelo antigo requer adaptador'})
            continue
        file = files[0]
        pairs = set(zip(keys.CO_IES, keys.CO_CURSO))
        wanted = KEY + ['NO_CURSO', 'CO_CINE_AREA_GERAL', 'CO_CINE_ROTULO', 'NO_CINE_ROTULO', 'CO_MUNICIPIO', 'TP_DIMENSAO'] + MET
        parts = []
        for chunk in pd.read_csv(file, sep=';', encoding='latin1', dtype=str,
                                 usecols=lambda c: c in wanted, chunksize=50000):
            parts.append(chunk.loc[[pair in pairs for pair in zip(chunk.CO_IES, chunk.CO_CURSO)]])
        raw = pd.concat(parts)
        for _, key in keys.iterrows():
            a = raw[(raw.CO_IES == key.CO_IES) & (raw.CO_CURSO == key.CO_CURSO)]
            b = e[(e.NU_ANO_CENSO == year) & (e.CO_IES == key.CO_IES) & (e.CO_CURSO == key.CO_CURSO)]
            pp = p[(p.NU_ANO_CENSO == year) & (p.CO_IES == key.CO_IES) & (p.CO_CURSO == key.CO_CURSO)]
            ak = ['CO_MUNICIPIO', 'TP_DIMENSAO']
            fields = [c for c in ['QT_MAT', 'QT_ING', 'QT_CONC'] if c in a.columns]
            def vector(df, compare_fields):
                d = df[ak + compare_fields].copy().fillna('')
                for c in compare_fields:
                    d[c] = pd.to_numeric(d[c], errors='coerce').astype(float)
                return sorted(d.to_csv(index=False, header=False).splitlines())
            same = len(a) > 0 and vector(a, fields) == vector(b, fields)
            situations = [c for c in MET if c.startswith('QT_SIT_')]
            complete = all(c in a.columns for c in situations)
            situations_equal = complete and len(a) > 0 and vector(a, situations) == vector(b, situations)
            evidence.append({**key.to_dict(), 'ARQUIVO_FONTE': str(file.relative_to(ROOT)),
                'LINHAS_BRUTAS': len(a), 'LINHAS_EXPANDIDA': len(b),
                'STATUS': 'MAT ING CONC por municipio/dimensao iguais a fonte' if same else 'divergencia ou registro ausente; investigar',
                'STATUS_SITUACOES': ('iguais a fonte por municipio/dimensao' if situations_equal else
                    'divergencia; investigar' if complete else 'campos indisponiveis na fonte selecionada'),
                'NOME_FONTE': ' | '.join(a.NO_CURSO.dropna().unique()),
                'AREA_GERAL_FONTE': ' | '.join(a.get('CO_CINE_AREA_GERAL', pd.Series(dtype=str)).dropna().unique()),
                'ROTULO_FONTE': ' | '.join(a.get('CO_CINE_ROTULO', pd.Series(dtype=str)).dropna().unique()),
                'ROTULO_OFICIAL': ' | '.join(pp.CO_ROTULO_AREA.dropna().unique()),
                'MAT_BRUTA_SOMA': pd.to_numeric(a.QT_MAT, errors='coerce').sum(min_count=1)})
        print(f'Fonte conferida: {year}', flush=True)
    pd.DataFrame(evidence).to_csv(OUT / '15_conferencia_fonte.csv', sep=';', index=False, encoding='utf-8-sig')
    print(json.dumps(counts, indent=2))
    print(f'{len(result)} ocorrencias; {len(result[KEY].drop_duplicates())} chaves; {len(evidence)} conferencias')


if __name__ == '__main__':
    main()
