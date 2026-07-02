import requests
import re
import os
import datetime
import shutil
from concurrent.futures import ThreadPoolExecutor
import urllib3

# Ayarlar
FILE_PATH = os.path.join(os.getcwd(), "tr.m3u")
ZIRH_LIMIT = 5100
HEADERS = {'User-Agent': 'Mozilla/5.0'}

urllib3.disable_warnings()
session = requests.Session()
session.headers.update(HEADERS)
session.verify = False

def main():
    print(f"Çalışma dizini: {os.getcwd()}")
    
    # 1. Zırhlı kısmı al
    ana_liste_zirh = []
    eklenen_urller = set()
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            ana_liste_zirh = lines[:ZIRH_LIMIT]
            for s in ana_liste_zirh:
                if s.strip().startswith("http"):
                    eklenen_urller.add(s.strip())

    # 2. Patron.m3u'yu indir
    try:
        r = session.get("https://link.testworkery0.workers.dev/patron.m3u", timeout=20)
        bulunan = re.findall(r"(#EXTINF:.*?\n+https?.*?)(?=#EXTINF|$)", r.text, re.DOTALL | re.IGNORECASE)
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return

    # 3. Dosyayı yeniden oluştur
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(ana_liste_zirh)
        f.write(f"\n# --- GÜNCEL EKLENENLER ({datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}) --- #\n")
        
        for blok in bulunan:
            link = blok.split('\n')[-1].strip()
            if link not in eklenen_urller:
                f.write(blok + "\n")
                eklenen_urller.add(link)

    print("İşlem tamamlandı, tr.m3u kaydedildi.")

if __name__ == "__main__":
    main()
