# Adding Challenge 11

## Structure

Create a new directory under `challenges/11-your-name/` with:

- `app/backend/main.py`
- `app/frontend/index.html`
- `app/frontend/styles.css`
- `app/frontend/app.js`
- `app/data/`
- `tests/`
- `Dockerfile`
- `.dockerignore`
- `challenge.yml`
- `README.md`
- `WRITEUP.md`

## Backend Pattern

Use `shared.common.challenge.ChallengeRuntime` unless the challenge truly needs a custom app factory.

Minimum pieces:

- `build_initial_state()`
- `bootstrap_payload(state)`
- `handle_chat(state, message)`
- Optional `handle_upload(state, file)`
- Optional `extra_routes(app, store)`

## LLM Usage

- Use `shared.deepseek.client.DeepSeekClient`
- Keep prompts short and targeted
- Use `mock_handler=` in tests
- Use `LLM_PROVIDER=mock` for CI

## Tool Challenges

Use `shared.common.agent.run_tool_agent` and keep tool authorization flaws narrow and explicit. The model may choose arguments; the backend should illustrate the real mistake.

## Tests

Add:

- `tests/config.py` with `EXPECTED_FLAG` and `SOLUTION`
- `tests/__init__.py`
- The five standard wrapper tests

The exploit path must go through the real routes, not direct state mutation.

## Frontend Expectations

- Real seeded content
- Loading, error, empty, and disabled states
- Responsive layout
- Distinct visual identity from existing challenges

## Docs

- Player-facing `README.md`
- Instructor-facing `WRITEUP.md`
- Update `DESIGN.md`, root `README.md`, `docs/ADMIN.md`, `docker-compose.yml`, `reverse-proxy/nginx.conf`, and the scripts that enumerate all challenges

## Security Boundaries

Never expose infrastructure secrets, shell access, or host-level attack paths. Keep the vulnerability inside the intended AI application workflow.
