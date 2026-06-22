"""Testes da API administrativa (/admin) — configuração do e-mail de disparo."""

from app.api.deps import get_settings_service, get_test_email_sender
from app.core.constants import MSG_TEST_EMAIL_SENT
from app.main import fastapi_app
from app.services.settings_service import EmailConfig
from tests.conftest import create_user_and_login

_EMAIL_PAYLOAD = {
    "host": "smtp.provedor.com",
    "port": 587,
    "username": "apikey",
    "password": "segredo",
    "from_email": "no-reply@papodevweb.com.br",
    "from_name": "Papo Dev Web",
    "use_tls": True,
}


async def _login_admin(client, sent_emails, user_repository, *, email="admin@example.com") -> dict:
    creds = await create_user_and_login(
        client, sent_emails, full_name="Admin", email=email
    )
    await user_repository.set_admin(creds["id"], is_admin=True)
    return creds


async def test_get_email_settings_requires_auth(client):
    response = await client.get("/admin/settings/email")
    assert response.status_code == 401


async def test_get_email_settings_forbidden_for_non_admin(client, sent_emails):
    creds = await create_user_and_login(
        client, sent_emails, full_name="Comum", email="comum@example.com"
    )
    response = await client.get("/admin/settings/email", headers=creds["headers"])
    assert response.status_code == 403


async def test_admin_get_email_settings_defaults(client, sent_emails, user_repository):
    creds = await _login_admin(client, sent_emails, user_repository)
    response = await client.get("/admin/settings/email", headers=creds["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["host"] == ""
    assert body["password_set"] is False
    assert "password" not in body


async def test_admin_update_email_settings(client, sent_emails, user_repository):
    creds = await _login_admin(client, sent_emails, user_repository)
    response = await client.put(
        "/admin/settings/email", json=_EMAIL_PAYLOAD, headers=creds["headers"]
    )
    assert response.status_code == 200
    body = response.json()
    assert body["host"] == "smtp.provedor.com"
    assert body["username"] == "apikey"
    assert body["password_set"] is True
    assert "password" not in body

    # Persistiu: GET reflete o estado salvo.
    again = await client.get("/admin/settings/email", headers=creds["headers"])
    assert again.json()["password_set"] is True


async def test_admin_update_without_password_keeps_existing(client, sent_emails, user_repository):
    creds = await _login_admin(client, sent_emails, user_repository)
    await client.put("/admin/settings/email", json=_EMAIL_PAYLOAD, headers=creds["headers"])
    payload = {**_EMAIL_PAYLOAD, "host": "smtp.novo"}
    payload.pop("password")
    response = await client.put("/admin/settings/email", json=payload, headers=creds["headers"])
    assert response.status_code == 200
    assert response.json()["host"] == "smtp.novo"
    assert response.json()["password_set"] is True


async def test_admin_send_test_email(client, sent_emails, user_repository):
    creds = await _login_admin(client, sent_emails, user_repository)
    await client.put("/admin/settings/email", json=_EMAIL_PAYLOAD, headers=creds["headers"])
    response = await client.post(
        "/admin/settings/email/test", json={"to": "qa@example.com"}, headers=creds["headers"]
    )
    assert response.status_code == 200
    assert response.json()["message"] == MSG_TEST_EMAIL_SENT
    assert ("qa@example.com", "__test__") in sent_emails


async def test_send_test_email_forbidden_for_non_admin(client, sent_emails):
    creds = await create_user_and_login(
        client, sent_emails, full_name="Comum", email="comum2@example.com"
    )
    response = await client.post(
        "/admin/settings/email/test", json={"to": "x@example.com"}, headers=creds["headers"]
    )
    assert response.status_code == 403


async def test_send_test_email_not_configured_returns_400(client, sent_emails, user_repository):
    creds = await _login_admin(client, sent_emails, user_repository)

    class _EmptyService:
        async def get_effective_email_config(self) -> EmailConfig:
            return EmailConfig(
                host="", port=587, username="", password="",
                from_email="", from_name="", use_tls=True,
            )

    fastapi_app.dependency_overrides[get_settings_service] = lambda: _EmptyService()
    try:
        response = await client.post(
            "/admin/settings/email/test", json={"to": "x@example.com"}, headers=creds["headers"]
        )
    finally:
        fastapi_app.dependency_overrides.pop(get_settings_service, None)
    assert response.status_code == 400


async def test_send_test_email_smtp_failure_returns_502(client, sent_emails, user_repository):
    creds = await _login_admin(client, sent_emails, user_repository)
    await client.put("/admin/settings/email", json=_EMAIL_PAYLOAD, headers=creds["headers"])

    async def failing_sender(_to: str) -> None:
        raise RuntimeError("smtp caiu")

    fastapi_app.dependency_overrides[get_test_email_sender] = lambda: failing_sender
    try:
        response = await client.post(
            "/admin/settings/email/test", json={"to": "x@example.com"}, headers=creds["headers"]
        )
    finally:
        # restaura o override padrão do conftest na próxima fixture (clear no teardown)
        fastapi_app.dependency_overrides.pop(get_test_email_sender, None)
    assert response.status_code == 502
