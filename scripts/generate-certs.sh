#!/usr/bin/env bash
# Gera um certificado TLS self-signed para desenvolvimento local (HTTPS).
# Necessário para recursos que exigem contexto seguro (notificações, geolocalização).
#
# Uso: ./scripts/generate-certs.sh  (ou `make certs`)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="${ROOT_DIR}/certs"
CERT_FILE="${CERT_DIR}/cert.pem"
KEY_FILE="${CERT_DIR}/key.pem"

mkdir -p "${CERT_DIR}"

if [[ -f "${CERT_FILE}" && -f "${KEY_FILE}" && "${1:-}" != "--force" ]]; then
  echo "Certificados já existem em ${CERT_DIR} (use --force para recriar)."
  exit 0
fi

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "${KEY_FILE}" \
  -out "${CERT_FILE}" \
  -days 825 \
  -subj "/C=BR/ST=SP/L=Local/O=Papo Dev Web/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:backend,DNS:frontend,IP:127.0.0.1"

chmod 600 "${KEY_FILE}"
echo "Certificado self-signed gerado em ${CERT_DIR} (válido por 825 dias)."
echo "Aceite o certificado no navegador ao acessar https://localhost:5173 e https://localhost:8000."
