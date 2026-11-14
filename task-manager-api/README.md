# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

## Configuração

Toda a configuração vem de variáveis de ambiente (ou de um arquivo `.env`; veja `.env.example`): `SECRET_KEY`, `TOKEN_MAX_AGE` (validade do token, padrão 8 h), `DATABASE_URL`, `FLASK_DEBUG` (desligado por padrão), `HOST`, `PORT`, `CORS_ORIGINS`, `LOG_LEVEL` e `SMTP_*`.

## Autenticação

`POST /login` devolve em `token` um token assinado (HMAC com `SECRET_KEY`, com expiração) — não existe mais o `fake-jwt-token-<id>`. Envie-o como `Authorization: Bearer <token>`. O token carrega só o id; papel e status (`active`) são relidos do banco a cada requisição.

**Papel definido pelo servidor:** o cadastro público (`POST /users`) sempre cria `role = "user"`, mesmo que o corpo envie `"role": "admin"`. Só um admin autenticado pode escolher o papel no cadastro ou alterar `role`/`active` em `PUT /users/<id>`.

| Acesso | Rotas |
|---|---|
| Público | `GET /`, `GET /health`, `POST /users`, `POST /login` |
| Autenticado | `/tasks` (CRUD, `search`, `stats`), `GET /categories` |
| Autenticado (dono ou admin) | `GET /users/<id>`, `PUT /users/<id>`, `GET /users/<id>/tasks`, `GET /reports/user/<id>` |
| Admin | `GET /users`, `DELETE /users/<id>`, `GET /reports/summary`, `POST/PUT/DELETE /categories` |

Sem token ou com token inválido/expirado → `401`; sem permissão → `403`. Admin de desenvolvimento do seed: `joao@email.com` / `1234`.

```bash
TOKEN=$(curl -s -X POST localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -H "Authorization: Bearer $TOKEN" localhost:5000/users
```

## Estrutura

`app.py` (composition root, `create_app`) → `routes/` (blueprints) → `controllers/` (fluxo HTTP + validação) → `services/` (regras de negócio) → `models/` (entidades + consultas). Serialização em `views/`, erros centralizados em `middlewares/error_handler.py`, autenticação/autorização em `middlewares/auth.py` + `services/auth_service.py`, configuração em `config/`.

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.
