================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python (versão não declarada; 3.14.5 no ambiente) + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1)
Files:   15 analyzed | ~1158 lines of code
Date:    2026-11-23

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 8 | LOW: 5

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-02 Credenciais e segredos hardcoded | app.py:13, services/notification_service.py:7-10 |
| 2 | CRITICAL | AP-03 Armazenamento inseguro de senhas | models/user.py:27-32 |
| 3 | CRITICAL | AP-04 Exposição de dados sensíveis | models/user.py:21, routes/user_routes.py:33,85,129,209 |
| 4 | HIGH | AP-07 Regra de negócio na rota (Fat Controller) | routes/task_routes.py:85-154,156-223,273-299; routes/report_routes.py:12-101,103-155 |
| 5 | HIGH | AP-08 Acesso a dados fora da camada Model | routes/task_routes.py, routes/user_routes.py, routes/report_routes.py |
| 6 | HIGH | AP-10 Configuração insegura | app.py:11,15,34 |
| 7 | HIGH | AP-11 Autenticação/autorização ausente ou falsa | routes/user_routes.py:52,71-78,119-125,210 (todas as rotas) |
| 8 | MEDIUM | AP-13 Acoplamento a efeitos colaterais (código morto) | services/notification_service.py:4-48 |
| 9 | MEDIUM | AP-14 Query N+1 | routes/task_routes.py:42,51; routes/user_routes.py:22; routes/report_routes.py:56,163 |
| 10 | MEDIUM | AP-15 Lógica duplicada / implementações paralelas | routes/task_routes.py:30-39,71-80,284-287; routes/user_routes.py:171-180; ... |
| 11 | MEDIUM | AP-16 Validação de entrada ausente ou incompleta | routes/task_routes.py:113,167,182,261,264; routes/report_routes.py:196-202; ... |
| 12 | MEDIUM | AP-17 Tratamento de erros descentralizado | routes/task_routes.py:62,137,204,236; routes/user_routes.py:130,149; ... |
| 13 | MEDIUM | AP-18 APIs deprecated e dependências vulneráveis | requirements.txt:1-6; models/task.py:15-21; routes/*.py (Query.get, utcnow) |
| 14 | MEDIUM | AP-19 Agregação ineficiente | routes/task_routes.py:275-287; routes/report_routes.py:15-43 |
| 15 | MEDIUM | AP-20 Integridade referencial manual / órfãos | routes/user_routes.py:140-142; routes/report_routes.py:211-223 |
| 16 | LOW | AP-21 Magic numbers e strings | routes/task_routes.py:96-113; routes/user_routes.py:64,71; ... |
| 17 | LOW | AP-22 print como logging | routes/task_routes.py:149,153,219,234; routes/user_routes.py:83,89,147; ... |
| 18 | LOW | AP-23 Nomenclatura ruim | routes/report_routes.py:24-28; routes/*.py (loops `t`, `u`, `c`) |
| 19 | LOW | AP-24 Código morto e imports não usados | app.py:7; routes/task_routes.py:7; utils/helpers.py:2-108; ... |
| 20 | LOW | AP-25 Código verboso / não idiomático | models/task.py:38-60; models/user.py:34-38; ... |

## Findings

### #1 [CRITICAL] AP-02 — Credenciais e segredos hardcoded
File: app.py:13, services/notification_service.py:7-10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` fixo no código; `NotificationService` define `self.email_user = 'taskmanager@gmail.com'` e `self.email_password = 'senha123'` (SMTP `smtp.gmail.com:587`) como literais.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de assinatura (permitiria forjar tokens/sessões assim que houver autenticação real) e a senha da conta de e-mail.
Recommendation: Criar `config/settings.py` lendo do ambiente (com `.env` via python-dotenv): `SECRET_KEY` (ausente → segredo aleatório `secrets.token_hex(32)` gerado no boot + aviso no log de que tokens não sobrevivem a reinícios), `SMTP_HOST`, `SMTP_PORT` (padrão 587), `SMTP_USER`, `SMTP_PASSWORD` (sem padrão; sem credencial o envio é desabilitado e registrado no log). Remover todos os literais e criar `.env.example` com placeholders (→ T02).

### #2 [CRITICAL] AP-03 — Armazenamento inseguro de senhas
File: models/user.py:27-32
Description: `set_password` grava `hashlib.md5(pwd.encode()).hexdigest()` e `check_password` compara com MD5 — hash rápido, sem salt (a senha `1234` do seed vira `81dc9bdb52d04dc20036dbd8313ed055`, confirmado em runtime na resposta do login).
Impact: Hashes MD5 sem salt são revertidos instantaneamente por rainbow tables; combinado com o finding #3 qualquer cliente obtém as senhas em claro.
Recommendation: Usar `werkzeug.security.generate_password_hash` / `check_password_hash` (scrypt com salt). `check_password` aceita hashes MD5 legados (32 hex) apenas para migrar: se baterem, a senha é re-gravada com o novo hash no mesmo login. Credenciais de desenvolvimento do seed mantidas (mesmos e-mails/senhas, agora com hash forte) (→ T03).

### #3 [CRITICAL] AP-04 — Exposição de dados sensíveis (respostas e logs)
File: models/user.py:21, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` inclui `'password': self.password`; é usado em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login` (resposta do login confirmada em runtime com `"password": "81dc9bdb..."`). Nenhuma dessas rotas exige autenticação.
Impact: Exploração trivial pela API pública: `GET /users/1` devolve o hash da senha do admin, reversível (finding #2).
Recommendation: Remover `password` de `User.to_dict()` (todas as respostas). Mudança de contrato de segurança permitida, listada na Fase 3 (→ T04).

### #4 [HIGH] AP-07 — Regra de negócio na rota/controller (Fat Controller)
File: routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/task_routes.py:11-63, routes/task_routes.py:273-299, routes/user_routes.py:42-90, routes/user_routes.py:153-183, routes/report_routes.py:12-101, routes/report_routes.py:103-155
Description: Handlers de 50-90 linhas com validação, regras de atraso (`if t.due_date < datetime.utcnow(): if t.status != 'done' and t.status != 'cancelled'`), cálculos de `completion_rate`, contagem de prioridade alta (`t.priority <= 2`), parsing de datas e tags e montagem de relatórios. `report_routes.py` ainda hospeda o CRUD de categorias (outro domínio) em 157-223.
Impact: Regras não testáveis isoladamente, impossíveis de reutilizar e espalhadas por três arquivos.
Recommendation: Decomposição incremental: `services/` (task_service, user_service, report_service, category_service) com as regras; `controllers/` com leitura/validação de input e escolha de status; `routes/` só mapeia HTTP → controller. CRUD de categorias movido para `routes/category_routes.py` (mesmos paths). Formato das respostas idêntico (→ T06).

### #5 [HIGH] AP-08 — Acesso a dados fora da camada Model
File: routes/task_routes.py:14,42,51,67,117,122,147-148,247-266, routes/user_routes.py:12,29,35,67,81-82,109,140-146, routes/report_routes.py:15-56,105,109,159,163,183-184,205,218-219 (+ demais `db.session`/`Model.query` nos três arquivos de rotas)
Description: Todos os handlers chamam `Model.query...` e `db.session.add/commit/rollback/delete` diretamente.
Impact: Camada de persistência acoplada ao HTTP; trocar consulta/banco ou testar regras exige tocar nas rotas.
Recommendation: Concentrar consultas e escritas em métodos dos models (`models/*.py`: `get_by_id`, `search`, `count_by_status`, `save`, `delete` etc.), chamados apenas pelos services; nenhuma rota/controller importa `db` (→ T05/T06).

### #6 [HIGH] AP-10 — Configuração insegura
File: app.py:11, app.py:15, app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)`, `CORS(app)` sem restrição de origem, `SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'` fixo e ausência de app factory.
Impact: Debugger interativo do Werkzeug exposto na rede (execução remota de código); qualquer site pode chamar a API via browser.
Recommendation: App factory `create_app()` + `config/settings.py` com defaults seguros: `DEBUG` desligado (só liga com `DEBUG=1`), `HOST=127.0.0.1` (expor na rede exige `HOST=0.0.0.0` explícito), `PORT=5000`, `DATABASE_URL` padrão `sqlite:///tasks.db`, **CORS fechado por padrão** (`CORS_ORIGINS` vazio = nenhuma origem externa recebe `Access-Control-Allow-Origin`; lista separada por vírgula libera só essas; `*` só se definido explicitamente), `SECRET_KEY` aleatório com aviso quando ausente. `python app.py` e `from app import app, db` (seed) continuam funcionando (→ T02 + T17).

### #7 [HIGH] AP-11 — Autenticação/autorização ausente ou falsa
File: routes/user_routes.py:210, routes/user_routes.py:52, routes/user_routes.py:71-78, routes/user_routes.py:119-125, routes/user_routes.py:134-151, routes/report_routes.py:12, routes/report_routes.py:167-223 (nenhuma rota possui verificação de autenticação)
Description: Login devolve `'token': 'fake-jwt-token-' + str(user.id)` (previsível, nunca verificado); nenhuma rota exige credencial; `POST /users` aceita `role` do corpo (`role = data.get('role', 'user')` → qualquer um se cadastra como `admin`); `PUT /users/<id>` permite a qualquer cliente alterar `role` e `active`; `DELETE /users/<id>`, `GET /users` e `GET /reports/summary` estão abertos.
Impact: Escalada de privilégio trivial, exclusão de qualquer usuário e leitura de dados de todos os usuários por clientes anônimos.
Recommendation: Token assinado com expiração (`itsdangerous.URLSafeTimedSerializer` com `SECRET_KEY`, `TOKEN_MAX_AGE` padrão 3600 s) emitido no campo `token` do login; middleware `middlewares/auth.py` com `login_required`/`admin_required` que valida `Authorization: Bearer <token>` e relê o usuário (e o papel) do banco a cada requisição — sem token/token inválido/usuário inativo → 401; sem permissão → 403. Matriz de acesso: **Público** `GET /`, `GET /health`, `POST /login`, `POST /users` (cadastro público grava sempre `role='user'`, ignorando `role` do corpo); **Autenticado** `GET/POST /tasks`, `GET/PUT/DELETE /tasks/<id>`, `GET /tasks/search`, `GET /tasks/stats`, `GET /categories`; **Dono ou admin** `GET/PUT /users/<id>`, `GET /users/<id>/tasks`, `GET /reports/user/<id>`; **Admin** `GET /users`, `DELETE /users/<id>`, alterar `role`/`active` em `PUT /users/<id>` (não-admin → 403), definir `role` em `POST /users` com token admin, `POST /categories`, `PUT/DELETE /categories/<id>`, `GET /reports/summary`. Seed mantém `joao@email.com` como admin. README e `.env.example` documentam o uso do token (→ T16).

### #8 [MEDIUM] AP-13 — Acoplamento forte a efeitos colaterais
File: services/notification_service.py:4-48
Description: `NotificationService` instancia `smtplib.SMTP` diretamente com credenciais próprias, faz `print` de sucesso/erro e guarda notificações numa lista em memória (`self.notifications`). Severidade reduzida de HIGH para MEDIUM: a classe nunca é instanciada nem importada (código morto — confirmado via Grep).
Impact: Impossível testar sem SMTP real; credenciais acopladas ao código; lista em memória se perde a cada boot.
Recommendation: Tornar o serviço injetável: recebe configuração SMTP de `config/settings.py` (finding #1) e um `sender` substituível (padrão SMTP; desabilitado e registrado no log quando não há credenciais), usa `logging` em vez de `print`; o histórico passa a ser um `store` injetável (padrão: lista em memória, documentada como volátil); o serviço é instanciado no composition root (`app.extensions['notifications']`). Pending: ligar notificações a eventos (ex.: e-mail ao atribuir uma task) cria um efeito que o código original nunca executou, e persistir o histórico exige uma tabela nova — decisões de negócio; o serviço fica disponível, mas não conectado a rotas (→ T15).

### #9 [MEDIUM] AP-14 — Query N+1
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/user_routes.py:22, routes/report_routes.py:56, routes/report_routes.py:163
Description: `GET /tasks` faz `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` para cada task; `GET /users` acessa `len(u.tasks)` (lazy load) por usuário; `/reports/summary` faz `Task.query.filter_by(user_id=u.id).all()` por usuário; `GET /categories` faz um `count()` por categoria.
Impact: 1 + 2N queries em `GET /tasks`; cresce linearmente com o volume de dados.
Recommendation: `joinedload(Task.user, Task.category)` na listagem de tasks; contagens de tasks por usuário/categoria e produtividade por usuário com uma única query agregada (`func.count` + `GROUP BY` / outer join). Mesmas chaves e valores nas respostas (→ T07).

### #10 [MEDIUM] AP-15 — Lógica duplicada / implementações paralelas
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:284-287, routes/user_routes.py:171-180, routes/report_routes.py:34-36, routes/report_routes.py:132-135, routes/task_routes.py:17-28, routes/task_routes.py:110,177 (+ ocorrências: models/task.py:39, utils/helpers.py:75,110; routes/user_routes.py:61,106 × utils/helpers.py:21; routes/user_routes.py:71,120 × utils/helpers.py:111; routes/task_routes.py:89-144 × 166-213 × utils/helpers.py:57-108)
Description: A regra de "task atrasada" está copiada 6 vezes enquanto `Task.is_overdue()` (models/task.py:50) nunca é usada; `GET /tasks` reimplementa `Task.to_dict()` campo a campo; a lista `['pending', 'in_progress', 'done', 'cancelled']` aparece 5 vezes; a regex de e-mail é duplicada em vez de usar `validate_email`; a lista de roles é duplicada em vez de `VALID_ROLES`; validação de task feita separadamente em create, update e no helper `process_task_data` (não usado), com regras divergentes.
Impact: Correções precisam ser replicadas; regras já divergem entre create e update (ver #11).
Recommendation: Uma única fonte para cada regra: `Task.is_overdue()` e `Task.to_dict()` reutilizados; constantes `VALID_STATUSES`/`VALID_ROLES` e `validate_email`/`is_valid_color`/`calculate_percentage` de `utils/helpers.py` reaproveitados; um único validador de payload de task (create/update) em `controllers`/`validators` (→ T06 + T13).

### #11 [MEDIUM] AP-16 — Validação de entrada ausente ou incompleta
File: routes/task_routes.py:113, routes/task_routes.py:182, routes/task_routes.py:167-169, routes/task_routes.py:261, routes/task_routes.py:264, routes/task_routes.py:105-106, routes/report_routes.py:196-202, routes/report_routes.py:180 (+ routes/user_routes.py:102-103,124-125)
Description: `priority < 1` com valor string do JSON gera `TypeError` → 500 (confirmado em runtime: `POST /tasks {"priority": "2"}` → 500); `len(data['title'])` com `null` → 500 no update; `int(priority)`/`int(user_id)` na busca → `ValueError` 500 com `?priority=abc`; `PUT /categories/<id>` sem JSON → `'name' in None` → 500; `color` aceito sem validação (`is_valid_color` existe e não é usado); `PUT /users/<id>` aceita `name` vazio e `active` de qualquer tipo; `user_id`/`category_id` sem checagem de tipo.
Impact: Erros 500 provocados pelo cliente e dados inválidos persistidos.
Recommendation: Validador único por entidade: `priority` deve ser inteiro (bool rejeitado) entre 1 e 5 → senão 400; `title` deve ser string com 3-200 caracteres → 400; `?priority`/`?user_id` não numéricos → 400; `PUT /categories/<id>` sem JSON → 400 `Dados inválidos`; `color` deve ser `#RRGGBB` (`is_valid_color`) → 400; `name` vazio no update de usuário → 400; `active` deve ser booleano → 400; `user_id`/`category_id` devem ser inteiros → 400. Mensagens e status existentes preservados; 500 por input inválido viram 400 (→ T12).

### #12 [MEDIUM] AP-17 — Tratamento de erros descentralizado / exceções engolidas
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:151, routes/task_routes.py:204, routes/task_routes.py:221, routes/task_routes.py:236, routes/user_routes.py:87, routes/user_routes.py:130 (+3 ocorrências: routes/user_routes.py:149, routes/report_routes.py:186,207,221; utils/helpers.py:46,49,88)
Description: `try/except` repetido em todo handler, vários `except:` bare (o de `GET /tasks` engole qualquer erro e devolve `{'error': 'Erro interno'}`); nenhum `@app.errorhandler`; exceções não previstas (ex.: #11) caem na página HTML 500 padrão.
Impact: Erros mascarados sem log, comportamento inconsistente e código repetitivo.
Recommendation: `middlewares/error_handler.py` com handler central para exceções não tratadas: `rollback` da sessão, log com stack trace (`logging`) e resposta `{'error': 'Erro interno'}` 500; erros de validação/negócio sinalizados por exceções próprias (`ValidationError` 400, `NotFoundError` 404, `ConflictError` 409) traduzidas para `{'error': <mensagem>}` com o mesmo status de hoje. As mensagens específicas de 500 (`Erro ao criar task`...) passam à genérica (mesmo status). Respostas 404/405 de rotas inexistentes mantêm o formato padrão do Flask (→ T08).

### #13 [MEDIUM] AP-18 — APIs deprecated / legadas e dependências vulneráveis
File: requirements.txt:1-6, models/task.py:15-16,20-21,52, models/user.py:14, models/category.py:11, routes/task_routes.py:42,51,67,158 (+ ocorrências: `Query.get` em routes/task_routes.py:117,122,188,195,227, routes/user_routes.py:29,94,136,155, routes/report_routes.py:105,192,213; `datetime.utcnow` em routes/task_routes.py:31,72,215,285, routes/user_routes.py:172, routes/report_routes.py:35,42,45,71,133, utils/helpers.py:38, services/notification_service.py:35, seed.py:66,67,69,70,74)
Description: `datetime.utcnow()` (deprecated no Python 3.12+, `DeprecationWarning` em runtime), `Model.query.get()` (`LegacyAPIWarning` em runtime, ex.: routes/report_routes.py:105), `backref=` legado em models/task.py:20-21. `pip-audit` encontrou 22 vulnerabilidades em 5 pacotes: flask 3.0.0 (corrigido em 3.1.3), flask-cors 4.0.0 (6.0.0), marshmallow 3.20.1 (3.26.2), requests 2.31.0 (2.33.0), python-dotenv 1.0.0 (1.2.2).
Impact: Quebra em versões futuras do Python/SQLAlchemy; vulnerabilidades conhecidas em dependências.
Recommendation: Helper `utc_now()` (`datetime.now(timezone.utc)` sem tzinfo, preservando o formato `str()` atual das datas); `db.session.get(Model, id)`; `back_populates=` nos relacionamentos; `requirements.txt` com `flask==3.1.3`, `flask-cors==6.0.0`, `python-dotenv==1.2.2`; `marshmallow` e `requests` removidos (nunca importados — ver #19). Validar com `pip-audit` limpo e boot sem warnings (→ T11).

### #14 [MEDIUM] AP-19 — Agregação ineficiente
File: routes/task_routes.py:275-287, routes/report_routes.py:15-43
Description: `/tasks/stats` executa 5 `count()` separados e depois `Task.query.all()` para contar atrasadas em Python; `/reports/summary` executa 12 `count()` consecutivos (status e prioridade, um por valor) e também carrega todas as tasks para filtrar atrasadas.
Impact: Dezenas de queries por requisição e carga de toda a tabela em memória.
Recommendation: Uma query `GROUP BY status` e uma `GROUP BY priority` (`func.count`), e atrasadas filtradas no SQL (`due_date < agora AND status NOT IN ('done','cancelled')`); mesmas chaves e valores nas respostas (→ T07).

### #15 [MEDIUM] AP-20 — Integridade referencial manual / registros órfãos
File: routes/user_routes.py:140-142, routes/report_routes.py:211-223, models/task.py:13-14
Description: `DELETE /users/<id>` apaga as tasks em loop na rota (`for t in tasks: db.session.delete(t)`); `DELETE /categories/<id>` apaga a categoria e deixa as tasks com `category_id` apontando para um id inexistente (SQLite sem `PRAGMA foreign_keys = ON`, FKs sem `ondelete`).
Impact: Cascata implícita na camada errada; tasks órfãs com `category_id` inválido.
Recommendation: Tasks **pertencem** ao usuário → exclusão em cascata no model (`cascade='all, delete-orphan'` no relacionamento `User.tasks`) na mesma transação. Tasks não pertencem à categoria (são do usuário), então apagar a categoria **desvincula** as tasks (`category_id = NULL`, `ForeignKey(..., ondelete='SET NULL')` + update explícito na mesma transação) em vez de apagá-las; `PRAGMA foreign_keys = ON` habilitado nas conexões SQLite. Respostas inalteradas (→ T09).

### #16 [LOW] AP-21 — Magic numbers e strings
File: routes/task_routes.py:96, routes/task_routes.py:99, routes/task_routes.py:104, routes/task_routes.py:113, routes/user_routes.py:64, routes/report_routes.py:45, routes/report_routes.py:129, app.py:34 (+ ocorrências: routes/report_routes.py:180 `'#000000'`, routes/user_routes.py:71,120 roles, routes/task_routes.py:110,177 status)
Description: Literais de regra espalhados: tamanho de título `3`/`200`, prioridade padrão `3` e faixa `1..5`, senha mínima `4`, janela de `7` dias, "alta prioridade" `<= 2`, cor `'#000000'`, porta `5000`, listas de status/roles inline — embora `utils/helpers.py:110-116` já defina constantes.
Impact: Regras difíceis de localizar e alterar com segurança.
Recommendation: Usar as constantes de `utils/helpers.py` (`MIN/MAX_TITLE_LENGTH`, `DEFAULT_PRIORITY`, `MIN_PASSWORD_LENGTH`, `DEFAULT_COLOR`, `VALID_STATUSES`, `VALID_ROLES`) e adicionar `MIN_PRIORITY`, `MAX_PRIORITY`, `HIGH_PRIORITY_THRESHOLD`, `RECENT_ACTIVITY_DAYS`; porta via `PORT` (padrão 5000). Valores inalterados (→ T13).

### #17 [LOW] AP-22 — `print` como logging
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21 (+3 ocorrências: services/notification_service.py:24, utils/helpers.py:39,41)
Description: `print(f"Task criada: ...")`, `print(f"ERRO: {str(e)}")` etc. no código da aplicação (os `print` de `seed.py` são de script CLI e ficam).
Impact: Sem nível, timestamp ou destino configurável; erros misturados à saída padrão.
Recommendation: `logging` com logger por módulo configurado no `create_app` (`LOG_LEVEL`, padrão `INFO`); `log_action` do helper passa a usar logging (→ T14).

### #18 [LOW] AP-23 — Nomenclatura ruim
File: routes/report_routes.py:24-28, routes/task_routes.py:16, routes/user_routes.py:14, routes/report_routes.py:53-56, routes/report_routes.py:161, models/category.py:14, models/task.py:45
Description: `p1`...`p5` para contagens por prioridade, loops com `t`, `u`, `c`, variável `d` em `Category.to_dict`, parâmetro `p` em `validate_priority`.
Impact: Leitura e manutenção mais lentas.
Recommendation: Renomear para nomes descritivos (`counts_by_priority`, `task`, `user`, `category`, `priority`) durante a extração para services, mantendo os nomes externos do contrato (→ T05/T06).

### #19 [LOW] AP-24 — Código morto e imports não usados
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:3-7, utils/helpers.py:9-108, requirements.txt:4-5 (+ models/task.py:38-48, models/user.py:34-38)
Description: Imports nunca usados (`os, sys, json` em app.py; `json, os, sys, time` em task_routes; `hashlib, json` em user_routes; `format_date, calculate_percentage, json` em report_routes; `json` em models/task.py; `os, json, sys, math, hashlib` em helpers); helpers `process_task_data`, `sanitize_string`, `generate_id`, `parse_date`, `format_date`, `log_action`, `validate_email`, `is_valid_color` sem chamadas; `Task.validate_status/validate_priority/is_overdue` e `User.is_admin` sem uso; `marshmallow` e `requests` declarados e nunca importados.
Impact: Ruído e superfície de dependências vulneráveis desnecessária (#13).
Recommendation: Remover imports mortos e as dependências `marshmallow`/`requests`; **reaproveitar** os helpers/métodos úteis (`is_overdue`, `is_admin`, `validate_email`, `is_valid_color`, `calculate_percentage`, `log_action`, constantes) nas novas camadas e remover os que continuarem sem uso (`process_task_data`, `sanitize_string`, `generate_id`, `parse_date`, `format_date`, `validate_status`, `validate_priority`) (→ T05).

### #20 [LOW] AP-25 — Código verboso / não idiomático
File: models/task.py:38-60, models/user.py:34-38, utils/helpers.py:21-23, utils/helpers.py:53-55, routes/task_routes.py:141, routes/task_routes.py:210, utils/helpers.py:103
Description: `if cond: return True else: return False`, `if` aninhados em 3 níveis em `is_overdue`, `type(tags) == list`.
Impact: Código mais longo e propenso a erro.
Recommendation: Expressões booleanas diretas (`return self.role == 'admin'`, `is_overdue` em uma expressão) e `isinstance(tags, list)` (→ T06).

## Deprecated APIs
| API | Location | Modern replacement | Evidence |
|---|---|---|---|
| `datetime.utcnow()` | models/task.py:15,16,52; models/user.py:14; models/category.py:11; routes/task_routes.py:31,72,215,285; routes/user_routes.py:172; routes/report_routes.py:35,42,45,71,133; utils/helpers.py:38; services/notification_service.py:35; seed.py:66-74 | `datetime.now(timezone.utc)` | `DeprecationWarning` em runtime (`python -W default seed.py` e requisições via test client, Python 3.14.5) |
| `Model.query.get()` (`Query.get`) | routes/task_routes.py:42,51,67,117,122,158,188,195,227; routes/user_routes.py:29,94,136,155; routes/report_routes.py:105,192,213 | `db.session.get(Model, id)` | `LegacyAPIWarning` em runtime (ex.: routes/report_routes.py:105) |
| `db.relationship(..., backref=...)` | models/task.py:20-21 | `back_populates=` | Tabela do catálogo (legado SQLAlchemy 2.x; sem warning em runtime) |
| Dependências vulneráveis | requirements.txt:1,3,4,5,6 | flask 3.1.3, flask-cors 6.0.0, python-dotenv 1.2.2; marshmallow/requests removidos | `pip-audit -r requirements.txt`: 22 vulnerabilidades em 5 pacotes |

## Architecture Notes
- Current architecture: Camadas nominais / parcialmente organizada — existem `models/`, `routes/`, `services/` e `utils/`, mas as rotas contêm toda a regra de negócio e o acesso a dados, `services/notification_service.py` e a maior parte de `utils/helpers.py` não são usados, e `report_routes.py` mistura relatórios com CRUD de categorias.
- Refactoring strategy: incremental layering — reaproveitar `models/`, `routes/` (como camada View), `services/` e `utils/`; adicionar `config/`, `controllers/` e `middlewares/`; mover regras das rotas para services e o acesso a dados para os models; eliminar as cópias.
- Contract constraints: 22 endpoints com paths/métodos inalterados (`/`, `/health`, `/tasks`, `/tasks/<id>`, `/tasks/search`, `/tasks/stats`, `/users`, `/users/<id>`, `/users/<id>/tasks`, `/login`, `/reports/summary`, `/reports/user/<id>`, `/categories`, `/categories/<id>`); campos de entrada (`title`, `description`, `status`, `priority`, `user_id`, `category_id`, `due_date` em `YYYY-MM-DD`, `tags` lista ou string; `name`, `email`, `password`, `role`, `active`; `color`; query `q`, `status`, `priority`, `user_id`); chaves das respostas (ex.: `overdue`, `user_name`, `category_name`, `task_count`, `token`, `user`) e mensagens de erro; `python seed.py` + `python app.py` na porta 5000; credenciais do seed (`joao@email.com`/`1234` admin, `maria@email.com`/`abcd`, `pedro@email.com`/`pass`). Mudanças de segurança previstas: remoção de `password` das respostas, token assinado e rotas protegidas (401/403), papel definido pelo servidor, CORS fechado e bind local por padrão, 500 por input inválido → 400.

================================
Total: 20 findings
================================
