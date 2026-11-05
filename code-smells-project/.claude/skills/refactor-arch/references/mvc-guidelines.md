# Guidelines de Arquitetura MVC (Fase 3)

## 1. Camadas e responsabilidades

Para APIs backend, "View" é a camada de apresentação HTTP: **definição de rotas + serialização da resposta**. A arquitetura alvo é MVC com camadas de apoio:

| Camada | Pasta | Responsabilidade | NÃO pode |
|---|---|---|---|
| **Config** | `config/` | Ler variáveis de ambiente, defaults seguros de desenvolvimento, constantes de negócio nomeadas | Conter segredos reais de produção |
| **Model** | `models/` | Entidades, acesso a dados (queries parametrizadas/ORM), regras intrínsecas da entidade (ex.: `task.is_overdue()`), transações | Importar framework web (`flask.request`, `req`/`res`), decidir status HTTP |
| **Service** (opcional, recomendado quando há regra que envolve várias entidades ou efeitos externos) | `services/` | Regras de negócio/casos de uso (checkout, criação de pedido, relatórios), orquestração de models, efeitos colaterais via dependências injetadas (notificação, pagamento) | Conhecer HTTP |
| **Controller** | `controllers/` | Fluxo da requisição: extrair e validar input, chamar service/model, escolher status HTTP, delegar serialização | Ter SQL, regras de negócio extensas, segredos |
| **View / Routes** | `views/` ou `routes/` | Mapear `METHOD /path` → função do controller; serializadores/presenters que definem o formato da resposta (removendo campos sensíveis) | Ter lógica além do mapeamento/serialização |
| **Middlewares** | `middlewares/` | Error handler centralizado, logging de requisições, (auth quando aprovado) | Regras de negócio |
| **Entry point / composition root** | `app.py` / `src/app.js` (ou `server.js`) | Criar o app (factory), carregar config, inicializar banco, instanciar dependências e registrar rotas e middlewares | Ter rotas de negócio inline |

### Regra de dependência

```
routes/views  →  controllers  →  services  →  models  →  database
       ↘ middlewares            ↘ config (qualquer camada pode ler config)
```
- Dependências apontam **só para a direita**. Model nunca importa controller; controller nunca executa SQL.
- Dependências externas (conexão de banco, notificador, gateway de pagamento) são **injetadas** (parâmetro do construtor/factory ou `app.extensions`/contexto), não criadas dentro da regra de negócio.

## 2. Estruturas alvo por stack

### Python / Flask
```
<projeto>/
├── app.py                  # composition root: create_app() + if __name__ == "__main__": app.run(...)
├── config/
│   └── settings.py         # Config via os.environ com defaults de dev
├── database.py             # conexão/sessão (por requisição ou extensão), init_db/seed
├── models/                 # <entidade>_model.py (acesso a dados + regras da entidade)
├── services/               # <caso_de_uso>_service.py (opcional)
├── controllers/            # <entidade>_controller.py
├── views/  (ou routes/)    # <entidade>_routes.py (Blueprints) + serializers
├── middlewares/
│   └── error_handler.py
└── requirements.txt
```

### Node.js / Express
```
<projeto>/
├── src/
│   ├── app.js              # composition root: cria app, injeta dependências, listen
│   ├── config/index.js     # process.env com defaults de dev
│   ├── database/           # conexão, schema, seed, helpers Promise (run/get/all)
│   ├── models/             # <entidade>Model.js (repositórios)
│   ├── services/           # <casoDeUso>Service.js
│   ├── controllers/        # <entidade>Controller.js
│   ├── routes/             # <entidade>Routes.js (express.Router)
│   └── middlewares/        # errorHandler.js, asyncHandler.js
└── package.json            # "start" continua funcionando
```

Outras stacks: mantenha os mesmos papéis com a convenção idiomática da linguagem.

## 3. Estratégia conforme o estado atual

- **Monolito (decomposição):** crie a estrutura completa acima, mova cada função para a camada correta, depois apague os arquivos antigos que ficaram vazios. Não deixe "arquivos ponte" com lógica duplicada.
- **Parcialmente organizado (incremental):** mantenha pastas existentes que já cumprem o papel (ex.: `models/`, `routes/` como camada View); adicione as camadas faltantes (`config/`, `controllers/`, `services/`, `middlewares/`); mova a lógica das rotas para controllers/services; **reaproveite** helpers e métodos de model existentes (ex.: `is_overdue()`) e elimine as cópias. Não renomeie pastas/arquivos sem necessidade.

## 4. Preservação do contrato (obrigatório)

Devem permanecer **idênticos**:
- Paths, métodos HTTP e parâmetros de rota/query.
- Nomes dos campos de entrada (mesmo ruins — ex.: `usr`, `eml`, `c_id`: mapeie para nomes claros **dentro** do controller).
- Estrutura das respostas de sucesso (mesmas chaves, mesmo envelope, ex.: `{"dados": ..., "sucesso": true}`) e status HTTP de sucesso e de erro esperados.
- Comando de execução documentado (`python app.py`, `npm start`), porta padrão e scripts auxiliares (ex.: `seed.py` que importa `from app import app, db` deve continuar funcionando).

Mudanças de contrato **permitidas** (por segurança) — devem ser listadas no resumo da Fase 3:
- Remover campos sensíveis das respostas (`password`, `senha`, hash, `secret_key`, `debug`, `db_path`).
- Trocar mensagens de erro internas (`str(e)`) por mensagens genéricas, **mantendo o status HTTP**.
- Remover endpoints de execução arbitrária (AP-05, ex.: `/admin/query`). Endpoints destrutivos administrativos (ex.: reset) podem ser mantidos protegidos por token configurado via ambiente (desabilitados quando o token não está definido).
- Transformar 500 causados por input inválido em 400.

Mudanças que **NÃO** devem ser aplicadas automaticamente (listar em "Pending (requires human decision)"):
- Exigir autenticação em endpoint hoje público (quebra clientes).
- Alterar regras de negócio (valores de desconto, regra de aprovação de pagamento), apenas extraí-las para constantes/serviços.
- Trocar o banco de dados ou major version de framework.

## 5. Convenções de qualidade no código refatorado

- Segredos só via ambiente: `os.environ.get("SECRET_KEY")` / `process.env.SECRET_KEY`. Default de desenvolvimento **não** pode ser um segredo fixo de aparência real: gere um aleatório em runtime (`secrets.token_hex(32)` / `crypto.randomBytes(32)`) e registre um aviso.
- `debug` desligado por padrão (`FLASK_DEBUG`/`APP_DEBUG=1` para ligar). Host padrão pode permanecer o original para não quebrar o contrato de acesso, mas debug nunca ligado por padrão.
- Queries 100% parametrizadas.
- Senhas com hash forte (werkzeug `generate_password_hash`/`scrypt` do Node) e migração transparente de hashes legados (ver T03).
- Logging via `logging` (Python) / logger simples (Node) — sem `print`/`console.log` espalhados.
- Um error handler central; controllers não repetem `try/except` genérico.
- Sem imports mortos; constantes nomeadas para regras.

## 6. Protocolo de validação

Execute **antes** (baseline, código original) e **depois** (código refatorado), nas mesmas condições:

1. **Preparação**
   - Dependências: `pip install -r requirements.txt` (de preferência em venv fora do projeto) / `npm install`.
   - Estado limpo: remova o banco local gerado pela aplicação (ex.: `*.db` ignorado pelo git) e rode o seed se o projeto exigir. Bancos em memória já iniciam limpos.
2. **Boot** em background com o comando original, redirecionando a saída para um log **fora do projeto**:
   - Python: `python -W default app.py > <tmp>/server.log 2>&1 &` (o `-W default` exibe DeprecationWarnings).
   - Node: `node --trace-deprecation src/app.js > <tmp>/server.log 2>&1 &` (ou `npm start`).
   - Aguarde a porta responder (loop curto com `curl`, até ~10s). Se não subir, leia o log.
3. **Requisições:** para cada endpoint do inventário, execute as mesmas chamadas (válidas e inválidas) com `curl -s -o <tmp>/<n>.json -w "%{http_code}"`, **na mesma ordem** (a ordem importa quando há escrita). Inclua no mínimo: listagem, busca por id existente e inexistente, criação válida e inválida, atualização, exclusão, login correto e incorreto, relatórios.
4. **Comparação:** para cada requisição, status HTTP igual ao baseline e mesmas chaves de primeiro nível no JSON (exceto remoções de segurança documentadas). Valores voláteis (timestamps, ids gerados) não precisam coincidir.
5. **Log:** o log do servidor não deve conter tracebacks nem warnings de deprecated originados no código do projeto.
6. **Encerramento:** derrube **todos** os processos iniciados (o reloader do modo debug cria processo filho):
   - Linux/macOS: `kill <pid>` / `pkill -f "app.py"`.
   - Windows (PowerShell): `Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? { $_.CommandLine -like '*app.py*' } | % { Stop-Process -Id $_.ProcessId -Force }` (análogo para `node.exe`).
7. Reporte o resultado como `X/Y requests match baseline`, listando cada divergência e se é intencional.
