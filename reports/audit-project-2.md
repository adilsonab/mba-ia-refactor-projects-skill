================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js v20.19.5, versão não declarada) + Express ^4.18.2 (resolvido 4.22.1)
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 4 | HIGH: 7 | MEDIUM: 5 | LOW: 6

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-02 Credenciais e segredos hardcoded | src/utils.js:1-7 |
| 2 | CRITICAL | AP-03 Armazenamento inseguro de senhas | src/utils.js:17-23, src/AppManager.js:68 |
| 3 | CRITICAL | AP-04 Exposição de dados sensíveis (logs) | src/AppManager.js:45 |
| 4 | CRITICAL | AP-06 God Class | src/AppManager.js:4-139 |
| 5 | HIGH | AP-07 Regra de negócio na rota | src/AppManager.js:28-78, src/AppManager.js:80-129 |
| 6 | HIGH | AP-08 Acesso a dados fora da camada Model | src/AppManager.js:37-133 |
| 7 | HIGH | AP-09 Estado global mutável | src/utils.js:9-15 |
| 8 | HIGH | AP-11 Autenticação/autorização ausente | src/AppManager.js:80, src/AppManager.js:131 |
| 9 | HIGH | AP-12 Multi-escrita sem transação | src/AppManager.js:50-61, src/AppManager.js:69-72 |
| 10 | HIGH | AP-13 Callback hell / efeitos colaterais acoplados | src/AppManager.js:37-77, src/AppManager.js:83-128 |
| 11 | HIGH | AP-16 Validação de entrada ausente (↑ de MEDIUM) | src/AppManager.js:29-35, src/AppManager.js:46 |
| 12 | MEDIUM | AP-14 Query N+1 | src/AppManager.js:89-106 |
| 13 | MEDIUM | AP-17 Erros engolidos / sem tratamento central | src/AppManager.js:57, src/AppManager.js:92-106, src/AppManager.js:133-135, src/app.js:1-14 |
| 14 | MEDIUM | AP-18 APIs legadas e dependências vulneráveis | package.json:10-11, src/AppManager.js:11-133 |
| 15 | MEDIUM | AP-19 Agregação ineficiente | src/AppManager.js:83-123 |
| 16 | MEDIUM | AP-20 Registros órfãos | src/AppManager.js:131-136, src/AppManager.js:12-15 |
| 17 | LOW | AP-21 Magic numbers e strings | src/AppManager.js:46, src/utils.js:6, src/utils.js:19 |
| 18 | LOW | AP-22 console.log como logging | src/AppManager.js:45, src/utils.js:13, src/app.js:13 |
| 19 | LOW | AP-23 Nomenclatura ruim | src/AppManager.js:29-33, src/utils.js:17 |
| 20 | LOW | AP-24 Código morto | src/utils.js:2-3, src/utils.js:5, src/utils.js:10, src/AppManager.js:2 |
| 21 | LOW | AP-25 Código não idiomático | src/AppManager.js:26, src/AppManager.js:86-122 |
| 22 | LOW | AP-26 Formato de resposta inconsistente | src/AppManager.js:35-84, src/AppManager.js:135 |

## Findings

### #1 [CRITICAL] AP-02 — Credenciais e segredos hardcoded
File: src/utils.js:2, src/utils.js:3, src/utils.js:4, src/utils.js:5
Description: O objeto `config` contém literais sensíveis: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (prefixo de chave de produção) e `smtpUser`. Nenhum valor é lido de `process.env`.
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais de produção do banco e do gateway de pagamento; rotacionar segredos exige alterar código e fazer deploy.
Recommendation: Mover para variáveis de ambiente (`process.env.PAYMENT_GATEWAY_KEY`, etc.) em um módulo `config/` com defaults seguros apenas para desenvolvimento; documentar em `.env.example` (→ T02).

### #2 [CRITICAL] AP-03 — Armazenamento inseguro de senhas
File: src/utils.js:17-23, src/AppManager.js:68, src/AppManager.js:18
Description: `badCrypto(pwd)` faz `Buffer.from(pwd).toString('base64').substring(0, 2)` em loop e trunca em 10 caracteres — é uma codificação reversível/colidível, sem salt. Quando `pwd` não é enviado, usa a senha padrão `badCrypto(p || "123456")`. O seed grava `pass = '123'` em texto puro.
Impact: Senhas são trivialmente recuperáveis (os 2 primeiros caracteres de base64 repetidos); senhas diferentes colidem; usuários criados sem senha ficam com uma senha conhecida.
Recommendation: Usar `crypto.scrypt`/`pbkdf2` com salt aleatório (biblioteca padrão) ou `bcrypt`; não aplicar senha padrão — gerar valor aleatório ou exigir o campo (→ T03).

### #3 [CRITICAL] AP-04 — Exposição de dados sensíveis (logs)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` grava o número completo do cartão e a chave do gateway no stdout. Confirmado em runtime: o log exibiu `Processando cartão 4111222233334444 na chave pk_live_1234567890abcdef`.
Impact: Violação de PCI-DSS; qualquer um com acesso aos logs obtém cartões e a chave de pagamento.
Recommendation: Nunca logar PAN nem segredos; no máximo os 4 últimos dígitos mascarados (`**** 4444`) (→ T04).

### #4 [CRITICAL] AP-06 — God Class
File: src/AppManager.js:4-139
Description: A classe `AppManager` cria a conexão (`new sqlite3.Database(':memory:')`, linha 7), define o schema e o seed (10-23), registra todas as rotas (25-137), simula o gateway de pagamento (46), cria usuários, matrículas, auditoria e monta o relatório financeiro — 4 domínios (usuários, cursos/matrículas, pagamentos, relatórios) em um arquivo. O handler de checkout tem 51 linhas e o de relatório 50.
Impact: Impossível testar regras isoladamente; qualquer mudança toca o arquivo inteiro; não há pontos de extensão (trocar banco ou gateway exige reescrever a classe).
Recommendation: Decompor em `config/`, `database/` (conexão + schema/seed), `models/` (repositórios por entidade), `services/` (checkout, pagamento, relatório), `controllers/`, `routes/` e `middlewares/`, com `app.js` como composition root (→ T05 + T17).

### #5 [HIGH] AP-07 — Regra de negócio na rota (Fat Controller)
File: src/AppManager.js:28-78, src/AppManager.js:46, src/AppManager.js:66-75, src/AppManager.js:80-129, src/AppManager.js:108-110
Description: O callback de `app.post('/api/checkout')` decide aprovação do pagamento (`cc.startsWith("4") ? "PAID" : "DENIED"`), cria o usuário se não existir, matricula e audita. O callback de `/api/admin/financial-report` calcula receita (`if (payment && payment.status === 'PAID') courseData.revenue += payment.amount`).
Impact: Regras de pagamento e de faturamento não são reutilizáveis nem testáveis sem HTTP; o "gateway" fake fica misturado ao fluxo da requisição.
Recommendation: Extrair `CheckoutService`, `PaymentGateway` (injetável) e `ReportService`; controllers apenas leem input, chamam o service e escolhem o status (→ T06).

### #6 [HIGH] AP-08 — Acesso a dados fora da camada Model
File: src/AppManager.js:37, src/AppManager.js:40, src/AppManager.js:50, src/AppManager.js:54, src/AppManager.js:57, src/AppManager.js:69, src/AppManager.js:83, src/AppManager.js:92 (+3 ocorrências: 104, 106, 133)
Description: Todos os handlers chamam `this.db.get/run/all` com SQL diretamente (ex.: `this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [cid], ...)`).
Impact: SQL espalhado pelas rotas; impossível trocar o storage ou mockar o banco em testes; queries duplicáveis.
Recommendation: Criar repositórios (`UserModel`, `CourseModel`, `EnrollmentModel`, `PaymentModel`, `AuditLogModel`) que encapsulam o SQL parametrizado (→ T05/T06).

### #7 [HIGH] AP-09 — Estado global mutável
File: src/utils.js:9, src/utils.js:12-15, src/AppManager.js:59
Description: `let globalCache = {}` no escopo do módulo é mutado por `logAndCache` a cada checkout (`globalCache[key] = data`) e exportado; nunca é lido nem limpo.
Impact: Crescimento de memória sem limite (uma chave por usuário), estado compartilhado entre requisições e não reproduzível em múltiplas instâncias.
Recommendation: Remover o cache sem leitores ou encapsulá-lo em um serviço injetável com limite/TTL (→ T10).

### #8 [HIGH] AP-11 — Autenticação/autorização ausente
File: src/AppManager.js:80, src/AppManager.js:131
Description: `GET /api/admin/financial-report` (nomes de alunos e valores pagos) e `DELETE /api/users/:id` não têm nenhum middleware de autenticação/autorização.
Impact: Qualquer cliente anônimo lê dados financeiros/pessoais e apaga usuários.
Recommendation: Adicionar middleware de autenticação/papel admin. Como exigir auth quebra o contrato atual, isso deve ser decisão humana na Fase 3 (→ T16).

### #9 [HIGH] AP-12 — Operação multi-escrita sem transação
File: src/AppManager.js:50-61, src/AppManager.js:69-72
Description: O checkout executa até 4 `INSERT` encadeados (usuário → `enrollments` → `payments` → `audit_logs`) sem `BEGIN/COMMIT/ROLLBACK`.
Impact: Se o insert do pagamento falhar, a matrícula fica gravada sem pagamento (aluno matriculado de graça); se o pagamento for recusado ou o processo cair (ver #11), o usuário recém-criado permanece.
Recommendation: Envolver matrícula + pagamento + auditoria em uma transação com rollback em erro, dentro do `CheckoutService` (→ T09).

### #10 [HIGH] AP-13 — Callback hell / efeitos colaterais acoplados
File: src/AppManager.js:37-77, src/AppManager.js:83-128, src/AppManager.js:45-46, src/AppManager.js:59
Description: O checkout aninha 6 níveis de callbacks (`db.get` → `db.get` → `db.run` → `db.run` → `db.run`); o relatório aninha 4 níveis com contadores manuais. Pagamento (45-46) e cache (59) são executados inline, sem abstração injetável.
Impact: Fluxo de erro difícil de seguir (vários `return res...` em níveis diferentes), alto risco de resposta dupla ou nenhuma resposta; impossível substituir o gateway por um mock.
Recommendation: Promisificar o driver (`util.promisify`) e reescrever com `async/await`; injetar `PaymentGateway` no service (→ T06 + T15).

### #11 [HIGH] AP-16 — Validação de entrada ausente (severidade elevada de MEDIUM)
File: src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:132
Description: O checkout só verifica presença (`if (!u || !e || !cid || !cc)`); não valida tipos nem formato (e-mail, `c_id` numérico, `card` string). Com `card` numérico, `cc.startsWith("4")` lança `TypeError` dentro de um callback do sqlite. **Confirmado em runtime:** `POST /api/checkout` com `"card": 4111222233334444` derrubou o processo (`TypeError: cc.startsWith is not a function`, AppManager.js:46) — e o usuário já havia sido criado. `:id` do DELETE não é validado.
Impact: Uma única requisição anônima derruba a API inteira (DoS trivial) — por isso a severidade sobe um nível conforme a regra de calibração.
Recommendation: Validar tipos/formato no controller e retornar 400 antes de chamar o service; tratar exceções assíncronas via middleware (→ T12 + T08).

### #12 [MEDIUM] AP-14 — Query N+1
File: src/AppManager.js:89-92, src/AppManager.js:102-106
Description: Para cada curso, `SELECT * FROM enrollments WHERE course_id = ?`; para cada matrícula, `SELECT name, email FROM users WHERE id = ?` e `SELECT amount, status FROM payments WHERE enrollment_id = ?`.
Impact: 1 + C + 2·E queries por chamada do relatório; cresce linearmente com o número de matrículas.
Recommendation: Uma única query com `LEFT JOIN` entre `courses`, `enrollments`, `users` e `payments`, agrupando no service (→ T07).

### #13 [MEDIUM] AP-17 — Erros engolidos / tratamento descentralizado
File: src/AppManager.js:57, src/AppManager.js:92-93, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133-135, src/app.js:1-14
Description: Callbacks ignoram `err`: a auditoria (57) responde sucesso mesmo com erro; em 92 `enrollments.length` é lido sem checar `err` (crash se a query falhar); 104/106 ignoram erros; o DELETE (133-135) responde "Usuário deletado" mesmo com erro ou id inexistente. Não há middleware de erro `(err, req, res, next)` em `app.js`.
Impact: Falhas silenciosas, respostas enganosas e exceções não tratadas que derrubam o processo.
Recommendation: Centralizar em um middleware de erro e propagar erros com `async/await` + `next(err)` (→ T08).

### #14 [MEDIUM] AP-18 — APIs legadas e dependências vulneráveis
File: package.json:10-11, src/AppManager.js:11-133
Description: `npm audit --omit=dev` reporta 13 vulnerabilidades (2 critical, 8 high, 1 moderate, 2 low): `sqlite3@5.1.7` (direta, high, via `tar`/`node-gyp`/`cacache` — correção em `sqlite3@6.0.1`, major) e transitivas do Express (`body-parser`, `path-to-regexp`, `qs`, `proxy-addr`, `brace-expansion`, `ip-address`) corrigíveis com `npm audit fix`. O código usa exclusivamente a API de callbacks aninhados do sqlite3 (padrão legado). `node --trace-deprecation src/app.js` não emitiu nenhum DeprecationWarning.
Impact: Exposição a CVEs conhecidos (DoS em `qs`/`path-to-regexp`, path traversal em `tar` na instalação).
Recommendation: Rodar `npm audit fix` (sem quebra) e avaliar o upgrade de `sqlite3` para 6.x; substituir callbacks por Promises/`async-await` (→ T11).

### #15 [MEDIUM] AP-19 — Agregação ineficiente
File: src/AppManager.js:83-123
Description: A receita por curso é calculada em memória carregando todas as linhas (`courseData.revenue += payment.amount`) em vez de `SUM(...) ... GROUP BY`.
Impact: Transferência e processamento desnecessários; lógica de agregação dispersa em callbacks.
Recommendation: Calcular a receita no SQL (`SUM(CASE WHEN p.status='PAID' THEN p.amount ELSE 0 END)` com `GROUP BY c.id`) ou em uma única passada no service (→ T07).

### #16 [MEDIUM] AP-20 — Integridade referencial manual / registros órfãos
File: src/AppManager.js:131-136, src/AppManager.js:12-15
Description: `DELETE FROM users WHERE id = ?` não remove `enrollments`/`payments`; a própria resposta admite: "Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco." O schema não declara `FOREIGN KEY` nem `ON DELETE` e não ativa `PRAGMA foreign_keys`.
Impact: Dados órfãos; o relatório financeiro passa a exibir alunos `'Unknown'` com pagamentos de usuários removidos.
Recommendation: Exclusão transacional de matrículas/pagamentos do usuário (ou FKs com `ON DELETE CASCADE` + `PRAGMA foreign_keys = ON`). Mudar o texto da resposta altera o contrato → decisão humana (→ T09).

### #17 [LOW] AP-21 — Magic numbers e strings
File: src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:108, src/utils.js:6, src/utils.js:19
Description: Regra de aprovação `"4"` (prefixo do cartão), status `"PAID"`/`"DENIED"` repetidos como literais, senha padrão `"123456"`, porta `3000` fixa sem `process.env.PORT`, `10000` iterações em `badCrypto`.
Impact: Regras escondidas e duplicadas; mudar status ou porta exige caçar literais.
Recommendation: Constantes nomeadas (`PAYMENT_STATUS`, `APPROVED_CARD_PREFIX`) e porta via ambiente (→ T13).

### #18 [LOW] AP-22 — console.log como logging
File: src/AppManager.js:45, src/utils.js:13, src/app.js:13
Description: `console.log` usado para eventos de negócio (`[LOG] Salvando no cache`, processamento de cartão) e boot.
Impact: Sem níveis nem formato estruturado; facilita vazamentos como o #3.
Recommendation: Logger simples com níveis (módulo `utils/logger`) (→ T14).

### #19 [LOW] AP-23 — Nomenclatura ruim
File: src/AppManager.js:29-33, src/utils.js:17, src/AppManager.js:4
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`; função `badCrypto`; classe genérica `AppManager`.
Impact: Leitura difícil; nomes não comunicam intenção.
Recommendation: Renomear internamente (`name`, `email`, `password`, `courseId`, `cardNumber`) mantendo os nomes externos do payload (`usr`, `eml`, `pwd`, `c_id`, `card`) (→ T05/T06).

### #20 [LOW] AP-24 — Código morto
File: src/utils.js:2-3, src/utils.js:5, src/utils.js:10, src/utils.js:25, src/AppManager.js:2
Description: `totalRevenue` é declarado, exportado e importado em `AppManager.js:2`, mas nunca usado; `config.dbUser`, `config.dbPass` e `config.smtpUser` não são lidos em lugar nenhum; `globalCache` é exportado sem consumidores.
Impact: Ruído e falsa impressão de funcionalidade (ex.: SMTP inexistente).
Recommendation: Remover (→ T05).

### #21 [LOW] AP-25 — Código não idiomático
File: src/AppManager.js:26, src/AppManager.js:50-54, src/AppManager.js:86-122
Description: `const self = this` misturado com arrow functions e `function(err)` (necessária só para `this.lastID`); contadores manuais `coursesPending`/`enrPending` para sincronizar callbacks.
Impact: Confusão sobre o valor de `this`; risco de resposta nunca enviada se um contador errar.
Recommendation: `async/await` com `Promise.all` ou query única elimina os contadores e o `self` (→ T06).

### #22 [LOW] AP-26 — Formato de resposta inconsistente
File: src/AppManager.js:35, src/AppManager.js:38, src/AppManager.js:41, src/AppManager.js:48, src/AppManager.js:51, src/AppManager.js:55, src/AppManager.js:70, src/AppManager.js:84 (+1 ocorrência: 135)
Description: Erros são texto puro (`res.status(400).send("Bad Request")`, `"Curso não encontrado"`, `"Erro DB"`) enquanto sucessos são JSON (`{ msg: "Sucesso", enrollment_id }`); o DELETE responde texto.
Impact: Clientes precisam tratar dois formatos.
Recommendation: Manter os status HTTP e os corpos de sucesso; padronizar erros só se não quebrar clientes — mudar o corpo de erro é decisão humana (→ T08).

## Deprecated APIs
| API | Location | Modern replacement | Evidence |
|---|---|---|---|
| API de callbacks aninhados do `sqlite3` (`db.run/get/all(sql, params, cb)`) | src/AppManager.js:11-21, 37-133 | Promises + `async/await` (`util.promisify` ou wrapper) | Tabela do catálogo (padrão legado); `node --trace-deprecation` não emitiu warnings |
| `sqlite3@5.1.7` (dependências `tar`, `node-gyp`, `cacache` vulneráveis) | package.json:11 | `sqlite3@6.0.1` (major) | `npm audit --omit=dev`: 2 critical / 8 high no total |
| Transitivas do `express@4.22.1` (`body-parser`, `path-to-regexp`, `qs`, `proxy-addr`) | package.json:10 | versões corrigidas via `npm audit fix` | `npm audit --omit=dev` |

Nenhuma API marcada como deprecated pelo Node.js/Express foi detectada em runtime (`node --trace-deprecation --trace-warnings src/app.js` + checkout e relatório executados sem warnings).

## Architecture Notes
- Current architecture: Monolítica — `AppManager.js` cria o banco em memória, faz schema+seed, registra as 3 rotas, processa pagamento e monta o relatório; `utils.js` mistura config com segredos, cache global e "hash" de senha.
- Refactoring strategy: monolith decomposition — não existem camadas a reaproveitar; decompor em config / database / models / services / controllers / routes / middlewares com `app.js` como composition root (`npm start` → `node src/app.js` deve continuar funcionando).
- Contract constraints: `POST /api/checkout` com campos `usr`, `eml`, `pwd`, `c_id`, `card`; sucesso `200 {"msg":"Sucesso","enrollment_id":N}`; erros em texto com status 400 ("Bad Request", "Pagamento recusado"), 404 ("Curso não encontrado") e 500; `GET /api/admin/financial-report` → array `[{course, revenue, students:[{student, paid}]}]`; `DELETE /api/users/:id` → texto 200; porta 3000; seed automático no boot (banco em memória).

================================
Total: 22 findings
================================
