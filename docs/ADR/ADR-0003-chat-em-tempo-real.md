# ADR-0003 — Chat em tempo real (mensagens, mídia e filtros)

- **Status:** Aceito
- **Data:** 2026-06-17
- **Relacionado:** [[ADR-0001]] (stack e arquitetura inicial), [[ADR-0002]] (confirmação de e-mail)

## Contexto

A UI do WhatsApp Web estava montada com dados de exemplo (mock). Era preciso
tornar o chat **funcional**: envio/recebimento de mensagens e objetos (imagens,
arquivos e áudio) em tempo real, além dos filtros da lista de conversas
(busca, Tudo, Não lidas, Favoritas, Grupos). Não havia sistema de contatos.

## Decisão

### Modelo de dados (MongoDB)

- **`conversations`**: `type` (`direct`/`group`), `participants` (lista de
  subdocumentos `{user_id, unread, favourite, last_read_at}`), `name` (grupos),
  `last_message` (prévia para a lista) e `updated_at` (ordenação).
- **`messages`**: `conversation_id`, `sender_id`, `type`
  (`text`/`image`/`document`/`audio`), `text`, `media`, `delivered_to` e
  `read_by`. O **status** (enviado/entregue/lido) é derivado desses arrays sob a
  ótica de quem enviou.
- Metadados por participante (não-lidos e favorito) ficam **embutidos** na
  conversa — favoritar é por usuário, e a listagem filtra no cliente.

### Início de conversa (sem contatos)

- Busca de usuários por **nome ou e-mail** (`GET /users/search`), excluindo o
  próprio e contas inativas. E-mail é único; nomes podem repetir.
- `POST /conversations` cria conversa **direta** (idempotente: reaproveita a
  existente) ou **grupo** (nome + participantes).

### Tempo real (Socket.IO + Redis)

- Autenticação no **handshake** pelo access token JWT.
- O servidor emite para **salas por usuário** (`user:{id}`) — assim novas
  mensagens chegam mesmo sem a conversa aberta — e usa salas por conversa
  (`conv:{id}`) para digitação.
- Eventos: `message:send` (ack com a mensagem salva), `message:new`,
  `message:status` (entregue/lido), `typing`, `conversation:open`,
  `conversation:updated` e `presence`.
- **Recibos**: ao conectar, as pendências são marcadas como entregues; ao abrir
  a conversa, como lidas — com broadcast dos recibos ao remetente.
- **Presença**: online/visto por último em Redis, anunciada aos contatos.
- O `AsyncRedisManager` permite **escalar horizontalmente** sem perder eventos.

### Mídia (MinIO)

- `POST /media` faz upload (imagem/arquivo/áudio), valida tipo e tamanho
  (máx. 16 MB) e devolve uma URL assinada. O cliente envia a mensagem com a
  referência da mídia via socket.

### Sair de grupo e excluir conversa

- **Sair do grupo** (`POST /conversations/{id}/leave`): remove o usuário dos
  `participants` (a conversa some da lista dele, pois a listagem filtra por
  participante). Se o grupo ficar **vazio**, ele é apagado por completo
  (mensagens + mídias). Conversas diretas não podem ser "deixadas".
- **Excluir conversa** (`DELETE /conversations/{id}?scope=me|everyone&delete_media=`):
  - `me` (só para mim): adiciona o usuário a `deleted_for` e grava um marco
    `cleared_at`; a conversa some da SUA lista e o SEU histórico passa a mostrar
    apenas mensagens posteriores. Ela **reaparece** ao chegar nova mensagem
    (o `bump` limpa `deleted_for`). Quando **todos** excluem, os dados são
    removidos de vez.
  - `everyone` (para todos): apaga a conversa e todas as mensagens.
  - `delete_media`: em `everyone` purga todas as mídias da conversa no MinIO; em
    `me` purga apenas as mídias enviadas pelo próprio usuário.
- O `ChatService` retorna as **chaves de mídia** a purgar; a rota chama o
  `MediaService.delete`, mantendo o serviço de chat livre de dependência direta
  do armazenamento.
- **Resiliência:** exclusão/saída são **idempotentes** (excluir algo já removido =
  no-op/204) e o frontend sempre remove a conversa da visão local (mesmo se a API
  falhar), evitando conversas "presas".

### Excluir mensagem individual (para mim / para todos)

- Via Socket.IO (`message:delete`), espelhando o envio. Eventos: `message:delete`
  (cliente) e `message:deleted` (servidor).
- **Para mim** (`scope=me`): adiciona o usuário a `Message.deleted_for`; a mensagem
  some apenas da visão dele (o histórico passa a filtrar por `viewer_id`). O recibo
  é emitido só para as sessões do próprio usuário (multi-dispositivo).
- **Para todos** (`scope=everyone`, apenas o autor): marca `deleted_for_everyone`,
  limpa texto/mídia e vira um **tombstone** ("🚫 Esta mensagem foi apagada") para
  todos, em tempo real; a mídia é purgada do MinIO e a prévia da conversa é
  atualizada se a mensagem apagada era a última.
- A purga de mídia é injetada na camada de tempo real (`ChatRealtime`) como um
  callable, mantendo a separação de responsabilidades.

### URL de mídia em tempo de leitura

- A URL assinada das mídias é **gerada na leitura** (a partir da chave do objeto),
  não gravada no envio — assim nunca expira em definitivo e acompanha mudanças de
  endpoint. O `ChatService` recebe um resolver (`presign`) por injeção; o cliente
  MinIO **público** (`MINIO_PUBLIC_ENDPOINT`) assina URLs acessíveis pelo navegador,
  com região fixa para permitir assinatura offline.

### Arquitetura e qualidade

- Camadas mantidas: **Repository → Service → Rotas/DI**. A lógica de tempo real
  vive em `ChatRealtime`, recebendo `sio`, `ChatService` e `PresenceService` por
  **injeção de dependência** (testável com fakes; SOLID).
- Infra (Redis/MinIO) abstraída por `Protocol`, com fakes em memória nos testes.
- Tradução centralizada de erros de domínio → HTTP (`error_mapping`) evita
  repetição (DRY). Conversão de `ObjectId` extraída para utilitário único.
- **Cobertura**: backend 100%, frontend acima dos limiares (95% linhas/funções,
  85% branches). Validação ponta a ponta no Docker (duas contas trocando
  mensagem + recibo de leitura via Socket.IO real).

## Consequências

- **Positivas:** chat funcional e em tempo real, escalável, com mídia e filtros;
  base de domínio reutilizável; toda a lógica coberta por testes.
- **Trade-offs / limitações conhecidas:**
  - Não-lidos e prévia usam **read-modify-write** na conversa (robusto com o
    mock de testes, mas sujeito a corrida sob altíssima concorrência; migrar para
    `$inc` com `arrayFilters` quando necessário).
  - Histórico paginado por cursor de tempo (`before`), sem busca full-text dentro
    das mensagens (a busca atua sobre nomes de conversa).
  - Sem edição/remoção de mensagens, encaminhamento ou administração de grupos
    (entrar/sair, promover) — próximos passos naturais.
