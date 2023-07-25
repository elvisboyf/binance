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
    print(f"Tu dirección IP pública es: {public_ip}")
else:
    print("No se pudo obtener la dirección IP pública.")
