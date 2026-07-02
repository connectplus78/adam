import requests
import os
import datetime

# Dosyayı her zaman scriptin bulunduğu dizine yaz
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tr.m3u")

def main():
    print(f"DEBUG: Dosya şu konuma yazılacak: {FILE_PATH}")
    
    try:
        # Sadece Patron linkini çek
        response = requests.get("https://link.testworkery0.workers.dev/patron.m3u", timeout=20)
        
        if response.status_code == 200:
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("BAŞARILI: tr.m3u dosyası başarıyla oluşturuldu.")
        else:
            print(f"HATA: İndirme başarısız, status code: {response.status_code}")
            
    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    main()
