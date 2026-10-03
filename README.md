# Job Application Tracker

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for the Swagger UI.

## Optional: Postgres
```bash
docker compose up -d db
# then set DATABASE_URL to the Postgres line in .env
```
