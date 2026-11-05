# Catálogo de Anti-patterns (Fase 2)

Cada entrada tem: **severidade padrão**, **o que é**, **sinais de detecção** (concretos, grep-áveis quando possível, com exemplos em Python e JS), **falsos positivos** a descartar e a **transformação** do `refactoring-playbook.md` que o corrige.

## Escala de severidade

- **CRITICAL** — falha de segurança grave ou violação total da separação de responsabilidades: impede o funcionamento correto ou expõe dados sensíveis (credenciais hardcoded, SQL Injection, God Class).
- **HIGH** — forte violação de MVC/SOLID que dificulta muito manutenção e testes (regra de negócio no controller/rota, acoplamento sem injeção de dependência, estado global mutável).
- **MEDIUM** — padronização, duplicação, performance moderada (N+1, middleware inadequado, validação ausente).
- **LOW** — legibilidade, nomes ruins, magic numbers.

### Regras de calibração

- Use a severidade padrão. Suba **um nível** apenas se houver evidência de exploração trivial pela API pública (ex.: endpoint sem autenticação que expõe senhas). Desça **um nível** se o código afetado for morto/inalcançável — e diga isso no finding.
- Um mesmo trecho pode gerar mais de um finding se violar anti-patterns diferentes (ex.: SQL Injection **e** query N+1).
- Agrupe todas as ocorrências do mesmo anti-pattern em **um** finding com todas as localizações.

## Índice

| ID | Anti-pattern | Severidade |
|---|---|---|
| AP-01 | SQL/NoSQL Injection | CRITICAL |
| AP-02 | Credenciais e segredos hardcoded | CRITICAL |
| AP-03 | Armazenamento inseguro de senhas | CRITICAL |
| AP-04 | Exposição de dados sensíveis (respostas e logs) | CRITICAL |
| AP-05 | Endpoint de execução arbitrária / operação destrutiva aberta | CRITICAL |
| AP-06 | God Class / God File | CRITICAL |
| AP-07 | Regra de negócio na rota/controller (Fat Controller) | HIGH |
| AP-08 | Acesso a dados fora da camada Model | HIGH |
| AP-09 | Estado global mutável | HIGH |
| AP-10 | Configuração insegura (debug em produção, CORS aberto) | HIGH |
| AP-11 | Autenticação/autorização ausente ou falsa | HIGH |
| AP-12 | Operação multi-escrita sem transação | HIGH |
| AP-13 | Acoplamento forte a efeitos colaterais / callback hell | HIGH |
| AP-14 | Query N+1 | MEDIUM |
| AP-15 | Lógica duplicada / implementações paralelas | MEDIUM |
| AP-16 | Validação de entrada ausente ou incompleta | MEDIUM |
| AP-17 | Tratamento de erros descentralizado / exceções engolidas | MEDIUM |
| AP-18 | APIs deprecated / legadas e dependências vulneráveis | MEDIUM |
| AP-19 | Agregação ineficiente | MEDIUM |
| AP-20 | Integridade referencial manual / registros órfãos | MEDIUM |
| AP-21 | Magic numbers e strings | LOW |
| AP-22 | `print`/`console.log` como logging | LOW |
| AP-23 | Nomenclatura ruim / sombreamento de built-ins | LOW |
| AP-24 | Código morto e imports não usados | LOW |
| AP-25 | Código verboso / não idiomático | LOW |
| AP-26 | Formato de resposta inconsistente | LOW |

---

## CRITICAL

### AP-01 — SQL/NoSQL Injection
**O que é:** dados externos concatenados/interpolados em uma query.
**Sinais de detecção:**
- Python: `execute("..." + var)`, `execute(f"... {var} ...")`, `execute("... %s" % var)`, `.format(` dentro de string SQL; `text(f"...")` no SQLAlchemy.
- JS: template literal ou `+` dentro de `db.run/get/all/query(` — `` `SELECT ... ${id}` ``, `"... WHERE id = " + id`.
- Regex útil: `(execute|run|get|all|query)\(\s*(f["']|["'][^"']*["']\s*\+|`[^`]*\$\{)`
- Query montada incrementalmente com `query += " AND campo = '" + valor + "'"`.
**Falsos positivos:** placeholders `?`, `%s` com tupla separada, `:param`, ORM com filtros (`filter_by`, `.like(f'%{q}%')` do ORM é parametrizado → **não** é injection).
**Correção:** T01.

### AP-02 — Credenciais e segredos hardcoded
**O que é:** chaves, senhas, tokens e URIs com credenciais escritos no código.
**Sinais de detecção:**
- Nomes: `SECRET_KEY`, `secret`, `password`, `passwd`, `pwd`, `pass`, `api_key`, `apiKey`, `token`, `dbPass`, `email_password`, `paymentGatewayKey` atribuídos a **literais**.
- Prefixos de chaves reais: `pk_live_`, `sk_live_`, `AKIA`, `ghp_`, `xoxb-`.
- URIs com credenciais: `postgres://user:senha@`, `mongodb+srv://user:senha@`.
- O mesmo segredo retornado em resposta (ver AP-04).
**Falsos positivos:** leitura de ambiente (`os.environ`, `os.getenv`, `process.env`), placeholders de exemplo em `.env.example`, senhas de **seed** de desenvolvimento (estas caem em AP-03 se estiverem em texto puro).
**Correção:** T02.

### AP-03 — Armazenamento inseguro de senhas
**O que é:** senha guardada/comparada em texto puro, com hash rápido sem salt, ou "criptografia" reversível.
**Sinais de detecção:**
- Coluna/campo `senha`/`password`/`pass` gravado direto do input: `INSERT ... senha ...` com o valor recebido.
- Login comparando no SQL: `WHERE email = ? AND senha = ?`.
- `hashlib.md5(`, `hashlib.sha1(`, `sha256` sem salt/iterações; `crypto.createHash('md5'|'sha1')`.
- "Hash" caseiro: `base64`, `Buffer.from(pwd).toString('base64')`, loops com `substring`.
- Senha padrão quando ausente: `pwd || "123456"`.
**Falsos positivos:** `bcrypt`, `argon2`, `scrypt`, `pbkdf2` com salt, `werkzeug.security.generate_password_hash`.
**Correção:** T03.

### AP-04 — Exposição de dados sensíveis (respostas e logs)
**O que é:** senha/hash, segredo, configuração interna ou dado de cartão saindo em resposta HTTP ou log.
**Sinais de detecção:**
- Serializadores (`to_dict`, `toJSON`, montagem manual de dict) contendo `password`/`senha`/`pass`.
- Health/status retornando `secret_key`, `debug`, `db_path`, connection strings.
- Logs com `card`, `cc`, `cvv`, número de cartão, chaves (`console.log(\`... ${cc} ... ${config.key}\`)`), ou e-mail/senha de usuário.
- Respostas de erro com `str(e)`/`err.message`/stack trace (também AP-17).
**Correção:** T04.

### AP-05 — Endpoint de execução arbitrária / operação destrutiva aberta
**O que é:** rota que executa SQL/comando vindo do cliente ou que apaga/reseta dados sem nenhuma proteção.
**Sinais de detecção:** `cursor.execute(dados["sql"])`, `eval(`, `exec(`, `child_process.exec(req...)`, rotas `/admin/query`, `/admin/reset-db`, `/debug/*` sem verificação de autenticação.
**Correção:** T16.

### AP-06 — God Class / God File
**O que é:** um arquivo/classe concentra 3+ responsabilidades (conexão/schema/seed, rotas, validação, regras de negócio, formatação) e/ou vários domínios.
**Sinais de detecção:**
- Classe com nomes genéricos (`AppManager`, `Utils`, `Manager`, `Helper`) que cria conexão **e** registra rotas **e** contém regra de negócio.
- Arquivo com funções de 3+ entidades diferentes (produtos, usuários, pedidos, relatórios) misturando SQL e regras.
- Arquivo > ~300 linhas com responsabilidades heterogêneas; método > ~50 linhas.
**Falsos positivos:** arquivo grande mas coeso (uma única responsabilidade e um único domínio).
**Correção:** T05 (decomposição) + T17 (composition root).

---

## HIGH

### AP-07 — Regra de negócio na rota/controller (Fat Controller)
**O que é:** cálculos e decisões de domínio dentro do handler HTTP ou dentro do model de acesso a dados.
**Sinais de detecção:**
- Handler com > ~30 linhas, com `if/elif` de regra (desconto, estoque, pagamento, status, atraso) além de ler input e responder.
- Cálculos (`total +=`, `* 0.1`, percentuais, datas) dentro de funções decoradas com rota ou dentro de callbacks de `app.post(...)`.
- "Gateway" simulado inline (`cc.startsWith("4") ? "PAID" : "DENIED"`).
**Correção:** T06.

### AP-08 — Acesso a dados fora da camada Model
**O que é:** SQL/ORM chamado diretamente em rotas/controllers.
**Sinais de detecção:** `cursor.execute`, `get_db()`, `db.session`, `Model.query...`, `db.run/get/all` em arquivos de rotas/controllers.
**Correção:** T05/T06 (mover para model/repositório).

### AP-09 — Estado global mutável
**O que é:** variáveis de módulo alteradas em tempo de execução e compartilhadas entre requisições.
**Sinais de detecção:** `global x` em Python; `let cache = {}`/`let total = 0` no topo de módulo JS alterados em funções; conexão de banco única global (`db_connection = None` + `global`), `check_same_thread=False`; listas de "notificações" em memória.
**Falsos positivos:** constantes imutáveis; objetos de extensão inicializados uma vez (`db = SQLAlchemy()`).
**Correção:** T10.

### AP-10 — Configuração insegura
**O que é:** modo debug/flags de desenvolvimento fixos no código e expostos.
**Sinais de detecção:** `debug=True`, `app.config["DEBUG"] = True`, `app.run(host="0.0.0.0", debug=True)`, `CORS(app)` / `cors()` sem restrição de origem, URIs/portas fixas sem leitura de ambiente, ausência de app factory (`create_app`).
**Correção:** T02 + T17.

### AP-11 — Autenticação/autorização ausente ou falsa
**O que é:** rotas administrativas/destrutivas sem autenticação; token falso; cliente define o próprio papel.
**Sinais de detecção:** rotas `/admin/*`, `DELETE` de usuários, relatórios financeiros sem decorator/middleware de auth; `'fake-jwt-token-' + id`; `role = data.get('role', ...)` aceito no cadastro público.
**Nota para a Fase 3:** exigir autenticação em rota hoje pública **quebra o contrato** → registrar em "Pending (requires human decision)", salvo quando o endpoint executa código arbitrário (AP-05).
**Correção:** T16.

### AP-12 — Operação multi-escrita sem transação
**O que é:** várias escritas relacionadas (pedido + itens + estoque; matrícula + pagamento + auditoria) sem atomicidade, ou "verifica-depois-debita" sem lock.
**Sinais de detecção:** sequência de `INSERT/UPDATE` com um único `commit` no final mas sem `rollback` em erro; callbacks encadeados de `db.run` sem `BEGIN/COMMIT/ROLLBACK`; verificação de estoque e débito em queries separadas.
**Correção:** T09.

### AP-13 — Acoplamento forte a efeitos colaterais / callback hell
**O que é:** envio de e-mail/SMS/push, cache, auditoria, pagamento feitos inline na rota sem abstração injetável; callbacks aninhados 3+ níveis.
**Sinais de detecção:** `print("ENVIANDO EMAIL...")`, `smtplib` instanciado na rota/serviço com credenciais próprias, `new Service()` dentro do handler; indentação crescente com `function(err, ...) {` aninhados.
**Correção:** T15 (serviço injetável) e T06 (async/await).

---

## MEDIUM

### AP-14 — Query N+1
**O que é:** uma query por item de uma lista já carregada.
**Sinais de detecção:** `execute`/`query`/`.get(`/`db.get(` **dentro de** `for`/`forEach`/`map`; acesso a relacionamento lazy dentro de loop (`len(u.tasks)`, `t.user.name`); `Model.query.get(x.fk_id)` dentro de loop; `count()` por item.
**Correção:** T07.

### AP-15 — Lógica duplicada / implementações paralelas
**O que é:** o mesmo bloco (validação, serialização, cálculo) copiado em vários lugares, ou uma regra implementada no model/utils e reimplementada nas rotas.
**Sinais de detecção:** blocos de 5+ linhas idênticos ou quase idênticos; mesma lista literal (`['pending','in_progress','done','cancelled']`) repetida; funções quase iguais (`get_pedidos_usuario` × `get_todos_pedidos`); helpers/métodos de model **nunca referenciados** (verifique com Grep) enquanto rotas repetem a lógica.
**Correção:** T06 + T13.

### AP-16 — Validação de entrada ausente ou incompleta
**O que é:** input usado sem checar presença, tipo, faixa ou formato.
**Sinais de detecção:** `request.get_json()` seguido de `.get()` sem checar `None`; comparação numérica com valor do JSON sem conversão (`priority < 1` com string → TypeError/500); `len(data['x'])` com possível `None`; validações diferentes entre create e update da mesma entidade; campos opcionais que deveriam ser obrigatórios.
**Correção:** T12.

### AP-17 — Tratamento de erros descentralizado / exceções engolidas
**O que é:** `try/except` repetido em todo handler, `except:` genérico, erros ignorados em callbacks, mensagem interna devolvida ao cliente.
**Sinais de detecção:** `except:` (bare) ou `except Exception as e: return jsonify({"erro": str(e)}), 500` em todos os handlers; callbacks `(err, row) =>` sem `if (err)`; ausência de `@app.errorhandler`/middleware `(err, req, res, next)`.
**Correção:** T08.

### AP-18 — APIs deprecated / legadas e dependências vulneráveis
**O que é:** uso de APIs marcadas como obsoletas pela linguagem/framework, padrões legados com substituto moderno, ou dependências com vulnerabilidades conhecidas.
**Sinais de detecção:** consultar a tabela abaixo (Grep) e confirmar em runtime quando possível:
- Python: `python -W default` exibe `DeprecationWarning`/`LegacyAPIWarning` com arquivo:linha.
- Node: `node --trace-deprecation <entry>`; `npm audit --omit=dev`; `npm outdated`.

| Stack | Deprecated / legado | Substituto moderno |
|---|---|---|
| Python ≥3.12 | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| Python | `distutils`, `imp`, `pkg_resources`, `asyncio.get_event_loop()` fora de loop | `setuptools`/`packaging`, `importlib`, `importlib.metadata`, `asyncio.run()` |
| SQLAlchemy 2.x | `Model.query.get(id)` / `Query.get()` | `db.session.get(Model, id)` / `db.get_or_404(Model, id)` |
| SQLAlchemy 2.x | `engine.execute()`, `declarative_base()` de `sqlalchemy.ext.declarative`, `backref=` (legado) | `with engine.connect() as c: c.execute(text(...))`, `sqlalchemy.orm.DeclarativeBase`, `back_populates=` |
| Flask ≥2.3 | `@app.before_first_request`, `flask.json.JSONEncoder`, `app.json_encoder`, `JSON_AS_ASCII` | lógica em `create_app()`, `app.json` provider (`DefaultJSONProvider`) |
| Werkzeug | `werkzeug.contrib.*`, `safe_str_cmp` | bibliotecas dedicadas, `hmac.compare_digest` |
| Node.js | `new Buffer()`, `url.parse()`, `fs.exists()`, `crypto.createCipher()`, `util.isArray()` | `Buffer.from()`, `new URL()`, `fs.existsSync()`/`fs.promises.access`, `crypto.createCipheriv()`, `Array.isArray()` |
| Express 4→5 | `req.param()`, `res.send(status)`, `res.json(status, body)`, `app.del()`, `body-parser` avulso | `req.params/query/body`, `res.status(s).send()`, `res.status(s).json(b)`, `app.delete()`, `express.json()` |
| Node (legado) | APIs de callback aninhadas (`db.run(sql, cb)`) | Promises + `async/await` (wrapper `util.promisify` ou driver com Promise) |
| Qualquer | Dependências com CVE (saída do `npm audit`/`pip-audit`) | Atualizar para versão corrigida |

**Correção:** T11.

### AP-19 — Agregação ineficiente
**O que é:** várias queries de contagem separadas ou carregar todas as linhas para contar/somar em memória.
**Sinais de detecção:** 3+ `COUNT(*)`/`.count()` consecutivos com filtros diferentes na mesma função; `Model.query.all()` seguido de loop que só conta/soma.
**Correção:** T07 (agregação com `GROUP BY`/`func.count`).

### AP-20 — Integridade referencial manual / registros órfãos
**O que é:** exclusões que deixam filhos órfãos ou cascata feita à mão na rota.
**Sinais de detecção:** `DELETE FROM pai` sem tratar tabelas filhas; loop `for t in filhos: delete(t)` na rota; FKs sem `ON DELETE`/`cascade`; SQLite sem `PRAGMA foreign_keys = ON`.
**Correção:** T09 (exclusão transacional) / cascade no model.

---

## LOW

### AP-21 — Magic numbers e strings
**Sinais:** literais de regra no código (`0.1`, `10000`, `5000`, `7` dias, `200`, `3`, `'#000000'`, `"4"`), listas de status/categorias/roles inline, porta fixa.
**Correção:** T13.

### AP-22 — `print`/`console.log` como logging
**Sinais:** `print(` / `console.log(` em código de aplicação (fora de scripts CLI); mensagens "ERRO", "ENVIANDO EMAIL".
**Correção:** T14.

### AP-23 — Nomenclatura ruim / sombreamento de built-ins
**Sinais:** variáveis de 1-3 letras sem significado (`u`, `e`, `p`, `cc`, `cid`), sufixos numéricos (`cursor2`, `cursor3`), parâmetros chamados `id`, `type`, `list`, `input` em Python; nomes enganosos (`badCrypto`, `AppManager`).
**Correção:** renomear durante T05/T06 (mantendo os nomes **externos** do contrato).

### AP-24 — Código morto e imports não usados
**Sinais:** `import x` sem uso (Grep pelo nome no arquivo), variáveis/exports nunca lidos (`totalRevenue`), funções sem chamadas.
**Correção:** remover (T05). Se a funcionalidade morta for útil (helper correto), **reaproveitar** em vez de remover.

### AP-25 — Código verboso / não idiomático
**Sinais:** `if cond: return True else: return False`; `if` aninhados 3+ níveis que viram uma expressão booleana; `type(x) == list` (usar `isinstance`); `const self = this` misturado com arrow functions.
**Correção:** simplificar durante T06.

### AP-26 — Formato de resposta inconsistente
**Sinais:** erros às vezes em texto (`res.send("Bad Request")`) e às vezes JSON; chaves de erro diferentes (`erro` × `error`) no mesmo projeto.
**Correção:** T08 — ao padronizar, **preserve** o formato atual do sucesso; padronize apenas o corpo de erro se isso não quebrar clientes (status HTTP deve permanecer).
