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
make certs                    # gera o certificado TLS self-signed (HTTPS local)
docker compose up --build
```

> `make up` já executa `make certs` automaticamente se os certificados não existirem.

Serviços expostos:

| Serviço            | URL / Porta                           |
| ------------------ | ------------------------------------- |
| Frontend (Vite)    | https://localhost:5173                |
| Backend (API)      | https://localhost:8000 — docs `/docs` |
| MongoDB            | localhost:27017                       |
| Redis              | localhost:6379                        |
| RabbitMQ (painel)  | http://localhost:15672                |
| MinIO (console)    | http://localhost:9001                 |

### HTTPS local (certificado self-signed)

O frontend e o backend rodam sob **HTTPS** mesmo em `localhost`, pois recursos como
**notificações** e **geolocalização** exigem um contexto seguro.

- O certificado é gerado em `./certs` (`cert.pem` + `key.pem`) por `make certs`
  (script `scripts/generate-certs.sh`), com SAN para `localhost` e `127.0.0.1`.
- A chave privada **não é versionada** (está no `.gitignore`); cada ambiente gera a sua.
- Por ser **self-signed**, o navegador exibirá um aviso na primeira visita. Aceite o
  certificado em **https://localhost:5173** e também em **https://localhost:8000**
  (a API/Socket.IO usa o mesmo certificado, em outra origem).
- Para recriar o certificado: `make certs` (ou `./scripts/generate-certs.sh --force`).

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
