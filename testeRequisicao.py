import re 
import json
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import ast
from bs4 import BeautifulSoup

url_report_do = "https://hemera.elfsm.com.br/hemera/sgc/relatorio/reportreading.do"
url_login = "https://hemera.elfsm.com.br/hemera/login.do"

headers = {
    "origin" : "https://hemera.elfsm.com.br",
    "accept" : "*/*" ,
    "User-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-requested-with" : "XMLHttpRequest",
    "content-type" : "application/x-www-form-urlencoded" ,
    "referer" : "https://hemera.elfsm.com.br/hemera/sgc/relatorio/report_phasorial.jsp?i=0&id_customer=5424&id_measurement_point=5585&id_meter=7300"
}

payload = {
    "selecteds" : "2",
    "idMeter" : "7300",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
}

payload_login = {
    "modele" : "login",
    "action" : "login",
    "username" :"dferreira",
    "password" : "dferreira@1",
    "cmbDomain" : "1"
}


lista_usinas = [
     {#COLATINA 1
    "selecteds" : "2",
    "idMeter" : "7298",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },

    {#COLATINA 2
    "selecteds" : "2",
    "idMeter" : "7300",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },
    {#COLATINA 3
    "selecteds" : "2",
    "idMeter" : "7302",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },
    {#PANCAS 1
    "selecteds" : "2",
    "idMeter" : "7152",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },
    {#PANCAS 2
    "selecteds" : "2",
    "idMeter" : "7232",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },

    {#PANCAS 3
    "selecteds" : "2",
    "idMeter" : "7156",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },

    {#COLATINA 4
    "selecteds" : "2",
    "idMeter" : "7498",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },

    {#COLATINA 4
    "selecteds" : "2",
    "idMeter" : "7496",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },

    {#F47
    "selecteds" : "2",
    "idMeter" : "7858",
    "month" : "5",
    "year" : "2026",
    "check_consolidated" : "false",
    "isPreencheCombo" : "true",
    "selectedChannels" : "4,5,6"
    },
]
    
lista_valueF = []

lista_valores = []
dif_listaValores = []

sessao = requests.Session()

def login():
    try: 
        resposta_login = sessao.post(url_login,data=payload_login,headers=headers)
    
        print("Login realizado com sucesso")

    except:
    
        print("Erro no login")


login()

def realizar_coleta():
    resposta = sessao.post(
        url_report_do,
        data=payload,
        headers=headers
    )

    texto = resposta.text

    txt = texto.strip("()")
    
    texto_limpo = txt.strip("[]")
    print(texto_limpo)
    


    padrao = r"valueF:'(.*?)',textF:'(.*?)'"
    resultados = re.findall(padrao,texto)

    for valueF, periodos in resultados:
        # print(f"valueF : {valueF} em {periodos}")
        # print("-"*30)
        lista_valueF.append(valueF)
        
        y = (valueF)

        payload_usinaX = {#COLATINA 1
            "selecteds" : "2",
            "idMeter" : "7858",
            "idCustomer" : "5423",
            "cmbMonth" : "5",
            "cmbYear" : "2026",
            "idMeterRead" : y,
            "selecteds" : "2",
            "selectedChannels" : "4,5,6"
            }
        
    
        x = sessao.post(url_report_do,data = payload_usinaX, headers=headers)
        
        
        soup = BeautifulSoup(x.text, 'html.parser')
        
        total_dr = soup.find_all('td', class_= 'relatCol1_left')
        
        valor_final = total_dr[51].get_text(strip =True)  #LINHA 41 PEGA ESSES VALORES, ABAIXO : <td class="relatCol1_left" style="min-width: 100px; width: 100px;" width="100px"> 13.311.331,00 </td> print(i)

        
        lista_valores.append(valor_final)



        print(total_dr[51])


        # for i in range(0,len(total_dr)):
        #     print(f"------------{i}-----------")
        #     print(total_dr[i])

        for i in range(0, len(lista_valores)-1):

            if lista_valores[i+1] is not None and lista_valores[i+1] != 0:

                atual = float(lista_valores[i].replace('.', '').replace(',', '.'))
        
                proximo = float(lista_valores[i+1].replace('.', '').replace(',', '.'))
                

                if(proximo != 0 and proximo is not None):
                    valor = atual - proximo
                    # print(f"{atual}")
                    dif_listaValores.append(valor)

#CONSTANTES : COLATINA 1,2 e 3 : voce multiplica cada diferença de valores por : (13800/115	) * ( 30/5 ) * (3/10) * 1/1000
#PANCAS 1,2,3 : voce multiplica cada diferença de valores por :  13800/115 * 40/5  *  3/10	* 1/1000
#COLATINA 4,5 : voce multiplica cada diferença de valores por : 13800/115	* 40/5	 * 6/10 * 1/1000
#F47 ? : voce multiplica cada diferença de valores por : 8050/115	* 40/5	 * 3/10 * 1/1000
 

realizar_coleta()