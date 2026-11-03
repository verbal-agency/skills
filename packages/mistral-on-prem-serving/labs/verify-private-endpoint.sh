#!/usr/bin/env bash
set -euo pipefail

: "${PROXY_URL:?Set PROXY_URL, for example http://127.0.0.1:8081}"
: "${AUTH_HEADER:?Set AUTH_HEADER to the proxy Authorization value}"

if ! command -v ss >/dev/null 2>&1; then
  echo "ss is required to verify the bind address" >&2
  exit 2
fi

if ss -ltn | grep -Eq '(^|[[:space:]])(0\.0\.0\.0|\*):8080([[:space:]]|$)|\[::\]:8080'; then
  echo "vLLM is listening beyond loopback on port 8080" >&2
  exit 1
fi

unauthorized=$(curl --silent --output /dev/null --write-out '%{http_code}' "$PROXY_URL/v1/models")
case "$unauthorized" in
  401|403) ;;
  *) echo "expected unauthenticated request to be rejected, got HTTP $unauthorized" >&2; exit 1 ;;
esac

authorized=$(curl --silent --fail --output /dev/null --write-out '%{http_code}' \
  -H "Authorization: $AUTH_HEADER" "$PROXY_URL/v1/models")
case "$authorized" in
  2*) echo "private endpoint checks passed (unauthenticated=$unauthorized authorized=$authorized)" ;;
  *) echo "authorized request failed with HTTP $authorized" >&2; exit 1 ;;
esac
