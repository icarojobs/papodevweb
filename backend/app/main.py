"""Ponto de entrada da aplicação: FastAPI + Socket.IO."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health
from app.core.config import get_settings
from app.db.migrations import run_migrations
from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.db.seed import run_seeders
from app.realtime.socket import build_asgi_app


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    database = get_database()
    await run_migrations(database)
    # Seeders só em desenvolvimento — evita credenciais conhecidas em produção.
    if not get_settings().is_production:
        await run_seeders(database)
    yield
    await close_mongo_connection()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Papo Dev Web API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    return app


fastapi_app = create_app()

# Aplicação ASGI final exposta ao Uvicorn (FastAPI + Socket.IO).
app = build_asgi_app(fastapi_app)
