# NutriCompare - CSE 412 Group 27

A web app to browse, search, and compare nutritional information for foods
sourced from the USDA FoodData Central database.

## Team
- Dakota Burke
- Jooho Kim
- Rishith Mody

## Repo Structure
- `ddl/schema.sql` — table definitions (Phase 1)
- `ddl/data.sql` — generated INSERT statements from USDA API (Phase 2)
- `ddl/generate_data.py` — script that calls the USDA API and writes `data.sql`
- `ddl/queries.sql` — sample SQL queries (Phase 3)
- `frontend/` — Flask web application (Phase 4)

## Setup (Frontend)

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally on port 5432

### 1. Make sure Postgres is running
```bash
pg_isready          # should print "accepting connections"
# macOS Homebrew users:  brew services start postgresql@15
```

### 2. Install Python dependencies
```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Build the database
This creates a fresh `nutricompare` database and loads schema + data:
```bash
python setup_db.py
```

Expected output:
```
Recreated database 'nutricompare'.
Schema loaded from schema.sql.
Data loaded from data.sql.
  food: 1911
  food_category: 158
  food_nutrient: 133306
```

### 4. Start the server
```bash
python app.py
```
Open http://127.0.0.1:5001 in your browser.

### Connection settings
Defaults assume a local Postgres install with the current OS user as the
superuser (typical for Homebrew on macOS). Override with environment
variables if needed:
```bash
PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=secret \
PGDATABASE=nutricompare python app.py
```

## Regenerating the dataset (optional)
`ddl/data.sql` is committed, so you don't need to run this — but if you
want fresh data from the USDA API:
```bash
cd ddl
python generate_data.py    # rewrites data.sql
```
Then re-run `frontend/setup_db.py`.
