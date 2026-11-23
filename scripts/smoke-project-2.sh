#!/usr/bin/env bash
# Smoke test do Projeto 2 (ecommerce-api-legacy) — LMS API Node/Express.
# Uso: ADMIN_PASSWORD=<senha> bash scripts/smoke-project-2.sh [BASE_URL]
# Pré-requisito: a API rodando com a MESMA senha de admin (ADMIN_PASSWORD=<senha> npm start).
# O banco é em memória: reinicie a API antes de cada execução.
# As requisições do baseline são repetidas com o token do papel adequado (POST /api/login);
# depois vêm as checagens de autorização (AP-11) e dos defaults seguros / correções.
BASE="${1:-http://localhost:3000}"
ADMIN_PWD="${ADMIN_PASSWORD:?defina ADMIN_PASSWORD (a mesma usada para subir a API)}"
PASS=0; FAIL=0

check() { # check <metodo> <path> <status_esperado> [json] [token]
  local method="$1" path="$2" expected="$3" body="$4" token="$5" code args=()
  [ -n "$token" ] && args+=(-H "Authorization: Bearer $token")
  [ -n "$body" ] && args+=(-H "Content-Type: application/json" -d "$body")
  code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "${args[@]}" "$BASE$path")
  if [ "$code" = "$expected" ]; then PASS=$((PASS+1)); echo "  OK   $method $path -> $code"
  else FAIL=$((FAIL+1)); echo "  FAIL $method $path -> $code (esperado $expected)"; fi
}

assert_contains() { # assert_contains <descricao> <texto> <trecho>
  if echo "$2" | grep -q "$3"; then PASS=$((PASS+1)); echo "  OK   $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1 (resposta: $2)"; fi
}

cors_closed() { # AP-10: sem CORS_ORIGINS, origem externa não recebe Access-Control-Allow-Origin
  local headers; headers=$(curl -s -D - -o /dev/null -H "Origin: http://evil.example" "$BASE/")
  if echo "$headers" | grep -qi '^access-control-allow-origin'; then FAIL=$((FAIL+1)); echo "  FAIL CORS aberto para origem externa"
  else PASS=$((PASS+1)); echo "  OK   CORS fechado por padrão (origem externa sem Access-Control-Allow-Origin)"; fi
}

login() { # login <email> <senha> -> imprime o token
  curl -s -X POST -H "Content-Type: application/json" -d "{\"eml\":\"$1\",\"pwd\":\"$2\"}" "$BASE/api/login" \
    | sed -n 's/.*"token": *"\([^"]*\)".*/\1/p'
}

echo "Smoke test: $BASE"
ADMIN=$(login admin@fullcycle.com.br "$ADMIN_PWD")   # admin do seed (senha definida pelo servidor)
STUDENT=$(login leonan@fullcycle.com.br 123)          # aluno do seed
[ -n "$ADMIN" ] && [ -n "$STUDENT" ] && echo "  tokens obtidos via POST /api/login" || echo "  FALHA ao obter tokens"

# Contrato original do payload (usr, eml, pwd, c_id, card) — continua aceito após a refatoração.
check POST   /api/checkout                200 '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}'
check POST   /api/checkout                200 '{"usr":"Leonan","eml":"leonan@fullcycle.com.br","pwd":"123","c_id":2,"card":"4111222233334444"}'
check POST   /api/checkout                400 '{"usr":"João","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}'
check POST   /api/checkout                400 '{"usr":"Sem curso","eml":"x@teste.com"}'
check POST   /api/checkout                404 '{"usr":"Curso X","eml":"y@teste.com","pwd":"123","c_id":999,"card":"4111222233334444"}'

echo "Autorização (AP-11):"
check POST   /api/login                   401 '{"eml":"leonan@fullcycle.com.br","pwd":"errada"}'
check GET    /api/admin/financial-report  401
check GET    /api/admin/financial-report  401 "" "token-errado"
check GET    /api/admin/financial-report  401 "" "${ADMIN}x"
check GET    /api/admin/financial-report  403 "" "$STUDENT"
check DELETE /api/users/1                 401
check DELETE /api/users/1                 403 "" "$STUDENT"
# E-mail já cadastrado não serve mais como identidade sem a senha correta
check POST   /api/checkout                401 '{"usr":"Intruso","eml":"leonan@fullcycle.com.br","pwd":"chute","c_id":1,"card":"4111222233334444"}'
# Papel definido pelo servidor: quem se cadastra pelo checkout (mesmo mandando role=admin) é aluno
check POST   /api/checkout                200 '{"usr":"Mallory","eml":"mallory@teste.com","pwd":"segredo123","c_id":1,"card":"4111222233334444","role":"admin"}'
MALLORY=$(login mallory@teste.com segredo123)
check GET    /api/admin/financial-report  403 "" "$MALLORY"

check GET    /api/admin/financial-report  200 "" "$ADMIN"
# Receitas: curso 1 = 997 (seed) + 997 (Mallory) e curso 2 = 994 (2 checkouts de 497)
REPORT=$(curl -s -H "Authorization: Bearer $ADMIN" "$BASE/api/admin/financial-report")
echo "  relatório: $REPORT"
assert_contains "receitas do relatório conferem (1994 e 994)" "$REPORT" '"revenue":1994,.*"revenue":994'

echo "Defaults seguros e correções (AP-10, AP-16, AP-17, AP-20):"
cors_closed
check POST   /api/checkout                400 '{"usr":"Cartao numerico","eml":"n@teste.com","pwd":"123","c_id":2,"card":4111222233334444}'
check DELETE /api/users/abc               400 "" "$ADMIN"
check DELETE /api/users/9999              404 "" "$ADMIN"
check DELETE /api/users/3                 200 "" "$ADMIN"
check DELETE /api/users/3                 404 "" "$ADMIN"
# O usuário 3 (Guilherme, curso 2 por 497) foi removido em cascata: sem órfãos 'Unknown'
REPORT2=$(curl -s -H "Authorization: Bearer $ADMIN" "$BASE/api/admin/financial-report")
echo "  relatório após exclusão: $REPORT2"
if echo "$REPORT2" | grep -q 'Unknown'; then FAIL=$((FAIL+1)); echo "  FAIL relatório tem aluno órfão (Unknown)"
else PASS=$((PASS+1)); echo "  OK   exclusão em cascata: relatório sem alunos órfãos"; fi
assert_contains "receita do curso 2 após a exclusão = 497" "$REPORT2" '"revenue":1994,.*"revenue":497'

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
