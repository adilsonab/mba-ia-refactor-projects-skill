#!/usr/bin/env bash
# Smoke test do Projeto 1 (code-smells-project) — API de E-commerce Flask.
# Uso: bash scripts/smoke-project-1.sh [BASE_URL]
# Pré-requisito: a API rodando (python app.py) com o banco recém-criado (apague loja.db antes).
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
  curl -s -X POST -H "Content-Type: application/json" -d "{\"email\":\"$1\",\"senha\":\"$2\"}" "$BASE/login" \
    | sed -n 's/.*"token": *"\([^"]*\)".*/\1/p'
}

cors_closed() { # AP-10: sem CORS_ORIGINS, origem externa não recebe Access-Control-Allow-Origin
  local headers; headers=$(curl -s -D - -o /dev/null -H "Origin: http://evil.example" "$BASE/")
  if echo "$headers" | grep -qi '^access-control-allow-origin'; then FAIL=$((FAIL+1)); echo "  FAIL CORS aberto para origem externa"
  else PASS=$((PASS+1)); echo "  OK   CORS fechado por padrão (origem externa sem Access-Control-Allow-Origin)"; fi
}

echo "Smoke test: $BASE"
ADMIN=$(login admin@loja.com admin123)   # seed: tipo admin (id 1)
JOAO=$(login joao@email.com 123456)      # seed: tipo cliente (id 2)
[ -n "$ADMIN" ] && [ -n "$JOAO" ] && echo "  tokens obtidos via POST /login" || echo "  FALHA ao obter tokens"

check GET    /                         200
check GET    /health                   200
check GET    /produtos                 200
check GET    "/produtos/busca?q=mouse" 200
check GET    /produtos/1               200
check GET    /produtos/9999            404
check POST   /produtos                 201 '{"nome":"Produto Teste","preco":10.5,"estoque":5,"categoria":"geral"}' "$ADMIN"
check POST   /produtos                 400 '{"nome":"Sem preco"}' "$ADMIN"
check PUT    /produtos/1               200 '{"nome":"Notebook Gamer","preco":5999.99,"estoque":10,"categoria":"informatica"}' "$ADMIN"
check DELETE /produtos/10              200 "" "$ADMIN"
check GET    /usuarios                 200 "" "$ADMIN"
check GET    /usuarios/1               200 "" "$ADMIN"
check POST   /usuarios                 201 '{"nome":"Novo","email":"novo@email.com","senha":"abc12345"}'
check POST   /login                    200 '{"email":"joao@email.com","senha":"123456"}'
check POST   /login                    401 '{"email":"joao@email.com","senha":"errada"}'
check POST   /pedidos                  201 '{"usuario_id":2,"itens":[{"produto_id":2,"quantidade":1}]}' "$JOAO"
check POST   /pedidos                  400 '{"usuario_id":2,"itens":[]}' "$JOAO"
check GET    /pedidos                  200 "" "$ADMIN"
check GET    /pedidos/usuario/2        200 "" "$JOAO"
check PUT    /pedidos/1/status         200 '{"status":"aprovado"}' "$ADMIN"
check PUT    /pedidos/1/status         400 '{"status":"invalido"}' "$ADMIN"
check GET    /relatorios/vendas        200 "" "$ADMIN"

echo "Autorização (AP-11):"
LOGIN=$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"joao@email.com","senha":"123456"}' "$BASE/login")
assert_contains "login devolve token assinado em dados.token" "$LOGIN" '"token": *"[A-Za-z0-9_.-]\{20,\}"'
check GET    /usuarios                 401
check POST   /pedidos                  401 '{"usuario_id":2,"itens":[{"produto_id":2,"quantidade":1}]}'
check GET    /relatorios/vendas        401 "" "${ADMIN}x"
check POST   /admin/reset-db           401
check GET    /usuarios                 403 "" "$JOAO"
check GET    /usuarios/1               403 "" "$JOAO"
check GET    /usuarios/2               200 "" "$JOAO"
check POST   /pedidos                  403 '{"usuario_id":3,"itens":[{"produto_id":2,"quantidade":1}]}' "$JOAO"
check GET    /pedidos/usuario/3        403 "" "$JOAO"
check GET    /pedidos                  403 "" "$JOAO"
check PUT    /pedidos/1/status         403 '{"status":"cancelado"}' "$JOAO"
check DELETE /produtos/1               403 "" "$JOAO"
check GET    /relatorios/vendas        403 "" "$JOAO"
check POST   /admin/reset-db           403 "" "$JOAO"
# Cadastro público com tipo=admin: o servidor grava sempre "cliente"
check POST   /usuarios                 201 '{"nome":"Mallory","email":"mallory@email.com","senha":"abc12345","tipo":"admin"}'
MALLORY_LOGIN=$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"mallory@email.com","senha":"abc12345"}' "$BASE/login")
assert_contains "cadastro público com tipo=admin vira tipo=cliente" "$MALLORY_LOGIN" '"tipo": *"cliente"'
MALLORY=$(echo "$MALLORY_LOGIN" | sed -n 's/.*"token": *"\([^"]*\)".*/\1/p')
check GET    /usuarios                 403 "" "$MALLORY"
echo "Correções v1.3 (AP-10 defaults seguros, AP-16 404, AP-20 soft delete):"
cors_closed
check PUT    /pedidos/9999/status      404 '{"status":"aprovado"}' "$ADMIN"
check POST   /pedidos                  201 '{"usuario_id":2,"itens":[{"produto_id":3,"quantidade":1}]}' "$JOAO"
check DELETE /produtos/3               200 "" "$ADMIN"
check GET    /produtos/3               404
check DELETE /produtos/3               404 "" "$ADMIN"
check POST   /pedidos                  400 '{"usuario_id":2,"itens":[{"produto_id":3,"quantidade":1}]}' "$JOAO"
HIST=$(curl -s -H "Authorization: Bearer $JOAO" "$BASE/pedidos/usuario/2")
assert_contains "histórico do pedido mantém o nome do produto excluído" "$HIST" 'Teclado Mec'
# Operação destrutiva por último: admin autenticado pode resetar
check POST   /admin/reset-db           200 "" "$ADMIN"

echo "Resultado: $PASS OK, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
