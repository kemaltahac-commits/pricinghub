## 2026-10-26

Ne yaptım: price_history şemaları + POST/GET /products/{id}/prices endpoint'leri. TestClient ile 6/6 test geçti (201, 201, sıra [119.9, 129.9], 404, 404).
Ne takıldım: app/main.py ve app/schemas.py'yi komple yeniden yazıp içeriği iki kez kaybettim. Uvicorn --reload child process ölünce port "Listen" görünüyor ama bağlantı reddediyor — 40 dk kaybettim.
Yarın ne: scraper iskeleti (Playwright, tek site, tek ürün).