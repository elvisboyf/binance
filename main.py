from tradingview_ta import *
import tradingview_ta, time, json
#import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
nBela = ""
# with open("datosorden.json", "r") as archivo:
#     datosorden = json.load(archivo)
# archivo.close()
#mambra
key = "b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa"
priv = "AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI"

#mio
# key= "JiiNHqwuxhhvUfayfHbAaFLkIUDlAMloAlPQHFMFIc7wk8QVskMgq2HdXKam0KZn"
# priv= "XGRMtw8rsyDSiBsB0AghvY7ewuCFgyybjR63Zv40k5HVpPX117FNCX80n2VqLsjv"

client = Client(key,priv)
orden = "nulo"
entrada = "0.3703"
moneda = "OCEANUSDT.P"
usdt = 100
print("me estoy ejecutando")
buenaIP = "54.254.162.138"
import requests

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
if public_ip:
    if public_ip == buenaIP:
        while True:
            
            try:
                
               
                analiza = TA_Handler(
                    symbol=moneda,
                    screener="crypto",
                    exchange="BINANCE",
                    interval=Interval.INTERVAL_1_MINUTE
                    )
                indicadores = analiza.get_analysis().indicators
                señal = analiza.get_analysis().summary
                ociladores = analiza.get_analysis().oscillators
                medias = analiza.get_analysis().moving_averages
                pOpen= analiza.get_analysis().indicators['open']
                pHigh = analiza.get_analysis().indicators['high']
                pLow = analiza.get_analysis().indicators['low']
                pClose = analiza.get_analysis().indicators['close']
                
                print(nBela)
                print(pClose)
                if pOpen != nBela:
                    nBela = pOpen
                    print("Mi señal es: "+señal['RECOMMENDATION'])
                    if float(indicadores['EMA100']) < float(pClose):
                        print("tendencia alcista")
                        try:
                            entra = señal['RECOMMENDATION'].index("BUY")
                            entra = "BUY"
                        except Exception:
                            entra = señal['RECOMMENDATION']
                            orden = entra
                        
                        if entra == "BUY" and orden != entra:
                            orden = entra
                            orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                            
                            #aqui vamos con el precio al que debe estar como minimo
                            precioC = float(orders[1]["entryPrice"])-(float(orders[1]["entryPrice"])*0.004)
                            cantidad = round(usdt / float(orders[0]["markPrice"]),0)
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
                                        time.sleep(5)
                                        orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                                        time.sleep(5)
                                        close_long = client.futures_create_order(
                                            symbol=moneda[:moneda.index("USDT")+4].upper(),
                                            side='SELL',
                                            positionSide='LONG',
                                            type=ORDER_TYPE_LIMIT,
                                            timeinforce='GTC',
                                            quantity=abs(float(orders[1]["positionAmt"])),
                                            price=round(float(orders[1]["entryPrice"])+(float(orders[1]["entryPrice"])*0.002),4)
                                        )
                                        break
                            
                            
                            
                            
                            
                    if float(indicadores['EMA100']) > float(pClose):
                        print("tendecia bajista")
                        try:
                            entra = señal['RECOMMENDATION'].index("SELL")
                            entra = "SELL"
                        except Exception:
                            entra = señal['RECOMMENDATION']
                            orden = entra
                        
                        if entra == "SELL" and orden != entra:
                            orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                            orden = entra
                            #Aqui va el precio minimo al que debe estar
                            precioV = float(orders[2]["entryPrice"])+(float(orders[2]["entryPrice"])*0.004)
                            cantidad = round(usdt / float(orders[0]["markPrice"]),0)
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
                                        orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                                        time.sleep(5)
                                        close_short = client.futures_create_order(
                                              symbol=moneda[:moneda.index("USDT")+4].upper(),
                                              side='BUY',
                                              positionSide='SHORT',
                                              type=ORDER_TYPE_LIMIT,
                                              timeinforce='GTC',
                                              quantity=abs(float(orders[2]["positionAmt"])),
                                              price=round(float(orders[2]["entryPrice"])-(float(orders[2]["entryPrice"])*0.002),4)
                                          )
                                        break
                                    
                                    
                                
                                
            
                
                            
            except Exception as e:    
                print("TENGO ERROR")
                print(e)
                
            time.sleep(5)
    else:
        print("La ip que me con la que estoy arrancando no es buena")
else:
    print("no he puede validar tu ip")
