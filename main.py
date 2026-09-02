import json
import requests
from datetime import datetime


class IpDetector:
    def __init__(self):
        self.api_url = "https://api.ipify.org?format=json"

    def get_ip(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            return response.json().get("ip")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Ошибка получения IP: {e}")
            return None


class GeoDetector:
    def __init__(self):
        self.api_url = "https://ipinfo.io/{}/geo"

    def get_geo_data(self, ip):
        if not ip:
            return None
        try:
            response = requests.get(self.api_url.format(ip), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Ошибка получения геоданных: {e}")
            return None


class YandexDiskUploader:
    def __init__(self, token, folder_name):
        self.token = token
        self.folder_name = folder_name
        self.headers = {"Authorization": f"OAuth {token}"}
        self.base_url = "https://cloud-api.yandex.net/v1/disk"

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def create_folder(self):
        self.log(f"Создание папки: {self.folder_name}", "INFO")
        url = f"{self.base_url}/resources"
        params = {"path": self.folder_name}
        try:
            response = requests.put(url, headers=self.headers, params=params, timeout=30)
            if response.status_code in [200, 201]:
                self.log(f"Папка '{self.folder_name}' создана или уже существует", "SUCCESS")
                return True
            self.log(f"Ошибка создания папки: {response.status_code}", "ERROR")
            return False
        except requests.exceptions.RequestException as e:
            self.log(f"Ошибка при создании папки: {e}", "ERROR")
            return False

    def upload_file(self, file_name, file_data):
        self.log(f"Загрузка файла: {file_name}", "INFO")
        url = f"{self.base_url}/resources/upload"
        params = {"path": f"{self.folder_name}/{file_name}", "overwrite": True}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            upload_url = response.json()["href"]
            self.log("URL для загрузки получен", "SUCCESS")
            response = requests.put(upload_url, data=file_data, headers={"Content-Type": "application/json"}, timeout=60)
            response.raise_for_status()
            self.log(f"Файл '{file_name}' загружен успешно!", "SUCCESS")
            return True
        except requests.exceptions.RequestException as e:
            self.log(f"Ошибка при загрузке файла: {e}", "ERROR")
            return False


def main():
    print("\n" + "=" * 60)
    print("🌍 IP DETECTOR - Определение местоположения по IP")
    print("=" * 60 + "\n")

    token = input("Введите токен Яндекс.Диска: ").strip()
    if not token:
        print("❌ Токен не может быть пустым!")
        return

    folder_name = input("Введите название папки на Яндекс.Диске: ").strip()
    if not folder_name:
        folder_name = "IP_Detector"
        print(f"⚠️ Используем название папки по умолчанию: {folder_name}")

    print("\n" + "-" * 60)
    print("🚀 Начинаем процесс...")
    print("-" * 60 + "\n")

    ip_detector = IpDetector()
    ip = ip_detector.get_ip()
    if not ip:
        print("❌ Не удалось получить IP-адрес. Завершение работы.")
        return

    print(f"✅ Ваш IP-адрес: {ip}\n")

    geo_detector = GeoDetector()
    geo_data = geo_detector.get_geo_data(ip)
    if not geo_data:
        print("❌ Не удалось получить геоданные. Завершение работы.")
        return

    print("✅ Геоданные получены:")
    print(json.dumps(geo_data, indent=2, ensure_ascii=False))
    print()

    result_data = {
        "ip": ip,
        "geo_data": geo_data,
        "timestamp": datetime.now().isoformat()
    }

    json_str = json.dumps(result_data, indent=4, ensure_ascii=False)
    json_bytes = json_str.encode("utf-8")
    file_name = f"ip_info_{ip.replace('.', '_')}.json"

    uploader = YandexDiskUploader(token, folder_name)

    if not uploader.create_folder():
        print("❌ Не удалось создать папку. Завершение работы.")
        return

    if uploader.upload_file(file_name, json_bytes):
        print("\n" + "=" * 60)
        print("✅ РАБОТА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print(f"📁 Папка на Яндекс.Диске: {folder_name}")
        print(f"📄 Файл: {file_name}")
        print("=" * 60)
    else:
        print("❌ Ошибка при загрузке файла на Яндекс.Диск.")
        return


if __name__ == "__main__":
    main()
