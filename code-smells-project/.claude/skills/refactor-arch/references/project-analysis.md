# Análise de Projeto — Heurísticas (Fase 1)

Objetivo: descobrir **o que** é o projeto e **como** ele está organizado, de forma independente de tecnologia, usando evidências (arquivos, imports, manifestos) — nunca suposições.

## 1. Detecção de linguagem

Ordem de evidência (da mais forte para a mais fraca):

| Evidência | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, maioria de `*.py` | Python |
| `package.json` + `*.js`/`*.mjs`/`*.cjs` | JavaScript (Node.js) |
| `package.json` + `tsconfig.json` / `*.ts` | TypeScript (Node.js) |
| `go.mod` | Go |
| `pom.xml`, `build.gradle` | Java/Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj` | C# |

- Conte arquivos por extensão (excluindo pastas ignoradas) — a extensão dominante confirma.
- Versão da linguagem: `python_requires`/`.python-version`, `engines.node` no `package.json`, `.nvmrc`. Se não declarada, informe "versão não declarada" (pode citar a versão instalada no ambiente, deixando claro).

## 2. Detecção de framework (e versão)

Procure no manifesto **e** confirme pelos imports no código:

| Sinal no manifesto | Sinal no código | Framework |
|---|---|---|
| `flask` | `from flask import Flask`, `Blueprint`, `@app.route` | Flask |
| `fastapi` | `FastAPI()`, `@app.get` | FastAPI |
| `django` | `settings.py`, `urls.py`, `models.Model` | Django |
| `express` | `require('express')`, `app.get(`, `express.Router()` | Express |
| `@nestjs/core` | decorators `@Controller` | NestJS |
| `koa`, `fastify`, `hapi` | `new Koa()`, `fastify()` | Koa / Fastify / Hapi |
| `spring-boot` | `@RestController` | Spring Boot |
| `gin-gonic/gin` | `gin.Default()` | Gin |

- Versão: use a versão do manifesto (`flask==3.1.1`, `"express": "^4.18.2"`). Se for um range (`^4.18.2`), cite o range e, se existir lockfile/`node_modules`, a versão resolvida.
- Liste extensões relevantes (ex.: `flask-cors`, `flask-sqlalchemy`, `marshmallow`, `sqlite3`, `mongoose`).

## 3. Detecção de banco de dados e forma de acesso

| Sinal | Banco / acesso |
|---|---|
| `import sqlite3`, `sqlite3.connect(`, `require('sqlite3')`, `new sqlite3.Database(` | SQLite, SQL cru |
| `':memory:'` | SQLite **em memória** (dados somem a cada boot) |
| `SQLAlchemy`, `db.Model`, `SQLALCHEMY_DATABASE_URI` | ORM SQLAlchemy (URI indica o engine) |
| `psycopg2`, `pg`, `mysql`, `mysql2`, `pymysql` | PostgreSQL / MySQL, SQL cru |
| `mongoose`, `pymongo` | MongoDB |
| `prisma`, `sequelize`, `typeorm`, `knex` | ORM/Query builder Node |

- **Tabelas:** procure `CREATE TABLE`, `__tablename__`, `class X(db.Model)`, `mongoose.model(`. Liste todas.
- **Seed/migração:** procure scripts `seed*`, inserts no boot, `db.create_all()`. Anote se o projeto exige rodar seed antes do boot (importante para a validação da Fase 3).

## 4. Detecção de domínio

Infira o domínio a partir de **nomes de tabelas/models + paths de rotas + mensagens**:

- `produtos`, `pedidos`, `carrinho`, `checkout` → E-commerce
- `courses`, `enrollments`, `students` → LMS / plataforma de cursos
- `tasks`, `categories`, `due_date`, `priority` → Task Manager
- Descreva em uma linha: "<Tipo> API (<entidades principais>)". Ex.: "LMS API com checkout (cursos, matrículas, pagamentos, usuários)".

## 5. Inventário de endpoints

| Framework | Onde encontrar rotas |
|---|---|
| Flask | `@app.route(`, `@<bp>.route(`, `app.add_url_rule(`, `methods=[...]` (default GET), `url_prefix` do Blueprint |
| Express | `app.<verbo>(`, `router.<verbo>(`, `app.use('<prefixo>', router)` |
| FastAPI | `@app.get/post/...`, `APIRouter(prefix=...)` |

Para cada rota registre: método, path completo (com prefixo), handler e `arquivo:linha`, e se recebe body/query params (e quais campos). Esse inventário é o **contrato** a preservar na Fase 3.

Também registre: comando de execução (`python app.py`, `npm start` → `scripts.start`), porta (`app.run(port=...)`, `app.listen(...)`, `config.port`) e pré-requisitos (seed).

## 6. Mapeamento e classificação da arquitetura

Para cada arquivo-fonte, identifique quais responsabilidades ele contém:

| Responsabilidade | Sinais |
|---|---|
| Roteamento (View/Route) | decorators/registro de rotas, `request`, `req`/`res` |
| Controle de fluxo (Controller) | leitura de input, chamada a regras, escolha de status HTTP |
| Regra de negócio (Service/Model) | cálculos, validações de domínio, decisões (desconto, estoque, pagamento) |
| Acesso a dados (Model) | SQL, `cursor.execute`, `db.run`, `Model.query`, `session` |
| Configuração | `SECRET_KEY`, URIs, portas, credenciais |
| Infra / bootstrap | criação do app, `listen`, `run`, schema/seed |

Classifique:

| Classificação | Critério |
|---|---|
| **Monolítica (sem camadas)** | Um ou poucos arquivos acumulam 3+ responsabilidades da tabela acima (ex.: classe que cria DB, faz seed e define rotas). |
| **Camadas nominais / parcialmente organizada** | Existem pastas `models/`, `routes/`, `services/`..., mas as rotas contêm regra de negócio e acesso a dados, ou há código de camada que ninguém usa. |
| **Em camadas (MVC/Clean)** | Cada camada tem uma responsabilidade e as dependências fluem em um só sentido (routes → controllers → services → models). |

Escreva a justificativa em uma frase com evidência concreta: "Monolítica — `AppManager.js` cria o banco, faz seed, define rotas e processa pagamento".

## 7. Contagem

- `Source files`: apenas arquivos de código-fonte da aplicação (inclua scripts como `seed.py`; exclua testes gerados, manifestos e lockfiles — mas informe-os à parte se relevante).
- Linhas: soma de `wc -l` dos arquivos-fonte (aproximada com `~`).
