================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask (flask==3.1.1, flask-cors==5.0.1)
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 6 | HIGH: 7 | MEDIUM: 6 | LOW: 6

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-01 SQL Injection | models.py:28, models.py:47-50, models.py:109-111, models.py:126-129, models.py:279-281, models.py:289-299 (+more) |
| 2 | CRITICAL | AP-02 Hardcoded credentials/secrets | app.py:7, controllers.py:289 |
| 3 | CRITICAL | AP-03 Insecure password storage | models.py:109-111, models.py:126-129, database.py:75-83 |
| 4 | CRITICAL | AP-04 Sensitive data exposure | models.py:83, models.py:99, controllers.py:285-289, controllers.py:161, controllers.py:179-182 |
| 5 | CRITICAL | AP-05 Arbitrary execution / open destructive endpoint | app.py:47-57, app.py:59-78 |
| 6 | CRITICAL | AP-06 God File | models.py:1-314, database.py:7-86 |
| 7 | HIGH | AP-07 Business rules in controller/model | models.py:137-146, models.py:256-262, controllers.py:43-54, controllers.py:247-250 |
| 8 | HIGH | AP-08 Data access outside Model | app.py:49-55, app.py:66-76, controllers.py:266-274 |
| 9 | HIGH | AP-09 Mutable global state | database.py:4-11 |
| 10 | HIGH | AP-10 Insecure configuration | app.py:8, app.py:9, app.py:88, controllers.py:286-288, database.py:5 |
| 11 | HIGH | AP-11 Missing authentication/authorization | app.py:16, app.py:18, app.py:26, app.py:28, app.py:47, app.py:59, controllers.py:180 |
| 12 | HIGH | AP-12 Multi-write without transaction | models.py:133-169 |
| 13 | HIGH | AP-13 Coupling to side effects | controllers.py:208-210, controllers.py:247-250 |
| 14 | MEDIUM | AP-14 N+1 queries | models.py:139-141, models.py:154-156, models.py:187-199, models.py:219-231 |
| 15 | MEDIUM | AP-15 Duplicated logic | models.py:171-201 × models.py:203-233, models.py:12-21/31-40/304-313, controllers.py:28-46 × controllers.py:72-90 |
| 16 | MEDIUM | AP-16 Missing/incomplete input validation | controllers.py:43-46, controllers.py:81-90, controllers.py:169-170, controllers.py:196-201, controllers.py:239-245, models.py:144 |
| 17 | MEDIUM | AP-17 Decentralized error handling | controllers.py:10-12, controllers.py:21-22, ... (16 handlers), app.py:77-78 |
| 18 | MEDIUM | AP-19 Inefficient aggregation | models.py:239-254, controllers.py:269-274 |
| 19 | MEDIUM | AP-20 Manual referential integrity / orphans | models.py:65-70, database.py:36-53, models.py:196 |
| 20 | LOW | AP-21 Magic numbers and strings | models.py:257-262, controllers.py:47-50, controllers.py:52, controllers.py:242, app.py:88 |
| 21 | LOW | AP-22 print as logging | controllers.py:8, controllers.py:208-210, app.py:56, ... |
| 22 | LOW | AP-23 Poor naming / shadowed built-ins | controllers.py:14, controllers.py:56, models.py:24, models.py:187-191 |
| 23 | LOW | AP-24 Dead code / unused imports | models.py:2, database.py:2 |
| 24 | LOW | AP-25 Verbose / non-idiomatic code | models.py:9-22, controllers.py:200, models.py:63, models.py:70 |
| 25 | LOW | AP-26 Inconsistent response format | controllers.py:20, controllers.py:70, controllers.py:183, controllers.py:292 |

## Findings

### #1 [CRITICAL] AP-01 — SQL Injection
File: models.py:28, models.py:47-50, models.py:57-61, models.py:109-111, models.py:126-129, models.py:279-281, models.py:289-299, models.py:68 (+11 occurrences: models.py:92, 140, 148-151, 155, 157-161, 163-166, 174, 188, 192, 220, 224)
Description: Virtually every query is built via string concatenation with request data, e.g. `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` (login), `"UPDATE pedidos SET status = '" + novo_status + "' ..."`, and the incremental search `query += " AND (nome LIKE '%" + termo + "%' ..."` fed directly from `?q=` and `?categoria=`.
Impact: Login bypass with `email = "admin@loja.com' --"`; `GET /produtos/busca?q=' UNION SELECT ...` reads any table (including passwords); `POST /produtos` / `POST /usuarios` with a quote in `nome` can alter or destroy data.
Recommendation: Use parameterized queries (`?` + tuple) for all data access, concentrated in the Model layer; build the search filter with a list of clauses + parameter list (→ T01).

### #2 [CRITICAL] AP-02 — Hardcoded credentials and secrets
File: app.py:7, controllers.py:289
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` is a literal in the code, and the same value is duplicated as a literal in the `/health` response (`"secret_key": "minha-chave-super-secreta-123"`).
Impact: Anyone with repository access (or who calls `/health`) knows the key used to sign sessions/cookies; rotating it requires a code change.
Recommendation: Read `SECRET_KEY` from an environment variable in a config module, with a dev-only default; never echo it (→ T02).

### #3 [CRITICAL] AP-03 — Insecure password storage
File: models.py:109-111, models.py:126-129, database.py:75-83
Description: `criar_usuario` stores `senha` exactly as received (`INSERT INTO usuarios (... senha ...) VALUES ('...' + senha + '...')`); login compares plaintext in SQL (`WHERE email = '...' AND senha = '...'`); the seed inserts `"admin123"`, `"123456"`, `"senha123"` in plaintext.
Impact: Any DB leak (or the open `/admin/query` / `GET /usuarios`) exposes every user's password directly.
Recommendation: Hash with `werkzeug.security.generate_password_hash` on create/seed, look up by email and verify with `check_password_hash` on login; migrate existing plaintext rows on boot (→ T03).

### #4 [CRITICAL] AP-04 — Sensitive data exposure (responses and logs)
File: models.py:83, models.py:99, controllers.py:285-289, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:12 (+ every `str(e)` response, see #17)
Description: The user serializers include `"senha": row["senha"]`, so the public `GET /usuarios` and `GET /usuarios/<id>` return every password. `GET /health` returns `"secret_key"`, `"debug": True`, `"db_path": "loja.db"`. Logs print user e-mails (`print("Login falhou: " + email)`). Errors return `str(e)` (internal SQL/exception text) to the client.
Impact: Trivial exploitation through a public endpoint with no authentication: full credential dump with a single GET; internal configuration leak helps attackers.
Recommendation: Remove `senha` from every serializer (a dedicated `to_public_dict`), remove `secret_key`/`debug`/`db_path` from `/health`, log without PII, return a generic error message on 500 (→ T04).

### #5 [CRITICAL] AP-05 — Arbitrary execution / open destructive endpoint
File: app.py:47-57, app.py:59-78
Description: `POST /admin/query` runs `cursor.execute(dados.get("sql"))` with any SQL sent by the client and commits it; `POST /admin/reset-db` runs `DELETE FROM` on all 4 tables. Neither has any authentication.
Impact: Any network client (the server listens on `0.0.0.0`) can read, alter or wipe the whole database.
Recommendation: Remove `/admin/query`; protect `/admin/reset-db` (e.g. enable it only with an admin token from the environment, or only in development) (→ T16).

### #6 [CRITICAL] AP-06 — God File
File: models.py:1-314, database.py:7-86
Description: `models.py` (314 lines) mixes 4 domains (products, users, orders, reports) and 3 responsibilities: SQL access, business rules (stock check and order total at lines 139-146, discount tiers at 256-262) and JSON serialization. `database.py::get_db` (80 lines) handles connection, schema creation and seeding in one function.
Impact: Any change touches a shared file; rules cannot be tested without a database; high merge-conflict and regression risk.
Recommendation: Split into `models/` per entity (data access only), `services/` (orders, reports), and `database/` with connection, schema and seed separated (→ T05 + T17).

### #7 [HIGH] AP-07 — Business rules in controller/model (Fat Controller)
File: models.py:137-146, models.py:256-262, controllers.py:43-54, controllers.py:247-250
Description: Order total calculation and stock check (`total = total + (produto["preco"] * item["quantidade"])`, `if produto["estoque"] < item["quantidade"]`) live in the data-access function; the discount rule (`if faturamento > 10000: desconto = faturamento * 0.1 ...`) lives in the model; product domain validation (price, category list) and post-status-change actions live in the HTTP handlers.
Impact: Rules are not reusable or unit-testable; the model depends on domain decisions; the controller grows with every new rule.
Recommendation: Move order creation and the sales report into `services/` (`OrderService`, `ReportService`); keep only input reading and status choice in controllers (→ T06).

### #8 [HIGH] AP-08 — Data access outside the Model layer
File: app.py:49-55, app.py:66-76, controllers.py:266-274
Description: `app.py` calls `get_db()` + `cursor.execute("DELETE FROM ...")` directly in the reset route; `controllers.health_check` runs `SELECT COUNT(*)` on 3 tables directly.
Impact: SQL spread across 3 layers; schema changes require hunting queries across the code.
Recommendation: Move the counts and the reset to Model/repository functions called by the controller (→ T05/T06).

### #9 [HIGH] AP-09 — Mutable global state
File: database.py:4-11
Description: `db_connection = None` at module level, mutated with `global db_connection`, and opened with `sqlite3.connect(db_path, check_same_thread=False)` — a single connection shared by every request/thread.
Impact: Under concurrency (the Flask dev server is threaded) transactions from different requests mix: one request's `commit()` can persist another's partial writes; possible `ProgrammingError`/inconsistency; hard to isolate in tests.
Recommendation: One connection per request via `flask.g` + `teardown_appcontext`, with the DB path from config (→ T10).

### #10 [HIGH] AP-10 — Insecure configuration
File: app.py:8, app.py:9, app.py:88, controllers.py:286-288, database.py:5
Description: `app.config["DEBUG"] = True` and `app.run(host="0.0.0.0", port=5000, debug=True)` hardcoded (Werkzeug debugger exposed on the network); `CORS(app)` with no origin restriction; `db_path = "loja.db"` and port fixed; `/health` hardcodes `"ambiente": "producao"` while running in debug; no app factory.
Impact: The interactive debugger allows remote code execution if an exception page is reachable; any origin can call the API from a browser.
Recommendation: Config module reading `FLASK_DEBUG`, `HOST`, `PORT`, `DATABASE_PATH`, `CORS_ORIGINS` from the environment with safe defaults; `create_app()` factory (→ T02 + T17).

### #11 [HIGH] AP-11 — Missing authentication/authorization
File: app.py:16, app.py:18, app.py:26, app.py:28, app.py:47, app.py:59, controllers.py:180
Description: No route has any authentication: `DELETE /produtos/<id>`, `GET /usuarios` (full listing), `PUT /pedidos/<id>/status`, `GET /relatorios/vendas` (financial data) and the `/admin/*` routes are public. `POST /login` returns only user data, with no token/session, so nothing can be protected afterwards.
Impact: Any client can delete products, approve/cancel orders and read revenue figures. (The admin endpoints are already counted as CRITICAL in #5.)
Recommendation: Introduce token-based auth and an admin-role decorator. Requiring auth on routes that are public today breaks the contract → human decision (→ T16).

### #12 [HIGH] AP-12 — Multi-write operation without transaction
File: models.py:133-169
Description: `criar_pedido` checks stock (lines 139-145), then does `INSERT pedidos`, N × `INSERT itens_pedido` and N × `UPDATE produtos SET estoque = estoque - ...` with a single `commit()` at the end and no `rollback` on exceptions; the stock check and the debit are separate queries (check-then-act).
Impact: An exception midway leaves pending writes on the shared connection (#9), which the next request's commit persists → order without items or stock debited without an order; concurrent orders can drive stock negative.
Recommendation: Wrap it in an explicit transaction (`with conn:` / `BEGIN ... COMMIT/ROLLBACK`) and debit with `UPDATE ... SET estoque = estoque - ? WHERE id = ? AND estoque >= ?`, checking `rowcount` (→ T09).

### #13 [HIGH] AP-13 — Tight coupling to side effects
File: controllers.py:208-210, controllers.py:247-250
Description: Notifications are "sent" inline in the handler: `print("ENVIANDO EMAIL: Pedido ...")`, `print("ENVIANDO SMS: ...")`, `print("ENVIANDO PUSH: ...")` and `print("NOTIFICAÇÃO: Pedido ... cancelado. Devolver estoque.")` — with no abstraction (and the stock return mentioned in the message never happens).
Impact: Swapping to a real channel requires editing the controller; impossible to mock in tests; an "action" (returning stock) that exists only as a log line.
Recommendation: Injectable `NotificationService` (interface + logging implementation) called by the order service (→ T15).

### #14 [MEDIUM] AP-14 — N+1 query
File: models.py:187-199, models.py:219-231, models.py:139-141, models.py:154-156
Description: For each order, `SELECT * FROM itens_pedido WHERE pedido_id = ...` (`cursor2`), and for each item `SELECT nome FROM produtos WHERE id = ...` (`cursor3`). In `criar_pedido` each product is fetched twice (validation loop and insert loop).
Impact: `GET /pedidos` with P orders and I items runs 1 + P + P·I queries; degrades linearly as data grows.
Recommendation: A single query with `JOIN itens_pedido` + `LEFT JOIN produtos`, grouped in memory by `pedido_id`; load the order's products once with `WHERE id IN (...)` (→ T07).

### #15 [MEDIUM] AP-15 — Duplicated logic / parallel implementations
File: models.py:171-201, models.py:203-233, models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, controllers.py:28-46, controllers.py:72-90
Description: `get_pedidos_usuario` and `get_todos_pedidos` are identical except for the `WHERE`; the product dict is copied 3 times and the user dict twice; required-field/price/stock validation is copied between `criar_produto` and `atualizar_produto` (and diverges: update does not validate name or category).
Impact: Fixes applied in only one copy (as already happened with validation) → inconsistent behavior.
Recommendation: A single serializer per entity, a single order function with an optional filter, a shared validator for create/update (→ T06 + T13).

### #16 [MEDIUM] AP-16 — Missing or incomplete input validation
File: controllers.py:43-46, controllers.py:81-90, controllers.py:169-170, controllers.py:196-201, controllers.py:239-245, controllers.py:118-121, models.py:144, models.py:164
Description: `preco < 0` / `estoque < 0` with no type check (`"preco": "abc"` → `TypeError` → 500); `PUT /produtos` accepts any category and name length; `login` and `atualizar_status_pedido` call `dados.get(...)` without checking `dados is None` (body without JSON → 500); order items are not validated (missing `produto_id` → `KeyError` 500; `quantidade` zero or negative is accepted and *increases* stock at models.py:164); `float(preco_min)` with invalid text → 500; the status update does not check whether the order exists (returns 200 for a nonexistent id).
Impact: Client errors become 500s; data corruption (negative quantity inflates stock and reduces the total).
Recommendation: Validate presence, type and range in a validation layer before reaching the service; return 400/404 (→ T12).

### #17 [MEDIUM] AP-17 — Decentralized error handling
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62, controllers.py:95-96, controllers.py:108-109, controllers.py:125-126, controllers.py:133-134, controllers.py:143-144 (+9 occurrences: controllers.py:164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292; app.py:77-78)
Description: All 17 handlers repeat `except Exception as e: return jsonify({"erro": str(e)}), 500`; there is no `@app.errorhandler`.
Impact: Repetition, leaks internal messages (#4), and inconsistent behavior when one handler forgets the block.
Recommendation: Centralized error handler (domain exceptions → 4xx, generic `Exception` → 500 with a fixed message and a log with stack trace) (→ T08).

### #18 [MEDIUM] AP-19 — Inefficient aggregation
File: models.py:239-254, controllers.py:269-274
Description: `relatorio_vendas` runs 5 separate queries (`COUNT(*)`, `SUM(total)` and 3 × `COUNT(*) WHERE status = '...'`); `health_check` runs 3 consecutive `COUNT(*)` plus a redundant `SELECT 1`.
Impact: Unnecessary round-trips; the report is not computed on a consistent snapshot.
Recommendation: One query with `COUNT(*)`, `SUM(total)` and `SUM(CASE WHEN status = ? THEN 1 ELSE 0 END)` (or `GROUP BY status`) (→ T07).

### #19 [MEDIUM] AP-20 — Manual referential integrity / orphaned records
File: models.py:65-70, database.py:36-53, models.py:196
Description: `DELETE FROM produtos WHERE id = ...` with no handling of `itens_pedido` referencing the product; tables have no `FOREIGN KEY` and no `PRAGMA foreign_keys = ON`; the code already compensates for orphans with `"Desconhecido"` (models.py:196). The `ativo` column exists but is never used (no soft delete).
Impact: Order history loses the name of the purchased product; dangling references.
Recommendation: Use soft delete (`ativo = 0`) or declare FKs + enable `PRAGMA foreign_keys`; a transactional delete in the model (→ T09). Changing hard delete to soft delete alters observable behavior → confirm with the business.

### #20 [LOW] AP-21 — Magic numbers and strings
File: models.py:257-262, controllers.py:47-50, controllers.py:52, controllers.py:242, app.py:88, app.py:36, controllers.py:285
Description: Discount thresholds `10000/5000/1000` and rates `0.1/0.05/0.02`; name limits `2`/`200`; category list `["informatica", "moveis", ...]` and status list `["pendente", "aprovado", ...]` inline; port `5000`; version `"1.0.0"` duplicated.
Impact: Rules hidden in the code; changing them requires finding every copy.
Recommendation: Named constants in a domain/config module (→ T13).

### #21 [LOW] AP-22 — print as logging
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:208-210, controllers.py:219, controllers.py:248, controllers.py:250 (+7 occurrences: controllers.py:106, 161, 179, 182; app.py:56, 83-86)
Description: Uses `print("ERRO: " + str(e))`, `print("Listando ... produtos")`, `print("!!! BANCO DE DADOS RESETADO !!!")` instead of `logging`.
Impact: No levels, timestamps or configurable destination; mixes with stdout.
Recommendation: `logging.getLogger(__name__)` with a central configuration (→ T14).

### #22 [LOW] AP-23 — Poor naming / shadowed built-ins
File: controllers.py:14, controllers.py:56, controllers.py:64, controllers.py:98, controllers.py:160, models.py:24, models.py:54, models.py:65 (+5 occurrences: models.py:89, 187, 191, 219, 223)
Description: Parameters and variables named `id` shadow the built-in (`def buscar_produto(id)`, `id = models.criar_produto(...)`); cursors with numeric suffixes `cursor2`, `cursor3`; `prod`, `e`.
Impact: Readability; risk of subtle bugs when `id()` is needed.
Recommendation: Rename internally (`produto_id`, `items_cursor`); the URL route parameter `<int:id>` can keep its name in the path (→ T05/T06).

### #23 [LOW] AP-24 — Dead code and unused imports
File: models.py:2, database.py:2
Description: `import sqlite3` in `models.py` and `import os` in `database.py` are never used.
Impact: Noise; misleading dependencies.
Recommendation: Remove (→ T05).

### #24 [LOW] AP-25 — Verbose / non-idiomatic code
File: models.py:9-22, models.py:63, models.py:70, models.py:146, controllers.py:200
Description: Field-by-field dict building instead of a single row-to-dict helper; `atualizar_produto`/`deletar_produto` always `return True` (a value no caller uses); `total = total + ...`; `if not itens or len(itens) == 0` (redundant).
Impact: More code to maintain with no gain.
Recommendation: Simplify during the decomposition (→ T06).

### #25 [LOW] AP-26 — Inconsistent response format
File: controllers.py:20, controllers.py:70, controllers.py:103, controllers.py:142, controllers.py:183, controllers.py:206, controllers.py:292
Description: 404s sometimes include `"sucesso": False` (controllers.py:20) and sometimes do not (70, 103, 142); 400/500 errors usually lack `sucesso`; `/health` uses a different error shape (`{"status": "erro", "detalhes": ...}`).
Impact: Clients need special cases per endpoint.
Recommendation: Standardize the error body in the centralized handler, keeping the current success format and HTTP status codes (→ T08).

## Deprecated APIs
None detected

Evidence: static search (Grep) for every pattern in the catalog's deprecated table for Python/Flask/Werkzeug (`utcnow`, `before_first_request`, `JSONEncoder`, `json_encoder`, `JSON_AS_ASCII`, `distutils`, `imp`, `pkg_resources`, `safe_str_cmp`, `.query.get(`) → no matches. The runtime check (`python -W default -c "import app"`) could **not** be run: Flask is not installed in the current environment (Python 3.14.5, `ModuleNotFoundError: No module named 'flask'`); it will run in Phase 3 after `pip install -r requirements.txt`.

## Architecture Notes
- Current architecture: Nominal layers / partially organized — files named `controllers.py` and `models.py` exist, but `models.py` holds business rules (order total, stock, discount) alongside SQL across 4 domains, `app.py` runs SQL directly (`/admin/*`) and `controllers.health_check` accesses the database.
- Refactoring strategy: incremental layering (reusing the current split, with decomposition of the god files) — split `models.py` per entity, extract `services/` (orders, reports, notifications), add `config`, `routes`/blueprints, an error handler and an app factory, keeping `python app.py` as the entry point.
- Contract constraints: preserve all 19 routes (paths, methods, `<int:id>`), input fields (`nome`, `descricao`, `preco`, `estoque`, `categoria`, `email`, `senha`, `usuario_id`, `itens[].produto_id`, `itens[].quantidade`, `status`, query `q`/`categoria`/`preco_min`/`preco_max`), the `{"dados": ..., "sucesso": ..., "mensagem": ...}` envelope, status codes (200/201/400/401/404/500), port 5000 and the `python app.py` command with auto-seeding. Intentional security changes: removing `senha` from user responses and `secret_key`/`debug`/`db_path` from `/health`.

================================
Total: 25 findings
================================
