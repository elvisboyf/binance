from tradingview_ta import *
import tradingview_ta, time, json, requests
#import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *

print("me estoy ejecutando")
buenaIP = "54.254.162.138"

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
    if public_ip == buenaIP:
        while True:
            
            try:
                
                pass
                break
                
                                    
                                    
                                
                                
            
                
                            
            except Exception as e:    
                print("TENGO ERROR")
                print(e)
                
            time.sleep(5)
    else:
        print("La ip que me con la que estoy arrancando no es buena")
else:
    print("no he puede validar tu ip")
