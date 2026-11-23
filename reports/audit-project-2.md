================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js 20.19.5 no ambiente; versão não declarada) + Express (^4.18.2, resolvido 4.22.1)
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-23

## Summary
CRITICAL: 5 | HIGH: 8 | MEDIUM: 4 | LOW: 6

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-02 Credenciais e segredos hardcoded | src/utils.js:1-7 |
| 2 | CRITICAL | AP-03 Armazenamento inseguro de senhas | src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68 |
| 3 | CRITICAL | AP-04 Exposição de dados sensíveis (logs) | src/AppManager.js:45 |
| 4 | CRITICAL | AP-05 Operação destrutiva aberta | src/AppManager.js:131-137 |
| 5 | CRITICAL | AP-06 God Class / God File | src/AppManager.js:4-139, src/utils.js:1-25 |
| 6 | HIGH | AP-07 Regra de negócio na rota | src/AppManager.js:28-78, src/AppManager.js:80-129 |
| 7 | HIGH | AP-08 Acesso a dados fora da camada Model | src/AppManager.js:37-133 |
| 8 | HIGH | AP-09 Estado global mutável | src/utils.js:9-15 |
| 9 | HIGH | AP-10 Configuração insegura | src/app.js:5-14, src/utils.js:6 |
| 10 | HIGH | AP-11 Autenticação/autorização ausente | src/AppManager.js:80, src/AppManager.js:131, src/AppManager.js:40-75 |
| 11 | HIGH | AP-12 Multi-escrita sem transação | src/AppManager.js:50-72 |
| 12 | HIGH | AP-13 Efeitos colaterais acoplados / callback hell | src/AppManager.js:37-77, src/AppManager.js:83-128 |
| 13 | HIGH | AP-16 Validação de entrada ausente (↑ de MEDIUM) | src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:132 |
| 14 | MEDIUM | AP-14 Query N+1 | src/AppManager.js:89-106 |
| 15 | MEDIUM | AP-17 Tratamento de erros descentralizado | src/AppManager.js:57, 92-93, 104, 106, 133-135 |
| 16 | MEDIUM | AP-18 APIs legadas e dependências vulneráveis | package.json:9-12, src/AppManager.js:37-133 |
| 17 | MEDIUM | AP-20 Registros órfãos | src/AppManager.js:12-15, src/AppManager.js:131-137 |
| 18 | LOW | AP-21 Magic numbers e strings | src/AppManager.js:46, 48, 68, src/utils.js:6, 19 |
| 19 | LOW | AP-22 console.log como logging | src/AppManager.js:45, src/utils.js:13, src/app.js:13 |
| 20 | LOW | AP-23 Nomenclatura ruim | src/AppManager.js:4, 29-33, src/utils.js:17 |
| 21 | LOW | AP-24 Código morto | src/AppManager.js:2, src/utils.js:2-3, 5, 10, 25 |
| 22 | LOW | AP-25 Código verboso / não idiomático | src/AppManager.js:26, 86-121 |
| 23 | LOW | AP-26 Formato de resposta inconsistente | src/AppManager.js:35, 38, 41, 48, 60, 135 |

## Findings

### #1 [CRITICAL] AP-02 — Credenciais e segredos hardcoded
File: src/utils.js:1-7
Description: Objeto `config` com literais: `dbPass: "senha_super_secreta_prod_123"`, `dbUser: "admin_master"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (prefixo de chave real `pk_live_`), `smtpUser: "no-reply@fullcycle.com.br"`.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de produção do gateway; rotação de segredos exige deploy; segredos vazam junto com o código.
Recommendation: Criar `src/config/index.js` que lê tudo de `process.env` (`PORT`, `HOST`, `PAYMENT_GATEWAY_KEY`, `SECRET_KEY`, `CORS_ORIGINS`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `TOKEN_TTL_SECONDS`, `LOG_LEVEL`); `PAYMENT_GATEWAY_KEY` sem default (vazio); nenhum segredo literal no código. `dbUser`/`dbPass`/`smtpUser` são removidos por não terem uso (SQLite em memória sem credencial, nenhum envio de e-mail — ver #21). Adicionar `.env.example` com placeholders e documentar no README (→ T02).

### #2 [CRITICAL] AP-03 — Armazenamento inseguro de senhas
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Description: `badCrypto` faz `Buffer.from(pwd).toString('base64').substring(0, 2)` repetido 10000 vezes e trunca em 10 caracteres — reversível/determinístico, sem salt (para `"123"` o "hash" é sempre `MTMTMTMTMT`). Senha padrão quando ausente: `badCrypto(p || "123456")`. Seed grava senha em texto puro: `INSERT INTO users (... pass) VALUES (..., '123')`.
Impact: Vazamento do banco revela as senhas trivialmente; todos os usuários criados sem `pwd` compartilham a senha `123456`; colisões massivas (só os 2 primeiros caracteres do base64 importam).
Recommendation: Substituir por `crypto.scrypt` (biblioteca padrão) com salt aleatório de 16 bytes por senha, formato `scrypt$<salt>$<hash>` e verificação com `crypto.timingSafeEqual`. Remover o default `"123456"`: checkout sem `pwd` gera senha aleatória (`crypto.randomBytes`) que não é logada nem retornada (o contrato atual não exige `pwd`, então a requisição continua aceita). Seed passa a gravar senhas com hash (→ T03).

### #3 [CRITICAL] AP-04 — Exposição de dados sensíveis (logs)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` — loga o número completo do cartão e a chave do gateway. Confirmado em runtime: `Processando cartão 4111222233334444 na chave pk_live_1234567890abcdef`.
Impact: PAN e chave de produção ficam em arquivos/agregadores de log (violação PCI-DSS, roubo de chave).
Recommendation: O log do pagamento passa a conter apenas os 4 últimos dígitos mascarados (`**** 4444`) e o resultado, nunca a chave do gateway nem o número completo (→ T04).

### #4 [CRITICAL] AP-05 — Operação destrutiva aberta
File: src/AppManager.js:131-137
Description: `app.delete('/api/users/:id', ...)` executa `DELETE FROM users WHERE id = ?` sem qualquer verificação de identidade ou papel.
Impact: Qualquer cliente anônimo apaga qualquer usuário (`DELETE /api/users/1`).
Recommendation: Manter a rota (operação destrutiva fixa) e exigir token válido de papel `admin` (401 sem token/token inválido, 403 para não-admin), conforme matriz de #10 (→ T16).

### #5 [CRITICAL] AP-06 — God Class / God File
File: src/AppManager.js:4-139, src/utils.js:1-25
Description: `AppManager` cria a conexão (`new sqlite3.Database(':memory:')`, l.7), define schema e seed (l.10-23), registra as 3 rotas (l.25-138), simula o gateway de pagamento (l.46), grava auditoria e cache e monta o relatório financeiro — 4 domínios (usuários, cursos, matrículas/pagamentos, relatórios). `utils.js` mistura configuração, cache global, "criptografia" e estado.
Impact: Impossível testar regras isoladamente; qualquer mudança toca o arquivo inteiro; sem fronteiras de responsabilidade.
Recommendation: Decompor em MVC: `src/config/`, `src/database/` (conexão, schema, seed), `src/models/` (repositórios por entidade), `src/services/` (checkout, relatório, usuários, pagamento, auth, cache), `src/controllers/`, `src/routes/`, `src/middlewares/` (auth, erros, CORS), `src/utils/` (logger, password, HttpError) e `src/app.js` como composition root; `AppManager.js` e `utils.js` são removidos (→ T05 + T17).

### #6 [HIGH] AP-07 — Regra de negócio na rota (Fat Controller)
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: O handler de checkout (50 linhas) decide pagamento inline (`cc.startsWith("4") ? "PAID" : "DENIED"`), cria usuário, matrícula, pagamento e auditoria. O handler do relatório (50 linhas) calcula `courseData.revenue += payment.amount` somando apenas `status === 'PAID'`.
Impact: Regras de pagamento e faturamento não reutilizáveis nem testáveis sem HTTP.
Recommendation: Mover para `CheckoutService` (fluxo de checkout), `PaymentGateway` (mesma regra: cartão iniciando em `"4"` → `PAID`, senão `DENIED`) e `ReportService` (receita = soma de pagamentos `PAID`); controllers só leem input, chamam o service e escolhem status (→ T06).

### #7 [HIGH] AP-08 — Acesso a dados fora da camada Model
File: src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133
Description: `this.db.get/run/all` com SQL direto dentro dos callbacks das rotas (`SELECT * FROM courses WHERE id = ? AND active = 1`, `INSERT INTO enrollments ...`, `DELETE FROM users ...`, etc.).
Impact: SQL espalhado pelas rotas; troca de banco ou de schema exige mexer na camada HTTP.
Recommendation: Criar repositórios `UserModel`, `CourseModel`, `EnrollmentModel`, `PaymentModel`, `AuditLogModel` e `ReportModel` em `src/models/`, todos com queries parametrizadas (`?`), únicos a falar com o banco (→ T05/T06).

### #8 [HIGH] AP-09 — Estado global mutável
File: src/utils.js:9-15
Description: `let globalCache = {}` no topo do módulo, mutado por `logAndCache(key, data)` (`globalCache[key] = data`) a cada checkout (`last_checkout_${userId}`) e exportado; `let totalRevenue = 0` mutável exportado.
Impact: Estado compartilhado entre requisições, cresce sem limite (vazamento de memória), não isolável em testes.
Recommendation: Substituir por um `CacheService` (classe com `set/get` sobre `Map`) instanciado uma única vez no composition root e injetado no `CheckoutService`, mantendo o registro `last_checkout_<userId>` → título do curso; `totalRevenue` é removido (ver #21) (→ T10).

### #9 [HIGH] AP-10 — Configuração insegura
File: src/app.js:5-14, src/utils.js:6
Description: `app.listen(config.port, ...)` sem host → em runtime o servidor escutou em `::` (todas as interfaces); porta `3000` fixa em `utils.js:6` sem leitura de ambiente; header `X-Powered-By: Express` exposto (observado na resposta); não há política de CORS explícita.
Impact: API (incluindo rotas administrativas) exposta na rede por padrão; fingerprinting do framework; configuração não ajustável por ambiente.
Recommendation: Defaults seguros sem nenhuma variável de ambiente: `HOST=127.0.0.1` (expor na rede exige `HOST=0.0.0.0` explícito), `PORT` padrão `3000`, `app.disable('x-powered-by')`, middleware de CORS com `CORS_ORIGINS` vazio por padrão = nenhuma origem externa recebe `Access-Control-Allow-Origin` (lista separada por vírgula libera só essas origens; `*` só se o operador definir), `SECRET_KEY` aleatório com aviso no log quando ausente. Não há modo debug no projeto; nenhum é introduzido (→ T02 + T17).

### #10 [HIGH] AP-11 — Autenticação/autorização ausente
File: src/AppManager.js:80, src/AppManager.js:131, src/AppManager.js:40-75
Description: `GET /api/admin/financial-report` (nomes de alunos e receita) e `DELETE /api/users/:id` não têm nenhum middleware de autenticação; o projeto não possui login nem token. No checkout, um `eml` já existente é aceito como identidade sem conferir senha (`SELECT id FROM users WHERE email = ?` → `processPaymentAndEnroll(user.id)`), permitindo matricular/cobrar em nome de outro usuário. A tabela `users` não tem papel.
Impact: Dados financeiros e pessoais públicos; qualquer um apaga usuários ou age em nome de outro e-mail.
Recommendation: Implementar T16: coluna `role` (`student` padrão, definido sempre pelo servidor; checkout cria usuários como `student`); novo endpoint aditivo `POST /api/login` (`{eml, pwd}` → `{token}`) que emite token HMAC-SHA256 assinado com `SECRET_KEY` e expiração (`TOKEN_TTL_SECONDS`, padrão 3600); middleware `authenticate` que valida assinatura/expiração e recarrega o usuário do banco, e `requireAdmin`. Matriz: `POST /api/checkout` público (e-mail já existente exige `pwd` correto ou Bearer do próprio usuário, senão 401); `POST /api/login` público; `GET /api/admin/financial-report` admin; `DELETE /api/users/:id` admin. Sem token/token adulterado → 401; não-admin → 403. Seed cria um admin a partir de `ADMIN_EMAIL` (padrão `admin@fullcycle.com.br`) e `ADMIN_PASSWORD` (se ausente, senha aleatória não logada e aviso de que o login admin exige definir a variável). Atualizar README e `.env.example` (→ T16).

### #11 [HIGH] AP-12 — Operação multi-escrita sem transação
File: src/AppManager.js:50-72
Description: Criação de usuário (l.69), matrícula (l.50), pagamento (l.54) e auditoria (l.57) são `db.run` encadeados sem `BEGIN/COMMIT/ROLLBACK`; falha no pagamento deixa matrícula sem pagamento. Além disso, o usuário é criado antes da decisão de pagamento, então um checkout recusado deixa um usuário criado.
Impact: Inconsistência de dados (matrícula sem pagamento, usuários "fantasmas" de checkouts recusados).
Recommendation: O pagamento é decidido antes de qualquer escrita; usuário + matrícula + pagamento + auditoria rodam em uma transação única (`BEGIN`/`COMMIT`, `ROLLBACK` em erro) via helper `withTransaction` serializado por fila (a conexão SQLite é única), usado também pela exclusão em cascata (#17) (→ T09).

### #12 [HIGH] AP-13 — Efeitos colaterais acoplados / callback hell
File: src/AppManager.js:37-77, src/AppManager.js:83-128
Description: Checkout com 5 níveis de callbacks aninhados (`db.get` → `db.get` → `db.run` → `db.run` → `db.run`); gateway de pagamento, auditoria e cache (`logAndCache`) acoplados inline. Relatório com 4 níveis de callbacks e contadores manuais.
Impact: Fluxo difícil de seguir, erros perdidos entre callbacks, impossível substituir gateway/cache em testes.
Recommendation: Wrapper Promise sobre o `sqlite3` (`run/get/all` → `async`), services em `async/await`; `PaymentGateway`, `CacheService` e `logger` injetados via construtor no composition root (→ T15 + T06).

### #13 [HIGH] AP-16 — Validação de entrada ausente (severidade elevada de MEDIUM)
File: src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:132
Description: Só verifica presença (`if (!u || !e || !cid || !cc)`); sem checagem de tipo/formato de `usr`, `eml`, `c_id`, `card`, `pwd`. **Confirmado em runtime:** `POST /api/checkout` com `"card": 4111` (número) lança `TypeError: cc.startsWith is not a function` dentro do callback e **derruba o processo** (servidor deixa de responder). `:id` do DELETE não é validado. Elevado a HIGH pela regra de calibração: exploração trivial (uma requisição anônima) pela API pública causa DoS.
Impact: Negação de serviço com uma única requisição; dados inválidos no banco.
Recommendation: Validação no controller: `usr` string não vazia, `eml` string com formato de e-mail, `c_id` inteiro positivo, `card` string de 13–19 dígitos, `pwd` opcional mas string quando enviado; inválido → 400 com o mesmo corpo atual `Bad Request`. `:id` não inteiro positivo → 400 `Bad Request`. Login valida `eml`/`pwd` string (→ T12).

### #14 [MEDIUM] AP-14 — Query N+1
File: src/AppManager.js:89-106
Description: `courses.forEach` → `SELECT * FROM enrollments WHERE course_id = ?` por curso → `enrollments.forEach` → `SELECT name, email FROM users WHERE id = ?` e `SELECT amount, status FROM payments WHERE enrollment_id = ?` por matrícula: 1 + C + 2·E queries.
Impact: Custo cresce linearmente com matrículas; relatório lento em bases reais; ordem dos cursos na resposta é não-determinística (observado: `Docker` antes de `Clean Architecture`).
Recommendation: Uma única query `courses LEFT JOIN enrollments LEFT JOIN users LEFT JOIN payments ORDER BY courses.id, enrollments.id` no `ReportModel`, agrupada no `ReportService` mantendo exatamente o formato `[{course, revenue, students: [{student, paid}]}]` (`'Unknown'`/`0` para ausentes); ordem passa a ser determinística por id do curso (→ T07).

### #15 [MEDIUM] AP-17 — Tratamento de erros descentralizado / erros engolidos
File: src/AppManager.js:57, src/AppManager.js:92-93, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133-135
Description: `err` ignorado no insert de auditoria (l.57), no `db.all` de enrollments (l.92 — com erro, `enrollments.length` lança TypeError), em users/payments (l.104/106) e no DELETE (l.133: sempre responde sucesso, inclusive para id inexistente). Não existe middleware de erro `(err, req, res, next)`; exceções em callbacks derrubam o processo (ver #13).
Impact: Falhas silenciosas, respostas de sucesso falsas, crash do servidor.
Recommendation: Handlers `async` com wrapper que encaminha rejeições a um middleware central de erros: `HttpError` mapeado para seu status/mensagem; erro inesperado → 500 com corpo `Erro interno` e log sem detalhes sensíveis. `DELETE` de id inexistente → 404 `Usuário não encontrado` (→ T08).

### #16 [MEDIUM] AP-18 — APIs legadas e dependências vulneráveis
File: package.json:9-12, src/AppManager.js:37-133
Description: `npm audit --omit=dev`: 13 vulnerabilidades (2 critical, 8 high, 1 moderate, 2 low). Via express 4.22.1 (corrigíveis sem major): `proxy-addr` (critical, 1.1.0–2.0.7), `body-parser` (high, ≤1.20.8), `path-to-regexp` (high, <0.1.13), `qs` (moderate, ≤6.16.0). Via `sqlite3@5.1.7` (direta, high) e sua cadeia de build: `tar` (critical, ≤7.5.20), `node-gyp`, `cacache`, `make-fetch-happen`, `ip-address`, `brace-expansion`, `http-proxy-agent`, `@tootallnate/once` — correção em `sqlite3@6.0.1` (major; exige Node ≥20.17.0, ambiente tem 20.19.5). Código usa API de callbacks aninhados (`db.run(sql, cb)`) — padrão legado. Runtime com `node --trace-deprecation src/app.js`: nenhum aviso de deprecation emitido.
Impact: Exposição a CVEs conhecidos (DoS em `qs`/`path-to-regexp`, path traversal em `tar` na instalação).
Recommendation: `npm audit fix` para atualizar as transitivas do express dentro de `^4`; atualizar `sqlite3` para `^6.0.1` e declarar `"engines": { "node": ">=20.17.0" }`; substituir callbacks por wrapper Promise + `async/await` (#12). Validar com `npm audit --omit=dev` limpo (→ T11).

### #17 [MEDIUM] AP-20 — Integridade referencial manual / registros órfãos
File: src/AppManager.js:12-15, src/AppManager.js:131-137
Description: Tabelas sem `FOREIGN KEY`, sem `PRAGMA foreign_keys = ON`; `DELETE FROM users WHERE id = ?` deixa matrículas e pagamentos órfãos — a própria resposta admite: "Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.".
Impact: Relatório financeiro passa a mostrar `Unknown` com valores pagos de usuários inexistentes; dados inconsistentes.
Recommendation: Matrículas e pagamentos pertencem ao usuário → exclusão em cascata na mesma transação (payments das matrículas do usuário → enrollments → user) no `UserService`; schema declara FKs com `ON DELETE CASCADE` e `PRAGMA foreign_keys = ON`. Resposta 200 passa a ser `Usuário deletado` (texto que não afirma mais dados sujos) (→ T09).

### #18 [LOW] AP-21 — Magic numbers e strings
File: src/AppManager.js:46, src/AppManager.js:48, src/AppManager.js:68, src/utils.js:6, src/utils.js:19
Description: Prefixo de cartão aprovado `"4"`, status `"PAID"`/`"DENIED"` literais, senha padrão `"123456"`, porta `3000`, `10000` iterações do "hash".
Impact: Regras escondidas e duplicáveis; difícil alterar com segurança.
Recommendation: `src/config/constants.js` com `PAYMENT_STATUS = { PAID, DENIED }`, `APPROVED_CARD_PREFIX = '4'`, `ROLES = { ADMIN, STUDENT }`; porta via config; `10000` e `"123456"` deixam de existir (#2) (→ T13).

### #19 [LOW] AP-22 — console.log como logging
File: src/AppManager.js:45, src/utils.js:13, src/app.js:13
Description: `console.log` para pagamento, cache (`[LOG] Salvando no cache: ...`) e boot.
Impact: Sem níveis nem controle; fácil vazar dados (ver #3).
Recommendation: `src/utils/logger.js` com níveis `debug/info/warn/error` controlados por `LOG_LEVEL` (padrão `info`), injetado nos services; nada sensível é logado (→ T14).

### #20 [LOW] AP-23 — Nomenclatura ruim
File: src/AppManager.js:4, src/AppManager.js:29-33, src/utils.js:17
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`; classe genérica `AppManager`; função `badCrypto`.
Impact: Leitura e manutenção prejudicadas.
Recommendation: Renomear internamente (`name`, `email`, `password`, `courseId`, `cardNumber`), mantendo os campos externos do contrato `usr`, `eml`, `pwd`, `c_id`, `card`; `AppManager`/`badCrypto` desaparecem na decomposição (→ T05/T06).

### #21 [LOW] AP-24 — Código morto
File: src/AppManager.js:2, src/utils.js:2-3, src/utils.js:5, src/utils.js:10, src/utils.js:25
Description: `totalRevenue` importado em AppManager.js:2 e nunca usado; declarado em utils.js:10 e nunca alterado/lido; `globalCache` exportado sem consumidor; `config.dbUser`, `config.dbPass` e `config.smtpUser` sem nenhuma referência.
Impact: Ruído e falsa impressão de funcionalidade (ex.: SMTP inexistente).
Recommendation: Remover `totalRevenue`, export de `globalCache`, `dbUser`, `dbPass` e `smtpUser` (→ T05).

### #22 [LOW] AP-25 — Código verboso / não idiomático
File: src/AppManager.js:26, src/AppManager.js:86-121
Description: `const self = this` misturado com arrow functions e `function(err){ this.lastID }`; contadores manuais `coursesPending`/`enrPending` para sincronizar callbacks.
Impact: Fácil introduzir bugs de concorrência/resposta dupla.
Recommendation: `async/await` com `lastID` retornado pelo wrapper Promise; contadores eliminados pela query única de #14 (→ T06).

### #23 [LOW] AP-26 — Formato de resposta inconsistente
File: src/AppManager.js:35, src/AppManager.js:38, src/AppManager.js:41, src/AppManager.js:48, src/AppManager.js:60, src/AppManager.js:135
Description: Sucesso do checkout em JSON (`{ msg, enrollment_id }`), erros em texto puro (`"Bad Request"`, `"Curso não encontrado"`, `"Pagamento recusado"`), DELETE com texto, cada um montado manualmente.
Impact: Clientes precisam tratar dois formatos; mensagens dispersas.
Recommendation: Preservar sucessos como estão e todos os erros como texto com os mesmos status e mensagens atuais, porém emitidos por um único ponto (`HttpError` + middleware de erro de #15), sem `res.status().send()` espalhado (→ T08).

## Deprecated APIs
| API | Location | Modern replacement | Evidence |
|---|---|---|---|
| Callbacks aninhados do `sqlite3` (`db.run/get/all(sql, params, cb)`) | src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133 | Wrapper Promise + `async/await` | Catálogo AP-18 (padrão legado Node); `node --trace-deprecation`: nenhum DeprecationWarning |
| `sqlite3@5.1.7` (e cadeia `tar`/`node-gyp`/`cacache`) | package.json:11 | `sqlite3@^6.0.1` | `npm audit --omit=dev` (high; `tar` critical) |
| `proxy-addr`, `body-parser`, `path-to-regexp`, `qs` (transitivas do express 4.22.1) | package.json:10 | Versões corrigidas via `npm audit fix` | `npm audit --omit=dev` (critical/high/moderate) |

## Architecture Notes
- Current architecture: Monolítica — `AppManager.js` cria o banco em memória, define schema e seed, registra todas as rotas, processa pagamento e monta relatório; `utils.js` mistura config, segredos, cache global e "crypto".
- Refactoring strategy: monolith decomposition — não há nenhuma camada a reaproveitar; decompor em config/database/models/services/controllers/routes/middlewares com `src/app.js` como composition root.
- Contract constraints: comando `npm start` (`node src/app.js`), porta 3000; `POST /api/checkout` com campos `usr`, `eml`, `pwd`, `c_id`, `card` → 200 `{msg:"Sucesso", enrollment_id}`, 400 `Bad Request`/`Pagamento recusado`, 404 `Curso não encontrado`; `GET /api/admin/financial-report` → `[{course, revenue, students:[{student, paid}]}]`; `DELETE /api/users/:id` → 200 texto. Mudanças de segurança previstas: token nas rotas admin, CORS fechado, bind local, `POST /api/login` aditivo.

================================
Total: 23 findings
================================
