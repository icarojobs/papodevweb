"""Testes de integração das rotas de autenticação."""

from app.core.constants import REFRESH_TOKEN_COOKIE_NAME
from tests.conftest import register_and_activate


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ----- Cadastro + confirmação de e-mail -----


async def test_register_creates_inactive_account_and_sends_verification(
    client, register_payload, sent_emails
):
    response = await client.post("/auth/register", json=register_payload)
    assert response.status_code == 201
    assert "24 horas" in response.json()["message"]

    assert len(sent_emails) == 1
    to_email, verify_link = sent_emails[0]
    assert to_email == "maria@example.com"
    assert "/confirmar-email?token=" in verify_link


async def test_register_password_mismatch_returns_422(client, register_payload):
    register_payload["confirm_password"] = "outraCoisa123"
    response = await client.post("/auth/register", json=register_payload)
    assert response.status_code == 422


async def test_register_duplicate_email_returns_409(client, register_payload):
    await client.post("/auth/register", json=register_payload)
    response = await client.post("/auth/register", json=register_payload)
    assert response.status_code == 409


async def test_login_before_verification_returns_403(client, register_payload):
    await client.post("/auth/register", json=register_payload)
    response = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert response.status_code == 403


async def test_verify_email_activates_account(client, register_payload, sent_emails):
    await client.post("/auth/register", json=register_payload)
    verify_token = sent_emails[0][1].split("token=")[1]

    verify = await client.post("/auth/verify-email", json={"token": verify_token})
    assert verify.status_code == 200

    login = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


async def test_verify_email_invalid_token_returns_400(client):
    response = await client.post("/auth/verify-email", json={"token": "invalido"})
    assert response.status_code == 400


# ----- Login / sessão -----


async def test_login_success(client, register_payload, sent_emails):
    await register_and_activate(client, register_payload, sent_emails)
    response = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert REFRESH_TOKEN_COOKIE_NAME in response.cookies


async def test_login_invalid_credentials_returns_401(client, register_payload, sent_emails):
    await register_and_activate(client, register_payload, sent_emails)
    response = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": "senhaErrada1"},
    )
    assert response.status_code == 401


async def test_me_requires_authentication(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_returns_current_user(client, register_payload, sent_emails):
    await register_and_activate(client, register_payload, sent_emails)
    login = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    access_token = login.json()["access_token"]
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "maria@example.com"


async def test_me_with_invalid_token_returns_401(client):
    response = await client.get("/auth/me", headers={"Authorization": "Bearer abc"})
    assert response.status_code == 401


async def test_refresh_rotates_access_token(client, register_payload, sent_emails):
    await register_and_activate(client, register_payload, sent_emails)
    login = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    cookie = login.cookies[REFRESH_TOKEN_COOKIE_NAME]
    response = await client.post(
        "/auth/refresh", cookies={REFRESH_TOKEN_COOKIE_NAME: cookie}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_refresh_without_cookie_returns_401(client):
    response = await client.post("/auth/refresh")
    assert response.status_code == 401


async def test_refresh_with_invalid_cookie_returns_401(client):
    response = await client.post(
        "/auth/refresh", cookies={REFRESH_TOKEN_COOKIE_NAME: "cookie-invalido"}
    )
    assert response.status_code == 401


async def test_logout_clears_cookie(client):
    response = await client.post("/auth/logout")
    assert response.status_code == 204


# ----- Redefinição de senha -----


async def test_forgot_password_sends_email_for_known_user(
    client, register_payload, sent_emails
):
    await register_and_activate(client, register_payload, sent_emails)
    response = await client.post(
        "/auth/forgot-password", json={"email": register_payload["email"]}
    )
    assert response.status_code == 202
    assert len(sent_emails) == 1
    to_email, reset_link = sent_emails[0]
    assert to_email == register_payload["email"]
    assert "/redefinir-senha?token=" in reset_link


async def test_forgot_password_unknown_email_does_not_send(client, sent_emails):
    response = await client.post(
        "/auth/forgot-password", json={"email": "naoexiste@example.com"}
    )
    assert response.status_code == 202
    assert sent_emails == []


async def test_reset_password_full_flow(client, register_payload, sent_emails):
    await register_and_activate(client, register_payload, sent_emails)
    await client.post("/auth/forgot-password", json={"email": register_payload["email"]})
    token = sent_emails[-1][1].split("token=")[1]

    reset = await client.post(
        "/auth/reset-password",
        json={"token": token, "password": "novaSenha123", "confirm_password": "novaSenha123"},
    )
    assert reset.status_code == 200

    login = await client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": "novaSenha123"},
    )
    assert login.status_code == 200


async def test_reset_password_invalid_token_returns_400(client):
    response = await client.post(
        "/auth/reset-password",
        json={"token": "invalido", "password": "novaSenha123", "confirm_password": "novaSenha123"},
    )
    assert response.status_code == 400


async def test_reset_password_mismatch_returns_422(client):
    response = await client.post(
        "/auth/reset-password",
        json={"token": "qualquer", "password": "novaSenha123", "confirm_password": "outra123"},
    )
    assert response.status_code == 422
