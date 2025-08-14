#!/usr/bin/env bash
set -euo pipefail

# Wait for Postgres
python - <<'PY'
import time, os, psycopg2
host = os.getenv("DATABASE_URL","")
import re
m = re.match(r'postgresql\+psycopg2://(.*?):(.*?)@(.*?):(.*?)/(.*)', host)
if not m:
    print("Invalid DATABASE_URL for readiness check:", host)
    raise SystemExit(1)
user, pwd, host, port, db = m.groups()
for _ in range(60):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db).close()
        break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("Postgres didn't become ready in time")
PY

# Run migrations and seed
alembic upgrade head || true
python -m app.seed || true

# Start the app
uvicorn app.main:app --host 0.0.0.0 --port 8000
