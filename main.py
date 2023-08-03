from tradingview_ta import *
import tradingview_ta
import time
from binance.client import Client
from binance.enums import *
import psycopg2 as pg

lBelas = {}
lOrden = {}

def conectar():
    while True:
        try:
            print("conectando DB")
            conecxion = pg.connect(
                host="postgres://root:FxoDBQeYSb82YvlJS538k883NlsbZEiW@dpg-cj4dputgkuvsl08la0s0-a/creativedb",
                user="root",
                password = "FxoDBQeYSb82YvlJS538k883NlsbZEiW",
                database = "creativedb",
                port = "5432")
            break
        except Exception:
            print("error en conection")
    return conecxion

while True:
    conn = conectar()
    cursor= conn.cursor()
    
    #verifica configuracion
    cursor.execute("SELECT * FROM public.config")
    config = cursor.fetchall()
    
    #buscar los usuarios activo
    cursor.execute("SELECT * FROM public.tokens WHERE actived = 1")
    tokens = cursor.fetchall()
    
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
                if float(indicadores['EMA100']) < float(pClose):
                    print("tendencia alcista")
                    try:
                        entra = señal['RECOMMENDATION'].index("BUY")
                        entra = "BUY"
                    except Exception:
                        entra = señal['RECOMMENDATION']
                        lOrden[moneda] = entra

                    if entra == "BUY" and lOrden[moneda] != entra:
                        cursor.execute("SELECT * FROM public.active WHERE token = '"+moneda+"'")
                        actives = cursor.fetchall()
                        for active in actives:
                            if active[2] > 0:
                                cursor.execute("SELECT * FROM public.users WHERE name = '"+active[1]+"'")
                                user = cursor.fetchall()
                                client = Client(user[0][2], user[0][3])
                                
                                lOrden[moneda] = entra
                                while True:
                                    try:
                                        orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT") + 4].upper())
                                        break
                                    except Exception as e:
                                        print(e)
                                        time.sleep(10)
                                        
                                # aqui vamos con el precio al que debe estar como mínimo
                                precioC = float(orders[1]["entryPrice"]) - (float(orders[1]["entryPrice"]) * float(active[4]))
                                cantidad = round(float(active[2]) / float(orders[0]["markPrice"]), int(token[2]))
                                if precioC >= float(orders[1]["markPrice"]) or precioC == 0.0:
                                    print("abrir Compra")
                                    print(pClose)
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

                elif float(indicadores['EMA100']) > float(pClose):
                    print("tendencia bajista")
                    try:
                        entra = señal['RECOMMENDATION'].index("SELL")
                        entra = "SELL"
                    except Exception:
                        entra = señal['RECOMMENDATION']
                        lOrden[moneda] = entra

                    if entra == "SELL" and lOrden[moneda] != entra:
                        cursor.execute("SELECT * FROM public.active WHERE token = '"+moneda+"'")
                        actives = cursor.fetchall()
                        
                        for active in actives:
                            if active[3] > 0:
                                cursor.execute("SELECT * FROM public.users WHERE name = '"+active[1]+"'")
                                user = cursor.fetchall()
                                client = Client(user[0][2], user[0][3])
                                
                                lOrden[moneda] = entra
                                while True:
                                    try:
                                        orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT") + 4].upper())
                                        break
                                    except Exception as e:
                                        print(e)
                                        time.sleep(10)

                                lOrden[moneda] = entra
                                # Aquí va el precio mínimo al que debe estar
                                precioV = float(orders[2]["entryPrice"]) + (float(orders[2]["entryPrice"]) * float(active[4]))
                                cantidad = round(float(active[3]) / float(orders[0]["markPrice"]), token[2])
                                
                                if precioV <= float(orders[2]["markPrice"]) or precioV == 0.0:
                                    order_short = ""
                                    order_short = client.futures_create_order(
                                        symbol=moneda[:moneda.index("USDT") + 4].upper(),
                                        side='SELL',
                                        positionSide='SHORT',
                                        type=ORDER_TYPE_MARKET,
                                        quantity=cantidad
                                    )
                                    print("abri short:")
                                    print(pClose)
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
            
        
        
        
        #AQUI TERMINA EL CODIGO A EJECUTAR
        
    else:
        print("Estoy Apagado")
        time.sleep(int(config[0][1]))
