# ADR-0005 — HTTPS local com certificado self-signed

- **Status:** Aceito
- **Data:** 2026-06-18
- **Relacionado:** [[ADR-0001]] (stack e arquitetura inicial)

## Contexto

Recursos planejados — **notificações** (Notification API) e **geolocalização**
(Geolocation API) — só funcionam em um **contexto seguro** (HTTPS), inclusive em
`localhost` para subdomínios/origens diferentes. Era preciso servir o projeto via
HTTPS no ambiente de desenvolvimento.

## Decisão

1. **Certificado self-signed** gerado em `./certs` (`cert.pem` + `key.pem`) por
   `scripts/generate-certs.sh` (alvo `make certs`), com `subjectAltName` para
   `localhost`, `backend`, `frontend` e `127.0.0.1` e validade de 825 dias.
2. **Frontend (Vite)** habilita `server.https` lendo os certificados montados em
   `/certs`. A configuração é **condicional**: sem os arquivos (build/CI/testes),
   cai automaticamente para HTTP, sem quebrar.
3. **Backend (Uvicorn)** sobe com `--ssl-keyfile`/`--ssl-certfile` apontando para
   `/certs`, servindo a API e o Socket.IO sob HTTPS/WSS.
4. **Compose** monta `./certs:/certs:ro` em ambos os serviços.
5. **Configuração** atualizada para HTTPS: `VITE_API_URL`, `VITE_SOCKET_URL` e
   `FRONTEND_ORIGIN` (CORS + origem do Socket.IO) passam a usar `https://`.

## Segurança

- A **chave privada não é versionada** (`.gitignore: certs/*.pem`). Commitar chaves
  privadas é um anti-padrão de segurança; cada ambiente gera o seu certificado.
- O certificado é **exclusivo de desenvolvimento**. Em produção, usa-se um
  certificado emitido por uma CA confiável (ex.: Let's Encrypt) e terminação TLS
  em proxy/reverse-proxy.

## Consequências

- **Positivas:** contexto seguro habilita notificações/geolocalização; paridade
  maior com produção; sem mudança na arquitetura (URLs absolutas preservadas).
- **Trade-offs / limitações conhecidas:**
  - Por ser self-signed, o navegador alerta na primeira visita; é preciso **aceitar
    o certificado** tanto em `https://localhost:5173` quanto em `https://localhost:8000`.
  - Alternativa para remover o aviso localmente: `mkcert` (CA local confiável) — não
    adotado para manter o requisito de "self-signed" e zero instalação extra.
