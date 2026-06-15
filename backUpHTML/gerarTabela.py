import pandas as pd


df_real_bruto = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Tabela1', header=1)

colunas_usinas = [
    'Colatina 1', 'Colatina 2', 'Colatina 3', 'Colatina 4', 'Colatina 5',
    'Pancas 1', 'Pancas 2', 'Pancas 3', 'SM F47'
]

df_real_longo = df_real_bruto.melt(id_vars=['Data'], value_vars=colunas_usinas, var_name='Usina', value_name='Geracao_Real')
df_real_longo = df_real_longo.dropna(subset=['Geracao_Real'])

regras_agrupamento = {
    'Colatina 1': 'COLATINA 1', 'Colatina 2': 'COLATINA 1', 'Colatina 3': 'COLATINA 1',
    'Colatina 4': 'COLATINA 2', 'Colatina 5': 'COLATINA 2',
    'Pancas 1': 'PANCAS', 'Pancas 2': 'PANCAS', 'Pancas 3': 'PANCAS',
    'SM F47': 'SM F47'
}


df_real_longo['Usina'] = df_real_longo['Usina'].replace(regras_agrupamento).str.strip().str.upper()
df_real = df_real_longo.groupby(['Data', 'Usina'], as_index=False)['Geracao_Real'].sum()

df_real['Data_dt'] = pd.to_datetime(df_real['Data'], format='mixed', dayfirst=True)
df_real['Mes'] = df_real['Data_dt'].dt.month


df_pv = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Pvsyst')

df_pv.columns = ['Data', 'Usina', 'pvsyst']
df_pv['Usina'] = df_pv['Usina'].str.strip().str.upper()


df_pv['Data_dt'] = pd.to_datetime(df_pv['Data'], format='mixed', dayfirst=True)
df_pv['Mes'] = df_pv['Data_dt'].dt.month
df_pv['dias_no_mes'] = df_pv['Data_dt'].dt.daysinmonth


df_final = pd.merge(df_real, df_pv[['Usina', 'Mes', 'pvsyst', 'dias_no_mes']], 
                    on=['Usina', 'Mes'], how='left')


df_final['PVsyst'] = (df_final['pvsyst'] / df_final['dias_no_mes']).round(2)


df_final['Data'] = df_final['Data_dt'].dt.strftime('%d/%m/%Y')
df_final_limpo = df_final[['Data', 'Usina', 'Geracao_Real', 'PVsyst']].fillna(0)

df_final_limpo.to_csv('dados_completos_dashboard.csv', index=False, sep=';', decimal=',')

print("Sucesso")


