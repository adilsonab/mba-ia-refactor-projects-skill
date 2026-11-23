# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

Configuração por variáveis de ambiente (veja `.env.example`). Os defaults são seguros: debug desligado, bind em `127.0.0.1`, CORS fechado (nenhuma origem externa) e `SECRET_KEY` aleatória quando não definida. Para expor na rede use `HOST=0.0.0.0`; para liberar origens de browser use `CORS_ORIGINS=https://app.exemplo.com`.

## Estrutura

```
app.py            composition root (create_app)
config/           settings (ambiente) e constantes de negócio
database.py       conexão por requisição e transações
models/           acesso a dados (SQL parametrizado), hash de senha, seed
services/         regras de negócio (pedidos, relatório, auth, notificações)
controllers/      fluxo HTTP e validação de entrada
routes/           mapeamento METHOD /path -> controller (matriz de acesso)
middlewares/      autenticação/autorização e error handler central
```

## Autenticação

`POST /login` com `{"email": "...", "senha": "..."}` retorna, além de `dados`, um campo `token` (assinado, expira em `TOKEN_EXPIRES_SECONDS`, padrão 3600s). Envie-o nas rotas protegidas:

```bash
curl -H "Authorization: Bearer <token>" http://127.0.0.1:5000/usuarios
```

Sem token ou com token inválido → `401`; sem permissão → `403`.

| Acesso | Endpoints |
|---|---|
| Público | `GET /`, `GET /health`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /usuarios`, `POST /login` |
| Autenticado (dono ou admin) | `GET /usuarios/<id>`, `GET /pedidos/usuario/<id>`, `POST /pedidos` (`usuario_id` deve ser o do token; se omitido, usa o do token) |
| Admin | `POST/PUT/DELETE /produtos...`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db` |

O cadastro público sempre cria usuários com tipo `cliente`. `POST /admin/query` foi removido.

### Credenciais de desenvolvimento (seed)

Somente para desenvolvimento local, gravadas com hash:

| Email | Senha | Tipo |
|---|---|---|
| admin@loja.com | admin123 | admin |
| joao@email.com | 123456 | cliente |
| maria@email.com | senha123 | cliente |
