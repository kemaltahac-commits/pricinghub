from fastapi import FastAPI

from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PricingHub")


@app.get("/health")
def health():
    return {"status": "ok"}