# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas armazenadas com hash).

## Configuração (variáveis de ambiente)

Veja `.env.example`. Principais: `SECRET_KEY` (sem ela, uma chave aleatória é gerada a cada boot), `FLASK_DEBUG=1` para modo debug (desligado por padrão), `PORT`, `DATABASE_PATH`, `CORS_ORIGINS` e `ADMIN_TOKEN` (habilita `POST /admin/reset-db` com o header `X-Admin-Token`).

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
middlewares/        # tratamento centralizado de erros
```
