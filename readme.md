# PricingHub

Trendyol'daki üç telefonun fiyatını günde bir kez toplayıp SQLite'a yazan, fiyat hareketini SQL ile sorgulanabilir hale getiren fiyat izleme sistemi.

## Problem

Trendyol ürün sayfası fiyatı DOM'a basmıyor. Sayfadaki 100'den fazla `data-testid` değerinin hiçbirinde fiyat yok — `add-to-cart-button`, `product-info`, `merchant-info` var ama fiyat yok. Fiyat yalnızca sayfaya gömülen schema.org JSON-LD bloğunda duruyor.

Bu yüzden selector tabanlı scraper kırılıyor: sayfa 662 KB HTML dönse, başlık doğru gelse bile `[data-testid="current-price"]` hiç var olmuyor ve 20 saniye timeout'a düşüyor. Sayfa "boş" değil, sadece fiyat orada değil.

## Çözüm

Fiyat, `<script type="application/ld+json">` içindeki `Product` nesnesinin `offers.price` alanından okunuyor:

```json
"offers": {
  "@type": "Offer",
  "priceCurrency": "TRY",
  "price": "13849.00",
  "availability": "https://schema.org/InStock"
}
```

JSON-LD bir schema.org standardı. Trendyol arayüzü değişse de ayakta kalıyor, çünkü Google'ın zengin sonuçları buna bağlı. Selector kırılganlığı ortadan kalkıyor.

Fiyat iki formatta geliyor: DOM'da `13.849,00` (TR), JSON-LD'de `13849.00`. Tek bir `parse_price` ikisini de tanıyor; birden fazla sayı görürse tahmin etmiyor, hata veriyor. Bu kontrol olmadan `13.849,00` değeri `1384900.0` olarak kaydedilir — sessiz, fark edilmesi zor bir hata.

## Mimari

```
Windows Task Scheduler (09:00)
        │
        ▼
docker compose run --rm app python -m scripts.scrape_all
        │
        ├── scrape_one.fetch()        Playwright + Chromium (headless)
        │       ├── JSON-LD parse     birincil yol
        │       └── DOM selector      yedek yol
        │
        ├── retry: 3 deneme, artan bekleme, rastgele user-agent
        ├── ürünler arası 8-15s rastgele bekleme
        │
        ▼
SQLite (data/pricinghub.db)
        ├── products
        └── price_history
        │
        ▼
data/scrape.log
```

## Ölçülmüş Sonuç

24 Kasım 2026, manuel çalıştırma:

```
2026-11-24 06:45:40 | === scrape basladi ===
2026-11-24 06:45:42 | BASARILI: Xiaomi REDMI A7 Pro 4GB+128GB Siyah | 10599.0
2026-11-24 06:45:42 | urunler arasi 10s bekleme
2026-11-24 06:45:54 | BASARILI: Xiaomi Redmi 13C 8 GB RAM 256 GB Lacivert | 13849.0
2026-11-24 06:45:54 | urunler arasi 14s bekleme
2026-11-24 06:46:10 | BASARILI: Samsung Galaxy S26FE 8/256 GB Grafit Gri | 44839.0
2026-11-24 06:46:10 | === bitti: 3 basarili, 0 basarisiz ===
```

Üç ürün, 30 saniye, sıfır hata. Sürenin çoğu ürünler arası kasıtlı bekleme — Trendyol'a art arda istek atmamak için.

## Analiz

Fiyat geçmişi SQL ile sorgulanabilir. Günlük fiyat farkı:

```sql
WITH sirali AS (
    SELECT
        product_id,
        price,
        scraped_at,
        LAG(price) OVER (PARTITION BY product_id ORDER BY scraped_at) AS onceki_fiyat
    FROM price_history
)
SELECT
    p.name,
    s.scraped_at,
    s.price,
    s.onceki_fiyat,
    s.price - s.onceki_fiyat AS fark_tl
FROM sirali s
JOIN products p ON p.id = s.product_id
WHERE s.onceki_fiyat IS NOT NULL
ORDER BY ABS(s.price - s.onceki_fiyat) DESC;
```

SQLite'ta pencere fonksiyonu doğrudan `WHERE` içinde kullanılamıyor; `LAG()` sonucu ancak dış sorguda filtrelenebiliyor, bu yüzden iki katmanlı subquery.

## Kurulum

```bash
docker compose build
docker compose run --rm app python -m scripts.scrape_all
```

Otomatik çalıştırma (Windows):

```bat
schtasks /create /tn "PricingHubScrape" /tr "cmd /c cd /d C:\Users\kemal\Desktop\pricinghub && docker compose run --rm app python -m scripts.scrape_all" /sc daily /st 09:00 /f
```

## Proje Yapısı

```
pricinghub/
├── app/
│   ├── db.py           SQLAlchemy session
│   └── models.py       Product, PriceHistory
├── scripts/
│   ├── scrape_one.py   fetch, parse_price, normalize_url
│   ├── scrape_all.py   retry + log + DB yazımı
│   └── db_check.py     kayıt sayısı kontrolü
├── data/
│   ├── pricinghub.db   SQLite (Docker volume)
│   └── scrape.log
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Sınırlar

Üç ürün, tek kaynak (Trendyol), tek ülke. JSON-LD satış fiyatını veriyor, üstü çizili liste fiyatını değil. Kampanya dönemi ile normal dönem arasındaki geçişler seride gerçek fiyat hareketi olarak görünür, ayrıca işaretlenmiyor.
