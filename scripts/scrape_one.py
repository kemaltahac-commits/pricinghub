from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError, sync_playwright

from app.db import SessionLocal
from app.models import Product, PriceHistory

URL = "https://www.trendyol.com/xiaomi/olmayan-urun-p-999999999"
SOURCE = "trendyol"


class ScrapeError(Exception):
    """Beklenen scraper hatalari. Beklenmeyenlerden ayri tutulur."""
    pass


def parse_price(text: str) -> float:
    cleaned = "".join(ch for ch in text if ch.isdigit() or ch in ".,")
    if not cleaned:
        raise ValueError(f"fiyat bulunamadi: {text!r}")
    return float(cleaned.replace(".", "").replace(",", "."))


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}{parts.path}"


def fetch(url: str) -> tuple[str, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            page = browser.new_page(locale="tr-TR")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_selector('[data-testid="current-price"]', timeout=20000)

            title = page.title().replace(" - Fiyatı", "").strip()
            raw = page.locator('[data-testid="current-price"]').first.inner_text().strip()
            return title, raw
        except PlaywrightError as e:
            raise ScrapeError(f"sayfa alinamadi: {url}") from e
        finally:
            browser.close()


def main() -> int:
    try:
        title, raw = fetch(URL)
        price = parse_price(raw)
    except (ScrapeError, ValueError) as e:
        print(f"HATA: {e}")
        return 1

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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())