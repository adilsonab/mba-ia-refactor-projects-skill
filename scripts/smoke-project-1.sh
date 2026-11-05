#!/usr/bin/env bash
# Smoke test do Projeto 1 (code-smells-project) — API de E-commerce Flask.
# Uso: bash scripts/smoke-project-1.sh [BASE_URL]
# Pré-requisito: a API rodando (python app.py) com o banco recém-criado (apague loja.db antes).
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
check GET    /                         200
check GET    /health                   200
check GET    /produtos                 200
check GET    "/produtos/busca?q=mouse" 200
check GET    /produtos/1               200
check GET    /produtos/9999            404
check POST   /produtos                 201 '{"nome":"Produto Teste","preco":10.5,"estoque":5,"categoria":"geral"}'
check POST   /produtos                 400 '{"nome":"Sem preco"}'
check PUT    /produtos/1               200 '{"nome":"Notebook Gamer","preco":5999.99,"estoque":10,"categoria":"informatica"}'
check DELETE /produtos/10              200
check GET    /usuarios                 200
check GET    /usuarios/1               200
check POST   /usuarios                 201 '{"nome":"Novo","email":"novo@email.com","senha":"abc12345"}'
check POST   /login                    200 '{"email":"joao@email.com","senha":"123456"}'
check POST   /login                    401 '{"email":"joao@email.com","senha":"errada"}'
check POST   /pedidos                  201 '{"usuario_id":2,"itens":[{"produto_id":2,"quantidade":1}]}'
check POST   /pedidos                  400 '{"usuario_id":2,"itens":[]}'
check GET    /pedidos                  200
check GET    /pedidos/usuario/2        200
check PUT    /pedidos/1/status         200 '{"status":"aprovado"}'
check PUT    /pedidos/1/status         400 '{"status":"invalido"}'
check GET    /relatorios/vendas        200

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
