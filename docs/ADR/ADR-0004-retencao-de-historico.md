# ADR-0004 — Retenção de histórico e expurgo automático

- **Status:** Aceito
- **Data:** 2026-06-18
- **Relacionado:** [[ADR-0003]] (chat em tempo real)

## Contexto

Por privacidade e custo de armazenamento, a plataforma deve manter **apenas os
últimos 7 dias** de histórico (conversas, mensagens e mídias). Após esse período,
os dados devem ser expurgados automaticamente, com a regra documentada nos
**Termos de Uso**.

## Decisão

1. **Política (global):** mantém-se uma janela de `RETENTION_DAYS = 7` dias.
   - **Mensagens** com `created_at < corte` são apagadas; suas **mídias** são
     removidas do MinIO.
   - **Conversas** sem atividade (`updated_at < corte`) são removidas por completo.
   - Conversas ativas preservam a prévia (`last_message`), pois `updated_at` é
     sempre ≥ ao instante da última mensagem mantida.
2. **`RetentionService.purge(now)`** concentra a lógica (testável): coleta as
   chaves de mídia antes do corte, apaga as mensagens, apaga as conversas
   inativas e purga as mídias. Retorna as contagens (`PurgeResult`).
3. **Agendamento:** `APScheduler` (`AsyncIOScheduler`) executa o expurgo
   **todos os dias às 00:01** (`CronTrigger`), no timezone configurável
   (`SCHEDULER_TIMEZONE`, padrão `America/Sao_Paulo`). O scheduler é iniciado no
   `lifespan` do FastAPI e encerrado no shutdown.
4. **Termos de Uso:** página pública `/termos` descreve a regra de retenção de
   forma explícita (incluindo o horário do expurgo e o caráter irreversível);
   link disponível nas telas de autenticação.

## Consequências

- **Positivas:** uso de armazenamento limitado; privacidade reforçada; regra
  transparente ao usuário; lógica isolada e 100% testada.
- **Trade-offs / limitações conhecidas:**
  - Em deploy com múltiplas instâncias, o job rodaria em cada uma — para
    produção, convém um *lock* distribuído (ex.: Redis) ou um worker dedicado.
  - O expurgo é definitivo (sem lixeira/retenção fria).
  - A camada de agendamento (`app/jobs/scheduler.py`) é fina e fica fora da
    métrica de cobertura; o núcleo (`RetentionService`) é coberto por testes.
