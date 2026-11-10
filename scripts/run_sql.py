import sqlite3, sys, pathlib

sql_file = pathlib.Path(sys.argv[1])
conn = sqlite3.connect("pricinghub.db")
cur = conn.execute(sql_file.read_text())
cols = [d[0] for d in cur.description]
print(" | ".join(cols))
for row in cur.fetchall():
    print(" | ".join(str(v) for v in row))