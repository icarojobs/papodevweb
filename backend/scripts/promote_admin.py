"""Concede (ou revoga) acesso administrativo a um usuário pelo e-mail.

Uso (dentro do container backend):
    python -m scripts.promote_admin <email>            # promove a admin
    python -m scripts.promote_admin <email> --revoke   # revoga o admin

Idempotente: rodar de novo não causa efeito colateral.
"""

import argparse
import asyncio
import logging
import sys

from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.repositories.user_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def promote(email: str, *, revoke: bool) -> int:
    await connect_to_mongo()
    try:
        repository = UserRepository(get_database())
        user = await repository.get_by_email(email)
        if user is None:
            logger.error("Usuário com e-mail '%s' não encontrado.", email)
            return 1
        await repository.set_admin(user.id, is_admin=not revoke)
        acao = "revogado" if revoke else "concedido"
        logger.info("Acesso admin %s para '%s'.", acao, email)
        return 0
    finally:
        await close_mongo_connection()


def main() -> None:
    parser = argparse.ArgumentParser(description="Promove/revoga admin de um usuário.")
    parser.add_argument("email", help="E-mail do usuário")
    parser.add_argument("--revoke", action="store_true", help="Revoga o acesso admin")
    args = parser.parse_args()
    sys.exit(asyncio.run(promote(args.email, revoke=args.revoke)))


if __name__ == "__main__":
    main()
