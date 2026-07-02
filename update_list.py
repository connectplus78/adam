import requests
import os

# 1. Dosya yolunu sabitliyoruz
dosya_adi = "tr.m3u"
dosya_yolu = os.path.join(os.getcwd(), dosya_adi)

print(f"DEBUG: Script çalışıyor. Hedef dosya: {dosya_yolu}")

try:
    # 2. İndirme işlemi
    url = "https://link.testworkery0.workers.dev/patron.m3u"
    print(f"DEBUG: {url} adresinden indiriliyor...")
    
    response = requests.get(url, timeout=30)
    response.raise_for_status() # Hata varsa yakalar
    
    # 3. Dosyaya yazma
    with open(dosya_yolu, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"BAŞARILI: {dosya_adi} dosyası {dosya_yolu} konumuna başarıyla yazıldı.")

except Exception as e:
    print(f"KRİTİK HATA: {e}")
    exit(1) # Hata durumunda scripti hata koduyla bitir
