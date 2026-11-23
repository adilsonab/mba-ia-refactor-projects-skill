# Execução da skill `/refactor-arch` — code-smells-project

Saída integral de uma sessão nova e não interativa do Claude Code (`claude -p`), sem contexto anterior, rodando sobre o
**código original** (commit inicial `6d1ce62`) com a versão final da skill. Comando:

```bash
cd code-smells-project
claude "/refactor-arch ../reports/audit-project-1.md"
```

- Fases 1 e 2: 18 turnos, 6.8 min. A sessão parou em
  `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e **nenhum arquivo do projeto tinha sido alterado**
  (conferido com `diff -r` contra uma cópia do original antes de responder).
- Resposta enviada: `y`.
- Fase 3: 69 turnos, 12.2 min.

---

## Fases 1 e 2 (saída impressa, inclui o relatório de auditoria)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (versão não declarada; 3.14.5 no ambiente)
Framework:     Flask 3.1.1
Dependencies:  flask==3.1.1, flask-cors==5.0.1, sqlite3 (stdlib)
Database:      SQLite (loja.db) via sqlite3, SQL cru
Domain:        API de e-commerce (produtos, usuários, pedidos, itens de pedido, relatório de vendas)
Architecture:  Camadas nominais / parcialmente organizada: existem controllers.py, models.py e database.py, mas models.py contém regras de negócio (total, estoque, desconto), controllers.py e app.py executam SQL, e database.py faz conexão global, schema e seed
Source files:  4 files analyzed (~780 lines)
DB tables:     produtos, usuarios, pedidos, itens_pedido
Endpoints:     19 (GET /, GET/POST /produtos, GET /produtos/busca, GET/PUT/DELETE /produtos/<id>,
               GET/POST /usuarios, GET /usuarios/<id>, POST /login, GET/POST /pedidos,
               GET /pedidos/usuario/<id>, PUT /pedidos/<id>/status, GET /relatorios/vendas,
               GET /health, POST /admin/reset-db, POST /admin/query)
Run command:   pip install -r requirements.txt && python app.py  (porta 5000; o seed roda sozinho no primeiro boot)
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask (3.1.1)
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-23

## Summary
CRITICAL: 6 | HIGH: 7 | MEDIUM: 7 | LOW: 6
```

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-01 SQL Injection | models.py:28, 47-50, 109-111, 126-129, 289-297 (+ mais 15) |
| 2 | CRITICAL | AP-02 Segredos hardcoded | app.py:7, controllers.py:289 |
| 3 | CRITICAL | AP-03 Senhas em texto puro | models.py:126-129, 109-111, database.py:75-83 |
| 4 | CRITICAL | AP-04 Exposição de dados sensíveis | models.py:83, 99, controllers.py:285-289, … |
| 5 | CRITICAL | AP-05 `/admin/query` (SQL livre) e `/admin/reset-db` abertos | app.py:59-78, 47-57 |
| 6 | CRITICAL | AP-06 God File | models.py, controllers.py, app.py, database.py |
| 7 | HIGH | AP-07 Regra de negócio no model/controller | models.py:137-146, 256-262, controllers.py:43-54, 242-250 |
| 8 | HIGH | AP-08 SQL fora da camada Model | controllers.py:266-274, app.py:49-55, 66-76 |
| 9 | HIGH | AP-09 Conexão global mutável | database.py:4-11 |
| 10 | HIGH | AP-10 Configuração insegura | app.py:8, 9, 88, database.py:5 |
| 11 | HIGH | AP-11 Sem autenticação ou autorização | controllers.py:167-186, app.py:11-30, 47, controllers.py:195 |
| 12 | HIGH | AP-12 Pedido sem transação | models.py:133-169 |
| 13 | HIGH | AP-13 Notificações inline | controllers.py:208-210, 247-250 |
| 14 | MEDIUM | AP-14 Query N+1 | models.py:186-199, 218-231, 139-141, 154-156 |
| 15 | MEDIUM | AP-15 Lógica duplicada | models.py:171-201 × 203-233, controllers.py:28-50 × 72-90 |
| 16 | MEDIUM | AP-16 Validação de entrada ausente | controllers.py:43-50, 87-90, 169-171, … |
| 17 | MEDIUM | AP-17 try/except com `str(e)` em todo handler | controllers.py (16 handlers), app.py:77-78 |
| 18 | MEDIUM | AP-18 Dependências vulneráveis | requirements.txt:1-2 |
| 19 | MEDIUM | AP-19 Agregação ineficiente | models.py:239-254, controllers.py:268-274 |
| 20 | MEDIUM | AP-20 Itens de pedido órfãos | models.py:65-70 |
| 21 | LOW | AP-21 Magic numbers | models.py:257-262, controllers.py:52, 242 |
| 22 | LOW | AP-22 `print` como logging | controllers.py, app.py |
| 23 | LOW | AP-23 `id` sombreando o built-in, `cursor2/3` | controllers.py:14, models.py:24, 187-193 |
| 24 | LOW | AP-24 Imports não usados | database.py:2, models.py:2, controllers.py:268 |
| 25 | LOW | AP-25 Código verboso (filtro `preco_min=0` é ignorado) | controllers.py:200, 118-121 |
| 26 | LOW | AP-26 Corpo de erro inconsistente | controllers.py:20 × 70, 292 |

**Confirmei estes pontos executando em um banco temporário. Nenhum arquivo do projeto foi alterado:**
- **#1 Login sem senha:** `POST /login` com `email = "admin@loja.com' --"` e qualquer senha retorna `Login OK` como Admin.
- **#4 Senha exposta:** `GET /usuarios/1`, público, devolve `"senha": "admin123"`.
- **#5 SQL livre:** `POST /admin/query`, sem autenticação, devolve as senhas de todos os usuários.
- **#16 Erros 500 e status errado:**
  - `preco` enviado como string → 500.
  - Item de pedido sem `quantidade` → 500.
  - `PUT /pedidos/999/status` (pedido inexistente) → 200.

**Verificação em tempo de execução (#18):**
- **APIs deprecated:** nenhuma detectada. Rodei com `python -W default` e não apareceu nenhum `DeprecationWarning`. Só apareceu um `ResourceWarning` de conexão SQLite nunca fechada, que já está coberto em #9.
- **Dependências:** o `pip-audit` encontrou falhas conhecidas em `flask 3.1.1` (corrigida na 3.1.3) e em `flask-cors 5.0.1` (corrigida na 6.0.0).

**O que a refatoração vai entregar, nos pontos que mais mudam o comportamento:**
- **Autenticação (#11):** o login passa a retornar um campo novo `token`, assinado e com validade de 1h. As rotas ficam divididas em públicas, de usuário autenticado (dono ou admin) e de admin.
- **`/admin/query` (#5):** a rota é removida e passa a responder 404.
- **Configuração (#10):** debug desligado, servidor escutando só em `127.0.0.1` e CORS fechado por padrão.
- **Exclusão de produto (#20):** passa a ser um soft delete usando a coluna `ativo`, que já existe.
- **Pendente de decisão de negócio (#16):** se o cancelamento de um pedido deve devolver o estoque e quais trocas de status são permitidas. Até lá, o comportamento atual continua.

O relatório completo, com File, Description, Impact e Recommendation de cada um dos 26 pontos, está em `C:\Users\adilsonbarbosa\AppData\Local\Temp\claude\6f98b0225f573235\153428c6-1893-4665-b768-c0c4d978f879\scratchpad\final\code-smells-project\reports\audit-project-1.md`.

```
================================
Total: 26 findings
================================
```

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---

## Fase 3 (resumo impresso pela skill)

```
================================
PHASE 3: REFACTORING COMPLETE
================================
```

## New Project Structure
```
code-smells-project/
├── app.py                      # composition root: create_app(); "python app.py" mantido
├── .env.example · README.md · requirements.txt
├── config/        settings.py (ambiente, defaults seguros) · constants.py
├── database.py                 # conexão por requisição (flask.g), transaction()
├── errors.py                   # ValidationError / Unauthorized / Forbidden / NotFound
├── models/        produto_model · usuario_model · pedido_model · sistema_model · passwords · seed
├── services/      produto · usuario · auth · pedido · relatorio · notification
├── controllers/   produto · usuario · pedido · relatorio · sistema · validators
├── routes/        produto · usuario · pedido · sistema (matriz de acesso visível)
└── middlewares/   auth.py · error_handler.py
```

## Findings Addressed
- **#1 [CRITICAL] SQL Injection:** 100% das queries parametrizadas em `models/*`. A busca é montada com cláusulas fixas e uma lista de parâmetros. O login com `' --` agora recebe 401.
- **#2 [CRITICAL] Segredos hardcoded:** `SECRET_KEY` vem do ambiente; sem ela, uma chave aleatória é gerada e um aviso vai para o log (`config/settings.py`). Criado o `.env.example`.
- **#3 [CRITICAL] Senhas em texto puro:**
  - Hash scrypt no cadastro e no seed (`models/passwords.py`).
  - O login busca por email e valida com `check_password_hash`.
  - Um banco antigo com senhas em texto puro é convertido para hash no boot (testado).
- **#4 [CRITICAL] Dados sensíveis:**
  - Respostas de usuário sem `senha`.
  - `/health` sem `secret_key`, `debug`, `db_path` e `ambiente`.
  - O log registra só o id do usuário.
  - Erros 500 devolvem mensagem genérica.
- **#5 [CRITICAL] Endpoints perigosos:** `POST /admin/query` removido (404). `POST /admin/reset-db` exige admin e roda em transação.
- **#6 [CRITICAL] God File:** decomposto nas camadas acima. `controllers.py` e `models.py` antigos foram removidos.
- **#7 [HIGH] Regra de negócio fora do lugar:** total e estoque em `pedido_service`, desconto em `relatorio_service`, regras de produto nos validators. Mesmos valores de antes.
- **#8 [HIGH] SQL fora da camada Model:** health e reset usam `models/sistema_model.py`.
- **#9 [HIGH] Estado global:** uma conexão por requisição com `teardown_appcontext`. Não existe mais conexão global nem `check_same_thread=False`.
- **#10 [HIGH] Configuração insegura:** debug desligado, `HOST=127.0.0.1`, `PORT=5000`, `DB_PATH=loja.db`, `CORS_ORIGINS` vazio e `create_app()`.
- **#11 [HIGH] Autenticação:**
  - O login devolve um token assinado (HMAC-SHA256, validade de 3600s) no campo novo `token`.
  - `login_required`/`admin_required` validam o token e releem o usuário do banco.
  - O cadastro público sempre grava `tipo=cliente`.
  - Matriz de acesso:
    - **Público:** `GET /`, `/health`, `GET /produtos*`, `POST /usuarios`, `POST /login`.
    - **Dono ou admin:** `GET /usuarios/<id>`, `GET /pedidos/usuario/<id>`, `POST /pedidos`.
    - **Admin:** escrita em produtos, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `/relatorios/vendas`, `/admin/reset-db`.
- **#12 [HIGH] Pedido sem transação:** `BEGIN IMMEDIATE` com débito condicional `estoque >= ?` e rollback em qualquer erro (`models/pedido_model.py`).
- **#13 [HIGH] Notificações inline:** `NotificationService` com `notificar_pedido_criado` e `notificar_status_pedido`, injetado no `PedidoService`.
- **#14 [MEDIUM] N+1:** a listagem de pedidos é uma única query com LEFT JOIN. A criação de pedido busca os produtos em uma única query.
- **#15 [MEDIUM] Duplicação:** uma só função de listagem de pedidos, um serializador por model e um validador de produto usado na criação e na atualização.
- **#16 [MEDIUM] Validação:**
  - Tipo errado, item inválido, quantidade ≤ 0, filtro de preço não numérico, email inválido ou duplicado e corpo ausente agora dão 400.
  - Status de pedido inexistente dá 404.
  - A devolução de estoque no cancelamento ficou em Pending.
- **#17 [MEDIUM] Tratamento de erros:** error handler central (`middlewares/error_handler.py`). Os 404/405 também respondem em JSON e os `try/except` dos handlers foram removidos.
- **#18 [MEDIUM] Dependências:** `flask==3.1.3`, `flask-cors==6.0.0` e `itsdangerous==2.2.0` fixado.
- **#19 [MEDIUM] Agregação:** o relatório e o health usam uma única query cada.
- **#20 [MEDIUM] Órfãos:** soft delete pela coluna `ativo`. O histórico de pedidos mantém o nome do produto ("Mouse Wireless" após a exclusão, verificado).
- **#21 [LOW] Magic numbers:** movidos para `config/constants.py`.
- **#22 [LOW] print:** substituído por `logging`, com `LOG_LEVEL` padrão `INFO`.
- **#23 [LOW] Nomenclatura:** `id` virou `produto_id`/`usuario_id`; `cursor2`/`cursor3` foram eliminados.
- **#24 [LOW] Código morto:** removidos `import os`, `import sqlite3` e o `SELECT 1` redundante.
- **#25 [LOW] Código verboso:** `if not itens`, filtros de preço com `is not None` (`preco_min=0` agora funciona) e `COALESCE`.
- **#26 [LOW] Formato de resposta:** o corpo de erro é sempre `{"erro", "sucesso": false}`. O health em erro devolve `{"status":"erro","database":"disconnected"}`.

## Security Contract Changes
- **Token obrigatório nas rotas protegidas,** conforme a matriz do #11: 401 sem token, 403 sem papel. O login ganhou o campo `token`, sem mudar as outras chaves.
- **`POST /pedidos` sem `usuario_id`:** antes dava 400; agora usa o usuário do token.
- **Campos removidos:** `senha` das respostas de usuário; `secret_key`, `debug`, `db_path` e `ambiente` do `/health`.
- **`POST /admin/query`** foi removido e responde 404.
- **Defaults seguros:** CORS fechado, bind em `127.0.0.1` e debug desligado.
- **`sucesso: false` nos erros:** campo adicionado; status HTTP e chave `erro` continuam iguais.
- **De 500 para 400** quando a entrada é inválida, e **de 200 falso para 404** em `PUT /pedidos/<inexistente>/status`.
- **Produto excluído vira inativo** (soft delete) em vez de ser apagado; a resposta do `DELETE` é a mesma.
- **Tokens e reinício:** sem `SECRET_KEY` definida, os tokens deixam de valer a cada reinício do servidor. Isso está documentado no README.

## Pending (requires human decision)
- **#16:** se o cancelamento de um pedido deve devolver o estoque e quais transições de status são permitidas são decisões de negócio. O comportamento original foi mantido.

## Validation
- ✓ Application boots without errors (`python app.py`): processo vivo, log com "Debug mode: off" e "Running on http://127.0.0.1:5000", zero tracebacks.
- ✓ All endpoints respond correctly (35/36 requests match the baseline status). A única divergência é `POST /admin/query` → 404, intencional.
  - As chaves de topo batem em 23/36. As 13 diferenças são as mudanças de segurança e aditivas listadas acima.
  - Pedidos, totais, itens, relatório e estoque têm valores idênticos ao baseline.
- ✓ Authentication enforced: 20 checagens passaram, entre elas:
  - Sem token → 401, token adulterado → 401, cliente em rota admin → 403.
  - Recurso de outro usuário → 403.
  - Cadastro com `tipo: admin` grava `cliente`.
- ✓ Secure defaults: debug desligado e bind `127.0.0.1` no log. Uma requisição com `Origin: http://evil.example` não recebe `Access-Control-Allow-Origin`. Com `CORS_ORIGINS` definido, só a origem configurada é liberada.
- ✓ No deprecated API warnings at runtime (com `-W default`); `pip-audit -r requirements.txt` → "No known vulnerabilities found".
- ✓ No CRITICAL/HIGH anti-patterns remaining (AP-10 e AP-11 incluídos). O Grep da re-auditoria só encontrou f-strings com constantes fixas, que não são injection.
- ✓ Every Recommendation delivered or declared Pending (26/26 findings reconciled).
  - O texto de #2, #6, #8, #14, #15 e #21 no relatório foi corrigido: citava nomes de arquivo e função diferentes dos que foram criados, ou "2 queries" onde foi entregue 1.
  - No #13, quem mudou foi o código, para usar os nomes de método prometidos.

```
================================
```

**Mudanças no projeto** (não é um repositório git, então não executei nenhum comando de versionamento):
- **Alterados:** `app.py`, `database.py`, `README.md`, `requirements.txt`.
- **Removidos:** `controllers.py`, `models.py`.
- **Criados:** `.env.example`, `errors.py` e os pacotes `config/`, `models/`, `services/`, `controllers/`, `routes/`, `middlewares/`.
- **Relatório:** `C:\Users\adilsonbarbosa\AppData\Local\Temp\claude\6f98b0225f573235\153428c6-1893-4665-b768-c0c4d978f879\scratchpad\final\code-smells-project\reports\audit-project-1.md` (com as correções de texto acima).

O `loja.db` gerado nos testes foi apagado; ele será recriado com o seed no próximo boot.
