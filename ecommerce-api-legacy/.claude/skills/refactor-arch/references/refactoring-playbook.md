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
| T16 | Remover/proteger endpoints perigosos | AP-05, AP-11 |
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
**Passos:** criar módulo de config; mover segredos, URIs, porta, debug; ler do ambiente com defaults **seguros** de desenvolvimento; substituir os usos; nunca retornar config em respostas.

```python
# ANTES (app.py)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# DEPOIS (config/settings.py)
import os, secrets, logging

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

if not os.environ.get("SECRET_KEY"):
    logging.getLogger(__name__).warning("SECRET_KEY não definida; usando chave aleatória (apenas desenvolvimento).")
```

```js
// ANTES (utils.js)
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123", port: 3000 };

// DEPOIS (src/config/index.js)
module.exports = {
  port: Number(process.env.PORT) || 3000,
  db: { user: process.env.DB_USER || '', pass: process.env.DB_PASS || '' },
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
};
```
Crie também um `.env.example` (sem valores reais) documentando as variáveis.

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

## T16 — Remover/proteger endpoints perigosos
**Passos:** remover rotas de execução arbitrária (SQL/código vindo do cliente); proteger rotas destrutivas administrativas com token de ambiente (desabilitadas se o token não estiver configurado); impedir que o cliente defina o próprio privilégio **somente** se não quebrar o contrato — caso contrário, listar como pendência.

```python
# ANTES
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(request.get_json()["sql"])

# DEPOIS — rota removida. Reset protegido:
def require_admin_token():
    expected = current_app.config.get("ADMIN_TOKEN")
    if not expected or not hmac.compare_digest(request.headers.get("X-Admin-Token", ""), expected):
        raise AppError("Não autorizado", 403)
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
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    register_routes(app)
    register_error_handlers(app)
    return app

app = create_app()            # mantém `from app import app` funcionando

if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
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
  app.listen(config.port, () => console.log(`Servidor rodando na porta ${config.port}`));
}
main();
```
