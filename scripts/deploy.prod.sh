#!/usr/bin/env bash
# Deploy de produção com ZERO-DOWNTIME.
# Executado pelo runner (CI/CD) a partir do diretório do projeto no servidor,
# mas também pode ser rodado manualmente lá:  bash scripts/deploy.prod.sh
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
COMPOSE="docker compose -f ${COMPOSE_FILE}"

cd "$(dirname "$0")/.."   # raiz do projeto (onde está o compose + .env)

if [ ! -f .env ]; then
  echo "::error:: .env ausente em $(pwd). Configure os segredos de produção antes do deploy." >&2
  exit 1
fi

echo "==> Garantindo a rede externa 'web' (Traefik)"
docker network inspect web >/dev/null 2>&1 || docker network create web

echo "==> Construindo imagens novas (backend, frontend)"
${COMPOSE} build backend frontend

echo "==> Garantindo serviços de estado no ar (no-op se já rodando)"
${COMPOSE} up -d mongodb redis rabbitmq minio minio-init

# Zero-downtime: se o serviço ainda não existe, sobe normal; senão, faz rollout.
rollout_or_up() {
  local svc="$1"
  if [ -z "$(${COMPOSE} ps -q "$svc" 2>/dev/null)" ]; then
    echo "==> Primeiro start de '$svc' (sem instância anterior)"
    ${COMPOSE} up -d "$svc"
  else
    echo "==> Rollout zero-downtime de '$svc'"
    docker rollout -f "${COMPOSE_FILE}" "$svc"
  fi
}

rollout_or_up backend
rollout_or_up frontend

echo "==> Limpando imagens órfãs"
docker image prune -f >/dev/null 2>&1 || true

echo "==> Estado final"
${COMPOSE} ps
echo "Deploy concluído."
