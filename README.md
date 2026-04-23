# NutriCompare - CSE 412 Group 27

Browse, search, and compare USDA food nutrition data.

**Team:** Dakota Burke · Jooho Kim · Rishith Mody

## Run it

Postgres must be running locally first (`pg_isready` should say "accepting connections").

```bash
cd frontend

# create project-local Python env
python3 -m venv .venv

# activate it
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# create DB + fetch ~2000 foods from USDA API (~1 min)
python setup_db.py

# start server at http://127.0.0.1:5001
uvicorn app:app --port 5001 --reload
```

Open http://127.0.0.1:5001 (and http://127.0.0.1:5001/docs for the Swagger UI).

## Files
- `ddl/` — schema, data, queries (Phase 1–3)
- `frontend/` — FastAPI app (Phase 4)
