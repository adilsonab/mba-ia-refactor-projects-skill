# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`, organizada em camadas MVC (`config/`, `models/`, `services/`, `controllers/`, `routes/`, `middlewares/`, `utils/`).

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Variáveis de ambiente (ou arquivo `.env`, veja `.env.example`). Defaults seguros:

| Variável | Default | Observação |
|---|---|---|
| `SECRET_KEY` | aleatória por boot (com aviso) | defina em produção; assina os tokens |
| `TOKEN_MAX_AGE` | `3600` | validade do token em segundos |
| `FLASK_DEBUG` | `0` | `1` só em desenvolvimento |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | `HOST=0.0.0.0` para expor na rede |
| `CORS_ORIGINS` | vazio (CORS fechado) | lista separada por vírgula ou `*` |
| `DATABASE_URL` | `sqlite:///tasks.db` | |

## Autenticação

1. Faça login: `POST /login` com `{"email": "joao@email.com", "password": "1234"}` (admin do seed; também `maria@email.com`/`abcd` e `pedro@email.com`/`pass`).
2. Envie o `token` retornado em `Authorization: Bearer <token>`.

| Acesso | Endpoints |
|---|---|
| Público | `GET /`, `GET /health`, `POST /login`, `POST /users` (cadastro sempre com papel `user`) |
| Autenticado | `/tasks` (todas as operações), `/tasks/search`, `/tasks/stats`, `GET /categories` |
| Dono ou admin | `GET/PUT /users/<id>`, `GET /users/<id>/tasks`, `GET /reports/user/<id>` |
| Admin | `GET /users`, `DELETE /users/<id>`, alterar `role`/`active`, definir `role` no cadastro, `POST/PUT/DELETE /categories`, `GET /reports/summary` |

Sem token ou com token inválido/expirado → `401`; sem permissão → `403`.
