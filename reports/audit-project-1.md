================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python (versão não declarada; 3.14.5 no ambiente) + Flask (3.1.1)
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-23

## Summary
CRITICAL: 6 | HIGH: 7 | MEDIUM: 7 | LOW: 6

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | AP-01 SQL Injection | models.py:28, models.py:47-50, models.py:109-111, models.py:126-129, ... |
| 2 | CRITICAL | AP-02 Credenciais e segredos hardcoded | app.py:7, controllers.py:289 |
| 3 | CRITICAL | AP-03 Armazenamento inseguro de senhas | models.py:126-129, models.py:109-111, database.py:75-83 |
| 4 | CRITICAL | AP-04 Exposição de dados sensíveis | models.py:83, models.py:99, controllers.py:285-289, ... |
| 5 | CRITICAL | AP-05 Endpoint de execução arbitrária / destrutivo aberto | app.py:59-78, app.py:47-57 |
| 6 | CRITICAL | AP-06 God File | models.py:1-314, controllers.py:1-292, database.py:7-86 |
| 7 | HIGH | AP-07 Regra de negócio no controller/model | models.py:137-146, models.py:256-262, controllers.py:43-54, controllers.py:242-250 |
| 8 | HIGH | AP-08 Acesso a dados fora da camada Model | controllers.py:266-274, app.py:49-55, app.py:66-76 |
| 9 | HIGH | AP-09 Estado global mutável | database.py:4-11 |
| 10 | HIGH | AP-10 Configuração insegura | app.py:8, app.py:9, app.py:88, database.py:5 |
| 11 | HIGH | AP-11 Autenticação/autorização ausente | controllers.py:167-186, app.py:11-30, app.py:47, controllers.py:195 |
| 12 | HIGH | AP-12 Operação multi-escrita sem transação | models.py:133-169 |
| 13 | HIGH | AP-13 Acoplamento a efeitos colaterais | controllers.py:208-210, controllers.py:247-250 |
| 14 | MEDIUM | AP-14 Query N+1 | models.py:186-199, models.py:218-231, models.py:139-141, models.py:154-156 |
| 15 | MEDIUM | AP-15 Lógica duplicada | models.py:171-201 × 203-233, controllers.py:28-50 × 72-90, ... |
| 16 | MEDIUM | AP-16 Validação de entrada ausente/incompleta | controllers.py:43-50, controllers.py:87-90, controllers.py:169-171, ... |
| 17 | MEDIUM | AP-17 Tratamento de erros descentralizado | controllers.py:10-12, controllers.py:60-62, ... (16 handlers), app.py:77-78 |
| 18 | MEDIUM | AP-18 Dependências vulneráveis | requirements.txt:1-2 |
| 19 | MEDIUM | AP-19 Agregação ineficiente | models.py:239-254, controllers.py:268-274 |
| 20 | MEDIUM | AP-20 Integridade referencial manual / órfãos | models.py:65-70, database.py:45-53 |
| 21 | LOW | AP-21 Magic numbers e strings | models.py:257-262, controllers.py:52, controllers.py:242, ... |
| 22 | LOW | AP-22 print como logging | controllers.py:8, controllers.py:208-210, app.py:56, app.py:83-86, ... |
| 23 | LOW | AP-23 Nomenclatura ruim / sombreamento de built-ins | controllers.py:14, models.py:24, models.py:187-193, ... |
| 24 | LOW | AP-24 Código morto e imports não usados | database.py:2, models.py:2, controllers.py:268 |
| 25 | LOW | AP-25 Código verboso / não idiomático | controllers.py:200, controllers.py:118-121, models.py:294-297 |
| 26 | LOW | AP-26 Formato de resposta inconsistente | controllers.py:20 × 70, controllers.py:292 |

## Findings

### #1 [CRITICAL] AP-01 — SQL Injection
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:289-297 (+12 ocorrências: models.py:140, 149-150, 155, 157-161, 163-166, 174, 188, 192, 220, 224, 280)
Description: Praticamente todas as queries são montadas por concatenação de strings com dados do request, ex.: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` (login) e `query += " AND (nome LIKE '%" + termo + "%' ..."` (busca).
Impact: Confirmado em runtime: `POST /login` com `email = "admin@loja.com' --"` e qualquer senha retorna o usuário Admin (`Login OK`). Permite ler, alterar e apagar qualquer tabela via `/produtos/busca?q=`, `POST /produtos`, `POST /usuarios` etc.
Recommendation: Reescrever todo o acesso a dados na camada Model com queries parametrizadas (`?` + tupla), inclusive a busca dinâmica (cláusulas fixas + lista de parâmetros; `LIKE ?` com `%termo%` no parâmetro) (→ T01).

### #2 [CRITICAL] AP-02 — Credenciais e segredos hardcoded
File: app.py:7, controllers.py:289
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` fixo no código e o mesmo valor devolvido literalmente pelo `GET /health` (`"secret_key": "minha-chave-super-secreta-123"`).
Impact: Qualquer pessoa com acesso ao repositório ou à rota pública `/health` conhece a chave usada para assinar sessões/tokens, permitindo forjá-los.
Recommendation: Criar `config/settings.py` lendo `SECRET_KEY` do ambiente; se ausente, gerar segredo aleatório (`secrets.token_hex(32)`) e registrar aviso no log (sem imprimir o valor). Remover o segredo da resposta do health (ver #4). Criar `.env.example` com placeholders (→ T02).

### #3 [CRITICAL] AP-03 — Armazenamento inseguro de senhas
File: models.py:126-129, models.py:109-111, database.py:75-83, database.py:31
Description: `criar_usuario` grava `senha` em texto puro; o login compara no SQL (`... AND senha = '" + senha + "'`); o seed insere `("Admin", "admin@loja.com", "admin123", "admin")` etc. sem hash.
Impact: Vazamento do banco (ou da rota `/admin/query`, ver #5) expõe imediatamente todas as senhas — confirmado: `SELECT email,senha FROM usuarios` retorna `admin123`, `123456`, `senha123`.
Recommendation: Gravar senhas com `werkzeug.security.generate_password_hash` (já dependência do Flask) no cadastro e no seed; login busca por email (query parametrizada) e valida com `check_password_hash`. Senhas legadas em texto puro de bancos existentes são migradas para hash no boot (detecção por ausência de prefixo de hash). As credenciais de seed de desenvolvimento são mantidas (agora com hash) e documentadas no README como apenas para dev (→ T03).

### #4 [CRITICAL] AP-04 — Exposição de dados sensíveis (respostas e logs)
File: models.py:83, models.py:99, controllers.py:285-289, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:12, controllers.py:22 (+14 ocorrências de `str(e)` na resposta: controllers.py:62, 96, 109, 126, 134, 144, 165, 186, 220, 227, 235, 255, 262, 292; app.py:78)
Description: Serialização de usuário inclui `"senha": row["senha"]` (`GET /usuarios` e `GET /usuarios/<id>`, ambos públicos — confirmado: `/usuarios/1` devolve `"senha": "admin123"`); `/health` devolve `secret_key`, `debug`, `db_path`, `ambiente`; logs com o e-mail do usuário em cadastro/login; mensagens de exceção internas (`str(e)`) devolvidas ao cliente.
Impact: Roubo de credenciais de todos os usuários por qualquer cliente anônimo; vazamento de configuração interna; detalhes de implementação expostos em erros.
Recommendation: Serializador de usuário sem `senha` (campos: `id`, `nome`, `email`, `tipo`, `criado_em`); `/health` passa a retornar apenas `status`, `database`, `counts` e `versao` (removidos `secret_key`, `debug`, `db_path`, `ambiente`); logs de login/cadastro registram apenas o id do usuário, nunca e-mail/senha; erros 500 respondem mensagem genérica (`"Erro interno do servidor"`) e o detalhe vai só para o log (ver #17) (→ T04).

### #5 [CRITICAL] AP-05 — Endpoint de execução arbitrária / operação destrutiva aberta
File: app.py:59-78, app.py:47-57
Description: `POST /admin/query` executa `cursor.execute(dados.get("sql"))` com SQL livre vindo do cliente, sem autenticação; `POST /admin/reset-db` apaga todas as tabelas sem nenhuma verificação.
Impact: Qualquer cliente anônimo lê/altera/apaga todo o banco (confirmado: leitura de todas as senhas) ou zera a loja com uma requisição.
Recommendation: Remover `POST /admin/query` (passa a responder 404) — mudança de contrato de segurança. Manter `POST /admin/reset-db` com a mesma resposta, mas exigindo token de usuário com papel `admin` (401 sem token, 403 sem papel), com a exclusão movida para a camada Model em transação (→ T16).

### #6 [CRITICAL] AP-06 — God Class / God File
File: models.py:1-314, controllers.py:1-292, app.py:1-88, database.py:7-86
Description: `models.py` (314 linhas) mistura 4 domínios (produtos, usuários, pedidos, relatórios), SQL, serialização e regras de negócio (cálculo de total, checagem de estoque, faixas de desconto); `controllers.py` concentra validação, regras de status, notificações e SQL de health para todos os domínios; `app.py` acumula configuração, rotas, handlers administrativos com SQL e bootstrap; `get_db()` cria a conexão, o schema e o seed.
Impact: Alto acoplamento, impossível testar regras isoladamente; qualquer mudança toca arquivos que servem a todos os domínios.
Recommendation: Decompor em pacote MVC: `config/` (settings + constants), `database.py` (conexão/schema; seed em `models/seed.py`), `models/` (um repositório por entidade), `services/` (regras de negócio), `controllers/` (fluxo HTTP + validação), `routes/` (Blueprints só com mapeamento), `middlewares/` (erros, auth) e `app.py` como composition root com `create_app()` mantendo `python app.py` (→ T05 + T17).

### #7 [HIGH] AP-07 — Regra de negócio na rota/controller (Fat Controller)
File: models.py:137-146, models.py:256-262, controllers.py:43-54, controllers.py:242-250
Description: Cálculo do total do pedido e verificação de estoque dentro do acesso a dados (`total = total + (produto["preco"] * item["quantidade"])`); faixas de desconto do relatório (`if faturamento > 10000: desconto = faturamento * 0.1 ...`) no model; regras de produto (categorias válidas, limites de nome) e de status de pedido no controller.
Impact: Regras de domínio espalhadas entre camadas, sem ponto único de teste ou alteração.
Recommendation: Mover cálculo do pedido/estoque para `services/pedido_service.py`, desconto do relatório para `services/relatorio_service.py`, regras de produto para `services/produto_service.py`; models ficam só com SQL, controllers só com leitura de input/validação e escolha de status HTTP, preservando os mesmos valores e respostas (→ T06).

### #8 [HIGH] AP-08 — Acesso a dados fora da camada Model
File: controllers.py:266-274, app.py:49-55, app.py:66-76
Description: `health_check` chama `get_db()` e executa `SELECT COUNT(*)` direto no controller; `reset_database` e `executar_query` executam SQL dentro de `app.py`.
Impact: Contorna a camada Model; SQL espalhado e não reutilizável.
Recommendation: Contagens do health e o reset passam para funções da camada Model (`models/sistema_model.py`) chamadas por controllers; `executar_query` é removido (#5) (→ T05/T06).

### #9 [HIGH] AP-09 — Estado global mutável
File: database.py:4-11
Description: `db_connection = None` global com `global db_connection` e `sqlite3.connect(db_path, check_same_thread=False)` — uma única conexão compartilhada entre todas as threads/requisições, nunca fechada (runtime: `ResourceWarning: unclosed database`).
Impact: Condições de corrida em escritas concorrentes, transações de uma requisição vazando para outra, conexão nunca liberada.
Recommendation: Uma conexão por requisição em `flask.g`, aberta sob demanda e fechada em `app.teardown_appcontext`; schema/seed executados uma vez em `create_app()`; caminho do banco vindo da config (→ T10).

### #10 [HIGH] AP-10 — Configuração insegura
File: app.py:8, app.py:9, app.py:88, database.py:5, controllers.py:286-288
Description: `app.config["DEBUG"] = True`, `CORS(app)` sem restrição (qualquer origem), `app.run(host="0.0.0.0", port=5000, debug=True)` (debugger Werkzeug exposto na rede), `db_path = "loja.db"` fixo, `"ambiente": "producao"`/`"debug": True` fixos; sem app factory.
Impact: Debugger interativo permite execução remota de código se exposto; qualquer site pode chamar a API com o navegador da vítima; configuração não ajustável por ambiente.
Recommendation: `config.py` lendo do ambiente com defaults seguros: `DEBUG` desligado (só liga com `DEBUG=true`), `HOST=127.0.0.1` (expor na rede exige `HOST=0.0.0.0` explícito), `PORT=5000`, `DB_PATH=loja.db`, `CORS_ORIGINS` vazio por padrão = nenhuma origem externa recebe `Access-Control-Allow-Origin` (lista separada por vírgula libera só essas origens; `*` só se o operador definir explicitamente), `SECRET_KEY` aleatório com aviso quando ausente; `create_app()` como app factory; `python app.py` continua funcionando (→ T02 + T17).

### #11 [HIGH] AP-11 — Autenticação/autorização ausente ou falsa
File: controllers.py:167-186, app.py:11-30, app.py:47, controllers.py:195, controllers.py:222-225
Description: `login` apenas devolve os dados do usuário, sem emitir credencial; nenhuma rota tem verificação — `GET /usuarios`, `DELETE /produtos/<id>`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db` são públicas; `criar_pedido` confia no `usuario_id` do corpo e `GET /pedidos/usuario/<id>` mostra pedidos de qualquer usuário.
Impact: Qualquer cliente anônimo administra a loja, vê pedidos e dados de todos os usuários e cria pedidos em nome de terceiros.
Recommendation: Login emite token assinado com expiração (`itsdangerous.URLSafeTimedSerializer` com `SECRET_KEY`, validade `TOKEN_EXPIRES_SECONDS`, padrão 3600), retornado em campo novo aditivo `"token"` na resposta (demais chaves inalteradas). Middleware `login_required`/`admin_required` lê `Authorization: Bearer <token>`, valida assinatura/expiração e recarrega o usuário do banco (401 se ausente/inválido, 403 sem papel). Matriz de acesso:
- Público: `GET /`, `GET /health`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /usuarios`, `POST /login`.
- Autenticado (dono ou admin): `GET /usuarios/<id>`, `GET /pedidos/usuario/<usuario_id>`, `POST /pedidos` (`usuario_id` do corpo deve ser o do token, salvo admin → senão 403; se omitido, usa o do token).
- Admin: `POST/PUT/DELETE /produtos...`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db`.
Papel sempre definido pelo servidor: cadastro público grava `tipo = 'cliente'` ignorando qualquer `tipo` no corpo. Seed garante o admin `admin@loja.com`. README e `.env.example` atualizados (→ T16).

### #12 [HIGH] AP-12 — Operação multi-escrita sem transação
File: models.py:133-169
Description: `criar_pedido` verifica estoque em um loop, depois insere `pedidos`, `itens_pedido` e faz `UPDATE produtos SET estoque = estoque - ...` em queries separadas, com um único `commit` no final e sem `rollback`; o estoque é verificado e debitado em momentos diferentes.
Impact: Falha no meio deixa pedido sem itens ou estoque debitado parcialmente (pendente na conexão compartilhada); duas compras simultâneas podem vender o mesmo estoque (estoque negativo).
Recommendation: Executar a criação do pedido em uma transação explícita (`BEGIN IMMEDIATE` / `commit` / `rollback` em qualquer erro) com débito condicional `UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?` verificando `rowcount`; falta de estoque mantém a resposta atual (400 `"Estoque insuficiente para <nome>"`) (→ T09).

### #13 [HIGH] AP-13 — Acoplamento forte a efeitos colaterais
File: controllers.py:208-210, controllers.py:247-250
Description: Notificações simuladas inline no controller: `print("ENVIANDO EMAIL: Pedido ...")`, `print("ENVIANDO SMS ...")`, `print("ENVIANDO PUSH ...")`, `print("NOTIFICAÇÃO: Pedido ... aprovado")`.
Impact: Impossível trocar o canal real (e-mail/SMS) ou testar sem efeitos colaterais; controller conhece detalhes de infraestrutura.
Recommendation: Criar `services/notification_service.py` (interface `notificar_pedido_criado`, `notificar_status_pedido`) com implementação padrão baseada em `logging`, injetada no `PedidoService` pelo composition root (→ T15).

### #14 [MEDIUM] AP-14 — Query N+1
File: models.py:186-199, models.py:218-231, models.py:139-141, models.py:154-156
Description: Para cada pedido, uma query de itens (`cursor2`) e, para cada item, uma query do nome do produto (`cursor3`); em `criar_pedido`, o produto é buscado duas vezes por item (verificação e de novo para o preço).
Impact: `GET /pedidos` faz 1 + P + I queries; degrada linearmente com o volume.
Recommendation: Listagem de pedidos em uma única query (`pedidos LEFT JOIN itens_pedido LEFT JOIN produtos`, agrupada em memória, mantendo `"Desconhecido"` quando o produto não existe); `criar_pedido` busca todos os produtos do pedido em uma única query e reutiliza o preço (→ T07).

### #15 [MEDIUM] AP-15 — Lógica duplicada / implementações paralelas
File: models.py:171-201 × models.py:203-233, models.py:12-21 × 31-40 × 304-313, models.py:79-86 × 95-102, controllers.py:28-50 × controllers.py:72-90
Description: `get_pedidos_usuario` e `get_todos_pedidos` são cópias com diferença só no `WHERE`; o dict de produto é montado 3 vezes e o de usuário 2 vezes; validação de produto copiada entre criar e atualizar (com divergências, ver #16).
Impact: Correções precisam ser replicadas; versões já divergiram.
Recommendation: Uma função de listagem de pedidos com filtro opcional de usuário; serialização única por model (lista de colunas + `_to_dict` em `produto_model`/`usuario_model`, a de usuário sem `senha`); um validador de produto único usado em create e update (→ T06 + T13).

### #16 [MEDIUM] AP-16 — Validação de entrada ausente ou incompleta
File: controllers.py:43-50, controllers.py:87-90, controllers.py:169-171, controllers.py:239-245, controllers.py:195-203, controllers.py:118-121, controllers.py:153-160, controllers.py:249-250
Description: `preco`/`estoque` comparados sem checar tipo (`"preco": "10"` → 500 confirmado); `atualizar_produto` não valida tamanho do nome nem categoria; `login` e `atualizar_status_pedido` chamam `dados.get` com `dados` possivelmente `None` (500); itens do pedido sem `produto_id`/`quantidade` → 500 (confirmado) e `quantidade` ≤ 0 não é rejeitada (quantidade negativa aumenta o estoque); `PUT /pedidos/999/status` em pedido inexistente → 200 (confirmado); `float(preco_min)` inválido → 500; cadastro aceita e-mail duplicado e sem formato; cancelamento apenas imprime "Devolver estoque" sem devolver e qualquer transição de status é aceita.
Impact: Erros 500 para entrada inválida, corrupção de estoque, atualizações silenciosas de recursos inexistentes.
Recommendation: Validador comum: `preco` numérico ≥ 0 e `estoque` inteiro ≥ 0 (senão 400), mesmas regras de nome/categoria em create e update; corpo JSON ausente → 400 `"Dados inválidos"` em todos os POST/PUT; cada item exige `produto_id` e `quantidade` inteiros > 0 (senão 400); pedido inexistente em `PUT /pedidos/<id>/status` → 404; `preco_min`/`preco_max` não numéricos → 400; e-mail sem `@` ou já cadastrado → 400. Pending: devolução de estoque no cancelamento e a máquina de transições de status permitidas são decisões de negócio — o comportamento atual (qualquer status válido aceito, sem devolver estoque) é preservado (→ T12).

### #17 [MEDIUM] AP-17 — Tratamento de erros descentralizado / exceções engolidas
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62, controllers.py:95-96, controllers.py:108-109, controllers.py:125-126, controllers.py:218-220, app.py:77-78 (+9 ocorrências: controllers.py:133-134, 143-144, 164-165, 185-186, 226-227, 234-235, 254-255, 261-262, 291-292)
Description: Todo handler repete `except Exception as e: return jsonify({"erro": str(e)}), 500`; não há `@app.errorhandler`.
Impact: Duplicação massiva, vazamento de detalhes internos, 404/405 do Flask respondidos em HTML.
Recommendation: `middlewares/error_handler.py` com handlers centralizados: `ValidationError` → 400, `NotFoundError` → 404, 401/403 de auth, 404/405 em JSON (`{"erro": ..., "sucesso": false}`), exceção genérica → 500 `{"erro": "Erro interno do servidor", "sucesso": false}` com stack trace só no log; remover os `try/except` dos handlers (→ T08).

### #18 [MEDIUM] AP-18 — APIs deprecated / legadas e dependências vulneráveis
File: requirements.txt:1, requirements.txt:2
Description: `pip-audit -r requirements.txt` (venv temporário): `flask==3.1.1` vulnerável (PYSEC-2026-2151, corrigido em 3.1.3); `flask-cors==5.0.1` vulnerável (PYSEC-2026-1383, PYSEC-2026-1384, PYSEC-2026-1385, corrigido em 6.0.0). Nenhuma API deprecated detectada (Grep na tabela do catálogo + import e requisições com `python -W default -X dev`: zero `DeprecationWarning`).
Impact: Vulnerabilidades conhecidas e públicas nas dependências de runtime.
Recommendation: Atualizar para `flask==3.1.3` e `flask-cors==6.0.0` e revalidar com `pip-audit` sem vulnerabilidades conhecidas (→ T11).

### #19 [MEDIUM] AP-19 — Agregação ineficiente
File: models.py:239-254, controllers.py:268-274
Description: `relatorio_vendas` faz 5 queries separadas (`COUNT(*)`, `SUM(total)`, três `COUNT(*) WHERE status = ...`); `health_check` faz `SELECT 1` + 3 `COUNT(*)`.
Impact: Várias varreduras da tabela por requisição; resultados podem ficar inconsistentes entre si.
Recommendation: Relatório em uma única query com `COUNT(*)`, `COALESCE(SUM(total),0)` e `SUM(CASE WHEN status = ? THEN 1 ELSE 0 END)`; health em uma query com subselects de contagem, sem o `SELECT 1` redundante (→ T07).

### #20 [MEDIUM] AP-20 — Integridade referencial manual / registros órfãos
File: models.py:65-70, database.py:45-53
Description: `DELETE FROM produtos WHERE id = ...` apaga o produto mesmo com `itens_pedido` apontando para ele (sem FK/`ON DELETE`); os pedidos passam a mostrar `"produto_nome": "Desconhecido"`. A coluna `ativo` existe mas nunca é usada.
Impact: Histórico de pedidos perde a referência ao produto vendido.
Recommendation: Soft delete usando a coluna existente `ativo`: `DELETE /produtos/<id>` faz `UPDATE produtos SET ativo = 0` com a mesma resposta (200 `"Produto deletado"`); listagem, busca, `GET /produtos/<id>`, update e criação de pedido consideram apenas `ativo = 1` (produto inativo → 404/"não encontrado"); itens de pedido continuam exibindo o nome do produto (→ T09).

### #21 [LOW] AP-21 — Magic numbers e strings
File: models.py:257-262, controllers.py:52, controllers.py:242, controllers.py:47-50, app.py:88, app.py:36, controllers.py:285
Description: Faixas e percentuais de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`), lista de categorias e de status inline, limites `2`/`200` do nome, porta `5000` e versão `"1.0.0"` repetida.
Impact: Regras implícitas e duplicadas, difíceis de ajustar.
Recommendation: `config/constants.py` com `CATEGORIAS_VALIDAS`, `STATUS_PEDIDO`, `FAIXAS_DESCONTO`, `NOME_PRODUTO_MIN/NOME_PRODUTO_MAX`, `API_VERSION`; porta via config (→ T13).

### #22 [LOW] AP-22 — `print` como logging
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:208-210, app.py:56, app.py:83-86 (+6 ocorrências: controllers.py:161, 179, 182, 219, 248, 250)
Description: `print("ERRO: " + str(e))`, `print("ENVIANDO EMAIL: ...")`, `print("!!! BANCO DE DADOS RESETADO !!!")` e banner de inicialização com `print`.
Impact: Sem níveis, sem destino configurável, mistura dados sensíveis no stdout.
Recommendation: Módulo `logging` com logger por módulo e nível configurável (`LOG_LEVEL`, padrão `INFO`) (→ T14).

### #23 [LOW] AP-23 — Nomenclatura ruim / sombreamento de built-ins
File: controllers.py:14, controllers.py:56, controllers.py:64, controllers.py:98, controllers.py:136, models.py:24, models.py:187-193, models.py:219-225 (+3 ocorrências: models.py:54, 65, 89)
Description: Parâmetros/variáveis chamados `id` (sombreiam o built-in), cursores `cursor2`/`cursor3`, exceções `e`.
Impact: Legibilidade reduzida e risco de bugs por sombreamento.
Recommendation: Renomear para `produto_id`, `usuario_id`, `itens_cursor` etc. nas camadas internas, mantendo paths, campos de entrada e chaves de resposta (→ T05/T06).

### #24 [LOW] AP-24 — Código morto e imports não usados
File: database.py:2, models.py:2, controllers.py:268
Description: `import os` em `database.py` e `import sqlite3` em `models.py` nunca usados; `cursor.execute("SELECT 1")` no health tem resultado descartado.
Impact: Ruído e falsa impressão de dependência.
Recommendation: Remover os imports não usados e a query redundante (→ T05).

### #25 [LOW] AP-25 — Código verboso / não idiomático
File: controllers.py:200, controllers.py:118-121, models.py:294-297, models.py:244-245
Description: `if not itens or len(itens) == 0` (redundante); `if preco_min:` / `if preco_max:` tratam `0` como ausente (filtro `preco_min=0` ignorado); `if faturamento is None: faturamento = 0` em vez de `COALESCE`.
Impact: Ruído e bug sutil no filtro com valor zero.
Recommendation: Simplificar para `if not itens`, testar `is not None` nos filtros de preço e usar `COALESCE` na query (→ T06).

### #26 [LOW] AP-26 — Formato de resposta inconsistente
File: controllers.py:20, controllers.py:70, controllers.py:142, controllers.py:292
Description: Erros às vezes com `"sucesso": False` (`controllers.py:20`), às vezes sem (`controllers.py:70`, `controllers.py:142`); o health em erro usa `{"status": "erro", "detalhes": ...}`.
Impact: Clientes precisam tratar formatos diferentes para o mesmo tipo de erro.
Recommendation: Corpo de erro padronizado `{"erro": <mensagem>, "sucesso": false}` em todas as rotas (chave `erro` e status HTTP preservados; `sucesso` aditivo); health em erro responde 500 `{"status": "erro", "database": "disconnected"}` sem detalhes internos. Respostas de sucesso inalteradas (→ T08).

## Deprecated APIs
None detected. Grep pelos sinais da tabela do catálogo (Python/Flask/Werkzeug) sem ocorrências; execução com `python -W default -X dev` (import do app + requisições GET em `/`, `/produtos`, `/health`, `/usuarios`, `/relatorios/vendas`, `/pedidos`, `/produtos/busca`) sem `DeprecationWarning` — apenas `ResourceWarning: unclosed database` (coberto em #9). Dependências vulneráveis: ver #18.

## Architecture Notes
- Current architecture: Camadas nominais / parcialmente organizada — existem `controllers.py`, `models.py` e `database.py`, mas `models.py` contém regras de negócio (total, estoque, desconto), `controllers.py` e `app.py` executam SQL, e `database.py` faz conexão global + schema + seed.
- Refactoring strategy: incremental layering — reaproveitar a separação existente (controllers/models/database) evoluindo para pacotes `models/`, `services/`, `controllers/`, `routes/`, `middlewares/` com `create_app()`, preservando `python app.py`.
- Contract constraints: rotas e métodos atuais (exceto `POST /admin/query`, removida), campos de entrada `nome`, `descricao`, `preco`, `estoque`, `categoria`, `email`, `senha`, `usuario_id`, `itens[].produto_id`, `itens[].quantidade`, `status`, query params `q`, `categoria`, `preco_min`, `preco_max`; envelope de resposta `{"dados", "sucesso", "mensagem", "total"}` e chave de erro `erro`; status HTTP 200/201/400/401/404; porta 5000; banco `loja.db` com seed automático no primeiro boot. Mudanças de segurança permitidas: exigência de token conforme matriz do #11, remoção de `senha` e de dados internos do `/health`, CORS fechado por padrão, bind em `127.0.0.1`.

================================
Total: 26 findings
================================
