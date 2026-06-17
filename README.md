# PAPO DEV WEB

Projeto 100% inspirado no whatsapp web (https://web.whatsapp.com) cujo os prints necessários para manter o look-and-feel real está em "docs/whatsapp-prints/*".

## Stack

| Camada            | Tecnologia                                              |
| ----------------- | ------------------------------------------------------- |
| Frontend          | React + TypeScript + Vite + TailwindCSS + Chakra UI     |
| Backend           | Python + FastAPI + Asyncio                              |
| Banco de dados    | MongoDB                                                 |
| Objetos / S3      | MinIO (áudios, vídeos, imagens, documentos)             |
| Filas / Mensageria| Redis + RabbitMQ                                        |
| Tempo real        | Socket.IO                                               |
| Orquestração      | Docker + Docker Compose                                 |

Decisões de arquitetura documentadas em [`docs/ADR/`](docs/ADR/).

## Como rodar (Docker)

```bash
cp .env.example .env          # ajuste os segredos (ex.: JWT_SECRET_KEY)
docker compose up --build
```

Serviços expostos:

| Serviço            | URL / Porta                          |
| ------------------ | ------------------------------------ |
| Frontend (Vite)    | http://localhost:5173                |
| Backend (API)      | http://localhost:8000 — docs `/docs` |
| MongoDB            | localhost:27017                      |
| Redis              | localhost:6379                       |
| RabbitMQ (painel)  | http://localhost:15672               |
| MinIO (console)    | http://localhost:9001                |

## Desenvolvimento

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest                     # roda os testes com cobertura (mínimo 95%)
pytest tests/test_auth_api.py::test_login_success   # um único teste
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev                   # ambiente de desenvolvimento
pnpm test                  # testes (Vitest)
pnpm test:coverage         # testes com cobertura
```

## Funcionalidades

- **Autenticação** ao acessar a aplicação:
  - **Cadastro:** Nome Completo, E-mail, Senha, Repetir senha
  - **Login:** E-mail, Senha
  - **Esqueceu a senha?** envio de link de redefinição por e-mail.
- **Confirmação de e-mail:** o cadastro cria a conta **inativa**; ela só é ativada
  após o usuário clicar no link de confirmação enviado por e-mail, válido por **24 horas**.
  O login fica bloqueado (403) até a confirmação.
- Sessão via JWT (access token + refresh token em cookie httpOnly).
- E-mails de confirmação/redefinição visíveis no **Mailpit**: http://localhost:8075

### Usuário padrão (desenvolvimento)

Em ambientes não-produtivos, os seeders criam automaticamente um usuário de teste
no startup do backend (idempotente). Também pode ser executado manualmente com `make seed`.

- **E-mail:** `teste@teste.com.br`
- **Senha:** `teste1234`

> ⚠️ Os seeders **não** rodam quando `ENVIRONMENT=production`.
