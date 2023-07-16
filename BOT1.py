import pandas as pd
import datetime
from binance.client import Client
from binance.enums import *

client = Client('hVCTeyRTLdl3Wedgbm1aAPGOcNNBVvcjxTxLfaAKbXRj6VuHByfYCYKoKzZI8l55', 'sWNKaWDEWzDnMg0Q5Jky84EdslGaR0udfagvRkXUEyytg7ZdviNNifF1b5icmIpP')
segundo=0
myslice=slice(2)

def Tiempo():
	shora = slice(5)
	x = datetime.datetime.utcnow()
	
	hora = x.strftime("%X")
	
	return hora[shora]

def Inicio():
	global segundo
	if "20:00"==Tiempo():
		print("Es hora de comprar")
		segundo=0
		Comprar(client.get_margin_price_index(symbol='ADAUSDT')['price'])
	else:
		for x in range(9800000):
			if x == 9799999:
				segundo = segundo +1
				#info = client.get_margin_price_index(symbol='ADAUSDT')['price']
				#print(info)
				Inicio()

def Comprar(precio):
	global PrecioVenta, orden, myslice
	PrecioVenta = precio +(precio*0.01)
	PrecioCompra=precio
	CantidadComprar = float(client.get_asset_balance(asset='USDT')['free'][myslice])/PrecioCompra
	CantidadComprar=str(CantidadComprar)[myslice]

	orden = client.create_order(
	    symbol='ADAUSDT',
	    side=SIDE_BUY,
	    type=ORDER_TYPE_LIMIT,
	    timeInForce=TIME_IN_FORCE_GTC,
	    quantity=CantidadComprar,
	    price=PrecioCompra)

	if orden:
		print("Se Compraran: "+str(CantidadComprar)+" Al precio de: "+str(PrecioCompra))
		Consulta()

def Vender():
	global PrecioVenta, orden, myslice
	CantidadVender = float(client.get_asset_balance(asset='ADA')['free'][myslice])

	orden = client.create_order(
	    symbol='ADAUSDT',
	    side=SIDE_SELL,
	    type=ORDER_TYPE_LIMIT,
	    timeInForce=TIME_IN_FORCE_GTC,
	    quantity=CantidadVender,
	    price=PrecioVenta)

	if orden:
		print("Se Venderan: "+str(CantidadVender)+" Al precio de: "+str(PrecioVenta))
		Consulta()

def Consulta():
	global orden
	
	if orden:
		for x in range(9800000):
			if x == 9799999:
				estado = client.get_order(
				    symbol='ADAUSDT',
				    orderId=orden['orderId'])
				if estado['status'] == "NEW" and estado['side']=="BUY":
					print("Aun Esperamos esperando la Compra")
					Consulta()
				elif estado['status'] == "FILLED" and estado['side']=="BUY":
					print("Se ha completado la compra, Ahora vamos a Vender")
					Vender()
				elif estado['status'] == "NEW" and estado['side']=="SELL":
					if "19:59"==Tiempo():
						cancelar = client.cancel_margin_order(
						    symbol='ADAUSDT',
						    orderId=orden['orderId'])

						if cancelar:
							CantidadVender = float(client.get_asset_balance(asset='ADA')['free'][myslice])
							ventaRapida = client.get_margin_price_index(symbol='ADAUSDT')['price']
							orden = client.create_order(
							    symbol='ADAUSDT',
							    side=SIDE_SELL,
							    type=ORDER_TYPE_LIMIT,
							    timeInForce=TIME_IN_FORCE_GTC,
							    quantity=CantidadVender,
							    price=ventaRapida)

					else:
						print("Aun estamos esperando la Venta")
						Consulta()
				elif estado['status'] == "FILLED" and estado['side']=="SELL":
					print("Se han completado la Venta")
					Inicio()
	else:
		print("No hay nada pendiente")
		


Inicio()
print("Estamos corriendo")
#***********PRUEBA CODIGO***********#
