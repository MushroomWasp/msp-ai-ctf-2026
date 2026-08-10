# AI Security CTF

AI Security CTF is a ten-challenge repository focused on realistic AI application security failures. Every challenge is an independent FastAPI application with its own frontend, seeded data, deterministic solve condition, Docker image, tests, player README, and instructor writeup.

## Architecture

- Reverse proxy: `nginx`
- Challenge apps: `FastAPI`, `Pydantic`, `httpx`
- LLM provider: DeepSeek OpenAI-compatible API
- State: per-challenge SQLite session store
- Retrieval: lightweight local chunking plus hashed-vector retrieval where needed
- Testing: mock LLM provider in CI, optional live DeepSeek smoke test

## Challenge Table

| # | Name | Application | Concept | Difficulty | Port |
| --- | --- | --- | --- | --- | --- |
| 01 | First Class | Travel perks portal | Direct instruction conflict | Easy | 8101 |
| 02 | Escalation Notes | Support workstation | Sensitive context exposure | Easy | 8102 |
| 03 | Memory Lane | Expense review portal | Conversation memory abuse | Easy / Medium | 8103 |
| 04 | DocuScan | Document review SaaS | Indirect prompt injection | Easy / Medium | 8104 |
| 05 | Orderly | E-commerce storefront | Unsafe tool authorization | Easy / Medium | 8105 |
| 06 | NimbusHR | HR knowledge portal | RAG trust boundary | Easy / Medium | 8106 |
| 07 | HelpHub | Support CRM | Cross-context stored injection | Medium | 8107 |
| 08 | Atlas Analytics | Analytics dashboard | Knowledge poisoning | Medium | 8108 |
| 09 | PatchPanel | IT self-service | Multi-step agent exploitation | Medium | 8109 |
| 10 | Meridian Research | Procurement research desk | Chained AI security failure | Medium / Hard | 8110 |

## DeepSeek Configuration

Root `.env`:

```env
DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

The repository includes `.env.example` with blank API key and never commits the real key.

## Quick Start

```bash
docker compose up -d --build
./scripts/healthcheck.sh
```

Proxy URL:

- `http://127.0.0.1:8180/`

Override the proxy host port if needed:

```bash
REVERSE_PROXY_PORT=8088 docker compose up -d --build
```

Direct challenge URLs:

- `http://127.0.0.1:8101/`
- `http://127.0.0.1:8102/`
- `http://127.0.0.1:8103/`
- `http://127.0.0.1:8104/`
- `http://127.0.0.1:8105/`
- `http://127.0.0.1:8106/`
- `http://127.0.0.1:8107/`
- `http://127.0.0.1:8108/`
- `http://127.0.0.1:8109/`
- `http://127.0.0.1:8110/`

## Make Targets

- `make build`
- `make up`
- `make down`
- `make restart`
- `make logs`
- `make status`
- `make health`
- `make test`
- `make reset`

## Testing

Mock-backed suite:

```bash
./scripts/test-all.sh
```

Optional live provider smoke test:

```bash
./scripts/test-deepseek.sh
```

## Operations

- Reset all sessions: `./scripts/reset-all.sh`
- View container state: `./scripts/status.sh`
- Tail logs: `docker compose logs -f --tail=100`
- Rotate DeepSeek key: update `.env`, then `docker compose up -d --build`
- Change model: update `DEEPSEEK_MODEL` in `.env`

## Resource Notes

- The stack is designed for moderate VPS hosting because model inference stays remote.
- Each challenge uses async request handling and local SQLite state.
- Retrieval stays local and lightweight.
- Rate limiting defaults to 10–15 requests per minute per session depending on challenge.

## Deployment and Authoring Docs

- [Deployment](docs/DEPLOYMENT.md)
- [Admin guide](docs/ADMIN.md)
- [Authoring guide](docs/AUTHORING.md)
