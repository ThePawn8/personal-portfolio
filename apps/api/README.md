# Portfolio API

FastAPI service that serves portfolio project content and receives contact messages.
Design and rationale: [../../docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) § 6.

## Running

```bash
uv sync                                                    # install, locked
uv run uvicorn portfolio_api.main:app --reload --port 8000
```

Interactive contract: <http://localhost:8000/docs>

## Quality gates

```bash
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy src tests        # strict typing
uv run pytest                # tests + coverage gate (80 %)
```

These are exactly the commands CI runs. From the repository root, `npm run check:api` runs
all four.

## Layout

```
src/portfolio_api/
├── main.py       Application factory and lifespan
├── core/         Settings, logging, error contract, rate limiting   (T-101)
├── models/       Beanie documents — persistence shape                (T-102)
├── schemas/      Pydantic models — wire shape
├── repositories/ Every MongoDB query lives here                      (T-103)
├── services/     Business rules                                      (T-103, T-105)
├── routers/      HTTP only: parse, delegate, serialise
└── seed/         content/ → validated documents → idempotent upsert  (T-107)
```

The dependency direction is `routers → services → repositories → models`. Nothing above
`repositories` imports the MongoDB driver.
