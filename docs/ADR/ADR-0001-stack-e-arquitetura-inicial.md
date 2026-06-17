# ADR-0001 — Stack e arquitetura inicial

- **Status:** Aceito
- **Data:** 2026-06-17
- **Contexto do projeto:** Papo Dev Web — clone do WhatsApp Web (ver `README.md` e `CLAUDE.md`).

## Contexto

O projeto partiu do zero (greenfield) e precisava de uma fundação que suportasse
chat em tempo real, armazenamento de mídias, mensageria/filas e autenticação,
mantendo o look-and-feel do WhatsApp Web. A stack foi definida pelo time:

- **Banco de dados:** MongoDB
- **Objetos/S3:** MinIO (áudios, vídeos, imagens, documentos)
- **Filas/Mensageria:** Redis + RabbitMQ
- **Tempo real:** Socket.IO
- **Frontend:** React + TypeScript + TailwindCSS + Chakra UI
- **Backend:** Python + FastAPI + Asyncio
- **Orquestração local:** Docker + `docker-compose.yml` na raiz

## Decisões

### 1. Arquitetura em camadas no backend
Adotado padrão **Repository → Service → API** com injeção de dependências do
FastAPI. Motivações: respeitar SOLID, isolar o MongoDB em uma única camada
(`repositories/`) e permitir testes unitários sem banco real (mongomock).

### 2. Autenticação por JWT
- **Access token** de curta duração (15 min), enviado no header `Authorization`.
- **Refresh token** de longa duração (7 dias) em **cookie httpOnly** (mitiga XSS),
  com `SameSite=Lax` e `Secure` em produção.
- Hash de senha com **Argon2** (resistente a GPU/ASIC), superior a bcrypt.

### 3. Tempo real com Socket.IO + Redis
O servidor Socket.IO usa o **AsyncRedisManager** como pub/sub, permitindo escalar
o backend horizontalmente. O handshake é autenticado pelo access token.

### 4. MinIO como camada S3
Bucket criado automaticamente no `docker-compose` (serviço `minio-init`).

### 5. Constantes centralizadas
Strings/números mágicos concentrados em `core/constants.py` (backend) e
`lib/constants.ts` (frontend), atendendo à diretriz DRY do `CLAUDE.md`.

### 6. Testes e cobertura
- Backend: pytest + pytest-asyncio + mongomock-motor, `--cov-fail-under=95`.
- Frontend: Vitest + Testing Library, thresholds de 95%.

## Consequências

- **Positivas:** alta testabilidade, separação de responsabilidades, segurança
  de autenticação sólida, infraestrutura reproduzível via Docker.
- **Negativas / trade-offs:** RabbitMQ e MinIO ainda não têm uso funcional nesta
  fundação (apenas provisionados); a complexidade da stack é alta para o estágio
  atual, justificada pelo roadmap de chat/mídia.

## Itens em aberto (próximas decisões)

- Modelagem de conversas/mensagens e contratos de eventos Socket.IO.
- Estratégia de upload de mídia via MinIO (presigned URLs).
- Workers consumindo filas do RabbitMQ (ex.: notificações, processamento de mídia).
