from datetime import timedelta
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import Base, engine, get_db
from app.models import Product, PriceHistory
from app.schemas import (
    ProductCreate,
    ProductRead,
    PriceHistoryCreate,
    PriceHistoryRead,
    PriceStats,
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
@app.get("/products/{product_id}/stats", response_model=PriceStats)
def product_stats(product_id: int, db: Session = Depends(get_db)):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")

    records, min_p, max_p, avg_p = (
        db.query(
            func.count(PriceHistory.id),
            func.min(PriceHistory.price),
            func.max(PriceHistory.price),
            func.avg(PriceHistory.price),
        )
        .filter(PriceHistory.product_id == product_id)
        .one()
    )

    latest = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at.desc(), PriceHistory.id.desc())
        .first()
    )

    change_30d_pct = None
    if latest:
        old = (
            db.query(PriceHistory)
            .filter(
                PriceHistory.product_id == product_id,
                PriceHistory.scraped_at <= latest.scraped_at - timedelta(days=30),
            )
            .order_by(PriceHistory.scraped_at.desc(), PriceHistory.id.desc())
            .first()
        )
        if old:
            change_30d_pct = ((latest.price - old.price) / old.price) * 100

    return PriceStats(
        product_id=product_id,
        records=records,
        min_price=min_p,
        max_price=max_p,
        avg_price=avg_p,
        latest_price=latest.price if latest else 0.0,
        change_30d_pct=change_30d_pct,
    )