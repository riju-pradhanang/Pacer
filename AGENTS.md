# AGENTS.md: rules for AI assistants working on Pacer

## Project
Pacer is a multi-tenant rate limiting API gateway. One codebase, three processes:
- gateway (data plane): authenticates consumers, enforces limits, proxies traffic
- control (admin API): tenants, users, upstreams, routes, rules, keys, analytics
- worker: consumes usage events, writes rollups, cleans up
Read docs/prd.md and docs/build-guide.md before changing behaviour.

## Stack (do not substitute or add libraries without asking)
Python 3.12, FastAPI, uvicorn, httpx, SQLAlchemy 2.0 async with asyncpg, Alembic,
Redis 7 via redis-py asyncio, Pydantic v2 and pydantic-settings, structlog,
prometheus-client, PyJWT, argon2-cffi, pytest, pytest-asyncio, testcontainers,
Hypothesis, ruff, mypy, uv.

## Layering (strict)
router -> service -> repository
- Routers: HTTP only (parse, authorise, call a service, return a schema).
- Services: business rules and transactions. No HTTP types. Services commit.
- Repositories: all SQL. They flush, never commit. Every method on a tenant-owned
  table takes tenant_id and filters by it.

## Hard rules
1. Limiter logic is a Redis Lua script. Never read then write limiter state from Python.
2. Lua scripts use redis.call('TIME'). Never use the application clock for limits.
3. All I/O is async. No requests, psycopg2, time.sleep or blocking file I/O in handlers.
   CPU-heavy work (password hashing) goes through asyncio.to_thread.
4. Every query on tenant-owned tables filters by tenant_id.
5. Never log secrets, full API keys, passwords, tokens or request bodies.
6. No SQL built with string formatting. Use bound parameters.
7. Configuration comes only from app.core.settings.Settings. No os.environ elsewhere.
8. Every new endpoint needs: a request schema, a response schema, a permission check,
   a test, and an OpenAPI summary.
9. Errors use RFC 9457 problem details through AppError. No bare HTTPException.
10. If a requirement is unclear, ask. Do not guess.

## Commands
uv run ruff check . && uv run ruff format --check .
uv run mypy app
uv run pytest -q
docker compose up -d postgres redis
uv run alembic upgrade head

## Definition of done for any task
Tests written and passing, ruff and mypy clean, migration included if the schema changed,
no secrets in code, metrics and logs added where the task says so.