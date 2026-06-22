"""Testes unitários de borda do repositório de usuários."""


async def test_set_admin_invalid_id_returns_false(user_repository):
    # ObjectId inválido: não encontra usuário, retorna False sem lançar.
    assert await user_repository.set_admin("id-invalido", is_admin=True) is False


async def test_set_admin_promotes_existing_user(user_repository):
    user = await user_repository.create(
        full_name="A", email="a@x.com", hashed_password="h", is_active=True
    )
    assert await user_repository.set_admin(user.id, is_admin=True) is True
    assert (await user_repository.get_by_id(user.id)).is_admin is True
