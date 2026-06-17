# ADR-0002 — Confirmação de e-mail para ativação de conta

- **Status:** Aceito
- **Data:** 2026-06-17
- **Relacionado:** [[ADR-0001]] (stack e arquitetura inicial)

## Contexto

O cadastro (`/cadastro`) passou a exigir que a conta seja **confirmada via e-mail**
antes de poder ser usada, com prazo de **até 24 horas** para a confirmação.

## Decisão

1. **Conta nasce inativa.** O registro cria o usuário com `is_active = False` e
   **não** autentica automaticamente (deixou de retornar tokens de sessão).
2. **Token de confirmação** é um JWT dedicado (`type=verify`) com expiração de
   **24 horas** (`jwt_verify_token_expire_hours`). O link aponta para
   `/confirmar-email?token=...` no frontend.
3. **Ativação** ocorre em `POST /auth/verify-email`: valida o token e marca
   `is_active = True`. Após expirar (24h), o link é inválido e a conta permanece inativa.
4. **Login bloqueado** para contas não confirmadas: `authenticate` lança
   `EmailNotVerifiedError`, traduzido para **HTTP 403** com mensagem em pt-br.
   A verificação de senha vem antes da de ativação (não revela se a conta existe).
5. **Envio de e-mail** reutiliza o `email_service` (SMTP/Mailpit) e é injetado via
   dependência (`get_verification_email_sender`), permitindo substituição em testes.
6. **Seeder** do usuário padrão de desenvolvimento cria a conta já **ativa**.

## Consequências

- **Positivas:** reduz contas falsas/abandonadas e valida a posse do e-mail;
  fluxo testável de ponta a ponta (Mailpit em dev).
- **Trade-offs / limitações conhecidas:**
  - Um e-mail cadastrado e **não confirmado** continua retornando 409 em novo
    cadastro — ainda **não há reenvio de confirmação**. Próximo passo sugerido:
    endpoint de "reenviar confirmação" e/ou limpeza de contas inativas expiradas.
  - Contas inativas permanecem no banco indefinidamente (sem job de expurgo).
