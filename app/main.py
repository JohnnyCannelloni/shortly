from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.database import Base, get_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Shortly",
    description="A fast URL shortener with clock analytics.",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(router)
