# Makefile — atalhos para o ambiente Docker do Papo Dev Web.

COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help setup certs up down ps logs build seed

help: ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: ## Cria o arquivo .env a partir do .env.example (se ainda não existir)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Arquivo .env criado a partir de .env.example. Ajuste os segredos (ex.: JWT_SECRET_KEY)."; \
	else \
		echo "Arquivo .env já existe — nenhuma alteração feita."; \
	fi

certs: ## Gera o certificado TLS self-signed para HTTPS local (em ./certs)
	@./scripts/generate-certs.sh

up: certs ## Gera os certificados (se faltarem) e sobe todos os serviços
	$(COMPOSE) up -d

down: ## Para e remove os contêineres
	$(COMPOSE) down

ps: ## Lista os serviços e seus status
	$(COMPOSE) ps

logs: ## Acompanha os logs de todos os serviços (Ctrl+C para sair)
	$(COMPOSE) logs -f

build: ## (Re)constrói as imagens dos serviços
	$(COMPOSE) build

seed: ## Roda migrations + seeders (cria o usuário padrão) no backend
	$(COMPOSE) exec backend python -m scripts.seed
