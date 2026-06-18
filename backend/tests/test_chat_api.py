"""Testes das rotas REST de chat (usuários, conversas e mídia)."""

import pytest

from app.core.constants import MAX_IMAGE_BYTES, MessageType
from app.schemas.chat import MediaPayload
from tests.conftest import create_user_and_login


@pytest.fixture
async def alice(client, sent_emails) -> dict:
    return await create_user_and_login(
        client, sent_emails, full_name="Alice Silva", email="alice@example.com"
    )


@pytest.fixture
async def bob(client, sent_emails) -> dict:
    return await create_user_and_login(
        client, sent_emails, full_name="Bob Souza", email="bob@example.com"
    )


# ----- Autenticação obrigatória -----


async def test_endpoints_require_auth(client):
    assert (await client.get("/conversations")).status_code == 401
    assert (await client.get("/users/search", params={"q": "a"})).status_code == 401


# ----- Busca de usuários -----


async def test_search_users(client, alice, bob):
    response = await client.get(
        "/users/search", params={"q": "bob"}, headers=alice["headers"]
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["full_name"] == "Bob Souza"
    assert body[0]["online"] is False


async def test_search_requires_query(client, alice):
    response = await client.get("/users/search", headers=alice["headers"])
    assert response.status_code == 422


# ----- Conversas -----


async def test_create_list_and_get_direct_conversation(client, alice, bob):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    assert created.status_code == 201
    conversation_id = created.json()["id"]
    assert created.json()["name"] == "Bob Souza"

    listed = await client.get("/conversations", headers=alice["headers"])
    assert listed.status_code == 200
    assert [c["id"] for c in listed.json()] == [conversation_id]

    fetched = await client.get(
        f"/conversations/{conversation_id}", headers=alice["headers"]
    )
    assert fetched.status_code == 200
    assert fetched.json()["id"] == conversation_id


async def test_create_direct_invalid_recipient_returns_404(client, alice):
    response = await client.post(
        "/conversations",
        json={"recipient_id": "000000000000000000000000"},
        headers=alice["headers"],
    )
    assert response.status_code == 404


async def test_create_group(client, alice, bob):
    response = await client.post(
        "/conversations",
        json={"type": "group", "name": "Equipe", "member_ids": [bob["id"]]},
        headers=alice["headers"],
    )
    assert response.status_code == 201
    assert response.json()["type"] == "group"


async def test_create_group_without_members_returns_400(client, alice):
    response = await client.post(
        "/conversations",
        json={"type": "group", "name": "Vazio", "member_ids": []},
        headers=alice["headers"],
    )
    assert response.status_code == 400


async def test_get_conversation_forbidden_and_not_found(client, alice, bob, sent_emails):
    eve = await create_user_and_login(
        client, sent_emails, full_name="Eve", email="eve@example.com"
    )
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    conversation_id = created.json()["id"]

    forbidden = await client.get(
        f"/conversations/{conversation_id}", headers=eve["headers"]
    )
    assert forbidden.status_code == 403

    missing = await client.get(
        "/conversations/000000000000000000000000", headers=alice["headers"]
    )
    assert missing.status_code == 404


async def test_toggle_favourite(client, alice, bob):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    conversation_id = created.json()["id"]

    first = await client.patch(
        f"/conversations/{conversation_id}/favourite", headers=alice["headers"]
    )
    assert first.json() == {"favourite": True}
    second = await client.patch(
        f"/conversations/{conversation_id}/favourite", headers=alice["headers"]
    )
    assert second.json() == {"favourite": False}


# ----- Mensagens (histórico) -----


async def test_list_messages(client, alice, bob, chat_service):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    conversation_id = created.json()["id"]

    empty = await client.get(
        f"/conversations/{conversation_id}/messages", headers=alice["headers"]
    )
    assert empty.json() == []

    # Injeta uma mensagem pelo serviço (mesmo banco) para validar o histórico.
    await chat_service.send_message(conversation_id, alice["id"], text="Olá!")

    messages = await client.get(
        f"/conversations/{conversation_id}/messages", headers=bob["headers"]
    )
    assert messages.status_code == 200
    assert [m["text"] for m in messages.json()] == ["Olá!"]


async def test_list_messages_invalid_limit(client, alice, bob):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    conversation_id = created.json()["id"]
    response = await client.get(
        f"/conversations/{conversation_id}/messages",
        params={"limit": 9999},
        headers=alice["headers"],
    )
    assert response.status_code == 422


# ----- Upload de mídia -----


async def test_upload_image(client, alice, media_storage):
    response = await client.post(
        "/media",
        files={"file": ("foto.png", b"binario", "image/png")},
        headers=alice["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "foto.png"
    assert body["mime"] == "image/png"
    assert body["key"] in media_storage.objects


async def test_upload_unsupported_media_returns_415(client, alice):
    response = await client.post(
        "/media",
        files={"file": ("x.woff2", b"x", "font/woff2")},
        headers=alice["headers"],
    )
    assert response.status_code == 415


async def test_upload_too_large_returns_413(client, alice):
    big = b"x" * (MAX_IMAGE_BYTES + 1)
    response = await client.post(
        "/media",
        files={"file": ("big.png", big, "image/png")},
        headers=alice["headers"],
    )
    assert response.status_code == 413


# ----- Sair de grupo / excluir conversa -----


async def test_leave_group_via_api(client, alice, bob):
    created = await client.post(
        "/conversations",
        json={"type": "group", "name": "Equipe", "member_ids": [bob["id"]]},
        headers=alice["headers"],
    )
    conversation_id = created.json()["id"]

    response = await client.post(
        f"/conversations/{conversation_id}/leave", headers=alice["headers"]
    )
    assert response.status_code == 204
    listed = await client.get("/conversations", headers=alice["headers"])
    assert listed.json() == []


async def test_leave_direct_via_api_returns_400(client, alice, bob):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    response = await client.post(
        f"/conversations/{created.json()['id']}/leave", headers=alice["headers"]
    )
    assert response.status_code == 400


async def test_delete_for_me_via_api(client, alice, bob):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    conversation_id = created.json()["id"]

    response = await client.delete(
        f"/conversations/{conversation_id}", params={"scope": "me"}, headers=alice["headers"]
    )
    assert response.status_code == 204
    assert (await client.get("/conversations", headers=alice["headers"])).json() == []
    # Bob mantém a conversa.
    assert len((await client.get("/conversations", headers=bob["headers"])).json()) == 1


async def test_delete_for_everyone_purges_media_via_api(
    client, alice, bob, chat_service, media_storage
):
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    conversation_id = created.json()["id"]
    # Mensagem com mídia + objeto correspondente no armazenamento.
    await chat_service.send_message(
        conversation_id,
        alice["id"],
        type=MessageType.IMAGE,
        media=MediaPayload(
            key="obj/foto.png", url="u", mime="image/png", size=1, name="f.png"
        ),
    )
    media_storage.objects["obj/foto.png"] = ("bucket", 1, "image/png")

    response = await client.delete(
        f"/conversations/{conversation_id}",
        params={"scope": "everyone", "delete_media": "true"},
        headers=alice["headers"],
    )
    assert response.status_code == 204
    assert "obj/foto.png" not in media_storage.objects
    assert (await client.get("/conversations", headers=bob["headers"])).json() == []


async def test_delete_missing_conversation_is_idempotent(client, alice):
    # DELETE é idempotente: excluir o que já não existe responde 204.
    response = await client.delete(
        "/conversations/000000000000000000000000", headers=alice["headers"]
    )
    assert response.status_code == 204


async def test_delete_not_participant_returns_403(client, alice, bob, sent_emails):
    eve = await create_user_and_login(
        client, sent_emails, full_name="Eve", email="eve@example.com"
    )
    created = await client.post(
        "/conversations", json={"recipient_id": bob["id"]}, headers=alice["headers"]
    )
    response = await client.delete(
        f"/conversations/{created.json()['id']}", headers=eve["headers"]
    )
    assert response.status_code == 403
