import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta


#DADOS DE INTERNET DO SITE:
url = "https://hemera.elfsm.com.br/hemera/sgc/relatorio/phasorialreport.do"
url_login = "https://hemera.elfsm.com.br/hemera/login.do"

headers = {
    "origin" : "https://hemera.elfsm.com.br",
    "accept" : "*/*" ,
    "User-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-requested-with" : "XMLHttpRequest",
    "content-type" : "application/x-www-form-urlencoded" ,
    "referer" : "https://hemera.elfsm.com.br/hemera/sgc/relatorio/report_phasorial.jsp?i=0&id_customer=5424&id_measurement_point=5585&id_meter=7300"
}

payload_login = {
    "modele" : "login",
    "action" : "login",
    "username" :"dferreira",
    "password" : "dferreira@1",
    "cmbDomain" : "1"
}


lista_usinas = [
    { # Colatina 1
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7298", "idCustomerHidden": "5423", "idMeasPointHidden": "5583", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR I", "meterSerialHidden" : "07037173"
    },
    { # Colatina 2
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7300", "idCustomerHidden": "5424", "idMeasPointHidden": "5585", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR II", "meterSerialHidden" : "01304884"
    },
    { # Colatina 3
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7302", "idCustomerHidden": "5425", "idMeasPointHidden": "5586", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR III", "meterSerialHidden" : "01304885"
    },
    { # Pancas 1
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7152", "idCustomerHidden": "5683", "idMeasPointHidden": "5883", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR IV", "meterSerialHidden" : "07056330"
    },
    { # Pancas 2
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7232", "idCustomerHidden": "5684", "idMeasPointHidden": "5884", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR V", "meterSerialHidden" : "07056270"
    },
    { # Pancas 3
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7156", "idCustomerHidden": "5685", "idMeasPointHidden": "5885", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR VI", "meterSerialHidden" : "07056329"
    },
    { # Colatina 4
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "0,2,4",
        "idMeterHidden": "7498", "idCustomerHidden": "5647", "idMeasPointHidden": "5843", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR VII", "meterSerialHidden" : "050083131"
    },
    { # Colatina 5
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "0,2,4",
        "idMeterHidden": "7496", "idCustomerHidden": "5648", "idMeasPointHidden": "5844", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR VIII", "meterSerialHidden" : "050083129"
    },
    { # F47 (Solar IX)
        "typeReportPeriod": "0", "comboMonth": "5", "comboYear": "2026", "dateDiary": "10/06/26", "datePersIni": "03/06/2026 00:00", "datePersFin": "10/06/2026 23:59", "phasorFields": "4",
        "idMeterHidden": "7858", "idCustomerHidden": "6263", "idMeasPointHidden": "6503", "customerNameHidden": "CONSORCIO SANTA MARIA ENERGIA SOLAR IX", "meterSerialHidden" : "07058871"
    }
]

def converter_para_numero(texto):
    texto_limpo = texto.strip().replace('.', '').replace(',', '.')
    try:
        return float(texto_limpo)
    except ValueError:
        return 0.0

sessao = requests.Session()

def realizar_login():
    """Função que autentica no sistema e guarda os cookies na sessão."""
    print(f"[{time.strftime('%H:%M:%S')}] Tentando realizar login no Hemera...")
    try:
        resposta = sessao.post(url_login, data=payload_login, headers=headers)
        
        if "Senha incorreta" in resposta.text or "Não autorizado" in resposta.text:
            print(" Falha no login! Verifique usuário/senha.")
            return False
            
        print(" Login realizado com sucesso! Cookies salvos.")
        return True
    except Exception as e:
        print(f" Erro ao tentar logar: {e}")
        return False

# Dicionário global que guarda o histórico em memória
dados_tempo_real = {}

def executar_coleta():
    global dados_tempo_real 
    
    print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando varredura das {len(lista_usinas)} usinas...")
    
    hoje = datetime.now().date()
    ontem = hoje - timedelta(days=1)

    for idx, usina_data in enumerate(lista_usinas):
        nome_curto = usina_data.get("customerNameHidden", f"Usina {idx+1}")
        print(f" -> Consultando {nome_curto}...")

        payload = usina_data.copy()
        
        # INJEÇÕES DINÂMICAS ABSOLUTAS
        payload["channels"] = "4,5,6"
        payload["check_consolidated"] = "false"
        payload["comboModoLeitura"] = "1"
        payload["comboQuantityMode"] = "0"
        
        # Corrige meses e anos para o backend não reclamar ao virar o mês
        payload["comboMonth"] = str(hoje.month - 1)  # Se o Hemera usar base 0 para os meses (ex: Jan=0, Mai=4) - AJUSTE SE NECESSÁRIO
        payload["comboYear"] = str(hoje.year)
        
        payload["dateDiary"] = hoje.strftime("%d/%m/%y")
        payload["datePersIni"] = ontem.strftime("%d/%m/%Y 00:00")
        payload["datePersFin"] = hoje.strftime("%d/%m/%Y 23:59")
        
        try:
            r = sessao.post(url, headers=headers, data=payload)
            
            if "type='password'" in r.text or "login" in r.url:
                print(" Sessão expirada no meio da coleta! Tentando relogar...")
                if realizar_login():
                    r = sessao.post(url, headers=headers, data=payload)
                else:
                    continue 

            blocos = r.text.split("{ 'report':")

            for bloco in blocos:
                if "class='relatTable'" in bloco:
                    soup = BeautifulSoup(bloco, 'html.parser')
                    
                    if nome_curto not in dados_tempo_real:
                        dados_tempo_real[nome_curto] = {"labels": [], "valores": []}

                    linhas = soup.find_all('tr', class_='line')

                    for linha in linhas:
                        colunas = linha.find_all('td')
                        if len(colunas) >= 5:
                            texto_data_hora = colunas[0].text.strip()
                            try:
                                data_hora_obj = datetime.strptime(texto_data_hora, "%d/%m/%Y %H:%M")
                                data_registro = data_hora_obj.date()
                                
                                inicio = data_hora_obj.strftime("%H:%M")
                                
                                if(inicio >= "05:00"):

                                    if data_registro == hoje:
                                        label_grafico = data_hora_obj.strftime("%d/%m - %H:%M")

                                        fase_a = converter_para_numero(colunas[2].text)
                                        fase_b = converter_para_numero(colunas[3].text)
                                        fase_c = converter_para_numero(colunas[4].text)

                                        soma_pura = sum(f for f in (fase_a, fase_b, fase_c) if f < 0)

                                        if idx in [0, 1, 2]: 
                                            soma_intervalo = abs((120 * 6 * 1 / 1000) * soma_pura)
                                        elif idx in [3, 4, 5]: 
                                            soma_intervalo = abs((120 * 8 * 1 / 1000) * soma_pura)
                                        elif idx in [6,7]:
                                            tensao_fase_a = converter_para_numero(colunas[2].text)
                                            tensao_fase_b = converter_para_numero(colunas[3].text)
                                            tensao_fase_c = converter_para_numero(colunas[4].text)

                                            corente_a = converter_para_numero(colunas[5].text)
                                            corente_b = converter_para_numero(colunas[6].text)
                                            corente_c = converter_para_numero(colunas[7].text)

                                            potencia_a = converter_para_numero(colunas[8].text)
                                            potencia_b = converter_para_numero(colunas[9].text)
                                            potencia_c = converter_para_numero(colunas[10].text)

                                            if(potencia_a < 0.001):
                                                potencia_a = -1

                                            if(potencia_b < 0.001):
                                                potencia_b = -1

                                            if(potencia_c < 0.001):
                                                potencia_b = -1

                                            geracao_a = tensao_fase_a * corente_a * potencia_a
                                            geracao_b = tensao_fase_b * corente_b * potencia_b
                                            geracao_c = tensao_fase_c * corente_c * potencia_c
                                            
                                            #print(f' {geracao_a} , {geracao_b}, {geracao_c}')
                                            soma =  sum(f for f in (geracao_a, geracao_b, geracao_c) if f < 0)
                                            soma_intervalo = abs((120 * 8 * 1 / 1000) * soma)

                                            
                                        else: 
                                            soma_intervalo = abs((70 * 8 * 1 / 1000) * soma_pura)       

                                        if label_grafico not in dados_tempo_real[nome_curto]["labels"]:
                                            
                                            dados_tempo_real[nome_curto]["labels"].append(label_grafico)
                                            dados_tempo_real[nome_curto]["valores"].append(soma_intervalo)
                            except ValueError:
                                pass
        except Exception as e:
            print(f" Erro ao consultar {nome_curto}: {e}")
            
        time.sleep(1)

    with open('tempo_real_.js', 'w', encoding='utf-8') as f:
        f.write(f"var dadosTR = {json.dumps(dados_tempo_real, ensure_ascii=False, indent=4)};")
    
    print(f" Arquivo atualizado! (Próxima checagem em 15 min)")

# Fluxo Principal
realizar_login()

while True:
    executar_coleta()
    time.sleep(300)