import pandas as pd

# 1. Lê a aba principal de geração
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

# Agrupa e soma
df_agrupado = df_agrupado.groupby(['Data', 'Usina'], as_index=False)['Geracao_Real'].sum()


df_real = pd.concat([df_agrupado, df_desacoplado], ignore_index=True)
df_real['Data_dt'] = pd.to_datetime(df_real['Data'], format='mixed', dayfirst=True)
df_real['Mes'] = df_real['Data_dt'].dt.month



df_pv = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Pvsyst')
df_pv.columns = ['Data', 'Usina', 'pvsyst']
df_pv['Usina'] = df_pv['Usina'].str.strip().str.upper()

novas_linhas_pv = []
for index, row in df_pv.iterrows():
    usina = row['Usina']
    val_mensal = row['pvsyst']
    data = row['Data']
    
    if usina == 'COLATINA 1': # Divide por 3
        novas_linhas_pv.append({'Data': data, 'Usina': 'Colatina 1 (Individual)', 'pvsyst': val_mensal / 3})
        novas_linhas_pv.append({'Data': data, 'Usina': 'Colatina 2 (Individual)', 'pvsyst': val_mensal / 3})
        novas_linhas_pv.append({'Data': data, 'Usina': 'Colatina 3 (Individual)', 'pvsyst': val_mensal / 3})
        
    elif usina == 'COLATINA 2': # Divide por 2
        novas_linhas_pv.append({'Data': data, 'Usina': 'Colatina 4 (Individual)', 'pvsyst': val_mensal / 2})
        novas_linhas_pv.append({'Data': data, 'Usina': 'Colatina 5 (Individual)', 'pvsyst': val_mensal / 2})
        
    elif usina == 'PANCAS': # Divide por 3
        novas_linhas_pv.append({'Data': data, 'Usina': 'Pancas 1 (Individual)', 'pvsyst': val_mensal / 3})
        novas_linhas_pv.append({'Data': data, 'Usina': 'Pancas 2 (Individual)', 'pvsyst': val_mensal / 3})
        novas_linhas_pv.append({'Data': data, 'Usina': 'Pancas 3 (Individual)', 'pvsyst': val_mensal / 3})
        
    elif usina == 'SM F47': # Fica igual (Divide por 1)
        novas_linhas_pv.append({'Data': data, 'Usina': 'SM F47 (Individual)', 'pvsyst': val_mensal})


df_pv_individuais = pd.DataFrame(novas_linhas_pv)
df_pv_completo = pd.concat([df_pv, df_pv_individuais], ignore_index=True)

df_pv_completo['Data_dt'] = pd.to_datetime(df_pv_completo['Data'], format='mixed', dayfirst=True)
df_pv_completo['Mes'] = df_pv_completo['Data_dt'].dt.month
df_pv_completo['dias_no_mes'] = df_pv_completo['Data_dt'].dt.daysinmonth


df_final = pd.merge(df_real, df_pv_completo[['Usina', 'Mes', 'pvsyst', 'dias_no_mes']], 
                    on=['Usina', 'Mes'], how='left')

# Transforma a meta mensal em meta diária
df_final['PVsyst'] = (df_final['pvsyst'] / df_final['dias_no_mes']).round(2)

df_final['Data'] = df_final['Data_dt'].dt.strftime('%d/%m/%Y')
df_final_limpo = df_final[['Data', 'Usina', 'Geracao_Real', 'PVsyst']].fillna(0)

# Salva o arquivo CSV
df_final_limpo.to_csv('teste.csv', index=False, sep=';', decimal=',')

print("Sucesso: Metas individuais calculadas e adicionadas ao CSV!")