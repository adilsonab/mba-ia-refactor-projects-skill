# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

Variáveis de ambiente opcionais (ver `.env.example`): `PORT` (padrão `3000`), `DATABASE_PATH` (padrão `:memory:`), `PAYMENT_GATEWAY_KEY` (sem valor padrão; o gateway roda em modo simulado) e `ADMIN_TOKEN`.

## Autenticação

| Acesso | Rotas |
|---|---|
| Público | `POST /api/checkout` |
| Admin (`Authorization: Bearer <ADMIN_TOKEN>`) | `GET /api/admin/financial-report`, `DELETE /api/users/:id` |

O projeto não tem login nem papéis de usuário, então a credencial de administrador é definida no servidor pela variável `ADMIN_TOKEN` (comparação em tempo constante). Sem a variável, as rotas administrativas ficam desabilitadas e respondem `401`.

```bash
ADMIN_TOKEN=$(node -e "console.log(require('crypto').randomBytes(24).toString('hex'))") npm start
curl -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:3000/api/admin/financial-report
```

## Estrutura

`src/app.js` (composition root) → `routes/` → `controllers/` → `services/` → `models/` → `database/`, com `config/`, `middlewares/` (tratamento central de erros e `auth.js` para as rotas administrativas) e `utils/` (logger, hash de senha).
