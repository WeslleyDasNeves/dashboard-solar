import pandas as pd


df_hidro_bruto = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Hidreletrica')

colunas_final = ['Data - Base diária', 'Hidreletrica', 'Ativa G (kWh)']
df_hidro = df_hidro_bruto[colunas_final].copy()

df_hidro = df_hidro.rename(columns={
    'Data - Base diária': 'Data',
    'Hidreletrica': 'Usina',
    'Ativa G (kWh)': 'Geracao_Real'
})

df_hidro['Data_dt'] = pd.to_datetime(df_hidro['Data'], format='mixed', dayfirst=True)
df_hidro['Data'] = df_hidro['Data_dt'].dt.strftime('%d/%m/%Y')
df_hidro['PVsyst'] = 0.0


df_hidro_limpo = df_hidro[['Data', 'Usina', 'Geracao_Real', 'PVsyst']]


df_real_bruto = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Tabela1', header=1)

colunas_usinas = [
    'Colatina 1', 'Colatina 2', 'Colatina 3', 'Colatina 4', 'Colatina 5',
    'Pancas 1', 'Pancas 2', 'Pancas 3', 'SM F47'
]


df_desacoplado = df_real_bruto.melt(id_vars=['Data'], value_vars=colunas_usinas, var_name='Usina', value_name='Geracao_Real')
df_desacoplado = df_desacoplado.dropna(subset=['Geracao_Real'])
df_desacoplado['Usina'] = df_desacoplado['Usina'] + ' (Individual)'


regras_agrupamento = {
    'Colatina 1': 'COLATINA 1', 'Colatina 2': 'COLATINA 1', 'Colatina 3': 'COLATINA 1',
    'Colatina 4': 'COLATINA 2', 'Colatina 5': 'COLATINA 2',
    'Pancas 1': 'PANCAS', 'Pancas 2': 'PANCAS', 'Pancas 3': 'PANCAS',
    'SM F47': 'SM F47'
}
df_agrupado = df_desacoplado.copy()
df_agrupado['Usina'] = df_agrupado['Usina'].str.replace(' \(Individual\)', '', regex=True)
df_agrupado['Usina'] = df_agrupado['Usina'].replace(regras_agrupamento).str.strip().str.upper()
df_agrupado = df_agrupado.groupby(['Data', 'Usina'], as_index=False)['Geracao_Real'].sum()


df_real_solar = pd.concat([df_agrupado, df_desacoplado], ignore_index=True)
df_real_solar['Data_dt'] = pd.to_datetime(df_real_solar['Data'], format='mixed', dayfirst=True)
df_real_solar['Mes'] = df_real_solar['Data_dt'].dt.month


df_pv = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Pvsyst')
df_pv.columns = ['Data', 'Usina', 'pvsyst']
df_pv['Usina'] = df_pv['Usina'].str.strip().str.upper()

novas_linhas_pv = []
for index, row in df_pv.iterrows():
    usina = row['Usina']
    val_mensal = row['pvsyst']
    data = row['Data']
    
    if usina == 'COLATINA 1':
        novas_linhas_pv.extend([{'Data': data, 'Usina': f'Colatina {i} (Individual)', 'pvsyst': val_mensal / 3} for i in range(1, 4)])
    elif usina == 'COLATINA 2':
        novas_linhas_pv.extend([{'Data': data, 'Usina': f'Colatina {i} (Individual)', 'pvsyst': val_mensal / 2} for i in range(4, 6)])
    elif usina == 'PANCAS':
        novas_linhas_pv.extend([{'Data': data, 'Usina': f'Pancas {i} (Individual)', 'pvsyst': val_mensal / 3} for i in range(1, 4)])
    elif usina == 'SM F47':
        novas_linhas_pv.append({'Data': data, 'Usina': 'SM F47 (Individual)', 'pvsyst': val_mensal})

df_pv_completo = pd.concat([df_pv, pd.DataFrame(novas_linhas_pv)], ignore_index=True)
df_pv_completo['Data_dt'] = pd.to_datetime(df_pv_completo['Data'], format='mixed', dayfirst=True)
df_pv_completo['Mes'] = df_pv_completo['Data_dt'].dt.month
df_pv_completo['dias_no_mes'] = df_pv_completo['Data_dt'].dt.daysinmonth


df_final_solar = pd.merge(df_real_solar, df_pv_completo[['Usina', 'Mes', 'pvsyst', 'dias_no_mes']], on=['Usina', 'Mes'], how='left')
df_final_solar['PVsyst'] = (df_final_solar['pvsyst'] / df_final_solar['dias_no_mes']).round(2)
df_final_solar['Data'] = df_final_solar['Data_dt'].dt.strftime('%d/%m/%Y')
df_solar_limpo = df_final_solar[['Data', 'Usina', 'Geracao_Real', 'PVsyst']].fillna(0)



df_dashboard = pd.concat([df_solar_limpo, df_hidro_limpo], ignore_index=True)


df_dashboard.to_csv('ReportGeracao.csv', index=False, sep=';', decimal=',')

print("Relatório gerado")