# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

## Configuração

Toda a configuração vem de variáveis de ambiente (ou de um arquivo `.env`; veja `.env.example`): `SECRET_KEY`, `DATABASE_URL`, `FLASK_DEBUG` (desligado por padrão), `HOST`, `PORT`, `CORS_ORIGINS`, `LOG_LEVEL` e `SMTP_*`.

## Estrutura

`app.py` (composition root, `create_app`) → `routes/` (blueprints) → `controllers/` (fluxo HTTP + validação) → `services/` (regras de negócio) → `models/` (entidades + consultas). Serialização em `views/`, erros centralizados em `middlewares/error_handler.py`, configuração em `config/`.

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.
