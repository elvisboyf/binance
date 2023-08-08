from tradingview_ta import *
import tradingview_ta, time, json, requests
from binance.client import Client
from binance.enums import *
import psycopg2 as pg

print("me reinicie")

lBelas = {}
lOrden = {}
nextEntry = {}
def conectar():
    while True:
        try:
            print("conectando DB")
            conecxion = pg.connect(
                # host="dpg-cj4dputgkuvsl08la0s0-a.singapore-postgres.render.com", #esta es remota
                host="dpg-cj4dputgkuvsl08la0s0-a", #esta es online
                user="root",
                password = "FxoDBQeYSb82YvlJS538k883NlsbZEiW",
                database = "creativedb",
                port = "5432")
            break
        except Exception:
            print("error en conection")
    return conecxion

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        data = response.json()
        public_ip = data['ip']
        return public_ip
    except requests.RequestException as e:
        print(f"Error al obtener la IP pública: {e}")
        return None

public_ip = get_public_ip()
print(public_ip)
if public_ip:
    conn = conectar()
    cursor= conn.cursor()
    
    #verifica configuracion
    cursor.execute("SELECT * FROM public.config")
    config = cursor.fetchall()
    cursor.close()
    #quitar los 1==1 cuando vaya para el servidor
    if public_ip == config[0][2] and config[0][3] == "render":
        while True:
            if len(nextEntry) == 0:
                conn = conectar()
                cursor= conn.cursor()
                cursor.execute("SELECT ordenes FROM public.entradas WHERE id = 1")
                entradas = cursor.fetchall()
                nextEntry = json.loads(entradas[0][0])
                cursor.close()
            
                
            try:
                #verifica configuracion
                cursor= conn.cursor()
                cursor.execute("SELECT * FROM public.config")
                config = cursor.fetchall()
                
                #buscar los usuarios activo
                # cursor= conn.cursor()
                cursor.execute("SELECT * FROM public.tokens WHERE actived = 1")
                tokens = cursor.fetchall()
                cursor.close()
                
                #LISTA DE BARIABLES QUE SE DEBEN REINICIAR CADA CICLO
                analiza = ""
                
                if config[0][0] =="on" and len(tokens) != 0:
                    #AQUI INICIA EL CODIGO A EJECUTAR
                    for token in tokens:
                        inicio = time.time()
                        moneda = token[1]
                        while True:
                            try:
                                analiza = TA_Handler(
                                    symbol=moneda + ".P",
                                    screener="crypto",
                                    exchange="BINANCE",
                                    interval=Interval.INTERVAL_1_MINUTE
                                )
                                if analiza != "":
                                    # LOS DATOS DE LOS INDICADORES
                                    indicadores = analiza.get_analysis().indicators
                                    señal = analiza.get_analysis().summary
                                    ociladores = analiza.get_analysis().oscillators
                                    medias = analiza.get_analysis().moving_averages
                                    pOpen = analiza.get_analysis().indicators['open']
                                    pHigh = analiza.get_analysis().indicators['high']
                                    pLow = analiza.get_analysis().indicators['low']
                                    pClose = analiza.get_analysis().indicators['close']
                                    break
                            except Exception as e:
                                print(e)
                                print("Estoy en un error")
                                time.sleep(5)
                        
                        
                        try:
                            nBela = lBelas[moneda]
                        except Exception:
                            lOrden[moneda] = 0
                            lBelas[moneda] = 0
                            nBela = 0

                        print(moneda + ":> " + str(pClose))
                        
                        if pOpen != nBela:
                            lBelas[moneda] = pOpen
                            print(moneda + " es: " + señal['RECOMMENDATION'])
                            if float(indicadores['EMA20']) < float(pClose):
                                print("tendencia alcista")
                                try:
                                    entra = señal['RECOMMENDATION'].index("BUY")
                                    entra = "BUY"
                                except Exception:
                                    entra = señal['RECOMMENDATION']
                                    lOrden[moneda] = entra
                                
                                
                                if entra == "BUY":
                                    cursor= conn.cursor()
                                    cursor.execute("SELECT * FROM public.active WHERE token = '"+moneda+"'")
                                    actives = cursor.fetchall()
                                    cursor.close()
                                    for active in actives:
                                        
                                        if active[2] > 0:
                                            cursor= conn.cursor()
                                            cursor.execute("SELECT * FROM public.users WHERE name = '"+active[1]+"'")
                                            user = cursor.fetchall()
                                            cursor.close()
                                            client = Client(user[0][2], user[0][3])
                                            
                                            lOrden[moneda] = entra
                                            while True:
                                                try:
                                                    orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT") + 4].upper())
                                                    break
                                                except Exception as e:
                                                    print("Error al consultar las ordenes linea 129")
                                                    print(e)
                                                    time.sleep(5)
                                            try:
                                                nextEntry[entra+moneda+active[1]]=nextEntry[entra+moneda+active[1]]
                                            except Exception:
                                                nextEntry[entra+moneda+active[1]]=0
                                            print(orders[1]["entryPrice"])
                                            if orders[1]["entryPrice"] == "0.0":
                                                nextEntry[entra+moneda+active[1]]=0
                                            elif float(nextEntry[entra+moneda+active[1]]) == 0 and orders[1]["entryPrice"] != "0.0":
                                                nextEntry[entra+moneda+active[1]] = orders[1]["entryPrice"]
                                                
                                            
                                            print(nextEntry)
                                            # aqui vamos con el precio al que debe estar como mínimo
                                            precioC = float(nextEntry[entra+moneda+active[1]]) - (float(nextEntry[entra+moneda+active[1]]) * float(active[4]))
                                            cantidad = round(float(active[2]) / float(orders[0]["markPrice"]), int(token[2]))
                                            if precioC == 0.0:
                                                nextEntry[entra+moneda+active[1]]=0
                                                
                                            if precioC >= float(orders[1]["markPrice"]) or precioC == 0.0:
                                                print("abrir Compra")
                                                print(pClose)
                                                nextEntry[entra+moneda+active[1]]=pClose
                                                print(nextEntry)
                                                conn = conectar()
                                                cursor= conn.cursor()
                                                json_data = json.dumps(nextEntry)
                                                sql = "UPDATE entradas SET ordenes = %s WHERE id = 1;"
                                                data = (json_data,)
                                                cursor.execute(sql, data)
                                                conn.commit()
                                                cursor.close()
                                                order_long = ""
                                                order_long = client.futures_create_order(
                                                    symbol=moneda[:moneda.index("USDT") + 4].upper(),
                                                    side='BUY',
                                                    positionSide='LONG',
                                                    type=ORDER_TYPE_MARKET,
                                                    quantity=cantidad
                                                )
                                                while True:
                                                    if order_long != "":
                                                        orders = ""
                                                        orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT") + 4].upper())
                                                        while True:
                                                            if orders != "":
                                                                close_long = client.futures_create_order(
                                                                    symbol=moneda[:moneda.index("USDT") + 4].upper(),
                                                                    side='SELL',
                                                                    positionSide='LONG',
                                                                    type=ORDER_TYPE_LIMIT,
                                                                    timeinforce='GTC',
                                                                    quantity=abs(float(orders[1]["positionAmt"])),
                                                                    price=round(float(orders[1]["entryPrice"]) + (float(orders[1]["entryPrice"]) * float(active[5])), int(token[3]))
                                                                )
                                                                break
                                                        break

                            elif float(indicadores['EMA20']) > float(pClose):
                                print("tendencia bajista")
                                try:
                                    entra = señal['RECOMMENDATION'].index("SELL")
                                    entra = "SELL"
                                except Exception:
                                    entra = señal['RECOMMENDATION']
                                    lOrden[moneda] = entra
                                
                                
                                if entra == "SELL":
                                    cursor= conn.cursor()
                                    cursor.execute("SELECT * FROM public.active WHERE token = '"+moneda+"'")
                                    actives = cursor.fetchall()
                                    cursor.close()
                                    
                                    for active in actives:
                                        if active[3] > 0:
                                            cursor= conn.cursor()
                                            cursor.execute("SELECT * FROM public.users WHERE name = '"+active[1]+"'")
                                            user = cursor.fetchall()
                                            cursor.close()
                                            client = Client(user[0][2], user[0][3])
                                            
                                            lOrden[moneda] = entra
                                            while True:
                                                try:
                                                    orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT") + 4].upper())
                                                    break
                                                except Exception as e:
                                                    print("Error al consultar las ordenes linea 190")
                                                    print(e)
                                                    time.sleep(10)
                                            try:
                                                nextEntry[entra+moneda+active[1]]=nextEntry[entra+moneda+active[1]]
                                            except Exception:
                                                nextEntry[entra+moneda+active[1]]=0
                                                
                                            if orders[2]["entryPrice"] == "0.0":
                                                nextEntry[entra+moneda+active[1]]=0
                                            elif float(nextEntry[entra+moneda+active[1]]) == 0 and orders[2]["entryPrice"] != "0.0":
                                                nextEntry[entra+moneda+active[1]] = orders[2]["entryPrice"]
                                                
                                            print(orders[2]["entryPrice"])
                                            print(nextEntry)
                                            lOrden[moneda] = entra
                                            # Aquí va el precio mínimo al que debe estar
                                            precioV = float(nextEntry[entra+moneda+active[1]]) + (float(nextEntry[entra+moneda+active[1]]) * float(active[4]))
                                            cantidad = round(float(active[3]) / float(orders[0]["markPrice"]), token[2])
                                            
                                                
                                            if precioV <= float(orders[2]["markPrice"]) or precioV == 0.0:
                                                print("abri short:")
                                                print(pClose)
                                                nextEntry[entra+moneda+active[1]]=pClose
                                                print(nextEntry)
                                                conn = conectar()
                                                cursor= conn.cursor()
                                                json_data = json.dumps(nextEntry)
                                                sql = "UPDATE entradas SET ordenes = %s WHERE id = 1;"
                                                data = (json_data,)
                                                cursor.execute(sql, data)
                                                conn.commit()
                                                cursor.close()
                                                order_short = ""
                                                order_short = client.futures_create_order(
                                                    symbol=moneda[:moneda.index("USDT") + 4].upper(),
                                                    side='SELL',
                                                    positionSide='SHORT',
                                                    type=ORDER_TYPE_MARKET,
                                                    quantity=cantidad
                                                )
                                                
                                                while True:
                                                    if order_short != "":
                                                        orders = ""
                                                        orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT") + 4].upper())

                                                        while True:
                                                            if orders != "":
                                                                close_short = client.futures_create_order(
                                                                    symbol=moneda[:moneda.index("USDT") + 4].upper(),
                                                                    side='BUY',
                                                                    positionSide='SHORT',
                                                                    type=ORDER_TYPE_LIMIT,
                                                                    timeinforce='GTC',
                                                                    quantity=abs(float(orders[2]["positionAmt"])),
                                                                    price=round(float(orders[2]["entryPrice"]) - (float(orders[2]["entryPrice"]) * float(active[5])), token[3])
                                                                )
                                                                break
                                                        break
                    
                        
                        
                        fin = time.time()
                        duracion = fin - inicio
                        espera = round(15-duracion, 0)
                        if espera >=1:
                            time.sleep(espera)                   
                else:
                    print("Estoy Apagado")
                    time.sleep(int(config[0][1]))          
            except Exception as e:    
                print("TENGO ERROR")
                print(e)
                time.sleep(5)
                break
                
            time.sleep(5)
    
    
    elif public_ip == config[0][2] and config[0][3] == "local" or config[0][3] == "none":
        conn = conectar()
        cursor= conn.cursor()
        json_data = "render"
        sql = "UPDATE config SET servidor = %s;"
        data = (json_data,)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
    elif public_ip != config[0][2] and config[0][3] == "render":
        conn = conectar()
        cursor= conn.cursor()
        json_data = "none"
        sql = "UPDATE config SET servidor = %s ;"
        data = (json_data,)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        time.sleep(int(config[0][1]))
    else:
        print("La ip que me con la que estoy arrancando no es buena")
        print(public_ip)
        print("Esto esta en un servidor online")
        print(config[0][3])
        time.sleep(int(config[0][1]))
        
else:
    print("no he puede validar tu ip")
