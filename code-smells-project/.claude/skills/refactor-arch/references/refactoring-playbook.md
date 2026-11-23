# Playbook de Refatoração (Fase 3)

Cada transformação indica os anti-patterns que resolve, os passos e um exemplo **antes → depois**. Os exemplos são ilustrativos: adapte nomes, campos e envelope de resposta ao projeto real **preservando o contrato** (ver `mvc-guidelines.md` §4).

| ID | Transformação | Resolve |
|---|---|---|
| T01 | Queries parametrizadas | AP-01 |
| T02 | Extrair configuração para ambiente | AP-02, AP-10 |
| T03 | Hash de senha seguro com migração transparente | AP-03 |
| T04 | Serialização segura e logs sem dados sensíveis | AP-04 |
| T05 | Decompor God Class/File em camadas MVC | AP-06, AP-08, AP-23, AP-24 |
| T06 | Extrair regra de negócio para service/model (e achatar callbacks) | AP-07, AP-13, AP-15, AP-25 |
| T07 | Eliminar N+1 e agregações ineficientes | AP-14, AP-19 |
| T08 | Error handler centralizado | AP-17, AP-26 |
| T09 | Transações em operações multi-escrita | AP-12, AP-20 |
| T10 | Substituir estado global por dependências gerenciadas | AP-09 |
| T11 | Substituir APIs deprecated | AP-18 |
| T12 | Validação de entrada centralizada | AP-16 |
| T13 | Constantes nomeadas | AP-21, AP-15 |
| T14 | Logging estruturado | AP-22 |
| T15 | Efeitos colaterais via serviço injetável | AP-13 |
| T16 | Remover/proteger endpoints perigosos e implementar autenticação real (token assinado + papel definido pelo servidor) | AP-05, AP-11 |
| T17 | App factory / composition root | AP-06, AP-10 |

---

## T01 — Queries parametrizadas
**Passos:** localizar toda query com concatenação/interpolação; trocar valores por placeholders; passar parâmetros separadamente; para filtros dinâmicos, montar a lista de cláusulas **e** a lista de parâmetros juntas.

```python
# ANTES
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")

query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND (nome LIKE '%" + termo + "%')"
cursor.execute(query)

# DEPOIS
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))

clauses, params = ["1=1"], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)")
    params += [f"%{termo}%", f"%{termo}%"]
cursor.execute(f"SELECT * FROM produtos WHERE {' AND '.join(clauses)}", params)  # só cláusulas fixas são interpoladas
```

```js
// ANTES
db.get(`SELECT * FROM users WHERE id = ${req.params.id}`, cb);
// DEPOIS
const user = await db.get('SELECT * FROM users WHERE id = ?', [id]);
```

## T02 — Extrair configuração para ambiente
**Passos:** criar módulo de config; mover segredos, URIs, porta, debug, host e origens de CORS; ler do ambiente com defaults **seguros** (os mesmos que a Recommendation do AP-10 cita); substituir os usos; nunca retornar config em respostas.

**Defaults seguros obrigatórios (AP-10, nunca "Pending"):**

| Variável | Default | Para o comportamento antigo |
|---|---|---|
| `FLASK_DEBUG` / `APP_DEBUG` | desligado | `FLASK_DEBUG=1` (só desenvolvimento) |
| `HOST` | `127.0.0.1` | `HOST=0.0.0.0` |
| `CORS_ORIGINS` | vazio = **nenhuma** origem externa | `CORS_ORIGINS=https://app.exemplo.com,https://admin.exemplo.com` (ou `*`, explicitamente) |
| `SECRET_KEY` | aleatório por boot + aviso no log | definir no ambiente |

```python
# ANTES (app.py)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
CORS(app)                                   # qualquer origem
app.run(host="0.0.0.0", port=5000, debug=True)

# DEPOIS (config/settings.py)
import os, secrets, logging

def _csv(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "127.0.0.1")       # expor na rede é explícito
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = _csv("CORS_ORIGINS")               # [] = CORS fechado; ["*"] só se definido

if not os.environ.get("SECRET_KEY"):
    logging.getLogger(__name__).warning("SECRET_KEY não definida; usando chave aleatória (apenas desenvolvimento).")
```
O registro do CORS fica no composition root (T17): só com lista não vazia.

```js
// ANTES (utils.js)
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123", port: 3000 };
app.use(cors());                                       // qualquer origem

// DEPOIS (src/config/index.js)
const csv = (v) => (v || '').split(',').map((s) => s.trim()).filter(Boolean);
module.exports = {
  port: Number(process.env.PORT) || 3000,
  host: process.env.HOST || '127.0.0.1',
  corsOrigins: csv(process.env.CORS_ORIGINS),          // [] = CORS fechado
  db: { user: process.env.DB_USER || '', pass: process.env.DB_PASS || '' },
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
};
// src/app.js: if (config.corsOrigins.length) app.use(cors({ origin: config.corsOrigins }));
// app.listen(config.port, config.host)
```
Crie também um `.env.example` (sem valores reais) documentando as variáveis e os defaults. Se o projeto original **não** usava CORS nem outro host, não acrescente nada: mantenha o comportamento (fechado) e só leia `PORT`/`HOST` do ambiente.

## T03 — Hash de senha seguro com migração transparente
**Passos:** usar algoritmo forte com salt; ao fazer login, se o hash armazenado for legado (texto puro, MD5, base64), validar pelo método antigo e **regravar** com o novo (migração sem quebrar usuários existentes); seeds passam a gravar hash; nunca comparar senha no SQL.

```python
# ANTES
self.password = hashlib.md5(pwd.encode()).hexdigest()
def check_password(self, pwd): return self.password == hashlib.md5(pwd.encode()).hexdigest()

# DEPOIS
import hashlib, hmac
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(raw):
    return generate_password_hash(raw)  # scrypt/pbkdf2 com salt

def verify_password(stored, raw):
    """Retorna (ok, precisa_rehash)."""
    if stored and stored.startswith(("scrypt:", "pbkdf2:")):
        return check_password_hash(stored, raw), False
    legacy_md5 = hashlib.md5(raw.encode()).hexdigest()
    ok = hmac.compare_digest(stored or "", legacy_md5) or hmac.compare_digest(stored or "", raw)  # MD5 ou texto puro legado
    return ok, ok
```
Login: `ok, rehash = verify_password(user.password, senha)`; se `ok and rehash`, salvar `hash_password(senha)`.

```js
// ANTES
function badCrypto(pwd) { /* base64 truncado */ }
// DEPOIS (Node, sem dependências extras)
const crypto = require('crypto');
function hashPassword(raw) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(raw, salt, 64).toString('hex');
  return `scrypt$${salt}$${hash}`;
}
function verifyPassword(stored, raw) {
  const [algo, salt, hash] = String(stored).split('$');
  if (algo !== 'scrypt') return false;
  const candidate = crypto.scryptSync(raw, salt, 64);
  return crypto.timingSafeEqual(candidate, Buffer.from(hash, 'hex'));
}
```
Se a senha for opcional no fluxo original, **não** use senha padrão conhecida: gere uma aleatória (`crypto.randomBytes(12).toString('hex')`).

## T04 — Serialização segura e logs sem dados sensíveis
**Passos:** criar serializer/presenter por entidade com lista explícita de campos públicos; remover `password`/hash/segredos; nunca logar cartão, CVV, chaves ou senhas (mascarar: `**** **** **** 4444`).

```python
# ANTES
def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password, "role": self.role}

# DEPOIS
PUBLIC_FIELDS = ("id", "name", "email", "role", "active", "created_at")
def to_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email, "role": self.role,
            "active": self.active, "created_at": str(self.created_at)}
```

```js
// ANTES
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
// DEPOIS
logger.info(`Processando pagamento com cartão final ${String(card).slice(-4)}`);
```

## T05 — Decompor God Class/File em camadas MVC
**Passos:**
1. Listar funções/métodos do arquivo e classificar cada um (rota, controller, regra, acesso a dados, config, bootstrap) — use o mapa da Fase 1.
2. Criar um model por entidade com as funções de acesso a dados (já parametrizadas — T01).
3. Criar controllers por entidade com o fluxo HTTP; services para regras entre entidades.
4. Criar routes/views registrando cada path → controller (mesmos paths/métodos).
5. Mover schema/seed para `database`; criar composition root (T17).
6. Remover o arquivo antigo, imports mortos e renomear variáveis ruins internas.

```python
# ANTES — models.py (God File: produtos + usuários + pedidos + relatórios, SQL + regras)
def criar_pedido(usuario_id, itens): ...  # valida estoque, calcula total, grava, baixa estoque
def relatorio_vendas(): ...              # SQL + regra de desconto

# DEPOIS
# models/produto_model.py   -> ProdutoModel.find_by_id / list / create / update / delete
# models/pedido_model.py    -> PedidoModel.create_with_items (transação), list_with_items (JOIN)
# services/pedido_service.py-> criar_pedido(usuario_id, itens) (valida estoque, total)
# services/relatorio_service.py -> relatorio_vendas() (regra de desconto com constantes)
# controllers/pedido_controller.py -> lê request, chama service, devolve status
# views/routes.py           -> Blueprint com os mesmos paths
```

```js
// ANTES — class AppManager { constructor(){ this.db = new sqlite3.Database(':memory:') } initDb(){...} setupRoutes(app){ app.post('/api/checkout', ...) } }
// DEPOIS
// src/database/index.js         -> createDatabase(), initSchema(), seed(), helpers Promise
// src/models/courseModel.js     -> findActiveById(id), listAll()
// src/services/checkoutService.js -> checkout({ name, email, password, courseId, card })
// src/controllers/checkoutController.js -> mapeia {usr, eml, pwd, c_id, card} e responde
// src/routes/index.js           -> router.post('/api/checkout', asyncHandler(controller.checkout))
// src/app.js                    -> composition root
```

## T06 — Extrair regra de negócio para service/model (e achatar callbacks)
**Passos:** mover cálculos/decisões para funções puras ou services que recebem dados e retornam resultado (ou lançam erro de domínio); controller fica com: ler input → validar → chamar service → responder. Em Node, converter callbacks em `async/await`. Reaproveitar métodos de model existentes e remover as cópias.

```python
# ANTES (rota)
@task_bp.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = Task.query.get(task_id)
    data = task.to_dict()
    if task.due_date:
        if task.due_date < datetime.utcnow():
            if task.status != 'done' and task.status != 'cancelled':
                data['overdue'] = True
    ...

# DEPOIS
# models/task.py
def is_overdue(self):
    return bool(self.due_date) and self.due_date < utcnow() and self.status not in CLOSED_STATUSES
# controllers/task_controller.py
def get_task(task_id):
    task = task_service.get_or_404(task_id)
    return jsonify(task_view.serialize(task)), 200   # serialize inclui 'overdue': task.is_overdue()
```

```js
// ANTES — 5 níveis de callback na rota
db.get(sqlCourse, [cid], (err, course) => { db.get(sqlUser, [e], (err, user) => { db.run(..., function () { self.db.run(..., () => { ... }) }) }) });

// DEPOIS — service com async/await
async function checkout({ name, email, password, courseId, card }) {
  const course = await courseModel.findActiveById(courseId);
  if (!course) throw new NotFoundError('Curso não encontrado');
  const user = await userModel.findByEmail(email) ?? await userModel.create({ name, email, password });
  const status = paymentGateway.charge(card, course.price);          // regra isolada e injetável
  if (status !== PAYMENT_STATUS.PAID) throw new PaymentDeclinedError('Pagamento recusado');
  return db.transaction(async (tx) => {                               // T09
    const enrollmentId = await enrollmentModel.create(tx, user.id, course.id);
    await paymentModel.create(tx, enrollmentId, course.price, status);
    await auditModel.log(tx, `Checkout curso ${course.id} por ${user.id}`);
    return enrollmentId;
  });
}
```

## T07 — Eliminar N+1 e agregações ineficientes
**Passos:** substituir query-dentro-de-loop por um `JOIN` (SQL cru) ou eager loading (ORM) e montar a estrutura em memória; substituir N `COUNT` por um `GROUP BY`.

```python
# ANTES — 1 + N + N*M queries
for row in pedidos:
    itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        prod = db.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))

# DEPOIS — 1 query
rows = db.execute("""
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    WHERE (? IS NULL OR p.usuario_id = ?)
    ORDER BY p.id""", (usuario_id, usuario_id)).fetchall()
# agrupar por p.id em um dict preservando a ordem
```

```python
# ORM — eager loading e agregação
from sqlalchemy.orm import joinedload
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

from sqlalchemy import func
counts = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
pending = counts.get("pending", 0)
```

```js
// ANTES — forEach com db.get por matrícula
// DEPOIS
const rows = await db.all(`
  SELECT c.id AS course_id, c.title, u.name AS student, p.amount, p.status
  FROM courses c
  LEFT JOIN enrollments e ON e.course_id = c.id
  LEFT JOIN users u ON u.id = e.user_id
  LEFT JOIN payments p ON p.enrollment_id = e.id
  ORDER BY c.id, e.id`);
```
**Atenção ao contrato:** mantenha a mesma forma do resultado (ex.: `student: 'Unknown'` quando o usuário não existe, `paid: 0` sem pagamento).

## T08 — Error handler centralizado
**Passos:** criar exceções de domínio (`NotFoundError`, `ValidationError`, ...) com status; registrar handler global; remover `try/except` genéricos dos controllers; mensagens genéricas para 500 (logar o detalhe no servidor).

```python
# ANTES — em cada controller
try:
    ...
except Exception as e:
    return jsonify({"erro": str(e)}), 500

# DEPOIS — middlewares/error_handler.py
class AppError(Exception):
    status_code = 400
    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code: self.status_code = status_code

class NotFoundError(AppError): status_code = 404

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": str(err), "sucesso": False}), err.status_code   # mesma chave de erro do projeto

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        app.logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
```

```js
// src/middlewares/errorHandler.js
class AppError extends Error { constructor(message, status = 400) { super(message); this.status = status; } }
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) return res.status(err.status).send(err.message); // preserve formato (texto/JSON) original
  logger.error(err);
  return res.status(500).send('Erro interno');
}
module.exports = { AppError, asyncHandler, errorHandler };
// app.js: app.use(errorHandler) DEPOIS das rotas
```

## T09 — Transações em operações multi-escrita
**Passos:** agrupar escritas relacionadas em uma transação com commit/rollback; fazer verificação e débito de estoque de forma atômica (`UPDATE ... SET estoque = estoque - ? WHERE id = ? AND estoque >= ?` e checar `rowcount`); exclusões em cascata dentro da mesma transação.

```python
# ANTES
cursor.execute("INSERT INTO pedidos ...")
for item in itens:
    cursor.execute("INSERT INTO itens_pedido ...")
    cursor.execute("UPDATE produtos SET estoque = estoque - ...")
db.commit()

# DEPOIS
with conn:   # sqlite3: commit no sucesso, rollback em exceção
    cur = conn.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)", (usuario_id, total))
    pedido_id = cur.lastrowid
    for item in itens:
        upd = conn.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                           (item["quantidade"], item["produto_id"], item["quantidade"]))
        if upd.rowcount == 0:
            raise ValidationError(f"Estoque insuficiente para o produto {item['produto_id']}")
        conn.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                     (pedido_id, item["produto_id"], item["quantidade"], precos[item["produto_id"]]))
```

```js
// Node + sqlite3 (conexão única): serializar transações com uma fila simples
let queue = Promise.resolve();
function transaction(work) {
  const result = queue.then(async () => {
    await run('BEGIN');
    try { const value = await work(); await run('COMMIT'); return value; }
    catch (err) { await run('ROLLBACK'); throw err; }
  });
  queue = result.catch(() => {});
  return result;
}
```

**Integridade referencial (AP-20) — escolha conforme o filho:**

```python
# Filho é histórico (itens de pedido → produto): SOFT DELETE do pai
# ANTES
conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))   # itens ficam apontando para o nada
# DEPOIS (model)
def deletar(produto_id):
    with conn:
        conn.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
def listar():
    return conn.execute("SELECT ... FROM produtos WHERE ativo = 1").fetchall()   # leituras públicas filtram ativos
# O histórico do pedido continua com o nome do produto; GET /produtos/<id> do excluído → 404 (como antes).
```

```js
// Filho pertence ao pai (matrículas e pagamentos de um usuário): CASCATA na mesma transação
// ANTES
db.run('DELETE FROM users WHERE id = ?', [id]);   // "matrículas e pagamentos ficaram sujos no banco"
// DEPOIS (service)
async function deleteUser(id) {
  return db.transaction(async () => {
    const user = await userModel.findById(id);
    if (!user) throw new NotFoundError('Usuário não encontrado');           // antes: 200 falso
    await paymentModel.deleteByUser(id);    // DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)
    await enrollmentModel.deleteByUser(id); // DELETE FROM enrollments WHERE user_id = ?
    await userModel.deleteById(id);
  });
}
```
Atualizações e exclusões que hoje respondem 200 para id inexistente passam a checar `rowcount`/`changes` e responder 404 (mudança permitida, `mvc-guidelines.md` §4).

## T10 — Substituir estado global por dependências gerenciadas
**Passos:** conexões por requisição (Flask `g` + `teardown_appcontext`) ou criadas no composition root e injetadas; caches com escopo e limite definidos (ou removidos se não lidos); remover variáveis globais mortas.

```python
# ANTES
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)
    return db_connection

# DEPOIS
from flask import g, current_app
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
# create_app(): app.teardown_appcontext(close_db)
```

```js
// ANTES: let globalCache = {}; let totalRevenue = 0;  (módulo)
// DEPOIS: cache como dependência explícita, com limite, criada no composition root
function createCache(max = 1000) {
  const store = new Map();
  return { set(k, v) { store.delete(k); store.set(k, v); if (store.size > max) store.delete(store.keys().next().value); }, get: (k) => store.get(k) };
}
```

## T11 — Substituir APIs deprecated
**Passos:** aplicar a tabela do AP-18; centralizar em helper quando o uso é repetido; validar em runtime com `-W default` / `--trace-deprecation`.

```python
# ANTES
created_at = db.Column(db.DateTime, default=datetime.utcnow)
task = Task.query.get(task_id)

# DEPOIS
from datetime import datetime, timezone
def utcnow():
    # mantém datetime "naive" em UTC para compatibilidade com dados já gravados no SQLite
    return datetime.now(timezone.utc).replace(tzinfo=None)

created_at = db.Column(db.DateTime, default=utcnow)
task = db.session.get(Task, task_id)          # ou db.get_or_404(Task, task_id)
```

```js
// ANTES
const buf = new Buffer(pwd); const u = url.parse(req.url);
res.json(201, body);
// DEPOIS
const buf = Buffer.from(pwd); const u = new URL(req.url, 'http://localhost');
res.status(201).json(body);
```

## T12 — Validação de entrada centralizada
**Passos:** criar validadores por entidade (funções puras ou schema) usados por create e update; checar body `None`, presença, **tipo**, faixa e formato; responder 400 (via `ValidationError` + T08).

```python
# ANTES
priority = data.get('priority', 3)
if priority < 1 or priority > 5:          # "alta" -> TypeError -> 500
    return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400

# DEPOIS — validators/task_validator.py (ou dentro do controller)
def parse_priority(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("Prioridade deve ser entre 1 e 5")
    if not MIN_PRIORITY <= value <= MAX_PRIORITY:
        raise ValidationError("Prioridade deve ser entre 1 e 5")
    return value

def require_json(req):
    data = req.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    return data
```
Mantenha as **mesmas mensagens** e status do código original quando existirem.

## T13 — Constantes nomeadas
**Passos:** mover números/listas de regra para `config/constants` (ou para o model/service dono da regra); reutilizar em todos os pontos; preservar valores exatamente.

```python
# ANTES
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05

# DEPOIS
DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))   # (faturamento mínimo exclusivo, taxa)
def calcular_desconto(faturamento):
    for limite, taxa in DISCOUNT_TIERS:
        if faturamento > limite:
            return faturamento * taxa
    return 0
```

## T14 — Logging estruturado
**Passos:** configurar logger no composition root; trocar `print`/`console.log` por níveis (`info`, `warning`, `error`); não logar dados sensíveis (T04).

```python
# ANTES
print("ERRO ao criar produto: " + str(e))
# DEPOIS
logger = logging.getLogger(__name__)
logger.exception("Erro ao criar produto")
```

```js
// src/utils/logger.js
const logger = { info: (...a) => console.log('[INFO]', ...a), error: (...a) => console.error('[ERROR]', ...a) };
module.exports = logger;
```

## T15 — Efeitos colaterais via serviço injetável
**Passos:** criar interface/serviço (`NotificationService`, `PaymentGateway`) com implementação atual (ex.: log ou simulação); injetar no service/controller pelo composition root; credenciais via config (T02). Comportamento observável deve continuar o mesmo.

```python
# ANTES (controller)
print("ENVIANDO EMAIL: Pedido " + str(pedido_id) + " criado para usuario " + str(usuario_id))
print("ENVIANDO SMS: Seu pedido foi recebido!")

# DEPOIS
class NotificationService:
    def __init__(self, logger): self.logger = logger
    def pedido_criado(self, pedido_id, usuario_id):
        self.logger.info("Notificação de pedido %s enviada ao usuário %s (email/sms/push)", pedido_id, usuario_id)

# services/pedido_service.py
class PedidoService:
    def __init__(self, pedido_model, notifier): ...
    def criar(self, usuario_id, itens):
        pedido = self.pedido_model.create_with_items(usuario_id, itens)
        self.notifier.pedido_criado(pedido["pedido_id"], usuario_id)
        return pedido
```

## T16 — Remover/proteger endpoints perigosos e implementar autenticação real
Resolve AP-05 e **AP-11 por completo**. AP-11 nunca vai para "Pending": a exigência de token nas rotas protegidas é mudança de contrato de segurança permitida (`mvc-guidelines.md` §4) e deve ser listada no resumo.

**Passos:**
1. **Remover** rotas de execução arbitrária (SQL/código vindo do cliente).
2. **Classificar** cada endpoint do inventário pela matriz de acesso (`mvc-guidelines.md` §4): público / autenticado (dono ou admin) / admin.
3. **Emitir token assinado no login:** HMAC com o `SECRET_KEY` da config (T02), com expiração; payload só com o id do usuário. Mantenha a chave da resposta original (`token`) ou adicione `token` dentro do envelope existente. Python/Flask: `itsdangerous` (já é dependência do Flask — fixe-a no manifesto); Node: `crypto.createHmac` (sem dependência nova). Em outras stacks, a biblioteca JWT/assinatura idiomática.
4. **Middleware de auth** (`middlewares/auth.*`): lê `Authorization: Bearer <token>`, valida assinatura e expiração, **recarrega o usuário do banco** (papel e `active` vêm do banco, nunca do token nem do corpo) e o disponibiliza na requisição (`g.current_user` / `req.user`). Erros: sem token/inválido/expirado/usuário inexistente ou inativo → 401; sem papel → 403 (via exceções do error handler central, T08).
5. **Aplicar a política na camada de rotas** (decorators `login_required`/`admin_required` ou middlewares por rota), deixando a matriz visível no arquivo de rotas. Verificação de **dono** (`usuario_id` da rota/corpo == usuário do token, salvo admin) fica no controller, com helper único `ensure_self_or_admin`.
6. **Papel definido pelo servidor:** o cadastro público grava o papel padrão e ignora `role`/`tipo`/`is_admin` do corpo; se quem chama é admin autenticado, o papel informado é aceito (validado contra a lista de papéis). No update, alterar `role`/`active` exige admin (403 para os demais).
7. **Projetos sem login/papéis:** proteger as rotas admin com credencial do servidor (`ADMIN_TOKEN` do ambiente, enviada como Bearer, comparada com `hmac.compare_digest`/`crypto.timingSafeEqual`); sem a variável, rotas admin desabilitadas (401). Nunca gerar e logar um token.
8. **Seed e documentação:** o seed deve ter ao menos um admin (senha com hash, T03); documente no README como obter e enviar o token e acrescente `SECRET_KEY`/`TOKEN_MAX_AGE`/`ADMIN_TOKEN` ao `.env.example`.
9. **Validar** (`mvc-guidelines.md` §6): mesmas respostas do baseline com token; 401 sem token/adulterado; 403 para usuário comum em rota admin e em recurso de outro usuário; cadastro com `role: admin` sem token → papel padrão.

```python
# ANTES
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(request.get_json()["sql"])          # → rota REMOVIDA

def login():
    ...
    return jsonify({"token": "fake-jwt-token-" + str(user.id), "user": user.to_dict()})

def create_user():
    user = User(name=data["name"], email=data["email"], role=data.get("role", "user"))  # cliente escolhe o papel

# DEPOIS — services/auth_service.py (token assinado com expiração)
import hashlib
from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

def _serializer():  # HMAC-SHA256 (o padrão do itsdangerous é SHA1)
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth-token",
                                  signer_kwargs={"digest_method": hashlib.sha256})

def issue_token(user):
    return _serializer().dumps({"uid": user.id})

def user_from_token(token):
    try:
        data = _serializer().loads(token, max_age=current_app.config["TOKEN_MAX_AGE"])
    except (BadSignature, SignatureExpired):
        raise UnauthorizedError("Token inválido ou expirado") from None
    user = User.get_by_id(data.get("uid"))            # papel e status relidos do banco
    if user is None or not user.active:
        raise UnauthorizedError("Token inválido ou expirado")
    return user

# DEPOIS — middlewares/auth.py
from functools import wraps
from flask import g, request

def _authenticate():
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedError("Autenticação necessária")
    g.current_user = auth_service.user_from_token(token.strip())

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        _authenticate()
        return view(*args, **kwargs)
    return wrapper

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        _authenticate()
        if not g.current_user.is_admin():
            raise ForbiddenError("Acesso restrito a administradores")
        return view(*args, **kwargs)
    return wrapper

def optional_user():
    """Usuário autenticado ou None (para o cadastro público aceitar papel apenas de admin)."""
    try:
        _authenticate()
        return g.current_user
    except UnauthorizedError:
        return None

def ensure_self_or_admin(user_id):
    if g.current_user.id != user_id and not g.current_user.is_admin():
        raise ForbiddenError("Acesso negado")

# DEPOIS — routes/user_routes.py (matriz de acesso visível)
user_bp.add_url_rule("/users", view_func=admin_required(user_controller.list_users), methods=["GET"])
user_bp.add_url_rule("/users", view_func=user_controller.create_user, methods=["POST"])        # público
user_bp.add_url_rule("/users/<int:user_id>", view_func=login_required(user_controller.get_user), methods=["GET"])
user_bp.add_url_rule("/users/<int:user_id>", view_func=admin_required(user_controller.delete_user), methods=["DELETE"])
user_bp.add_url_rule("/login", view_func=user_controller.login, methods=["POST"])              # público

# DEPOIS — controllers/user_controller.py (papel definido pelo servidor)
def create_user():
    fields = validators.user_create_payload(validators.json_body())
    caller = optional_user()
    if caller is None or not caller.is_admin():
        fields["role"] = DEFAULT_ROLE                  # cadastro público nunca escolhe o papel
    return jsonify(user_service.create_user(**fields).to_dict()), 201

def update_user(user_id):
    ensure_self_or_admin(user_id)
    changes = validators.user_update_payload(validators.json_body())
    if ({"role", "active"} & changes.keys()) and not g.current_user.is_admin():
        raise ForbiddenError("Somente administradores alteram papel ou status")
    ...

def login():
    ...
    return jsonify({"token": auth_service.issue_token(user), "user": user.to_dict()}), 200  # mesma chave "token"
```

```js
// DEPOIS — src/utils/token.js (HMAC-SHA256 + expiração, sem dependências)
const crypto = require('crypto');
const b64 = (buf) => Buffer.from(buf).toString('base64url');
function signToken(payload, secret, ttlSeconds) {
  const body = b64(JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + ttlSeconds }));
  return `${body}.${b64(crypto.createHmac('sha256', secret).update(body).digest())}`;
}
function verifyToken(token, secret) {
  const [body, sig] = String(token).split('.');
  if (!body || !sig) return null;
  const expected = crypto.createHmac('sha256', secret).update(body).digest();
  const given = Buffer.from(sig, 'base64url');
  if (given.length !== expected.length || !crypto.timingSafeEqual(given, expected)) return null;
  const payload = JSON.parse(Buffer.from(body, 'base64url').toString());
  return payload.exp > Date.now() / 1000 ? payload : null;
}

// DEPOIS — src/middlewares/auth.js
const bearer = (req) => { const [s, t] = (req.get('authorization') || '').split(' '); return s?.toLowerCase() === 'bearer' ? t : null; };
function createAuth({ userModel, config }) {
  const authenticate = async (req, res, next) => {
    const payload = verifyToken(bearer(req), config.secretKey);
    const user = payload && await userModel.findById(payload.uid);   // papel relido do banco
    if (!user) return next(new UnauthorizedError());
    req.user = user; next();
  };
  const requireAdmin = (req, res, next) => (req.user.role === 'admin' ? next() : next(new ForbiddenError()));
  return { authenticate, requireAdmin };
}
// Sem usuários/papéis no projeto: credencial de admin definida no servidor
function requireAdminToken(config) {
  return (req, res, next) => {
    const expected = Buffer.from(config.adminToken || '');
    const given = Buffer.from(bearer(req) || '');
    if (!expected.length || given.length !== expected.length || !crypto.timingSafeEqual(given, expected)) {
      return next(new UnauthorizedError());
    }
    next();
  };
}
// routes: router.get('/api/admin/financial-report', requireAdminToken(config), asyncHandler(...));
```

## T17 — App factory / composition root
**Passos:** `create_app(config)` cria o app, carrega config, inicializa banco/extensões, instancia dependências (models, services, notifier), registra rotas e error handlers; o entry point original continua funcionando (`python app.py`, `npm start`) e expõe `app` no módulo se scripts externos o importam (ex.: `seed.py`).

```python
# DEPOIS — app.py
from flask import Flask
from config.settings import Config
from database import init_db, close_db
from middlewares.error_handler import register_error_handlers
from views.routes import register_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if app.config["CORS_ORIGINS"]:                     # AP-10: CORS fechado por padrão
        CORS(app, origins=app.config["CORS_ORIGINS"])  # from flask_cors import CORS
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    register_routes(app)
    register_error_handlers(app)
    return app

app = create_app()            # mantém `from app import app` funcionando

if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])  # 127.0.0.1 / debug off por padrão
```

```js
// DEPOIS — src/app.js
const express = require('express');
const config = require('./config');
const { createDatabase } = require('./database');
const buildRoutes = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

async function main() {
  const db = await createDatabase();                 // schema + seed
  const app = express();
  app.use(express.json());
  app.use(buildRoutes({ db }));                      // injeta dependências
  app.use(errorHandler);
  app.listen(config.port, config.host, () => console.log(`Servidor rodando em ${config.host}:${config.port}`));
}
main();
```
