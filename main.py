from tradingview_ta import *
import tradingview_ta, time, json, requests
from binance.client import Client
from binance.enums import *

with open("datosmonedas.json", "r") as archivo:
    datosmonedas = json.load(archivo)
archivo.close()

#LISTA DE URLs
urlmontos = "https://dl.dropboxusercontent.com/s/x34e43ep4i25ye9/montos.js"
urlmonedas = "https://dl.dropboxusercontent.com/s/j3vhsfkwqwm2h7t/monedas.js"
urlconfig = "https://dl.dropboxusercontent.com/s/j3jmgb3tk01mvsl/config.js"
urlapikey = "https://dl.dropboxusercontent.com/s/7yzcbq4khj4uesf/apikey.js"


while True:
    try:
        connconfig = requests.get(urlconfig).text
        break
    except Exception as e:
        print("Error de conn urlconfig")
        time.sleep(5)
    
configuracion = json.loads(connconfig)
lBelas={}
lOrden = {}
if configuracion["bot"] == "On":
    print("ENCENDIENDO...")
    ciclos = configuracion["ciclos"]
    cciclos = 0
    while True:
        try:
            connmontos = requests.get(urlmontos).text
            datosmontos = json.loads(connmontos)
            break
        except Exception:
            print("Error urlmontos")
            time.sleep(5)
    while True:
        try:
            connmonedas = requests.get(urlmonedas).text
            listamondedas = json.loads(connmonedas)
            break
        except Exception:
            print("Error urlmonedas")
            time.sleep(5)
    while True:
        try:
            connapikey = requests.get(urlapikey).text
            listaapikey = json.loads(connapikey)
            break
        except Exception:
            print("Error urlapikey")
            time.sleep(5)
    for moneda in listamondedas:
        lBelas[moneda]=0
        lOrden[moneda]=0
    
    usuarios = list(listaapikey.keys())
    
    while True:
        
        if ciclos > cciclos:
            print("estoy corriendo ciclo "+str(cciclos))
            cciclos+=1
            for moneda in listamondedas:
                
                #TRAER LOS DATOS DE TRANDIGVIEW
                analiza = TA_Handler(
                    symbol=moneda+".P",
                    screener="crypto",
                    exchange="BINANCE",
                    interval=Interval.INTERVAL_1_MINUTE
                    )
                #LOS DATOS DE LOS INDICADORES
                indicadores = analiza.get_analysis().indicators
                señal = analiza.get_analysis().summary
                ociladores = analiza.get_analysis().oscillators
                medias = analiza.get_analysis().moving_averages
                pOpen= analiza.get_analysis().indicators['open']
                pHigh = analiza.get_analysis().indicators['high']
                pLow = analiza.get_analysis().indicators['low']
                pClose = analiza.get_analysis().indicators['close']
                
                nBela = lBelas[moneda]
                
                    
                print(moneda+":> "+str(pClose))
                if pOpen != nBela:
                    lBelas[moneda] = pOpen
                    print(moneda+" es: "+señal['RECOMMENDATION'])
                    if float(indicadores['EMA100']) < float(pClose):
                        print("tendencia alcista")
                        try:
                            entra = señal['RECOMMENDATION'].index("BUY")
                            entra = "BUY"
                        except Exception:
                            entra = señal['RECOMMENDATION']
                            lOrden[moneda] = entra
                        
                        if entra == "BUY" and lOrden[moneda] != entra:
                            for usuario in usuarios:
                                if listaapikey[usuario][2]==1:
                                    key = listaapikey[usuario][0]
                                    priv = listaapikey[usuario][1]
                                    client = Client(key,priv, )
                                    time.sleep(5)
                                    lOrden[moneda] = entra
                                    while True:
                                        try:
                                            orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                                            break
                                        except Exception as e:
                                            print(e)
                                            time.sleep(10)
                                    #aqui vamos con el precio al que debe estar como minimo
                                    precioC = float(orders[1]["entryPrice"])-(float(orders[1]["entryPrice"])*0.007)
                                    cantidad = round(float(datosmontos[moneda][0]) / float(orders[0]["markPrice"]),decimalmoneda)
                                    if  precioC >= float(orders[1]["markPrice"]) or precioC == 0.0:
                                        print("abrir Compra")
                                        print(pClose)
                                        order_long =""
                                         order_long = client.futures_create_order(
                                             symbol=moneda[:moneda.index("USDT")+4].upper(),
                                             side='BUY',
                                             positionSide='LONG',
                                             type=ORDER_TYPE_MARKET,
                                             quantity=cantidad
                                         )
                                        while True:
                                            if order_long != "":
                                                orders =""
                                                orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                                                while True:
                                                    if orders !="":
                                                         close_long = client.futures_create_order(
                                                             symbol=moneda[:moneda.index("USDT")+4].upper(),
                                                             side='SELL',
                                                             positionSide='LONG',
                                                             type=ORDER_TYPE_LIMIT,
                                                             timeinforce='GTC',
                                                             quantity=abs(float(orders[1]["positionAmt"])),
                                                             price=round(float(orders[1]["entryPrice"])+(float(orders[1]["entryPrice"])*0.003),decimalprecio)
                                                         )
                                                        break
                                                break
                            
                            
                            
                            
                            
                    if float(indicadores['EMA100']) > float(pClose):
                        print("tendecia bajista")
                        try:
                            entra = señal['RECOMMENDATION'].index("SELL")
                            entra = "SELL"
                        except Exception:
                            entra = señal['RECOMMENDATION']
                            lOrden[moneda] = entra
                        
                        if entra == "SELL" and lOrden[moneda] != entra:
                            for usuario in usuarios:
                                if listaapikey[usuario][2]==1:
                                    key = listaapikey[usuario][0]
                                    priv = listaapikey[usuario][1]
                                    client = Client(key,priv)
                                    time.sleep(5)
                                    while True:
                                        try:
                                            orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                                            break
                                        except Exception as e:
                                            print(e)
                                            time.sleep(10)
                                            
                                    lOrden[moneda] = entra
                                    #Aqui va el precio minimo al que debe estar
                                    precioV = float(orders[2]["entryPrice"])+(float(orders[2]["entryPrice"])*0.007)
                                    cantidad = round(float(atosmontos[moneda][1]) / float(orders[0]["markPrice"]),decimalmoneda)
                                    if  precioV <= float(orders[2]["markPrice"]) or precioV == 0.0 :
                                        order_short=""
                                         order_short = client.futures_create_order(
                                             symbol=moneda[:moneda.index("USDT")+4].upper(),
                                             side='SELL',
                                             positionSide='SHORT',
                                             type=ORDER_TYPE_MARKET,
                                             quantity=cantidad
                                         )
                                        print("abri short:")
                                        print(pClose)
                                        while True:
                                            if order_short != "":
                                                orders =""
                                                orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                                                
                                                while True:
                                                    if orders != "":
                                                         close_short = client.futures_create_order(
                                                               symbol=moneda[:moneda.index("USDT")+4].upper(),
                                                               side='BUY',
                                                               positionSide='SHORT',
                                                               type=ORDER_TYPE_LIMIT,
                                                               timeinforce='GTC',
                                                               quantity=abs(float(orders[2]["positionAmt"])),
                                                               price=round(float(orders[2]["entryPrice"])-(float(orders[2]["entryPrice"])*0.005),decimalprecio)
                                                           )
                                                        break
                                                break
            
        else:
            while True:
                try:
                    connconfig = requests.get(urlconfig).text
                    configuracion = json.loads(connconfig)
                    print("reconectado..")
                    break
                except Exception:
                    print("Error de conn urlconfig")
                        
            if configuracion["bot"] == "Update":
                print("Actualizando datos")
                ciclos = configuracion["ciclos"]
                cciclos = 0
                while True:
                    try:
                        connmontos = requests.get(urlmontos).text
                        datosmontos = json.loads(connmontos)
                        break
                    except Exception:
                        print("Error urlmontos")
                        time.sleep(5)
                while True:
                    try:
                        connmonedas = requests.get(urlmonedas).text
                        listamondedas = json.loads(connmonedas)
                        break
                    except Exception:
                        print("Error urlmonedas")
                        time.sleep(5)
                while True:
                    try:
                        connapikey = requests.get(urlapikey).text
                        listaapikey = json.loads(connapikey)
                        break
                    except Exception:
                        print("Error urlapikey")
                        time.sleep(5)
                
                for moneda in listamondedas:
                    lBelas[moneda]=0
                    lOrden[moneda]=0
                usuarios = list(listaapikey.keys())
                
            elif configuracion["bot"] == "Stop":
                print("Me detuve")
                break
            elif configuracion["bot"] == "Wait":
                print("que tiempo quiere que espere")
                print("esperare "+str(configuracion["wait"]))
            else:
                print("continuar igual")
                cciclos=0
                
    
    
else:
    print("Estoy Apagado")
    time.sleep(configuracion["wait"])
