# Shortly

A URL shortener with click analytics, built with FastAPI, PostgreSQL, and Redis.

## Architecture

The application follows a layered architecture: thin API routes delegate to a
service layer that contains all business logic, with PostgreSQL as the persistent
store and Redis as a cache-aside layer for fast URL lookups.

On the write path, `POST /shorten` generates a cryptographically random short
code, stores the URL mapping in Postgres, and caches it in Redis. On the read
path, `GET /{code}` checks Redis first (cache hit avoids a database query),
records click analytics, and returns a 307 redirect. A 307 (temporary) is used
instead of 301 (permanent) so browsers always hit the server, preserving
complete analytics.

## Tech Stack

- **FastAPI** — async Python web framework with auto-generated OpenAPI docs
- **PostgreSQL 16** — persistent storage for URLs and click events
- **Redis 7** — caching layer for fast URL resolution
- **SQLAlchemy 2.0** — ORM with modern typed column syntax
- **Docker Compose** — containerized local development
- **Pydantic v2** — request/response validation

## Quick Start

```bash
git clone https://github.com/JohnnyCannelloni/shortly.git
cd shortly
docker-compose up --build
```

The API is live at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shorten` | Create a shortened URL |
| GET | `/{short_code}` | Redirect to original URL |
| GET | `/stats/{short_code}` | Get click analytics |
| GET | `/health` | Health check |

## Usage

```bash
# Shorten a URL
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path"}'

# Check analytics
curl http://localhost:8000/stats/YOUR_CODE
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
shortly/
├── app/
│   ├── api/routes.py          # HTTP endpoint handlers
│   ├── core/
│   │   ├── config.py          # Settings via pydantic-settings
│   │   ├── database.py        # SQLAlchemy engine and session
│   │   └── redis.py           # Redis client
│   ├── models/url.py          # SQLAlchemy models (URL, Click)
│   ├── schemas/url.py         # Pydantic request/response schemas
│   ├── services/url_service.py # Business logic layer
│   └── main.py                # FastAPI app entry point
├── tests/
│   ├── conftest.py            # Test fixtures (fake Redis)
│   └── test_api.py            # API endpoint tests
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```