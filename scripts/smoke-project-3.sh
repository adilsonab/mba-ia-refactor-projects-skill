#!/usr/bin/env bash
# Smoke test do Projeto 3 (task-manager-api) — Task Manager Flask.
# Uso: bash scripts/smoke-project-3.sh [BASE_URL]
# Pré-requisito: banco recém-populado (python seed.py) e a API rodando (python app.py).
BASE="${1:-http://localhost:5000}"
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
check GET    /                          200
check GET    /health                    200
# Tasks
check GET    /tasks                     200
check GET    /tasks/1                   200
check GET    /tasks/9999                404
check POST   /tasks                     201 '{"title":"Nova task","priority":2,"user_id":1,"category_id":1,"due_date":"2030-01-01","tags":["a","b"]}'
check POST   /tasks                     400 '{"title":"ab"}'
check POST   /tasks                     400 '{"title":"Status ruim","status":"xpto"}'
check PUT    /tasks/1                   200 '{"status":"in_progress","priority":2}'
check PUT    /tasks/1                   400 '{"priority":9}'
check GET    "/tasks/search?q=login"    200
check GET    "/tasks/search?status=pending&priority=1" 200
check GET    /tasks/stats               200
check DELETE /tasks/11                  200
# Users
check GET    /users                     200
check GET    /users/1                   200
check GET    /users/9999                404
check POST   /users                     201 '{"name":"Ana","email":"ana@email.com","password":"segredo123"}'
check POST   /users                     409 '{"name":"Ana","email":"ana@email.com","password":"segredo123"}'
check POST   /users                     400 '{"name":"Bad","email":"invalido","password":"segredo123"}'
check PUT    /users/2                   200 '{"name":"Maria S."}'
check GET    /users/1/tasks             200
check POST   /login                     200 '{"email":"joao@email.com","password":"1234"}'
check POST   /login                     401 '{"email":"joao@email.com","password":"errada"}'
check DELETE /users/4                   200
# Reports & categories
check GET    /reports/summary           200
check GET    /reports/user/1            200
check GET    /reports/user/9999         404
check GET    /categories                200
check POST   /categories                201 '{"name":"QA","color":"#123456"}'
check PUT    /categories/5              200 '{"name":"Quality"}'
check DELETE /categories/5              200

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
