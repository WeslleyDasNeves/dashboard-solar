import pandas as pd


df = pd.read_excel('ResumoSolar_.xlsx', sheet_name='Hidreletrica', header=1)

print(df.columns)

colunas_final = ['Hidrelétrica', 'Ativa G (kWh)' , 'Data - Base diária']

df_filtrado = df[colunas_final]

print (df_filtrado)

df_filtrado = df_filtrado.rename(columns={
    'Hidrelétrica' : 'Usina',
    'Ativa G (kWh)' : 'Geracao_Real',
    'Data - Base diária' : 'data'
    
})


