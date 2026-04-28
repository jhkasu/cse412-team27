# NutriCompare - CSE 412 Group 27

Browse, search, and compare USDA food nutrition data.

**Team:** Dakota Burke · Jooho Kim · Rishith Mody

## Run it

Postgres must be running locally first (`pg_isready` should say "accepting connections").

```bash
cd backend

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

## Run with Docker

From the project root:

```bash
docker compose up --build
```

This starts:
- `db` (Postgres on `localhost:5432`)
- `backend` (FastAPI app on `http://127.0.0.1:5001`)

Startup flow:
1. Wait for Postgres to become healthy
2. Run `setup_db.py` to (re)create and seed `nutricompare`
3. Start Uvicorn on port `5001`

Stop everything:

```bash
docker compose down
```

Reset DB volume completely:

```bash
docker compose down -v
```

## Files
- `ddl/` — schema, data, queries (Phase 1, 2)
- `backend/` — FastAPI app + templates/static (Phase 3)
