# Local startup
Python 3.12 and Node 24; PostgreSQL 17 via Docker. Keep .env out of Git.
From repository root:
```sh
python3.12 -m venv .venv
.venv/bin/pip install -r backend/requirements-lock.txt
cp .env.example .env
# Set a random JWT_SECRET, leave APP_ENV=development and MODEL_MODE=baseline.
docker compose up -d db
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/python -m app.db.seed
../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 5050
```
In separate terminals:
```sh
cd backend
../.venv/bin/python -m app.workers.runner
```
```sh
cd frontend
npm ci
npm run dev -- --port 5173
```
Open http://localhost:5173. Synthetic reviewer@revenueops.example password
Demo-finance-2026!; admin/analyst/viewer use the corresponding email prefix and same
synthetic-only password. Demo seed is idempotent and refuses production.

If defaults are occupied, preserve existing processes. Use API port 5051 and Vite 5174:
CORS_ORIGINS must include http://127.0.0.1:5174 and http://localhost:5174.
REVENUEOPS_API_URL=http://127.0.0.1:5051 npm run dev -- --port 5174.
API_PORT/WEB_PORT set published Compose ports. DATABASE_URL controls DB connectivity.
The implementation session used 5051/5174 and DB 55433.

Container startup after environment configuration:
```sh
docker compose build
docker compose up -d
# Seed only after API migrations have completed.
docker compose exec api python -m app.db.seed
```
Web uses a same-origin reverse proxy. API and worker share the same schema/database;
web assets contain no server secrets. Preserve pgdata; never use down -v for ordinary stops.

## Local model
Ollama must already run, with llama3.2:3b installed. The implementation verified its
advertised completion/tools capabilities and a real small-case crew, not general accuracy.
Set MODEL_MODE=ollama, OLLAMA_URL=http://localhost:11434 for native processes or
http://host.docker.internal:11434 for Docker Desktop; OLLAMA_MODEL=llama3.2:3b.
Restart API and worker. Only configured local hostnames are permitted. Native OpenAI
compatibility uses a local placeholder key (not an OpenAI account or billable request).
Normal exact matches bypass inference. Exception buttons enqueue jobs; inspect Agent
workspace and manually refresh for recorded stages/errors. Baseline records not_executed.
One larger initial case timed out; a smaller two-agent case completed. Expect variable
latency on a MacBook Air. Do not mistake capability support for reliable large-case output.

Optional hosted mode uses CrewAI native OpenAI provider, HOSTED_ENABLED=true and
HOSTED_MODEL=openai/<approved-model>, with provider API key supplied outside Git.
This is explicit operator activation for billable work; it was not enabled or tested here.
