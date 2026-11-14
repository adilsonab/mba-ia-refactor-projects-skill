#!/usr/bin/env bash
# Smoke test do Projeto 3 (task-manager-api) — Task Manager Flask.
# Uso: bash scripts/smoke-project-3.sh [BASE_URL]
# Pré-requisito: banco recém-populado (python seed.py) e a API rodando (python app.py).
# As requisições do baseline são repetidas com o token do papel adequado; ao final, checagens de autorização (AP-11).
BASE="${1:-http://localhost:5000}"
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

login() { # login <email> <senha> -> imprime o token
  curl -s -X POST -H "Content-Type: application/json" -d "{\"email\":\"$1\",\"password\":\"$2\"}" "$BASE/login" \
    | sed -n 's/.*"token": *"\([^"]*\)".*/\1/p'
}

echo "Smoke test: $BASE"
ADMIN=$(login joao@email.com 1234)    # seed: role admin
USER=$(login maria@email.com abcd)    # seed: role user (id 2)
[ -n "$ADMIN" ] && [ -n "$USER" ] && echo "  tokens obtidos via POST /login" || echo "  FALHA ao obter tokens"

check GET    /                          200
check GET    /health                    200
# Tasks (qualquer usuário autenticado)
check GET    /tasks                     200 "" "$ADMIN"
check GET    /tasks/1                   200 "" "$ADMIN"
check GET    /tasks/9999                404 "" "$ADMIN"
check POST   /tasks                     201 '{"title":"Nova task","priority":2,"user_id":1,"category_id":1,"due_date":"2030-01-01","tags":["a","b"]}' "$ADMIN"
check POST   /tasks                     400 '{"title":"ab"}' "$ADMIN"
check POST   /tasks                     400 '{"title":"Status ruim","status":"xpto"}' "$ADMIN"
check PUT    /tasks/1                   200 '{"status":"in_progress","priority":2}' "$ADMIN"
check PUT    /tasks/1                   400 '{"priority":9}' "$ADMIN"
check GET    "/tasks/search?q=login"    200 "" "$ADMIN"
check GET    "/tasks/search?status=pending&priority=1" 200 "" "$ADMIN"
check GET    /tasks/stats               200 "" "$ADMIN"
check DELETE /tasks/11                  200 "" "$ADMIN"
# Users
check GET    /users                     200 "" "$ADMIN"
check GET    /users/1                   200 "" "$ADMIN"
check GET    /users/9999                404 "" "$ADMIN"
check POST   /users                     201 '{"name":"Ana","email":"ana@email.com","password":"segredo123"}'
check POST   /users                     409 '{"name":"Ana","email":"ana@email.com","password":"segredo123"}'
check POST   /users                     400 '{"name":"Bad","email":"invalido","password":"segredo123"}'
check PUT    /users/2                   200 '{"name":"Maria S."}' "$USER"
check GET    /users/1/tasks             200 "" "$ADMIN"
check POST   /login                     200 '{"email":"joao@email.com","password":"1234"}'
check POST   /login                     401 '{"email":"joao@email.com","password":"errada"}'
check DELETE /users/4                   200 "" "$ADMIN"
# Reports & categories
check GET    /reports/summary           200 "" "$ADMIN"
check GET    /reports/user/1            200 "" "$ADMIN"
check GET    /reports/user/9999         404 "" "$ADMIN"
check GET    /categories                200 "" "$ADMIN"
check POST   /categories                201 '{"name":"QA","color":"#123456"}' "$ADMIN"
check PUT    /categories/5              200 '{"name":"Quality"}' "$ADMIN"
check DELETE /categories/5              200 "" "$ADMIN"

echo "Autorização (AP-11):"
LOGIN=$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"joao@email.com","password":"1234"}' "$BASE/login")
if echo "$LOGIN" | grep -q 'fake-jwt-token'; then FAIL=$((FAIL+1)); echo "  FAIL login ainda devolve fake-jwt-token"
else PASS=$((PASS+1)); echo "  OK   login devolve token assinado (sem fake-jwt-token)"; fi
check GET    /tasks                     401
check GET    /users                     401
check GET    /users                     401 "" "fake-jwt-token-1"
check GET    /users                     401 "" "${ADMIN}x"
check GET    /users                     403 "" "$USER"
check DELETE /users/1                   403 "" "$USER"
check GET    /reports/summary           403 "" "$USER"
check POST   /categories                403 '{"name":"Hack"}' "$USER"
check GET    /users/1                   403 "" "$USER"
check GET    /reports/user/1            403 "" "$USER"
check GET    /users/2                   200 "" "$USER"
check PUT    /users/2                   403 '{"role":"admin"}' "$USER"
check PUT    /users/1                   403 '{"name":"Invasor"}' "$USER"
# Cadastro público com role=admin: criado com o papel padrão (definido pelo servidor)
SIGNUP=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"Mallory","email":"mallory@email.com","password":"segredo123","role":"admin"}' "$BASE/users")
assert_contains "cadastro público com role=admin vira role=user" "$SIGNUP" '"role": *"user"'
MALLORY=$(login mallory@email.com segredo123)
check GET    /users                     403 "" "$MALLORY"
# Admin autenticado pode definir o papel no cadastro
CREATED=$(curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN" \
  -d '{"name":"Gerente","email":"gerente@email.com","password":"segredo123","role":"manager"}' "$BASE/users")
assert_contains "admin autenticado define role=manager" "$CREATED" '"role": *"manager"'

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
