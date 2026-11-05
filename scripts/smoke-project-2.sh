#!/usr/bin/env bash
# Smoke test do Projeto 2 (ecommerce-api-legacy) — LMS API Node/Express.
# Uso: bash scripts/smoke-project-2.sh [BASE_URL]
# Pré-requisito: a API rodando (npm start). O banco é em memória: reinicie a API antes de cada execução.
BASE="${1:-http://localhost:3000}"
PASS=0; FAIL=0

check() { # check <metodo> <path> <status_esperado> [json]
  local method="$1" path="$2" expected="$3" body="$4" code
  if [ -n "$body" ]; then
    code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$body" "$BASE$path")
  else
    code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE$path")
  fi
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
check GET    /api/admin/financial-report  200
check DELETE /api/users/1                 200

# Conteúdo do relatório: 2 cursos, receita do curso 1 = 997 (seed) e do curso 2 = 994 (2 checkouts de 497)
REPORT=$(curl -s "$BASE/api/admin/financial-report")
echo "  relatório: $REPORT"
if echo "$REPORT" | grep -q '"revenue":997' && echo "$REPORT" | grep -q '"revenue":994'; then
  PASS=$((PASS+1)); echo "  OK   receitas do relatório conferem"
else
  FAIL=$((FAIL+1)); echo "  FAIL receitas do relatório divergem"
fi

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
