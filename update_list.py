import requests
import re
import os
import datetime
import urllib3

# Ayarlar
FILE_PATH = os.path.join(os.getcwd(), "tr.m3u")
HEADERS = {'User-Agent': 'Mozilla/5.0'}

urllib3.disable_warnings()
session = requests.Session()
session.headers.update(HEADERS)
session.verify = False

def main():
    print(f"DEBUG: Çalışma dizini -> {os.getcwd()}")
    
    # 1. Kaynağı indir
    try:
        print("DEBUG: Patron.m3u indiriliyor...")
        r = session.get("https://link.testworkery0.workers.dev/patron.m3u", timeout=20)
        if r.status_code != 200:
            print(f"HATA: İndirme başarısız, status code: {r.status_code}")
            return
        
        # M3U içeriğini al
        icerik = r.text
        
        # 2. Dosyayı kesinlikle yaz
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"# --- SON GÜNCELLEME: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')} --- #\n")
            f.write(icerik.replace("#EXTM3U", ""))
            
        print(f"BAŞARILI: tr.m3u {FILE_PATH} konumuna yazıldı.")
        
    except Exception as e:
        print(f"HATA: Kritik bir sorun oluştu: {e}")

if __name__ == "__main__":
    main()
