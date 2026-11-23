# Execução da skill `/refactor-arch` — ecommerce-api-legacy

Saída integral de uma sessão nova e não interativa do Claude Code (`claude -p`), sem contexto anterior, rodando sobre o
**código original** (commit inicial `6d1ce62`) com a versão final da skill. Comando:

```bash
cd ecommerce-api-legacy
claude "/refactor-arch ../reports/audit-project-2.md"
```

- Fases 1 e 2: 19 turnos, 5.2 min. A sessão parou em
  `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e **nenhum arquivo do projeto tinha sido alterado**
  (conferido com `diff -r` contra uma cópia do original antes de responder).
- Resposta enviada: `y`.
- Fase 3: 55 turnos, 9.9 min.

---

## Fases 1 e 2 (saída impressa, inclui o relatório de auditoria)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js; versão não declarada — ambiente: v20.19.5)
Framework:     Express ^4.18.2 (resolvido 4.22.1)
Dependencies:  express, sqlite3 ^5.1.6 (resolvido 5.1.7)
Database:      SQLite em memória (':memory:') via sqlite3, SQL cru com placeholders
Domain:        LMS API com checkout (usuários, cursos, matrículas, pagamentos, audit_logs)
Architecture:  Monolítica — AppManager.js cria o banco, faz schema/seed, define rotas, processa pagamento e monta relatório; utils.js mistura config/segredos, cache global e "crypto"
Source files:  3 files analyzed (~180 lines)
DB tables:     users, courses, enrollments, payments, audit_logs
Endpoints:     3 (POST /api/checkout [AppManager.js:28], GET /api/admin/financial-report [AppManager.js:80], DELETE /api/users/:id [AppManager.js:131])
Run command:   npm install && npm start (node src/app.js), porta 3000; seed automático no boot
================================
```

O relatório completo da Fase 2 está salvo em `C:\Users\adilsonbarbosa\AppData\Local\Temp\claude\6f98b0225f573235\153428c6-1893-4665-b768-c0c4d978f879\scratchpad\final\ecommerce-api-legacy\reports\audit-project-2.md`. Abaixo vai o resumo:

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js 20.19.5) + Express (^4.18.2 → 4.22.1)
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-23

## Summary
CRITICAL: 5 | HIGH: 8 | MEDIUM: 4 | LOW: 6
```

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-02 Credenciais hardcoded (`pk_live_…`, `dbPass`) | src/utils.js:1-7 |
| 2 | CRITICAL | AP-03 Senhas inseguras (`badCrypto` base64, default `"123456"`, seed em texto puro) | src/utils.js:17-23, src/AppManager.js:18, 68 |
| 3 | CRITICAL | AP-04 Número do cartão e chave do gateway no log | src/AppManager.js:45 |
| 4 | CRITICAL | AP-05 `DELETE /api/users/:id` aberto | src/AppManager.js:131-137 |
| 5 | CRITICAL | AP-06 God Class `AppManager` / God File `utils.js` | src/AppManager.js:4-139, src/utils.js |
| 6 | HIGH | AP-07 Regra de negócio na rota | src/AppManager.js:28-78, 80-129 |
| 7 | HIGH | AP-08 SQL nas rotas | src/AppManager.js:37-133 |
| 8 | HIGH | AP-09 `globalCache` mutável | src/utils.js:9-15 |
| 9 | HIGH | AP-10 Bind em todas as interfaces (`::`), porta fixa, `X-Powered-By` | src/app.js:5-14, src/utils.js:6 |
| 10 | HIGH | AP-11 Sem login/token; rotas admin abertas; `eml` existente aceito como identidade | src/AppManager.js:80, 131, 40-75 |
| 11 | HIGH | AP-12 Usuário + matrícula + pagamento + auditoria sem transação | src/AppManager.js:50-72 |
| 12 | HIGH | AP-13 Callback hell / efeitos colaterais acoplados | src/AppManager.js:37-77, 83-128 |
| 13 | HIGH | AP-16 Validação ausente (subiu de MEDIUM: **um `"card": 4111` derruba o processo**, confirmado) | src/AppManager.js:29-35, 46, 132 |
| 14 | MEDIUM | AP-14 N+1 no relatório (1 + C + 2·E queries) | src/AppManager.js:89-106 |
| 15 | MEDIUM | AP-17 Erros engolidos, sem middleware de erro | src/AppManager.js:57, 92-93, 104, 106, 133-135 |
| 16 | MEDIUM | AP-18 13 vulnerabilidades no npm audit (2 critical) + API de callbacks legada | package.json:9-12 |
| 17 | MEDIUM | AP-20 Matrículas e pagamentos órfãos no DELETE | src/AppManager.js:12-15, 131-137 |
| 18 | LOW | AP-21 Magic numbers e strings | src/AppManager.js:46, 48, 68, src/utils.js:6, 19 |
| 19 | LOW | AP-22 `console.log` usado como logging | src/AppManager.js:45, src/utils.js:13, src/app.js:13 |
| 20 | LOW | AP-23 Nomes ruins (`u`, `e`, `cc`, `badCrypto`) | src/AppManager.js:4, 29-33, src/utils.js:17 |
| 21 | LOW | AP-24 Código morto (`totalRevenue`, `dbUser`/`dbPass`/`smtpUser`) | src/AppManager.js:2, src/utils.js:2-3, 5, 10, 25 |
| 22 | LOW | AP-25 `self = this`, contadores manuais | src/AppManager.js:26, 86-121 |
| 23 | LOW | AP-26 Sucesso em JSON e erros em texto, montados à mão | src/AppManager.js:35-135 |

**O que a Fase 3 vai entregar:**
- **Segredos:** configuração lida de variáveis de ambiente, sem segredos no código. O padrão é bind em `127.0.0.1`, CORS fechado (`CORS_ORIGINS` vazio) e `x-powered-by` desligado.
- **Senhas:** hash com `crypto.scrypt` e salt aleatório. Quando `pwd` não for enviado, o checkout gera uma senha aleatória no lugar do `"123456"`.
- **Autenticação:** novo endpoint `POST /api/login` que emite um token HMAC assinado com expiração. O relatório financeiro e o DELETE passam a exigir admin (401 sem token, 403 sem papel). O papel é sempre definido pelo servidor (`student`) e o seed cria um admin a partir de `ADMIN_EMAIL`/`ADMIN_PASSWORD`. No checkout, um e-mail que já existe passa a exigir a senha correta.
- **Dados:** checkout em transação única, com o pagamento decidido antes de qualquer escrita. O relatório passa a usar um único JOIN, com o mesmo formato de resposta. O DELETE apaga em cascata e responde 404 quando o id não existe.
- **Dependências:** `npm audit fix` e `sqlite3` atualizado para `^6.0.1` (exige Node ≥20.17; o ambiente tem 20.19.5).

**APIs deprecated:** `node --trace-deprecation` não emitiu nenhum aviso em runtime. Os únicos itens legados são a API de callbacks do sqlite3 e as dependências vulneráveis.

**Arquitetura:** a estratégia é decompor o monolito. O contrato é preservado: `npm start`, porta 3000, campos `usr`/`eml`/`pwd`/`c_id`/`card` e as formas de resposta atuais.

Nada no projeto foi alterado. A única escrita foi o relatório. Os servidores que subi para os testes já foram encerrados, e `node_modules/` foi instalado via `npm ci`.

```
================================
Total: 23 findings
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
ecommerce-api-legacy/
├── .env.example
├── api.http
├── package.json            # express ^4.22.3, sqlite3 ^6.0.1, engines node >=20.17.0
├── README.md
└── src/
    ├── app.js              # composition root (npm start)
    ├── config/             # index.js, constants.js
    ├── database/           # index.js (Promise + transaction), schema.js, seed.js
    ├── models/             # index, user, course, enrollment, payment, auditLog, report
    ├── services/           # checkout, report, user, auth, paymentGateway, cacheService
    ├── controllers/        # checkout, report, user, auth
    ├── routes/index.js     # matriz de acesso
    ├── middlewares/        # auth.js, cors.js, errorHandler.js
    └── utils/              # errors, logger, password, token, validators
```
Removi `src/AppManager.js` e `src/utils.js`.

## Findings Addressed
- #1 [CRITICAL] AP-02 Segredos: agora vêm de variáveis de ambiente (`config/index.js`) e o `.env.example` foi criado. `dbUser`/`dbPass`/`smtpUser` foram removidos.
- #2 [CRITICAL] AP-03 Senhas:
  - hash `scrypt$salt$hash` com `timingSafeEqual` (`utils/password.js`);
  - sem `pwd`, o checkout gera uma senha aleatória;
  - o seed grava as senhas com hash.
- #3 [CRITICAL] AP-04 Logs: o pagamento loga só `**** 4444`, sem o número do cartão nem a chave do gateway (`services/paymentGateway.js`).
- #4 [CRITICAL] AP-05 `DELETE /api/users/:id` agora exige admin (`routes/index.js`).
- #5 [CRITICAL] AP-06 God Class decomposta em MVC, com `app.js` como composition root.
- #6 [HIGH] AP-07 Regras movidas para os services `checkoutService`, `paymentGateway` e `reportService`.
- #7 [HIGH] AP-08 SQL só existe em `models/` e `database/` (confirmado por grep).
- #8 [HIGH] AP-09 O `globalCache` virou um `CacheService` injetado, com limite de 1000 entradas. `totalRevenue` foi removido.
- #9 [HIGH] AP-10 Defaults seguros:
  - `HOST=127.0.0.1` e `PORT` lida do ambiente;
  - `x-powered-by` desligado;
  - CORS fechado sem `CORS_ORIGINS`;
  - `SECRET_KEY` aleatória com aviso no log quando não definida.
- #10 [HIGH] AP-11 Autenticação real:
  - coluna `role` (padrão `student`);
  - `POST /api/login` → `{token}` HMAC-SHA256 com expiração de 3600 s;
  - middleware que relê o usuário do banco a cada requisição;
  - admin criado no seed a partir de `ADMIN_EMAIL`/`ADMIN_PASSWORD`.
  - Matriz de acesso:

    | Endpoint | Acesso |
    |---|---|
    | `POST /api/login` | público |
    | `POST /api/checkout` | público; e-mail existente exige `pwd` correto ou token do próprio usuário |
    | `GET /api/admin/financial-report` | admin |
    | `DELETE /api/users/:id` | admin |

- #11 [HIGH] AP-12 O pagamento é decidido antes de qualquer escrita. Usuário, matrícula, pagamento e auditoria são gravados numa transação serializada (`database/index.js`).
- #12 [HIGH] AP-13 Callbacks trocados por wrapper Promise e `async/await`. Gateway, cache e logger são injetados.
- #13 [HIGH] AP-16 Validação de tipo e formato (`utils/validators.js`). Um `card` numérico agora recebe 400 em vez de derrubar o processo.
- #14 [MEDIUM] AP-14 O relatório usa um único LEFT JOIN, com o mesmo formato de resposta e ordem estável por id do curso.
- #15 [MEDIUM] AP-17 `asyncHandler`, `HttpError` e um error handler central (500 → `Erro interno`). DELETE de id inexistente → 404.
- #16 [MEDIUM] AP-18 `sqlite3` 6.0.1 e `engines` declarado. O `npm audit fix` não resolveu o `qs`, que o express 4.22.1 fixa em `~6.14`, então atualizei o express para `^4.22.3`, na mesma major.
- #17 [MEDIUM] AP-20 Exclusão em cascata numa transação, FKs com `ON DELETE CASCADE` e `PRAGMA foreign_keys = ON`. A resposta agora é `Usuário deletado`.
- #18 [LOW] AP-21 Constantes em `config/constants.js`: `PAYMENT_STATUS`, `APPROVED_CARD_PREFIX`, `ROLES`.
- #19 [LOW] AP-22 Logger com níveis definidos por `LOG_LEVEL`. Não sobrou nenhum `console.*` fora do logger.
- #20 [LOW] AP-23 Nomes internos claros. Os campos `usr`/`eml`/`pwd`/`c_id`/`card` continuam iguais.
- #21 [LOW] AP-24 Código morto removido.
- #22 [LOW] AP-25 Saíram `self = this` e os contadores manuais.
- #23 [LOW] AP-26 Erros continuam em texto, com as mesmas mensagens e status, mas agora saem de um único ponto.

## Security Contract Changes
- **Rotas admin:** relatório e DELETE exigem `Authorization: Bearer` de um admin (401 sem token ou com token inválido, 403 sem papel admin).
- **Novo endpoint:** `POST /api/login`.
- **Checkout com e-mail já cadastrado:** exige o `pwd` correto (ou o token do próprio usuário); sem isso, 401.
- **Rede e CORS:** bind em `127.0.0.1` por padrão; CORS fechado; header `X-Powered-By` removido.
- **DELETE:** id inexistente → 404, id inválido → 400. A exclusão apaga matrículas e pagamentos do usuário e a mensagem virou `Usuário deletado`.
- **Entrada inválida:** um `card` não-string, JSON malformado ou corpo ausente → 400 (antes: crash ou 500).
- **Relatório:** ordem determinística por id do curso.

## Pending (requires human decision)
None

## Validation
  ✓ Application boots without errors (`npm start` / `node --trace-deprecation src/app.js`)
  ✓ All endpoints respond correctly (9/13 requests match baseline; as 4 divergências são intencionais: DELETE 999 → 404, DELETE abc → 400, card numérico → 400 em vez de crash, servidor continua no ar)
  ✓ Authentication enforced:
    - sem token, com token adulterado ou forjado → 401;
    - aluno em rota admin → 403;
    - `role:"admin"` no corpo do checkout → usuário criado como `student` (recebe 403 na rota admin);
    - token expirado → rejeitado.
  ✓ Secure defaults (no debug mode exists; bind 127.0.0.1; no `Access-Control-Allow-Origin` for `http://evil.example`)
  ✓ No deprecated API warnings at runtime; dependency audit clean (`npm audit --omit=dev`: 0 vulnerabilities)
  ✓ No CRITICAL/HIGH anti-patterns remaining (AP-10 e AP-11 incluídos; re-grep de segredos, SQL interpolado e SQL fora de models: nenhum)
  ✓ Every Recommendation delivered or declared Pending (23/23 findings reconciled)
```
================================
```

**Para subir com acesso de admin:** sem `ADMIN_PASSWORD`, o admin recebe uma senha aleatória que não aparece em lugar nenhum, então o login admin fica indisponível. Use `ADMIN_PASSWORD=... npm start`. O aluno do seed continua sendo `leonan@fullcycle.com.br` / `123`.

Encerrei todos os servidores de teste. Não executei nenhum comando git. Arquivos alterados: `package.json`, `package-lock.json`, `README.md` e `api.http`. Criei `.env.example` e tudo o que está em `src/`, e removi `src/AppManager.js` e `src/utils.js`.
