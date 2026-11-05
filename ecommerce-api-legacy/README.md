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

Variáveis de ambiente opcionais (ver `.env.example`): `PORT` (padrão `3000`), `DATABASE_PATH` (padrão `:memory:`) e `PAYMENT_GATEWAY_KEY` (sem valor padrão; o gateway roda em modo simulado).

## Estrutura

`src/app.js` (composition root) → `routes/` → `controllers/` → `services/` → `models/` → `database/`, com `config/`, `middlewares/` (tratamento central de erros) e `utils/` (logger, hash de senha).
