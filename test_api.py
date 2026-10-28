from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 1) urun olustur
r = client.post("/products", json={
    "name": "Test Urun",
    "url": "https://example.com/p/test-1",
    "source": "trendyol",
})
print("1) POST /products ->", r.status_code, r.json())
pid = r.json()["id"]

# 2) 129.90
r = client.post(f"/products/{pid}/prices", json={"price": 129.90})
print("2) 129.90 ->", r.status_code, r.json())

# 3) 119.90
r = client.post(f"/products/{pid}/prices", json={"price": 119.90})
print("3) 119.90 ->", r.status_code, r.json())

# 4) gecmis
r = client.get(f"/products/{pid}/prices")
data = r.json()
print("4) GET prices ->", r.status_code, "kayit:", len(data), "sira:", [x["price"] for x in data])

# 5) olmayan urun GET
r = client.get("/products/9999/prices")
print("5) GET 9999 ->", r.status_code)

# 6) olmayan urun POST
r = client.post("/products/9999/prices", json={"price": 1})
print("6) POST 9999 ->", r.status_code)