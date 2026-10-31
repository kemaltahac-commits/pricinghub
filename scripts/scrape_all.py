from scripts.scrape_one import fetch, parse_price, normalize_url, ScrapeError, SOURCE
from app.db import SessionLocal
from app.models import Product, PriceHistory

URLS = [
    "https://www.trendyol.com/xiaomi/redmi-a7-pro-4gb-128gb-siyah-xiaomi-turkiye-garantili-p-1175413438",
    "https://www.trendyol.com/cep-telefonu-x-c103498",
]

basarili = 0
basarisiz = 0

for raw_url in URLS:
    try:
        title, raw = fetch(raw_url)
        price = parse_price(raw)
        url = normalize_url(raw_url)
        
        with SessionLocal() as db:
            product = db.query(Product).filter(Product.url == url).first()
            if product is None:
                product = Product(name=title, url=url, source=SOURCE)
                db.add(product)
                db.flush()
            db.add(PriceHistory(product_id=product.id, price=price))
            db.commit()
            
        basarili += 1
        print(f"BASARILI: {title}")
    except (ScrapeError, ValueError) as e:
        basarisiz += 1
        print(f"HATA: {e}")

print(f"Toplam: {basarili} basarili, {basarisiz} basarisiz")