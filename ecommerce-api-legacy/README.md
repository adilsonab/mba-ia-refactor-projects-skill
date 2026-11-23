# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

Requer Node.js >= 20.17.

```bash
npm install
npm start
```

A aplicação sobe em `http://127.0.0.1:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.
As variáveis de ambiente suportadas estão em `.env.example` (porta, host, CORS, segredo do token, admin, log).

Defaults seguros: bind apenas em `127.0.0.1` (use `HOST=0.0.0.0` para expor na rede) e CORS fechado
(`CORS_ORIGINS` vazio = nenhuma origem externa; defina uma lista separada por vírgula ou `*` explicitamente).

## Estrutura

```
src/
├── app.js          # composition root (cria dependências, middlewares, rotas, listen)
├── config/         # variáveis de ambiente e constantes de negócio
├── database/       # conexão SQLite (Promise + transações), schema e seed
├── models/         # acesso a dados (queries parametrizadas)
├── services/       # regras: checkout, relatório, usuários, auth, gateway, cache
├── controllers/    # validação de entrada e resposta HTTP
├── routes/         # mapeamento METHOD /path -> controller (matriz de acesso)
├── middlewares/    # auth, CORS, error handler
└── utils/          # logger, erros HTTP, hash de senha, token, validadores
```

## Autenticação

| Endpoint | Acesso |
|---|---|
| `POST /api/login` | público — `{ "eml", "pwd" }` → `{ "token" }` |
| `POST /api/checkout` | público; se o e-mail já existe, exige `pwd` correto (ou `Authorization` do próprio usuário) |
| `GET /api/admin/financial-report` | admin |
| `DELETE /api/users/:id` | admin |

O token é assinado (HMAC-SHA256 com `SECRET_KEY`) e expira em `TOKEN_TTL_SECONDS` (padrão 3600).
Envie-o como `Authorization: Bearer <token>`. Sem token ou com token inválido → 401; sem papel admin → 403.
Usuários criados no checkout recebem sempre o papel `student`.

Credenciais do seed:
- Aluno: `leonan@fullcycle.com.br` / `123`
- Admin: `ADMIN_EMAIL` (padrão `admin@fullcycle.com.br`) / `ADMIN_PASSWORD` — defina `ADMIN_PASSWORD` antes de subir,
  ex.: `ADMIN_PASSWORD=uma-senha-forte npm start`. Sem ela o admin recebe uma senha aleatória não divulgada.

Exemplos de requisições estão em `api.http`.
