import requests
import re
import os
import datetime
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
import urllib3

# --- AYARLAR ---
# GitHub Actions içerisinde dosyanın hep aynı yerde olması için mutlak yol
FILE_PATH = os.path.join(os.getcwd(), "tr.m3u")
ZIRH_LIMIT = 5100
THREADS = 64 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
session.verify = False

def kanal_ismini_temizle(extinf_satiri):
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
    except: return False

def kanal_isleme(kanal_metni, eklenen_urller):
    satir_grubu = kanal_metni.strip().split('\n')
    if len(satir_grubu) < 2: return None
    ext_satiri, link_satiri = satir_grubu[0], satir_grubu[-1].strip()
    
    if link_satiri in eklenen_urller: return None
    if link_saglam_mi(link_satiri):
        return f"{kanal_ismini_temizle(ext_satiri)}\n{link_satiri}"
    return None

def main():
    print(f"📁 Çalışma dizini: {os.getcwd()}")
    
    eklenen_urller = set()
    ana_liste_zirh = []

    # Eğer dosya varsa zırhı oku
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            tum_lines = f.readlines()
            ana_liste_zirh = tum_lines[:ZIRH_LIMIT]
            for s in ana_liste_zirh:
                if s.strip().startswith("http"):
                    eklenen_urller.add(s.strip())
    else:
        print("⚠️ tr.m3u bulunamadı, yeni liste oluşturulacak.")

    # Kaynağı çek
    print("📥 Patron.m3u indiriliyor...")
    try:
        r = session.get("https://link.testworkery0.workers.dev/patron.m3u", timeout=20)
        bulunan = re.findall(r"(#EXTINF:.*?\n+https?.*?)(?=#EXTINF|$)", r.text, re.DOTALL | re.IGNORECASE)
    except Exception as e:
        print(f"Hata: {e}")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        results = list(executor.map(lambda k: kanal_isleme(k, eklenen_urller), bulunan))
        final_listesi = [r for r in results if r is not None]

    # Dosyayı yaz (Eğer zırhlı liste yoksa M3U başlığını ekle)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        if ana_liste_zirh:
            f.writelines(ana_liste_zirh)
        else:
            f.write("#EXTM3U\n")
            
        if final_listesi:
            f.write(f"\n# --- GÜNCEL EKLENENLER ({datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}) --- #\n")
            f.write("\n".join(final_listesi) + "\n")

    print(f"🏁 İşlem tamamlandı. Dosya kaydedildi: {FILE_PATH}")

if __name__ == "__main__":
    main()
