# PartyUp.gg — Cross-Game LFG MVP (FastAPI + HTMX)

## Run (Docker)
```bash
cp .env.example .env
docker compose up --build
# Open http://localhost (nginx) or http://localhost:8000 (FastAPI)
```

## Run (Local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/partyup
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## API Endpoints (sample)
- `POST /auth/register {email,password,display_name}` -> JWT
- `POST /auth/login {email,password}` -> JWT
- `GET /listings?game=&server=&language=&availability=&tags=raid,keys&q=`
- `POST /listings` (JWT) -> create listing
- `GET /matching/suggestions` (JWT) -> scored suggestions
- `POST /messages` (JWT) -> send DM
- `GET /messages/thread/{user_id}` (JWT) -> message history
- `POST /reports` (JWT) -> report listing/message

## Why JSONB for `game_specific`?
MVP speed & flexibility. We index it with GIN for selective queries and keep the core fields normalized.

## v2 Ideas
- Vector similarity for profile-to-profile similarity (pgvector/FAISS)
- Notifications & mobile PWA
- Guild/Clan org accounts
- Advanced moderation (ML toxicity)
