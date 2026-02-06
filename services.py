import requests
import time
import socks

def rotate_proxy(url):
    try:
        requests.get(url, timeout=10)
        time.sleep(5) # Пауза, чтобы IP сменился
        return True
    except:
        return False

class SMSManager:
    def __init__(self, key):
        self.key = key
        self.url = "https://api.sms-activate.org/stora/v1/"

    def get_number(self, country=6): # 6 - Индонезия
        r = requests.get(f"{self.url}?api_key={self.key}&action=getNumber&service=tg&country={country}").text
        if "ACCESS_NUMBER" in r:
            return r.split(':')[1], r.split(':')[2] # ID и Номер
        return None, r

    def get_code(self, activation_id):
        for _ in range(30): # Ждем код до 2.5 минут
            r = requests.get(f"{self.url}?api_key={self.key}&action=getStatus&id={activation_id}").text
            if "STATUS_OK" in r:
                return r.split(':')[1]
            time.sleep(5)
        return None