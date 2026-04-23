# NutriCompare - CSE 412 Group 27

Browse, search, and compare USDA food nutrition data.

**Team:** Dakota Burke · Jooho Kim · Rishith Mody

## Run it

Postgres must be running locally first (`pg_isready` should say "accepting connections").

```bash
git checkout flask-frontend
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_db.py
uvicorn app:app --port 5001 --reload
```

Open http://127.0.0.1:5001 (and http://127.0.0.1:5001/docs for the Swagger UI).

## Files
- `ddl/` — schema, data, queries (Phase 1–3)
- `frontend/` — FastAPI app (Phase 4)
