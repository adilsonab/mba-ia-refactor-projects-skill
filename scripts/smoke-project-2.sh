#!/usr/bin/env bash
# Smoke test do Projeto 2 (ecommerce-api-legacy) — LMS API Node/Express.
# Uso: ADMIN_TOKEN=<token> bash scripts/smoke-project-2.sh [BASE_URL]
# Pré-requisito: a API rodando com o MESMO ADMIN_TOKEN (ADMIN_TOKEN=<token> npm start).
# O banco é em memória: reinicie a API antes de cada execução.
BASE="${1:-http://localhost:3000}"
ADMIN="${ADMIN_TOKEN:?defina ADMIN_TOKEN (o mesmo usado para subir a API)}"
PASS=0; FAIL=0

check() { # check <metodo> <path> <status_esperado> [json] [token]
  local method="$1" path="$2" expected="$3" body="$4" token="$5" code args=()
  [ -n "$token" ] && args+=(-H "Authorization: Bearer $token")
  [ -n "$body" ] && args+=(-H "Content-Type: application/json" -d "$body")
  code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "${args[@]}" "$BASE$path")
  if [ "$code" = "$expected" ]; then PASS=$((PASS+1)); echo "  OK   $method $path -> $code"
  else FAIL=$((FAIL+1)); echo "  FAIL $method $path -> $code (esperado $expected)"; fi
}

echo "Smoke test: $BASE"
# Contrato original do payload (usr, eml, pwd, c_id, card) — deve continuar aceito após a refatoração.
check POST   /api/checkout                200 '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}'
check POST   /api/checkout                200 '{"usr":"Leonan","eml":"leonan@fullcycle.com.br","pwd":"123","c_id":2,"card":"4111222233334444"}'
check POST   /api/checkout                400 '{"usr":"João","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}'
check POST   /api/checkout                400 '{"usr":"Sem curso","eml":"x@teste.com"}'
check POST   /api/checkout                404 '{"usr":"Curso X","eml":"y@teste.com","pwd":"123","c_id":999,"card":"4111222233334444"}'

echo "Autorização (AP-11):"
check GET    /api/admin/financial-report  401
check GET    /api/admin/financial-report  401 "" "token-errado"
check GET    /api/admin/financial-report  401 "" "${ADMIN}x"
check DELETE /api/users/1                 401
check DELETE /api/users/1                 401 "" "token-errado"

check GET    /api/admin/financial-report  200 "" "$ADMIN"
# Conteúdo do relatório: 2 cursos, receita do curso 1 = 997 (seed) e do curso 2 = 994 (2 checkouts de 497)
REPORT=$(curl -s -H "Authorization: Bearer $ADMIN" "$BASE/api/admin/financial-report")
echo "  relatório: $REPORT"
if echo "$REPORT" | grep -q '"revenue":997' && echo "$REPORT" | grep -q '"revenue":994'; then
  PASS=$((PASS+1)); echo "  OK   receitas do relatório conferem"
else
  FAIL=$((FAIL+1)); echo "  FAIL receitas do relatório divergem"
fi
check DELETE /api/users/1                 200 "" "$ADMIN"

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
