# Execução da skill `/refactor-arch` — task-manager-api

Saída integral de uma sessão nova e não interativa do Claude Code (`claude -p`), sem contexto anterior, rodando sobre o
**código original** (commit inicial `6d1ce62`) com a versão final da skill. Comando:

```bash
cd task-manager-api
claude "/refactor-arch ../reports/audit-project-3.md"
```

- Fases 1 e 2: 17 turnos, 7.2 min. A sessão parou em
  `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e **nenhum arquivo do projeto tinha sido alterado**
  (conferido com `diff -r` contra uma cópia do original antes de responder).
- Resposta enviada: `y`.
- Fase 3: 65 turnos, 13.2 min.

> Nota: o resumo da Fase 1 e as *Architecture Notes* contaram 23 endpoints; o código original tem 22 (conferido pela lista de rotas do Flask). Corrigi a contagem no relatório em `reports/`; aqui a saída fica como foi impressa.

---

## Fases 1 e 2 (saída impressa, inclui o relatório de auditoria)

================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (versão não declarada; 3.14.5 no ambiente)
Framework:     Flask 3.0.0 (Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0)
Dependencies:  flask, flask-sqlalchemy, flask-cors, marshmallow (não usado), requests (não usado), python-dotenv (não usado)
Database:      SQLite (`sqlite:///tasks.db`) via ORM SQLAlchemy
Domain:        Task Manager API (tasks, usuários, categorias, relatórios)
Architecture:  Camadas nominais / parcialmente organizada — há `models/`, `routes/`, `services/` e `utils/`, mas as rotas concentram a regra de negócio e o acesso a dados, e o service e os helpers não são usados
Source files:  15 files analyzed (~1158 lines)
DB tables:     users, tasks, categories
Endpoints:     23 (GET /, GET /health, GET|POST /tasks, GET|PUT|DELETE /tasks/<id>, GET /tasks/search, GET /tasks/stats, GET|POST /users, GET|PUT|DELETE /users/<id>, GET /users/<id>/tasks, POST /login, GET /reports/summary, GET /reports/user/<id>, GET|POST /categories, PUT|DELETE /categories/<id>)
Run command:   pip install -r requirements.txt && python seed.py && python app.py (porta 5000)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1)
Files:   15 analyzed | ~1158 lines of code
Date:    2026-11-23

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 8 | LOW: 5

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-02 Credenciais e segredos hardcoded | app.py:13, services/notification_service.py:7-10 |
| 2 | CRITICAL | AP-03 Armazenamento inseguro de senhas | models/user.py:27-32 |
| 3 | CRITICAL | AP-04 Exposição de dados sensíveis | models/user.py:21, routes/user_routes.py:33,85,129,209 |
| 4 | HIGH | AP-07 Fat Controller | routes/task_routes.py:85-154,156-223,273-299; routes/report_routes.py:12-101,103-155 |
| 5 | HIGH | AP-08 Acesso a dados fora do Model | routes/*.py |
| 6 | HIGH | AP-10 Configuração insegura | app.py:11,15,34 |
| 7 | HIGH | AP-11 Autenticação ausente/falsa | routes/user_routes.py:52,71-78,119-125,210 (todas as rotas) |
| 8 | MEDIUM | AP-13 Acoplamento a efeitos colaterais (código morto) | services/notification_service.py:4-48 |
| 9 | MEDIUM | AP-14 Query N+1 | routes/task_routes.py:42,51; routes/user_routes.py:22; routes/report_routes.py:56,163 |
| 10 | MEDIUM | AP-15 Lógica duplicada | routes/task_routes.py:30-39,71-80,284-287; routes/user_routes.py:171-180; ... |
| 11 | MEDIUM | AP-16 Validação de entrada ausente | routes/task_routes.py:113,167,182,261,264; routes/report_routes.py:196-202; ... |
| 12 | MEDIUM | AP-17 Tratamento de erros descentralizado | routes/task_routes.py:62,137,204,236; routes/user_routes.py:130,149; ... |
| 13 | MEDIUM | AP-18 Deprecated e dependências vulneráveis | requirements.txt:1-6; models/task.py:15-21; routes/*.py |
| 14 | MEDIUM | AP-19 Agregação ineficiente | routes/task_routes.py:275-287; routes/report_routes.py:15-43 |
| 15 | MEDIUM | AP-20 Integridade referencial / órfãos | routes/user_routes.py:140-142; routes/report_routes.py:211-223 |
| 16 | LOW | AP-21 Magic numbers e strings | routes/task_routes.py:96-113; routes/user_routes.py:64,71; ... |
| 17 | LOW | AP-22 print como logging | routes/task_routes.py:149,153,219,234; routes/user_routes.py:83,89,147; ... |
| 18 | LOW | AP-23 Nomenclatura ruim | routes/report_routes.py:24-28; loops `t`, `u`, `c` |
| 19 | LOW | AP-24 Código morto e imports não usados | app.py:7; routes/task_routes.py:7; utils/helpers.py:2-108; ... |
| 20 | LOW | AP-25 Código verboso | models/task.py:38-60; models/user.py:34-38; ... |

## Principais achados (o texto completo de cada finding está no arquivo)

- **#1 AP-02:** `SECRET_KEY = 'super-secret-key-123'` e a senha SMTP `'senha123'` estão escritas direto no código. A correção passa a ler esses valores do ambiente. Se `SECRET_KEY` não for definido, o boot gera um segredo aleatório e registra um aviso.
- **#2 AP-03:** as senhas são guardadas com MD5 sem salt. A correção usa o hash da werkzeug (scrypt). Hashes MD5 antigos continuam aceitos no login e são regravados com o novo hash nesse momento.
- **#3 AP-04:** `User.to_dict()` devolve `password`. Confirmei em runtime que o login retorna o hash do admin. O campo será removido de todas as respostas.
- **#6 AP-10:** a aplicação sobe com `debug=True`, `host='0.0.0.0'` e `CORS(app)` aberto. Os novos padrões são debug desligado, `HOST=127.0.0.1` e `CORS_ORIGINS` vazio, ou seja, nenhuma origem externa é liberada.
- **#7 AP-11:** o token é `'fake-jwt-token-' + id`, nenhuma rota exige credencial e qualquer cliente pode se cadastrar como `admin`. A correção traz:
  - token assinado com expiração;
  - checagem com `login_required` e `admin_required`;
  - papel definido pelo servidor;
  - matriz de acesso público / autenticado / dono ou admin / admin.
- **#11 AP-16:** confirmei em runtime que `POST /tasks {"priority":"2"}` retorna 500. Erros 500 causados por entrada inválida passam a retornar 400.
- **#13 AP-18:** o runtime mostra `DeprecationWarning` para `datetime.utcnow()` e `LegacyAPIWarning` para `Query.get()`. O `pip-audit` encontrou 22 vulnerabilidades em 5 pacotes:
  - flask: corrigida na 3.1.3
  - flask-cors: corrigida na 6.0.0
  - python-dotenv: corrigida na 1.2.2
  - marshmallow e requests: nunca são importados e serão removidos
- **#15 AP-20:** ao apagar um usuário, as tasks dele são apagadas em cascata no model, na mesma transação. Ao apagar uma categoria, as tasks são desvinculadas (`category_id = NULL`) em vez de ficarem apontando para uma categoria inexistente.
- **#8 AP-13:** é o único item com parte `Pending`. Ligar o envio de e-mail a eventos seria um comportamento novo e depende de uma decisão de negócio.

## Deprecated APIs
| API | Location | Modern replacement | Evidence |
|---|---|---|---|
| `datetime.utcnow()` | models/*.py, routes/*.py, utils/helpers.py:38, services/notification_service.py:35, seed.py:66-74 | `datetime.now(timezone.utc)` | `DeprecationWarning` em runtime |
| `Model.query.get()` | 16 ocorrências em routes/*.py | `db.session.get(Model, id)` | `LegacyAPIWarning` em runtime |
| `backref=` | models/task.py:20-21 | `back_populates=` | catálogo (sem warning) |
| Dependências vulneráveis | requirements.txt | ver #13 | `pip-audit`: 22 vulnerabilidades |

## Architecture Notes
- **Current architecture:** em camadas apenas no nome (parcialmente organizada). As pastas existem, mas a lógica está toda nas rotas.
- **Refactoring strategy:** camadas adicionadas aos poucos sobre a estrutura atual. Mantenho `models/`, `routes/`, `services/` e `utils/` e adiciono `config/`, `controllers/` e `middlewares/`.
- **Contract constraints:** os 23 endpoints, os nomes dos campos de entrada, as chaves das respostas, `python seed.py` + `python app.py` na porta 5000 e as credenciais do seed ficam iguais.

================================
Total: 20 findings
================================

Relatório completo gravado em: `C:\Users\adilsonbarbosa\AppData\Local\Temp\claude\6f98b0225f573235\153428c6-1893-4665-b768-c0c4d978f879\scratchpad\final\task-manager-api\reports\audit-project-3.md`

As verificações em runtime (seed, requisições e `pip-audit`) rodaram numa cópia temporária do projeto, com um venv em `C:\Users\adilsonbarbosa\AppData\Local\Temp\claude\c525e55f7fdd14f5\fb5dc51c-d77b-4b20-8a70-3b77e8d5e50d\scratchpad\venv3`. Nenhum arquivo do projeto foi alterado.

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---

## Fase 3 (resumo impresso pela skill)

Phase 3 is done. All 20 findings are fixed, with one partial exception: part of #8 is left as Pending, as the report already said it would be. Every check ran and passed. One thing to know first: protected routes now require a Bearer token, so existing clients must log in and send it.

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
```
task-manager-api/
├── app.py                      # create_app(); `python app.py` and `from app import app, db` still work
├── database.py                 # db + PRAGMA foreign_keys + save/commit/delete
├── seed.py                     # same credentials, now with scrypt hashes
├── requirements.txt · .env.example · README.md
├── config/settings.py          # environment config with secure defaults
├── models/                     # task.py, user.py, category.py (data access + entity rules)
├── services/                   # auth, task, user, category, report, notification
├── controllers/                # task, user, category, report + validators.py + serializers.py
├── routes/                     # task, user, report, category (new) + register_routes
├── middlewares/                # auth.py (login_required/admin_required), error_handler.py
└── utils/                      # helpers.py (constants + pure functions), errors.py
```

## Findings Addressed
- #1 [CRITICAL] AP-02 → `SECRET_KEY` and SMTP settings come from the environment. Without `SECRET_KEY`, a random key is generated at boot with a warning. `.env.example` added (`config/settings.py`).
- #2 [CRITICAL] AP-03 → scrypt via werkzeug. Old MD5 hashes are migrated on the next login; tested, the hash became `scrypt:` (`models/user.py`, `services/auth_service.py`).
- #3 [CRITICAL] AP-04 → `password` removed from `User.to_dict()`, so it leaves every response.
- #4 [HIGH] AP-07 → business rules moved into `services/*`, request handling into `controllers/*`, and `routes/*` only maps paths. Category CRUD moved to `routes/category_routes.py`.
- #5 [HIGH] AP-08 → no route or controller imports `db`. Queries and writes live in the models.
- #6 [HIGH] AP-10 → debug off, `HOST=127.0.0.1`, `PORT=5000`, CORS closed unless `CORS_ORIGINS` is set (`app.py`, `config/settings.py`).
- #7 [HIGH] AP-11 → signed itsdangerous token (HMAC-SHA256, `TOKEN_MAX_AGE=3600`). The role is re-read from the database on every request. Access matrix:
  - **Public:** `/`, `/health`, `POST /login`, `POST /users` (always created with role `user`)
  - **Authenticated:** all of `/tasks`, `GET /categories`
  - **Owner or admin:** `GET/PUT /users/<id>`, `/users/<id>/tasks`, `/reports/user/<id>`
  - **Admin:** `GET /users`, `DELETE /users/<id>`, changing `role`/`active`, `POST/PUT/DELETE /categories`, `/reports/summary`
- #8 [MEDIUM] AP-13 → `NotificationService` now gets an injected `SmtpSender` and an injected history store, logs instead of printing, and is created in `app.extensions['notifications']`. The event wiring stays Pending.
- #9 [MEDIUM] AP-14 → `joinedload` for the task list, and grouped queries for `task_count`, category counts and productivity.
- #10 [MEDIUM] AP-15 → `Task.is_overdue()` and `to_dict()` are reused everywhere. Helpers and constants are reused, and one validator covers both create and update.
- #11 [MEDIUM] AP-16 → `controllers/validators.py`: these 500s now return 400 — string `priority`, `null` title, bad `?priority`/`?user_id`, `PUT /categories` with no JSON, invalid color, non-boolean `active`.
- #12 [MEDIUM] AP-17 → one central handler (`middlewares/error_handler.py`) and domain exceptions in `utils/errors.py`. The bare `except:` blocks are gone.
- #13 [MEDIUM] AP-18 → `utc_now()`, `db.session.get`, `back_populates`. Dependencies are now flask 3.1.3, flask-cors 6.0.0 and python-dotenv 1.2.2, and itsdangerous 2.2.0 is pinned. marshmallow and requests were removed.
- #14 [MEDIUM] AP-19 → `GROUP BY` on status and priority, and overdue tasks filtered in SQL.
- #15 [MEDIUM] AP-20 → deleting a user deletes their tasks in the same transaction (ORM cascade). Deleting a category sets its tasks' `category_id` to NULL in the same transaction (`Category.delete_unlinking_tasks`). `PRAGMA foreign_keys=ON` is enabled.
- #16 [LOW] AP-21 → named constants in `utils/helpers.py`, and the port comes from `PORT`.
- #17 [LOW] AP-22 → `logging` with `LOG_LEVEL` (default INFO). `seed.py` keeps its `print` output as a CLI script.
- #18 [LOW] AP-23 → descriptive names (`counts_by_priority`, `task`, `user`, `category`).
- #19 [LOW] AP-24 → dead imports and unused helpers removed. `log_action` was removed too, because nothing uses it.
- #20 [LOW] AP-25 → boolean expressions simplified and `isinstance` used.

## Security Contract Changes
- **Auth:** protected routes need `Authorization: Bearer <token>` (401 with no token or a bad one, 403 without permission). The login `token` field is now signed and expires.
- **Roles:** public sign-up ignores `role`. Only an admin can set or change `role`/`active`.
- **Responses:** `password` is gone from all user responses.
- **Defaults:** CORS is closed and the server binds to 127.0.0.1 with debug off.
- **Errors:** input errors that returned 500 now return 400. Unexpected 500s return `{"error": "Erro interno"}`. The specific 500 messages were replaced with that generic one, and the status codes stay the same.

## Pending (requires human decision)
- #8: whether notifications should be sent on events (e.g. assigning a task). That would add an effect the original code never had.
- #8: whether to persist notification history, which needs a new table.

## Validation
  ✓ Application boots without errors (`python seed.py && python app.py`; log has no traceback or deprecation warning)
  ✓ All endpoints respond correctly (40/43 requests match baseline. The other 3 are the intended 500→400 changes: string priority, `?priority=abc`, `PUT /categories` with a null body. All non-volatile values are identical.)
  ✓ Authentication enforced (401 without token, with a tampered token and with an expired one; 403 for a regular user on admin routes and on another user's data; public sign-up with `role: admin` → `user`)
  ✓ Secure defaults (`Debug mode: off`, `Running on http://127.0.0.1:5000`, no `Access-Control-Allow-Origin` for `Origin: http://evil.example`; an explicit `CORS_ORIGINS` allows only that origin)
  ✓ No deprecated API warnings at runtime; dependency audit clean (`pip-audit`: No known vulnerabilities found)
  ✓ No CRITICAL/HIGH anti-patterns remaining (AP-10 and AP-11 included; grep re-audit and pyflakes clean)
  ✓ Every Recommendation delivered or declared Pending (20/20 findings reconciled)
================================

**Report correction:** I edited finding #8 in `../reports/audit-project-3.md`. Its Recommendation did not cover the in-memory list mentioned in its Impact. It now does, and persisting that history is declared Pending.

**Changed files** (I ran no git commands):
- **Rewritten:** `app.py`, `database.py`, `seed.py`, `requirements.txt`, `README.md`, the files in `models/` and `routes/`, `services/notification_service.py`, `utils/helpers.py`
- **New:** `config/`, `controllers/`, `middlewares/`, `services/{auth,task,user,category,report}_service.py`, `routes/category_routes.py`, `utils/errors.py`, `.env.example`

The database (`instance/tasks.db`) and `__pycache__` folders that validation created have been removed. Run `python seed.py` before the first boot.
