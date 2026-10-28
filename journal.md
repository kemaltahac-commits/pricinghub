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