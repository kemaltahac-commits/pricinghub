## 2026-10-26

Ne yaptım: price_history şemaları + POST/GET /products/{id}/prices endpoint'leri. TestClient ile 6/6 test geçti (201, 201, sıra [119.9, 129.9], 404, 404).
Ne takıldım: app/main.py ve app/schemas.py'yi komple yeniden yazıp içeriği iki kez kaybettim. Uvicorn --reload child process ölünce port "Listen" görünüyor ama bağlantı reddediyor — 40 dk kaybettim.
Yarın ne: scraper iskeleti (Playwright, tek site, tek ürün).

## 2026-10-27

Ne yaptım: Playwright 1.64.1 kuruldu, scripts/scrape_one.py ile Trendyol ürün sayfasından fiyat çekildi. Doğrulanmış selector: [data-testid="current-price"] (ilk element). TR formatı parse edildi: "11.490 TL" -> 11490.0 float.
Ne takıldım: URL'i iki kez yanlış yapıştırdım (çift https://, sonra kategori URL'i -c- yerine ürün URL'i -p-). Selector tahminleri (.prc-dsc, .prc-org) sıfır döndü; DOM'u gezip text node'ları listeleyen teşhis script'i ile gerçek selector bulundu. Upwork'te "Open for work" rozetinin haftada 14 connect yediğini öğrendim, açmadım.
Yarın ne: scrape_one.py'yi DB'ye bağla — Product'ı URL'den bul/oluştur, PriceHistory'ye yaz. API'ye dokunma, script bağımsız kalsın.

## Notlar

- Trendyol'da fiyat widget'ları karışık: .original/.discounted = "son 10 günün en düşük fiyatı", .new-price/.old-price = benzer ürün karuseli. Ürün fiyatı sadece data-testid="current-price".
- data-testid="current-price" iki kez geçebiliyor (biri price-current-price-with-lowest-duration). .first ile ilkini al.

## 2026-10-28

Ne yaptım: scrape_one.py DB'ye bağlandı. Playwright -> parse_price -> Product (URL'den bul/oluştur) -> PriceHistory. İki kez çalıştırdım: 1) YENI URUN id=2 / row id=3, 2) MEVCUT URUN id=2 / row id=4. Duplicate ürün yok, geçmiş birikiyor. Commit: 73510e6.
Ne takıldım: python scripts\scrape_one.py ModuleNotFoundError veriyor, doğrusu python -m scripts.scrape_one. URL'deki query string (?boutiqueId=...) her istekte değişebildiği için normalize_url ile kesildi. git commit -m yazmayınca Vim açıldı, :wq ile çıktım.
Yarın ne: hata yolları — ürün/fiyat yok, parse hatası, timeout. Her biri için net print + exit code, sessiz except yok. Kodu bu sefer ben yazacağım.

## 2026-10-30 (gun 9)

Ne yaptım: parse_price fonksiyona çevrildi (isdigit filtresi + boş girdide ValueError). fetch try/except/finally ile sarıldı — PlaywrightError -> ScrapeError, browser.close() her durumda çalışıyor. main -> int oldu, hata anında DB'ye hiç dokunmadan return 1. Üç senaryo doğrulandı: olmayan ürün, kategori sayfası, timeout.
Ne takıldım: URL satırını yanlışlıkla page.goto ile ezdim; ScrapeError sınıfı yoktu. İkisi de 2 dakikalık hata ama 20 dakika yedi.
Yarın ne: scrape_all — birden fazla URL döngüde, her biri için ayrı hata yakalama, tek ürün çökerse diğerleri devam etsin.


## 2026-10-31 (gun 10)
Ne yaptım: scripts/scrape_all.py yazıldı — URLS listesi üzerinde döngü, her URL için ayrı try/except ScrapeError, biri çökerse continue ile devam. Çıktı: 1 basarili, 1 basarisiz, script çökmedi. Çoklu URL + ürün bazlı hata yakalama çalışıyor.
Ne takıldım: -m scripts.scrape_all çalıştırırken dosya adı karışıklığı yaşadım (kısa süreli). Ayrica URLS listesinde test URL'i (kategori sayfası) kaldı, her çalıştırmada yapay "1 basarisiz" üretiyor. scrape_all'ın DB'ye yazdığı çıktıda görünmüyor, doğrulanmadı.
Yarın ne: URLS'e 2-3 gerçek ürün linki koy, test URL'ini çıkar, hepsi BASARILI olmalı. Sonra Docker + README (v0.1).

## 2026-11-02 (gun 12)
scripts/scrape_all.py güncellenerek gerçek çoklu URL'ler eklendi.

Çoklu ürün döngüsü ve hata yönetimi ile test edildi (2 başarılı, 1 başarısız).

git commit yapıldı.
Bugün `pricinghub` projesinde Docker entegrasyonunu eksiksiz bir şekilde tamamladık. Sırasıyla şu adımları gerçekleştirdik:

### 2026-11-03 (gun 13)

### 1. Sistem & Sanallaştırma Altyapısı

* **Docker Desktop Kurulumu:** Windows installer üzerinden kurulumu başlattık.
* **Virtual Machine Platform:** Eksik olan sanallaştırma özelliğini PowerShell (`dism.exe`) komutuyla aktifleştirip bilgisayarı yeniden başlattık.
* **WSL 2 Ayarı:** `wsl --install` komutuyla Linux alt sistemini kurduk ve Docker Engine'i çalışır (`Engine running`) duruma getirdik.

---

### 2. Dockerfile & Bağımlılık Onarımları

* **Playwright Bağımlılığı:** `requirements.txt` dosyasına eksik olan `playwright` paketini ekledik.
* **Dockerfile Güncellemesi:** Komut hatasını çözmek için bağımlılık yüklemesini `python -m playwright install --with-deps chromium` şeklinde yapılandırdık.

---

### 3. İmaj Derleme (Build)

* **Image Generation:** `docker build -t pricinghub .` komutuyla Chromium ve Python ortamı dahil tüm katmanları hatasız bir şekilde derledik ve `pricinghub:latest` imajını oluşturduk.

---

> **Son Durum:** Projenin tüm Docker altyapısı ve bağımlılıkları problemsiz bir şekilde yayına hazır hale getirildi.

### 2026-11-05 (gün 15)
 Docker Compose Yapılandırması ve Syntax Düzeltmesi:

pricinghub projesi için docker-compose.yml dosyası oluşturuldu.

Dosyadaki volummes: yazım hatası ve YAML girinti/mapping hatası giderildi; servis bağıntıları doğru hizalamayla standart hale getirildi.

Container Ayağa Kaldırma ve Sağlık Kontrolü:

docker compose up -d --build komutu çalıştırılarak pricinghub-app-1 container'ı hatasız şekilde derlendi ve başlatıldı.

Invoke-WebRequest ile http://localhost:8000/docs endpoint'ine istek atıldı; 200 OK yanıtı ve Uvicorn sunucu doğrulaması alındı.

SQLite Volume Kalıcılık (Persistence) Testi:

Yerel ./data dizini container içerisindeki /app/data dizinine volume olarak bağlandı.

docker compose down komutuyla container tamamen kaldırıldı.

docker compose up -d komutuyla tekrar ayağa kaldırıldığında veritabanı dosyasının ve verilerin silinmeyip kalıcı olarak korunduğu (volume persistence) doğrulandı.