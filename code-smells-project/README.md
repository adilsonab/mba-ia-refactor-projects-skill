# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000` (só local; para expor na rede use `HOST=0.0.0.0`). O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas armazenadas com hash).

## Configuração (variáveis de ambiente)

Veja `.env.example`. Principais: `SECRET_KEY` (sem ela, uma chave aleatória é gerada a cada boot), `FLASK_DEBUG=1` para modo debug (desligado por padrão), `HOST` (padrão `127.0.0.1`), `PORT`, `DATABASE_PATH`, `CORS_ORIGINS` e `TOKEN_MAX_AGE` (validade do token de acesso, padrão 8 h).

**CORS fechado por padrão:** sem `CORS_ORIGINS`, nenhum site de outra origem consegue chamar a API pelo navegador (a resposta não traz `Access-Control-Allow-Origin`). Para liberar um front-end, defina a lista de origens: `CORS_ORIGINS=https://loja.exemplo.com,https://admin.exemplo.com`. Clientes fora do navegador (curl, apps, outros servidores) não são afetados.

**Exclusão de produto:** `DELETE /produtos/<id>` faz *soft delete* (`ativo = 0`). O produto some do catálogo e não pode mais ser pedido, mas o histórico de pedidos mantém o nome dele.

## Autenticação

`POST /login` devolve um token assinado (HMAC com `SECRET_KEY`, com expiração) em `dados.token`. Envie-o como `Authorization: Bearer <token>`. O token carrega só o id do usuário; o papel (`tipo`) é sempre relido do banco. O cadastro público (`POST /usuarios`) sempre cria `tipo = "cliente"`, mesmo que o corpo envie outro valor.

| Acesso | Rotas |
|---|---|
| Público | `GET /`, `GET /health`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /usuarios`, `POST /login` |
| Autenticado (dono ou admin) | `GET /usuarios/<id>`, `POST /pedidos` (o `usuario_id` precisa ser o do token), `GET /pedidos/usuario/<id>` |
| Admin | `POST/PUT/DELETE /produtos`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db` |

Sem token ou com token inválido/expirado → `401`; sem permissão → `403`. Admin de desenvolvimento do seed: `admin@loja.com` / `admin123`.

```bash
TOKEN=$(curl -s -X POST localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"admin@loja.com","senha":"admin123"}' | python -c "import sys,json;print(json.load(sys.stdin)['dados']['token'])")
curl -H "Authorization: Bearer $TOKEN" localhost:5000/relatorios/vendas
```

## Estrutura

```
app.py              # composition root (create_app)
config/             # settings (ambiente) e constantes de negócio
database.py         # conexão por requisição, schema, seed e migração de senhas
errors.py           # exceções de domínio
models/             # acesso a dados (SQL parametrizado)
services/           # regras de negócio (pedidos, relatório, usuários, notificações)
controllers/        # fluxo HTTP e validação de entrada
views/              # rotas e serializers
middlewares/        # tratamento centralizado de erros e autenticação/autorização (auth.py)
```
