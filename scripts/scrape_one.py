from playwright.sync_api import sync_playwright

URL = "https://www.trendyol.com/xiaomi/redmi-a7-pro-4gb-128gb-siyah-xiaomi-turkiye-garantili-p-1175413438?boutiqueId=689770&merchantId=968"


def parse_price(text: str) -> float:
    cleaned = text.replace("TL", "").replace("₺", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    return float(cleaned)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="tr-TR")
        page.goto(URL, wait_until="domcontentloaded", timeout=45000)

        page.wait_for_selector('[data-testid="current-price"]', timeout=15000)

        title = page.title()
        raw = page.locator('[data-testid="current-price"]').first.inner_text().strip()
        price = parse_price(raw)

        print("TITLE:", title)
        print("RAW  :", repr(raw))
        print("PRICE:", price, type(price).__name__)

        browser.close()


if __name__ == "__main__":
    main()