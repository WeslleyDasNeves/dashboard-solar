import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime, timedelta

# ==========================================
# CONFIGURAÇÕES DE INTERNET E LOGIN
# ==========================================
url_login = "https://hemera.elfsm.com.br/hemera/login.do"
url_report_do = "https://hemera.elfsm.com.br/hemera/sgc/relatorio/reportreading.do"

headers = {
    "origin" : "https://hemera.elfsm.com.br",
    "accept" : "*/*" ,
    "User-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "x-requested-with" : "XMLHttpRequest",
    "content-type" : "application/x-www-form-urlencoded"
}

payload_login = {
    "modele" : "login",
    "action" : "login",
    "username" :"dferreira",
    "password" : "dferreira@1",
    "cmbDomain" : "1"
}

# ==========================================
# CONSTANTES MATEMÁTICAS POR GRUPO
# ==========================================
FATOR_COLATINA_123 = (13800/115) * (30/5) * (3/10) * (1/1000)
FATOR_PANCAS_123 = (13800/115) * (40/5) * (3/10) * (1/1000)
FATOR_COLATINA_45 = (13800/115) * (40/5) * (6/10) * (1/1000)
FATOR_F47 = (8050/115) * (40/5) * (3/10) * (1/1000)

# ==========================================
# LISTA DE USINAS
# ==========================================
lista_usinas = [
    { "nome": "COLATINA 1", "idMeter": "7298", "fator": FATOR_COLATINA_123 },
    { "nome": "COLATINA 2", "idMeter": "7300", "fator": FATOR_COLATINA_123 },
    { "nome": "COLATINA 3", "idMeter": "7302", "fator": FATOR_COLATINA_123 },
    { "nome": "PANCAS 1", "idMeter": "7152", "fator": FATOR_PANCAS_123 },
    { "nome": "PANCAS 2", "idMeter": "7232", "fator": FATOR_PANCAS_123 },
    { "nome": "PANCAS 3", "idMeter": "7156", "fator": FATOR_PANCAS_123 },
    { "nome": "COLATINA 4", "idMeter": "7498", "fator": FATOR_COLATINA_45 },
    { "nome": "COLATINA 5", "idMeter": "7496", "fator": FATOR_COLATINA_45 },
    { "nome": "F47", "idMeter": "7858", "fator": FATOR_F47 }
]

sessao = requests.Session()

def realizar_login():
    print(f"[{time.strftime('%H:%M:%S')}] Tentando realizar login...")
    try: 
        resposta_login = sessao.post(url_login, data=payload_login, headers=headers)
        if "Senha incorreta" in resposta_login.text or "Não autorizado" in resposta_login.text:
            print("❌ Falha no login! Verifique usuário/senha.")
            return False
        print("✅ Login realizado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

# Puxa sempre 2 meses para não quebrar a diferença do dia 01
QTD_MESES_HISTORICO = 2 

def realizar_coleta_historico():
    print(f"\nIniciando coleta de dados acumulados (Últimos {QTD_MESES_HISTORICO} meses)...")
    
    hoje_data = datetime.now().date()
    
    meses_para_consultar = []
    for i in range(QTD_MESES_HISTORICO):
        mes_calc = hoje_data.month - i
        ano_calc = hoje_data.year
        if mes_calc <= 0:
            mes_calc += 12
            ano_calc -= 1
        
        mes_hemera = str(mes_calc - 1) 
        ano_hemera = str(ano_calc)
        meses_para_consultar.append((mes_hemera, ano_hemera))
        
    meses_para_consultar.reverse()

    dados_historicos = {}

    for usina in lista_usinas:
        nome_usina = usina["nome"]
        print(f"\n-> Processando {nome_usina}...")
        
        leituras_brutas = [] 

        for mes_hemera, ano_hemera in meses_para_consultar:
            print(f"   Buscando mês {int(mes_hemera)+1}/{ano_hemera}...")
            
            payload_lista = {
                "selecteds" : "2",
                "idMeter" : usina["idMeter"],
                "month" : mes_hemera,
                "year" : ano_hemera,
                "check_consolidated" : "false",
                "isPreencheCombo" : "true",
                "selectedChannels" : "4,5,6"
            }
            
            resposta_lista = sessao.post(url_report_do, data=payload_lista, headers=headers)
            padrao = r"valueF:'(.*?)',textF:'(.*?)'"
            resultados = re.findall(padrao, resposta_lista.text)
            
            if not resultados:
                continue

            for valueF, data_str in resultados:
                
                # ==============================================================
                # BLINDAGEM DE HORÁRIO: Só pega o consolidado das 22h
                # ==============================================================
                usinas_filtro_22h = ["PANCAS 1", "PANCAS 2", "PANCAS 3", "COLATINA 4", "COLATINA 5", "F47"]
                if nome_usina in usinas_filtro_22h:
                    if " 22:" not in data_str:
                        continue 

                busca_data = re.search(r"(\d{2}/\d{2}/\d{4})", data_str)
                
                if busca_data:
                    data_limpa = busca_data.group(1)
                    data_obj = datetime.strptime(data_limpa, '%d/%m/%Y').date()
                    
                    if data_obj >= hoje_data:
                        continue 
                else:
                    continue 

                payload_dia = {
                    "idMeter" : usina["idMeter"],
                    "cmbMonth" : mes_hemera,
                    "cmbYear" : ano_hemera,
                    "idMeterRead" : valueF,
                    "selecteds" : "2",
                    "selectedChannels" : "4,5,6",
                    "comboModoLeitura" : "1",
                    "comboQuantityMode" : "0",
                    "comboOrderParameter" : "1"
                }
                
                resposta_dia = sessao.post(url_report_do, data=payload_dia, headers=headers)
                soup = BeautifulSoup(resposta_dia.text, 'html.parser')
                total_dr = soup.find_all('td', class_='relatCol1_left')
                
                # ==============================================================
                # AJUSTE DA POSIÇÃO 51
                # ==============================================================
                if len(total_dr) > 51:
                    valor_texto = total_dr[51].get_text(strip=True)
                    try:
                        valor_acumulado = float(valor_texto.replace('.', '').replace(',', '.'))
                        leituras_brutas.append({
                            "data": data_limpa,
                            "acumulado": valor_acumulado
                        })
                    except ValueError:
                        pass
                
                time.sleep(0.5)

        # ==============================================================
        # BLINDAGEM 4: FILTRO ANTI-DUPLICIDADE
        # O Hemera pode retornar o mesmo dia duas vezes. Vamos guardar
        # apenas o maior valor acumulado (última leitura) de cada dia.
        # ==============================================================
        leituras_unicas = {}
        for leitura in leituras_brutas:
            d_str = leitura['data']
            val = leitura['acumulado']
            if d_str not in leituras_unicas or val > leituras_unicas[d_str]:
                leituras_unicas[d_str] = val
                
        # Reconstrói a lista limpa, livre de dias repetidos
        leituras_brutas = [{'data': k, 'acumulado': v} for k, v in leituras_unicas.items()]

        # Agora sim, ordena a lista cronologicamente
        leituras_brutas.sort(key=lambda x: datetime.strptime(x['data'], '%d/%m/%Y'))
        
        geracao_diaria = {}
        
        if len(leituras_brutas) > 0:
            ultima_leitura_valida = leituras_brutas[0]

            for i in range(1, len(leituras_brutas)):
                leitura_atual = leituras_brutas[i]
                
                data_ant_obj = datetime.strptime(ultima_leitura_valida['data'], '%d/%m/%Y').date()
                data_atual_obj = datetime.strptime(leitura_atual['data'], '%d/%m/%Y').date()
                
                dia_anterior = ultima_leitura_valida['acumulado']
                dia_atual = leitura_atual['acumulado']
                
                # Dias passados sempre será 1 ou mais, a matemática não trava!
                dias_passados = (data_atual_obj - data_ant_obj).days

                if dia_atual >= dia_anterior and dias_passados > 0:
                    diferenca_crua = dia_atual - dia_anterior
                    geracao_total_periodo = diferenca_crua * usina["fator"]
                    
                    # Interpolação Linear (Rateio de Buracos Reais)
                    media_diaria = geracao_total_periodo / dias_passados
                    
                    for d in range(1, dias_passados + 1):
                        dia_intermediario = data_ant_obj + timedelta(days=d)
                        data_str_formatada = dia_intermediario.strftime('%d/%m/%Y')
                        geracao_diaria[data_str_formatada] = round(media_diaria, 2)
                        
                    ultima_leitura_valida = leitura_atual 
                        
                elif dia_atual < dia_anterior:
                    # Se o medidor resetar fisicamente, pega a nova leitura como âncora
                    ultima_leitura_valida = leitura_atual
                    
        dados_historicos[nome_usina] = geracao_diaria
        print(f"   [+] Concluído: {len(geracao_diaria)} dias processados perfeitamente.")

    with open('historico_geracao.js', 'w', encoding='utf-8') as f:
        f.write(f"var dadosHistorico = {json.dumps(dados_historicos, ensure_ascii=False, indent=4)};")
        
    print("\n✔ Coleta Histórica concluída! Arquivo 'historico_geracao.js' gerado.")

# ==========================================
# FLUXO DE EXECUÇÃO
# ==========================================
if realizar_login():
    realizar_coleta_historico()