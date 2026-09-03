import json
import requests
from datetime import datetime


class IpDetector:
    def get_ip(self):
        try:
            resp = requests.get("https://api.ipify.org?format=json", timeout=10)
            return resp.json().get("ip")
        except Exception as e:
            print(f"Ошибка получения IP: {e}")
            return None


class GeoDetector:
    def get_geo_data(self, ip):
        try:
            url = f"https://ipinfo.io/{ip}/geo"
            resp = requests.get(url, timeout=10)
            return resp.json()
        except Exception as e:
            print(f"Ошибка получения геоданных: {e}")
            return None


class YandexDiskClient:
    def __init__(self, token):
        self.headers = {"Authorization": f"OAuth {token}"}
        self.base_url = "https://cloud-api.yandex.net/v1/disk"

    def create_folder(self, folder_name):
        url = f"{self.base_url}/resources"
        params = {"path": folder_name}
        try:
            resp = requests.put(url, headers=self.headers, params=params, timeout=30)
            return resp.status_code in [200, 201, 409]
        except Exception as e:
            print(f"Ошибка создания папки: {e}")
            return False

    def upload_file(self, folder_name, file_name, file_data):
        url = f"{self.base_url}/resources/upload"
        params = {"path": f"{folder_name}/{file_name}", "overwrite": True}
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=30)
            upload_url = resp.json()["href"]
            resp = requests.put(upload_url, data=file_data, timeout=60)
            return resp.status_code == 201
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False


def main():
    token = input("Токен Яндекс.Диска: ").strip()
    if not token:
        print("Токен не введён")
        return

    folder_name = input("Название папки: ").strip()
    if not folder_name:
        folder_name = "IP_Detector"

    ip = IpDetector().get_ip()
    if not ip:
        print("Не удалось получить IP")
        return

    geo_data = GeoDetector().get_geo_data(ip)
    if not geo_data:
        print("Не удалось получить геоданные")
        return

    result = {
        "ip": ip,
        "city": geo_data.get("city"),
        "region": geo_data.get("region"),
        "country": geo_data.get("country"),
        "loc": geo_data.get("loc"),
        "org": geo_data.get("org"),
        "time": datetime.now().isoformat()
    }

    json_data = json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8")
    file_name = f"ip_{ip.replace('.', '_')}.json"

    client = YandexDiskClient(token)

    if not client.create_folder(folder_name):
        print("Не удалось создать папку")
        return

    if client.upload_file(folder_name, file_name, json_data):
        print(f"Файл {file_name} загружен в {folder_name}")
    else:
        print("Ошибка загрузки")


if __name__ == "__main__":
    main()