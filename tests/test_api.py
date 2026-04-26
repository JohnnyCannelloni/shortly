import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

Base.metadata.create_all(bind=TEST_ENGINE)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_shorten_url():
    resp = client.post("/shorten", json={"url": "https://example.com/some/long/path"})
    assert resp.status_code == 201
    data = resp.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/some/long/path"
    assert data["short_url"].endswith(data["short_code"])


def test_shorten_invalid_url():
    resp = client.post("/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 422


def test_redirect():
    create_resp = client.post("/shorten", json={"url": "https://example.com/redirect-test"})
    code = create_resp.json()["short_code"]

    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/redirect-test"


def test_redirect_not_found():
    resp = client.get("/nonexistent", follow_redirects=False)
    assert resp.status_code == 404


def test_stats():
    create_resp = client.post("/shorten", json={"url": "https://example.com/stats-test"})
    code = create_resp.json()["short_code"]

    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)

    stats_resp = client.get(f"/stats/{code}")
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    assert data["click_count"] == 3
    assert len(data["recent_clicks"]) == 3


def test_stats_not_found():
    resp = client.get("/stats/nonexistent")
    assert resp.status_code == 404
    