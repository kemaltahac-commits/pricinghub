from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from app.db import SessionLocal
from app.models import Product, PriceHistory

URL = "https://www.trendyol.com/xiaomi/redmi-a7-pro-4gb-128gb-siyah-xiaomi-turkiye-garantili-p-1175413438?boutiqueId=689770&merchantId=968"
SOURCE = "trendyol"


def parse_price(text: str) -> float:
    cleaned = text.replace("TL", "").replace("₺", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    return float(cleaned)


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}{parts.path}"


def fetch(url: str) -> tuple[str, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="tr-TR")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector('[data-testid="current-price"]', timeout=20000)

        title = page.title().replace(" - Fiyatı", "").strip()
        raw = page.locator('[data-testid="current-price"]').first.inner_text().strip()

        browser.close()
    return title, raw


def main():
    title, raw = fetch(URL)
    price = parse_price(raw)
    url = normalize_url(URL)

    print(f"TITLE: {title}")
    print(f"RAW  : {raw!r} -> {price}")

    with SessionLocal() as db:
        product = db.query(Product).filter(Product.url == url).first()

        if product is None:
            product = Product(name=title, url=url, source=SOURCE)
            db.add(product)
            db.flush()
            print(f"YENI URUN  : id={product.id}")
        else:
            print(f"MEVCUT URUN: id={product.id}")

        row = PriceHistory(product_id=product.id, price=price)
        db.add(row)
        db.commit()
        db.refresh(row)

        print(
            f"PRICE ROW  : id={row.id} product_id={row.product_id} "
            f"price={row.price} currency={row.currency} scraped_at={row.scraped_at}"
        )


if __name__ == "__main__":
    main()