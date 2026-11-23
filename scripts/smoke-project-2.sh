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

cors_closed() { # AP-10: sem CORS_ORIGINS, origem externa não recebe Access-Control-Allow-Origin
  local headers; headers=$(curl -s -D - -o /dev/null -H "Origin: http://evil.example" "$BASE/")
  if echo "$headers" | grep -qi '^access-control-allow-origin'; then FAIL=$((FAIL+1)); echo "  FAIL CORS aberto para origem externa"
  else PASS=$((PASS+1)); echo "  OK   CORS fechado por padrão (origem externa sem Access-Control-Allow-Origin)"; fi
}

assert_contains() { # assert_contains <descricao> <texto> <trecho>
  if echo "$2" | grep -q "$3"; then PASS=$((PASS+1)); echo "  OK   $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1 (resposta: $2)"; fi
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

echo "Correções v1.3 (AP-10, AP-16 validação, AP-17 404, AP-20 cascata):"
cors_closed
check POST   /api/checkout                400 '{"usr":"Email ruim","eml":"nao-e-email","pwd":"123","c_id":2,"card":"4111222233334444"}'
check POST   /api/checkout                400 '{"usr":"Curso ruim","eml":"z@teste.com","pwd":"123","c_id":"abc","card":"4111222233334444"}'
check POST   /api/checkout                400 '{"usr":"Cartao ruim","eml":"w@teste.com","pwd":"123","c_id":2,"card":"4111-abc"}'
check DELETE /api/users/abc               400 "" "$ADMIN"
check DELETE /api/users/9999              404 "" "$ADMIN"
check DELETE /api/users/1                 200 "" "$ADMIN"
check DELETE /api/users/1                 404 "" "$ADMIN"
# Usuário 1 (seed: curso 1 por 997 + checkout do curso 2 por 497) removido em cascata: sem órfãos 'Unknown'
REPORT2=$(curl -s -H "Authorization: Bearer $ADMIN" "$BASE/api/admin/financial-report")
echo "  relatório após exclusão: $REPORT2"
if echo "$REPORT2" | grep -q 'Unknown'; then FAIL=$((FAIL+1)); echo "  FAIL relatório tem aluno órfão (Unknown)"
else PASS=$((PASS+1)); echo "  OK   exclusão em cascata: relatório sem alunos órfãos"; fi
assert_contains "receitas após a exclusão (curso 1 = 0, curso 2 = 497)" "$REPORT2" '"revenue":0,.*"revenue":497'

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
