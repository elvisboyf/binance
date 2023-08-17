import time, json, requests


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
