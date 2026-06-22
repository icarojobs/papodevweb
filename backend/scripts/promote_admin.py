"""Cria/promove (ou revoga) um administrador pelo e-mail.

Resolve o "bootstrap" do primeiro admin em produção: como o cadastro exige
confirmação por e-mail (que depende do SMTP a ser configurado no /admin), o
primeiro admin precisa ser criado já ATIVO por aqui.

Uso (dentro do container backend):
    # promove um usuário existente a admin (e o ativa, se ainda não estiver)
    python -m scripts.promote_admin <email>

    # cria um admin já ativo (bootstrap do primeiro admin)
    python -m scripts.promote_admin <email> --password 'SENHA' --name 'Nome'

    # revoga o admin de um usuário existente
    python -m scripts.promote_admin <email> --revoke

Idempotente: rodar de novo não causa efeito colateral.
"""

import argparse
import asyncio
import logging
import sys

from app.core.security import hash_password
from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.repositories.user_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def promote(
    email: str, *, revoke: bool = False, password: str | None = None, name: str | None = None
) -> int:
    await connect_to_mongo()
    try:
        repository = UserRepository(get_database())
        user = await repository.get_by_email(email)

        if revoke:
            if user is None:
                logger.error("Usuário '%s' não encontrado.", email)
                return 1
            await repository.set_admin(user.id, is_admin=False)
            logger.info("Acesso admin revogado para '%s'.", email)
            return 0

        if user is None:
            if not password:
                logger.error(
                    "Usuário '%s' não existe. Informe --password para criar um admin.", email
                )
                return 1
            created = await repository.create(
                full_name=name or email,
                email=email,
                hashed_password=hash_password(password),
                is_active=True,  # admin de bootstrap nasce ativo (sem confirmação).
            )
            await repository.set_admin(created.id, is_admin=True)
            logger.info("Admin '%s' criado e ativado.", email)
            return 0

        # Usuário existente: promove e garante que está ativo (pode logar).
        await repository.set_admin(user.id, is_admin=True)
        await repository.activate_user(user.id)
        if password:
            await repository.update_password(user.id, hash_password(password))
        logger.info("Acesso admin concedido para '%s'.", email)
        return 0
    finally:
        await close_mongo_connection()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria/promove/revoga admin de um usuário.")
    parser.add_argument("email", help="E-mail do usuário")
    parser.add_argument("--revoke", action="store_true", help="Revoga o acesso admin")
    parser.add_argument("--password", help="Senha (cria o usuário se não existir; ou redefine)")
    parser.add_argument("--name", help="Nome completo (ao criar)")
    args = parser.parse_args()
    sys.exit(
        asyncio.run(
            promote(args.email, revoke=args.revoke, password=args.password, name=args.name)
        )
    )


if __name__ == "__main__":
    main()
