"""Ponto de entrada da aplicação: FastAPI + Socket.IO."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, conversations, health, media, users
from app.core.config import get_settings
from app.db.migrations import run_migrations
from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.db.seed import run_seeders
from app.jobs.scheduler import build_scheduler
from app.realtime.socket import build_asgi_app
from app.services.factory import build_media_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    database = get_database()
    await run_migrations(database)
    # Garante o bucket de mídia (idempotente) para uploads de imagens/áudio/arquivos.
    await build_media_service().ensure_bucket()
    # Seeders só em desenvolvimento — evita credenciais conhecidas em produção.
    if not get_settings().is_production:
        await run_seeders(database)
    # Job diário de retenção (00:01): expurga histórico/mídia com mais de 7 dias.
    scheduler = build_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
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
    app.include_router(users.router)
    app.include_router(conversations.router)
    app.include_router(media.router)
    app.include_router(admin.router)
    return app


fastapi_app = create_app()

# Aplicação ASGI final exposta ao Uvicorn (FastAPI + Socket.IO).
app = build_asgi_app(fastapi_app)
