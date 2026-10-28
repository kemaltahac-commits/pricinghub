from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Product, PriceHistory
from app.schemas import (
    ProductCreate,
    ProductRead,
    PriceHistoryCreate,
    PriceHistoryRead,
)

app = FastAPI(title="PricingHub")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/products", response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.url == payload.url).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Bu URL zaten kayitli")

    product = Product(name=payload.name, url=payload.url, source=payload.source)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.desc()).all()


@app.post(
    "/products/{product_id}/prices",
    response_model=PriceHistoryRead,
    status_code=201,
)
def create_price(
    product_id: int,
    payload: PriceHistoryCreate,
    db: Session = Depends(get_db),
):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")

    row = PriceHistory(product_id=product_id, price=payload.price)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/products/{product_id}/prices", response_model=list[PriceHistoryRead])
def list_prices(product_id: int, db: Session = Depends(get_db)):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at.desc(), PriceHistory.id.desc())
        .all()
    )