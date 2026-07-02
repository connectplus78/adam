import requests
import re
import os
import datetime
import shutil
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
import sys

# --- AYARLAR ---
FILE_PATH = "tr.m3u"
ZIRH_LIMIT = 5100  # Korunacak satır sayısı
THREADS = 64 
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.headers.update(HEADERS)
session.verify = False

# YASAKLI LİSTELER
YASAKLI_IP_LISTESI = ["87.121.104.29", "87.121.104.29:1071"]
HAVUZ_YASAKLI_KELIMELER = ["S01", "S02", "E01", "FILM", "MOVIES", "ADULT", "XXX", "+18"]

def kanal_ismini_temizle(extinf_satiri):
    # Kanal ismini temizleme mantığı
    if "," in extinf_satiri:
        prefix, kanal_adi = extinf_satiri.split(",", 1)
    else:
        prefix, kanal_adi = '#EXTINF:-1', extinf_satiri
    
    kanal_adi = re.sub(r'(?i)\b(HD|SD|FHD|4K|TURK|TÜRK)\b', '', kanal_adi)
    return f'{prefix},{kanal_adi.strip()}'

def link_saglam_mi(url):
    try:
        with session.get(url, timeout=5, stream=True) as r:
            return r.status_code in [200, 206]
    except:
        return False

def kanal_isleme(kanal_metni, eklenen_urller):
    satir_grubu = kanal_metni.strip().split('\n')
    if len(satir_grubu) < 2: return None
    ext_satiri, link_satiri = satir_grubu[0], satir_grubu[-1].strip()
    
    if link_satiri in eklenen_urller or any(ip in link_satiri for ip in YASAKLI_IP_LISTESI):
        return None
    if any(yasak.lower() in ext_satiri.lower() for yasak in HAVUZ_YASAKLI_KELIMELER):
        return None
        
    if link_saglam_mi(link_satiri):
        return f"{kanal_ismini_temizle(ext_satiri)}\n{link_satiri}"
    return None

def main():
    print("🛡️ SİSTEM BAŞLATILDI: Sadece Patron.m3u modu aktif.")
    
    # Yedeği al
    if os.path.exists(FILE_PATH):
        shutil.copyfile(FILE_PATH, FILE_PATH + ".bak")

    eklenen_urller = set()
    ana_liste_zirh = []

    # Zırhlı kısmı yükle
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            tum_lines = f.readlines()
            ana_liste_zirh = tum_lines[:ZIRH_LIMIT]
            for s in ana_liste_zirh:
                if s.strip().startswith("http"):
                    eklenen_urller.add(s.strip())

    # Kaynağı çek
    print("📥 Kaynak indiriliyor...")
    try:
        r = session.get("https://link.testworkery0.workers.dev/patron.m3u", timeout=15)
        bulunan = re.findall(r"(#EXTINF:.*?\n+https?.*?)(?=#EXTINF|$)", r.text, re.DOTALL | re.IGNORECASE)
    except Exception as e:
        print(f"Hata: {e}")
        return

    # İşle
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        results = list(executor.map(lambda k: kanal_isleme(k, eklenen_urller), bulunan))
        final_listesi = [r for r in results if r is not None]

    # Yaz
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(ana_liste_zirh)
        if final_listesi:
            f.write(f"\n# --- GÜNCEL EKLENENLER ({datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}) --- #\n")
            f.write("\n".join(final_listesi) + "\n")

    print(f"🏁 İşlem tamamlandı. Toplam {len(final_listesi)} yeni kanal eklendi.")

if __name__ == "__main__":
    main()
