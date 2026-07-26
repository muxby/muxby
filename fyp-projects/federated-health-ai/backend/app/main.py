"""FastAPI application entrypoint."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, hospitals, misc, models, predictions, rounds, ws
from app.core.config import get_settings
from app.db.session import Base, engine


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="federated-health-ai",
        description="Federated learning platform for hospital diagnosis without sharing patient data",
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = APIRouter(prefix="/api")
    api.include_router(auth.router)
    api.include_router(hospitals.router)
    api.include_router(rounds.router)
    api.include_router(models.router)
    api.include_router(predictions.router)
    api.include_router(misc.router)
    api.include_router(ws.router)
    app.include_router(api)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "service": settings.app_name}

    # Alembic owns schema migrations in deployment; create_all keeps
    # zero-config local startup working against a fresh SQLite file.
    Base.metadata.create_all(bind=engine)
    return app


app = create_app()
