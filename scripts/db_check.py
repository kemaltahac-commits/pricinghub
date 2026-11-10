import sqlite3

conn = sqlite3.connect("/app/data/pricinghub.db")
print(conn.execute("SELECT COUNT(*) FROM price_history").fetchone())