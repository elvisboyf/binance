from tradingview_ta import *
import tradingview_ta, time, json
#import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
nBela = ""

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
usdt = 40
print("he iniciado")
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
        

        if pOpen != nBela:
            nBela = pOpen
            print("Mi señal es: "+señal['RECOMMENDATION'])
            if float(indicadores['SMA50']) < float(pClose):
                
                try:
                    entra = señal['RECOMMENDATION'].index("BUY")
                    entra = "BUY"
                except Exception:
                    entra = señal['RECOMMENDATION']
                
                if entra == "BUY" and orden != entra:
                    orden = entra
                    orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                    
                    #aqui vamos con el precio al que debe estar como minimo
                    precioC = float(orders[1]["entryPrice"])-(float(orders[1]["entryPrice"])*0.004)
                    cantidad = round(usdt / float(orders[0]["markPrice"]),0)
                    if  precioC >= float(orders[1]["markPrice"]) or precioC == 0.0:
                        print("abrir Compra")
                        print(pClose)
                        
                        order_long = client.futures_create_order(
                            symbol=moneda[:moneda.index("USDT")+4].upper(),
                            side='BUY',
                            positionSide='LONG',
                            type=ORDER_TYPE_MARKET,
                            quantity=cantidad
                        )
                    
                
                elif entra != "BUY" and orden == "BUY":
                    orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                    
                    if abs(float(orders[1]["positionAmt"])) != 0 and float(orders[1]["unRealizedProfit"]) >= 0.10:
                       long_tp = client.futures_create_order(
                               symbol=moneda[:moneda.index("USDT")+4].upper(),
                               side='SELL',
                               positionSide='LONG',
                               type='TAKE_PROFIT_MARKET',
                               stopPrice=round(float(orders[1]["entryPrice"]),4),
                               quantity=round(abs(float(orders[1]["positionAmt"]))),
                               closePosition=True
                           )
                       print("cerrar posicion LONG")
                       
                       #aqui tengo que poner el codigo de cancelar todos los tp abiertos
                       
                    
                    orden = "nulo"
                    
                    
                    
                    
            if float(indicadores['SMA50']) > float(pClose):
                
                try:
                    entra = señal['RECOMMENDATION'].index("SELL")
                    entra = "SELL"
                except Exception:
                    entra = señal['RECOMMENDATION']
                
                if entra == "SELL" and orden != entra:
                    orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                    orden = entra
                    #Aqui va el precio minimo al que debe estar
                    precioV = float(orders[2]["entryPrice"])+(float(orders[2]["entryPrice"])*0.004)
                    cantidad = round(usdt / float(orders[0]["markPrice"]),0)
                    if  precioV <= float(orders[2]["markPrice"]) or precioV == 0.0 :
                        
                        order_short = client.futures_create_order(
                            symbol=moneda[:moneda.index("USDT")+4].upper(),
                            side='SELL',
                            positionSide='SHORT',
                            type=ORDER_TYPE_MARKET,
                            quantity=cantidad
                        )
                        print("abri short:")
                        print(pClose)
                        
                        
                    
                    
                
                elif entra != "SELL" and orden == "SELL":
                    orders = client.futures_position_information(symbol=moneda[:moneda.index("USDT")+4].upper())
                    
                    if abs(float(orders[2]["positionAmt"])) != 0 and float(orders[2]["unRealizedProfit"]) >= 0.10:
                       long_tp = client.futures_create_order(
                               symbol=moneda[:moneda.index("USDT")+4].upper(),
                               side='BUY',
                               positionSide='SHORT',
                               type='TAKE_PROFIT_MARKET',
                               stopPrice=round(float(orders[2]["entryPrice"]),4),
                               quantity=round(abs(float(orders[2]["positionAmt"]))),
                               closePosition=True
                           )
                       print("cerrar posicion SHORT")
                       
                       #aqui tengo que poner el codigo de cancelar todos los tp abiertos
                       
                    
                    orden = "nulo"
    except Exception as e:
        print("Estoy en un error asi que esperare")
        print(e)
        time.sleep(20)
    
                
            
                
    time.sleep(5)
