================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python (versão não declarada; ambiente 3.14.5) + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1
Files:   16 analyzed | ~1158 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 8 | LOW: 6

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-02 Credenciais e segredos hardcoded | app.py:13, services/notification_service.py:7-10 |
| 2 | CRITICAL | AP-03 Armazenamento inseguro de senhas | models/user.py:27-32 |
| 3 | CRITICAL | AP-04 Exposição de dados sensíveis (hash de senha nas respostas) | models/user.py:16-25 |
| 4 | HIGH | AP-07 Regra de negócio na rota (Fat Controller) | routes/task_routes.py:11-63, routes/report_routes.py:12-101 |
| 5 | HIGH | AP-08 Acesso a dados fora da camada Model | routes/task_routes.py, routes/user_routes.py, routes/report_routes.py |
| 6 | HIGH | AP-10 Configuração insegura | app.py:11-15, app.py:30-34 |
| 7 | HIGH | AP-11 Autenticação/autorização falsa | routes/user_routes.py:52, routes/user_routes.py:210 |
| 8 | MEDIUM | AP-13 Efeitos colaterais acoplados (↓ de HIGH, código morto) | services/notification_service.py:4-48 |
| 9 | MEDIUM | AP-14 Query N+1 | routes/task_routes.py:41-57, routes/user_routes.py:22 |
| 10 | MEDIUM | AP-15 Lógica duplicada / implementações paralelas | routes/task_routes.py:30-39, models/task.py:50-60, utils/helpers.py:57-108 |
| 11 | MEDIUM | AP-16 Validação de entrada ausente ou incompleta | routes/task_routes.py:113, routes/report_routes.py:196-197 |
| 12 | MEDIUM | AP-17 Tratamento de erros descentralizado / exceções engolidas | routes/task_routes.py:62-63, app.py:1-34 |
| 13 | MEDIUM | AP-18 APIs deprecated e dependências vulneráveis | routes/*.py (Query.get, utcnow), requirements.txt:1-6 |
| 14 | MEDIUM | AP-19 Agregação ineficiente | routes/task_routes.py:275-287, routes/report_routes.py:15-43 |
| 15 | MEDIUM | AP-20 Integridade referencial manual / registros órfãos | routes/user_routes.py:140-142, models/task.py:13-14 |
| 16 | LOW | AP-21 Magic numbers e strings | routes/task_routes.py:96-114, routes/user_routes.py:64,71 |
| 17 | LOW | AP-22 `print` como logging | routes/task_routes.py:149, routes/user_routes.py:83 |
| 18 | LOW | AP-23 Nomenclatura ruim | routes/report_routes.py:24-28, models/category.py:14 |
| 19 | LOW | AP-24 Código morto e imports não usados | app.py:7, utils/helpers.py:1-116, requirements.txt:4-6 |
| 20 | LOW | AP-25 Código verboso / não idiomático | models/task.py:38-60, models/user.py:34-38 |
| 21 | LOW | AP-26 Formato de resposta inconsistente | routes/task_routes.py:113, routes/task_routes.py:138,205 |

## Findings

### #1 [CRITICAL] AP-02 — Credenciais e segredos hardcoded
File: app.py:13, services/notification_service.py:7-10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` fixo no código; `NotificationService.__init__` define `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'` (além de host/porta SMTP) como literais.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de assinatura de sessão do Flask e a credencial SMTP; trocar os segredos exige alterar código e redeploy.
Recommendation: Extrair para `config.py` lendo `os.environ` (com default apenas de desenvolvimento) e injetar as credenciais SMTP no serviço de notificação (→ T02).

### #2 [CRITICAL] AP-03 — Armazenamento inseguro de senhas
File: models/user.py:27-32, routes/user_routes.py:64, routes/user_routes.py:115, seed.py:19, seed.py:26, seed.py:33
Description: `set_password` grava `hashlib.md5(pwd.encode()).hexdigest()` (MD5 sem salt) e `check_password` compara o MD5 com `==`. Senha mínima de apenas 4 caracteres (`len(password) < 4`); seed com senhas `'1234'`, `'abcd'`, `'pass'`.
Impact: MD5 sem salt é quebrado por rainbow tables em segundos; combinado ao finding #3 (hash exposto pela API), todas as senhas são recuperáveis.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (PBKDF2/scrypt com salt), mantendo verificação legada de MD5 com re-hash no próximo login para não invalidar usuários existentes (→ T03).

### #3 [CRITICAL] AP-04 — Exposição de dados sensíveis (hash de senha nas respostas)
File: models/user.py:16-25, routes/user_routes.py:33, routes/user_routes.py:85-86, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` inclui `'password': self.password`; é retornado por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login` (`'user': user.to_dict()`), todos sem autenticação.
Impact: Qualquer cliente anônimo lê o hash MD5 de qualquer usuário (`GET /users/1`), viabilizando a quebra offline das senhas (#2).
Recommendation: Remover `password` da serialização (serializer público na camada de view) — mudança intencional de contrato, por segurança (→ T04).

### #4 [HIGH] AP-07 — Regra de negócio na rota (Fat Controller)
File: routes/task_routes.py:11-63, routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/task_routes.py:273-299, routes/user_routes.py:42-90, routes/user_routes.py:153-183, routes/report_routes.py:12-101, routes/report_routes.py:103-155
Description: Os handlers contêm validação de domínio, cálculo de atraso (`if t.due_date < datetime.utcnow(): if t.status != 'done' and ...`), taxa de conclusão (`round((done / total) * 100, 2)`), conversão de tags e montagem dos relatórios. `summary_report` tem 90 linhas e `get_tasks` 53 linhas.
Impact: Regras não testáveis sem HTTP, impossíveis de reutilizar (ex.: atraso é recalculado em 6 lugares) e difíceis de alterar com segurança.
Recommendation: Criar `services/` (task_service, user_service, report_service, category_service) com as regras e deixar os handlers só lendo input e devolvendo resposta (→ T06).

### #5 [HIGH] AP-08 — Acesso a dados fora da camada Model
File: routes/task_routes.py:14, routes/task_routes.py:147-148, routes/task_routes.py:247-266, routes/user_routes.py:12, routes/user_routes.py:67, routes/user_routes.py:81-82, routes/report_routes.py:15-30, routes/report_routes.py:183-184 (+ todos os `Model.query`/`db.session` dos três arquivos de rotas)
Description: As rotas chamam diretamente `Task.query...`, `User.query.filter_by(...)`, `db.session.add/commit/rollback/delete`; não existe camada de repositório.
Impact: Acoplamento das rotas ao ORM; trocar consulta, adicionar eager-loading ou transação exige mexer em cada handler.
Recommendation: Concentrar consultas e escritas em funções/repositórios na camada Model, consumidos pelos services (→ T05/T06).

### #6 [HIGH] AP-10 — Configuração insegura
File: app.py:11, app.py:15, app.py:30-31, app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` expõe o debugger Werkzeug (execução de código) em todas as interfaces; `CORS(app)` libera qualquer origem; URI `'sqlite:///tasks.db'` fixa; `db.create_all()` executado no import do módulo; não há app factory (`create_app`).
Impact: Debugger interativo acessível pela rede permite RCE; impossível configurar ambientes distintos (teste/produção) sem editar código.
Recommendation: `config.py` lendo variáveis de ambiente (`FLASK_DEBUG`, `DATABASE_URL`, `CORS_ORIGINS`, `PORT`), `create_app()` como composition root, `python app.py` preservado (→ T02 + T17).

### #7 [HIGH] AP-11 — Autenticação/autorização ausente ou falsa
File: routes/user_routes.py:210, routes/user_routes.py:52, routes/user_routes.py:71-72, routes/user_routes.py:119-122, routes/user_routes.py:134-151
Description: `POST /login` retorna `'token': 'fake-jwt-token-' + str(user.id)` (previsível e nunca verificado); nenhuma rota exige autenticação; `POST /users` aceita `role` vindo do cliente (`data.get('role', 'user')`), permitindo auto-cadastro como `admin`; `DELETE /users/<id>` e troca de `role` em `PUT /users/<id>` são abertos.
Impact: Qualquer cliente anônimo cria administradores, altera papéis e apaga usuários com suas tasks.
Recommendation: Implementar autenticação real (token assinado) e autorização por papel; como exigir auth quebra o contrato atual, registrar como pendência de decisão humana (→ T16).

### #8 [MEDIUM] AP-13 — Efeitos colaterais acoplados (↓ de HIGH: código morto)
File: services/notification_service.py:4-48
Description: `NotificationService` instancia `smtplib.SMTP(...)` internamente com credenciais próprias, guarda notificações em lista em memória (`self.notifications = []`, estado mutável perdido a cada restart) e engole erros com `print`. A classe nunca é importada nem instanciada (verificado com Grep), por isso a severidade foi rebaixada.
Impact: Se for ligada às rotas como está, acopla o fluxo HTTP a SMTP síncrono, não é testável sem servidor de e-mail e perde notificações entre processos.
Recommendation: Tornar o serviço injetável (transport SMTP configurável via ambiente, implementação "log/no-op" em dev) e registrá-lo no composition root (→ T15).

### #9 [MEDIUM] AP-14 — Query N+1
File: routes/task_routes.py:41-57, routes/user_routes.py:22, routes/report_routes.py:55-56, routes/report_routes.py:161-163
Description: `get_tasks` faz `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` para cada task; `get_users` usa `len(u.tasks)` (lazy load por usuário); `summary_report` executa `Task.query.filter_by(user_id=u.id).all()` por usuário; `get_categories` executa `count()` por categoria.
Impact: 1 + 2N queries em `GET /tasks`; latência cresce linearmente com o volume.
Recommendation: Usar `joinedload`/`selectinload` ou consultas agregadas com `GROUP BY` na camada Model (→ T07).

### #10 [MEDIUM] AP-15 — Lógica duplicada / implementações paralelas
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-287, routes/user_routes.py:171-180, routes/report_routes.py:34-36, routes/report_routes.py:132-135, models/task.py:38-60, utils/helpers.py:57-108 (+ listas de status em task_routes.py:110,177, helpers.py:75,110, task.py:39; serialização manual em task_routes.py:17-28 e user_routes.py:162-169)
Description: O cálculo de atraso é copiado 6 vezes enquanto `Task.is_overdue()` existe e nunca é chamado; `Task.validate_status/validate_priority` e `helpers.process_task_data` (validação completa de task) também não são usados e as rotas reimplementam as mesmas regras; `validate_email`/`VALID_ROLES` em helpers são ignorados por user_routes (regex repetida em 61 e 106); `completion_rate` calculado 3 vezes em vez de `calculate_percentage`.
Impact: Regras divergem facilmente (create e update de task já validam de forma diferente); correções precisam ser replicadas em vários lugares.
Recommendation: Uma única implementação por regra (domínio no model/service, constantes centralizadas) reaproveitando os helpers corretos (→ T06 + T13).

### #11 [MEDIUM] AP-16 — Validação de entrada ausente ou incompleta
File: routes/task_routes.py:104, routes/task_routes.py:113, routes/task_routes.py:167-169, routes/task_routes.py:182, routes/task_routes.py:261, routes/task_routes.py:264, routes/report_routes.py:196-197, routes/report_routes.py:180, routes/user_routes.py:102-103, routes/user_routes.py:124-125
Description: `priority` do JSON é comparado sem conversão (`priority < 1`) — confirmado em runtime: `POST /tasks {"title":"abc","priority":"2"}` → 500; `len(data['title'])` com `null` → TypeError; `int(priority)`/`int(user_id)` em `/tasks/search` sem tratamento (`?priority=x` → 500); `update_category` não checa `data is None`; `color` não validado (`is_valid_color` existe e não é usado); `name`/`active` de usuário aceitos sem validação de tipo; `user_id`/`category_id` não validados como inteiros.
Impact: Entradas malformadas produzem 500 em vez de 400 e permitem gravar dados inválidos.
Recommendation: Validação centralizada por entidade (schema/validator) usada igualmente em create e update, devolvendo 400 (→ T12).

### #12 [MEDIUM] AP-17 — Tratamento de erros descentralizado / exceções engolidas
File: routes/task_routes.py:62-63, routes/task_routes.py:137, routes/task_routes.py:204, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207 (+4 ocorrências: report_routes.py:221, utils/helpers.py:46, 49, 88)
Description: `except:` genérico em todo o código; `get_tasks` envolve o handler inteiro em `try/except: return {'error': 'Erro interno'}` escondendo a causa; não há `@app.errorhandler` — exceções não tratadas retornam a página HTML padrão do Flask.
Impact: Erros reais são silenciados (sem log) e o cliente recebe formatos diferentes de erro; `except:` também captura `KeyboardInterrupt`/`SystemExit`.
Recommendation: Error handler centralizado (JSON `{'error': ...}` + log da exceção), exceções de domínio tipadas e remoção dos `try/except` repetidos (→ T08).

### #13 [MEDIUM] AP-18 — APIs deprecated / legadas e dependências vulneráveis
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/user_routes.py:29, routes/report_routes.py:105, routes/task_routes.py:31, models/task.py:15-16, requirements.txt:1-6 (+ demais ocorrências na tabela "Deprecated APIs")
Description: `Model.query.get(id)` (16 ocorrências) emite `LegacyAPIWarning` em runtime; `datetime.utcnow()` (Python ≥3.12) emite `DeprecationWarning`, inclusive como `default=` das colunas; `backref=` legado em `models/task.py:20-21`; `pip-audit` aponta 22 vulnerabilidades conhecidas em 5 pacotes (flask 3.0.0, flask-cors 4.0.0, requests 2.31.0, marshmallow 3.20.1, python-dotenv 1.0.0).
Impact: Quebra em versões futuras do SQLAlchemy/Python; dependências com CVEs publicados.
Recommendation: `db.session.get(Model, id)`, `datetime.now(timezone.utc)` (mantendo armazenamento naive-UTC para preservar o formato), `back_populates=`, atualizar dependências para versões corrigidas e remover as não usadas (→ T11).

### #14 [MEDIUM] AP-19 — Agregação ineficiente
File: routes/task_routes.py:275-287, routes/report_routes.py:15-43, routes/report_routes.py:111-135
Description: `task_stats` executa 5 `count()` separados e depois `Task.query.all()` só para contar atrasadas; `summary_report` executa 12 `count()` consecutivos (status e prioridade) mais um `all()`; `user_report` carrega todas as tasks do usuário para contar em Python.
Impact: Dezenas de round-trips ao banco por requisição e carga de todas as linhas em memória.
Recommendation: Agregar com `func.count` + `GROUP BY status/priority` e filtrar atrasadas no SQL (→ T07).

### #15 [MEDIUM] AP-20 — Integridade referencial manual / registros órfãos
File: routes/user_routes.py:140-142, models/task.py:13-14, models/task.py:20-21
Description: `delete_user` apaga as tasks do usuário em loop na rota (`for t in tasks: db.session.delete(t)`), em vez de declarar a política de exclusão no model; o SQLite roda sem `PRAGMA foreign_keys = ON`, então as FKs declaradas não são garantidas pelo banco. *Correção feita na Fase 3:* a versão inicial deste finding dizia que `delete_category` (routes/report_routes.py:211-223) deixava tasks órfãs; o teste em runtime mostrou que o relacionamento `backref` do ORM já anula o `category_id` das tasks, então esse trecho foi retirado.
Impact: Regra de exclusão espalhada pelas rotas; nada impede gravar referências inválidas direto no banco.
Recommendation: Declarar o cascade no relacionamento `User.tasks` e ligar `PRAGMA foreign_keys` na conexão (→ T09).

### #16 [LOW] AP-21 — Magic numbers e strings
File: routes/task_routes.py:96-114, routes/task_routes.py:177, routes/user_routes.py:64, routes/user_routes.py:71, routes/report_routes.py:45, routes/report_routes.py:129, routes/report_routes.py:180, app.py:34
Description: Limites `3`/`200` de título, faixa de prioridade `1..5`, senha mínima `4`, listas de status/roles inline, janela de `7` dias, `priority <= 2` como "alta prioridade", cor `'#000000'`, porta `5000`.
Impact: Mudar uma regra exige caçar literais em vários arquivos.
Recommendation: Constantes nomeadas em um módulo de domínio/config (→ T13).

### #17 [LOW] AP-22 — `print` como logging
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21 (+3 ocorrências: notification_service.py:24, utils/helpers.py:39, 41)
Description: Eventos e erros registrados com `print(...)`, ex.: `print(f"ERRO: {str(e)}")`.
Impact: Sem nível, timestamp ou destino configurável; erros se perdem em produção.
Recommendation: Usar o módulo `logging` (logger por módulo) (→ T14).

### #18 [LOW] AP-23 — Nomenclatura ruim
File: routes/report_routes.py:24-28, models/category.py:14, models/task.py:45, routes/task_routes.py:16, routes/user_routes.py:14, routes/report_routes.py:160
Description: Variáveis `p1`..`p5`, `d`, `p`, `t`, `u`, `c`, `cat` sem significado; `except Exception as e` com `e` não usado.
Impact: Leitura e manutenção mais difíceis.
Recommendation: Renomear durante a extração para services, preservando os nomes externos do contrato (→ T05/T06).

### #19 [LOW] AP-24 — Código morto e imports não usados
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:2-7, utils/helpers.py:9-108, requirements.txt:4-6
Description: Imports sem uso (`os, sys, json` em app.py; `json, os, sys, time` em task_routes; `hashlib, json` em user_routes; `format_date, calculate_percentage, json` em report_routes; `json` em models/task.py; `os, json, sys, math, hashlib` em helpers); funções de helpers nunca chamadas (`validate_email`, `sanitize_string`, `generate_id`, `log_action`, `parse_date`, `is_valid_color`, `process_task_data`); `User.is_admin` sem uso; `marshmallow`, `requests` e `python-dotenv` declarados e nunca importados.
Impact: Ruído, superfície de dependências vulneráveis desnecessária (ver #13).
Recommendation: Remover o que é inútil e reaproveitar os helpers corretos nas camadas novas (→ T05).

### #20 [LOW] AP-25 — Código verboso / não idiomático
File: models/task.py:38-60, models/user.py:34-38, utils/helpers.py:21-23, utils/helpers.py:53-55, routes/task_routes.py:141, routes/task_routes.py:210, utils/helpers.py:103
Description: `if cond: return True else: return False`; `is_overdue` com 3 níveis de `if` aninhados; `type(tags) == list` em vez de `isinstance`.
Impact: Código mais longo e propenso a erro.
Recommendation: Simplificar para expressões booleanas e `isinstance` durante a extração (→ T06).

### #21 [LOW] AP-26 — Formato de resposta inconsistente
File: routes/task_routes.py:113, routes/task_routes.py:138, routes/task_routes.py:205, routes/report_routes.py:197, routes/task_routes.py:96-100, routes/task_routes.py:167-170
Description: Erros previstos retornam JSON `{'error': ...}`, mas exceções não tratadas retornam HTML 500 do Flask (confirmado: `POST /tasks` com `priority: "2"`); mensagens divergentes para a mesma regra (`'Formato de data inválido. Use YYYY-MM-DD'` × `'Formato de data inválido'`; `'Senha deve ter no mínimo 4 caracteres'` × `'Senha muito curta'`).
Impact: Clientes precisam tratar dois formatos de erro.
Recommendation: Padronizar o corpo de erro via error handler central, mantendo status HTTP e formato de sucesso (→ T08).

## Deprecated APIs
| API | Location | Modern replacement | Evidence |
|---|---|---|---|
| `Query.get()` (`Model.query.get(id)`) | routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227; routes/user_routes.py:29, 94, 136, 155; routes/report_routes.py:105, 192, 213 | `db.session.get(Model, id)` | `LegacyAPIWarning` em runtime (`python -W default`, SQLAlchemy 2.x) |
| `datetime.utcnow()` | routes/task_routes.py:31, 72, 215, 285; routes/user_routes.py:172; routes/report_routes.py:35, 42, 45, 71, 133; models/task.py:15, 16, 52; models/user.py:14; models/category.py:11; utils/helpers.py:38; services/notification_service.py:35; seed.py:66-74 | `datetime.now(timezone.utc)` | `DeprecationWarning` em runtime (Python 3.14), inclusive via `default=` das colunas |
| `relationship(..., backref=...)` | models/task.py:20-21 | `back_populates=` nos dois lados | Busca estática (padrão legado SQLAlchemy 2.x) |
| Dependências vulneráveis | requirements.txt:1 (flask 3.0.0 → 3.1.3), :3 (flask-cors 4.0.0 → 6.0.0), :4 (marshmallow 3.20.1 → 3.26.2), :5 (requests 2.31.0 → 2.33.0), :6 (python-dotenv 1.0.0 → 1.2.2) | Atualizar/remover | `pip-audit -r requirements.txt`: 22 vulnerabilidades em 5 pacotes |

## Architecture Notes
- Current architecture: Camadas nominais / parcialmente organizada — existem `models/`, `routes/`, `services/`, `utils/`, mas as rotas concentram validação, regra de negócio, acesso a dados e serialização; `services/` e quase todo `utils/helpers.py` são código morto; o CRUD de categorias está em `report_routes.py`.
- Refactoring strategy: incremental layering — reaproveitar `models/` (entidades SQLAlchemy), `database.py`, e os helpers úteis; adicionar `config.py`, repositórios/consultas no model, `services/` com regras, `controllers/`, rotas finas (blueprints atuais), error handler central e `create_app()`.
- Contract constraints: preservar as 22 rotas e métodos (`/tasks`, `/tasks/<id>`, `/tasks/search`, `/tasks/stats`, `/users`, `/users/<id>`, `/users/<id>/tasks`, `/login`, `/reports/summary`, `/reports/user/<id>`, `/categories`, `/categories/<id>`, `/health`, `/`), campos de entrada (`title`, `description`, `status`, `priority`, `user_id`, `category_id`, `due_date` em `YYYY-MM-DD`, `tags` lista ou string, `name`, `email`, `password`, `role`, `active`, `color`; query `q`, `status`, `priority`, `user_id`), chaves das respostas (ex.: `overdue`, `user_name`, `category_name`, `task_count`, `token`), status HTTP (201/400/401/403/404/409) e o comando `python seed.py && python app.py` na porta 5000. Mudança intencional: remover `password` das respostas (#3).

================================
Total: 21 findings
================================
