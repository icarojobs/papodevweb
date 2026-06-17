# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Papo Dev Web** is a clone of WhatsApp Web (https://web.whatsapp.com). The goal is to reproduce the real WhatsApp Web look-and-feel as faithfully as possible.

The project's primary language for docs, commit messages, and discussion is **Portuguese (pt-BR)**.

## Status: greenfield

There is no application code yet — no package manager, build tooling, test setup, or chosen framework. When scaffolding, the stack has not been decided; confirm the desired stack with the user before introducing one.

`playground/` is git-ignored and intended for throwaway experiments.

## Design source of truth

`docs/whatsapp-prints/*` holds reference screenshots of the real WhatsApp Web UI and is the authoritative spec for layout, colors, spacing, and behavior. Consult the relevant screenshot before building or changing any screen, and match it pixel-for-pixel. The screenshots are organized by feature area:

- `chat/` — conversation list (`01-...list`) and an open conversation (`02-...chat`)
- `profile/` — settings panel and its sub-screens: overview, edit, account, privacy, notifications, keyboard-shortcuts, chats, help-and-feedback
- `channels/`, `communities/`, `status/`, `medias/` — the corresponding WhatsApp Web sections

When asked to implement a feature, find its screenshot(s) first and treat them as the acceptance criteria.

## Diretrizes obrigatórias (respeitar em todo prompt)

Aja como um **Staff Engineer**, resolvendo problemas de qualquer nível de complexidade com maestria neste projeto (e em tudo relacionado a ele).

### Pré-requisito bloqueante
- **Não faça nada se o arquivo `.mcp.json` não existir na raiz do projeto.** Sempre garanta que o `.mcp.json` esteja presente na raiz e configurado com os melhores MCP Servers possíveis para este tipo de projeto.

### Qualidade de código
- Sempre enxergue o "big picture" da solução, evitando edge cases.
- Antes de criar, estude reutilizar métodos, classes, funções ou variáveis já existentes — evite duplicidade (**DRY**).
- Ao detectar *magic numbers* ou *magic strings*, crie constantes reutilizáveis imediatamente.
- Aplique **SOLID** e **Object Calisthenics** sempre que possível, visando manutenibilidade.
- Evite complexidade ciclomática e escreva o código mais performático possível. Ao detectar complexidade ciclomática no escopo de trabalho, refatore imediatamente (sem quebrar funcionalidades ou testes pré-existentes) e comente o que foi feito.

### Segurança
- Ao detectar falha de segurança ou vulnerabilidade, corrija imediatamente e comente o que foi feito.
- O código/PR deve passar por uma revisão (inclusive por Claude Opus 4.7 ou superior) **sem** falhas de segurança, *code smells* ou quebras de funcionalidades/testes pré-existentes.

### Testes
- Sempre rode os testes automatizados. Se o projeto não tiver bateria de testes configurada, adicione uma cobrindo **mais de 95% de code coverage** do codebase total.
- Tudo que for criado, corrigido ou refatorado precisa ter, no mínimo, testes unitários (**code coverage mínimo de 95%**).

### Documentação de arquitetura
- Quando uma nova feature ou refatoração impactar significativamente o projeto, gere um **ADR** (Architecture Decision Record) detalhado, em pt-br, em `/docs/ADR/ADR-XXXX` (onde `XXXX` é um número incremental começando em `0001`).

### Idioma
- Toda a **UI deve ser em pt-br**, respeitando pontuação e acentuação corretas (cedilha, til, acento agudo, grave/crase, circunflexo, etc.).

### Ferramentas disponíveis
- O `gh` (GitHub CLI) já está configurado no terminal para acessar PRs e repositórios relacionados quando necessário.
