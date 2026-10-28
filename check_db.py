from sqlalchemy import inspect
from app.db import engine, Base
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

print("DB:", engine.url)
print("Tablolar:", inspect(engine).get_table_names())