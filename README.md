# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---
---

# Resolução do Desafio

> Esta parte documenta a solução. O enunciado acima foi mantido sem alterações.
>
> | Seção | Conteúdo |
> |---|---|
> | [A) Análise Manual](#a-análise-manual) | Problemas encontrados à mão em cada projeto, antes de escrever a skill |
> | [B) Construção da Skill](#b-construção-da-skill) | Design do `SKILL.md` e das referências, catálogo, independência de stack, iterações |
> | [C) Resultados](#c-resultados) | Findings por severidade, antes/depois, checklist preenchido, logs |
> | [D) Como Executar](#d-como-executar) | Pré-requisitos, comandos e como validar |
>
> **Entregáveis:** a skill em [`code-smells-project/.claude/skills/refactor-arch/`](code-smells-project/.claude/skills/refactor-arch/SKILL.md), com cópia idêntica nos outros 2 projetos; os relatórios em [`reports/`](reports/); a análise manual detalhada em [`docs/analise-manual.md`](docs/analise-manual.md); os smoke tests em [`scripts/`](scripts/); os logs pós-refatoração em [`docs/logs/`](docs/logs/).

## A) Análise Manual

Antes de escrever a skill, li todo o código dos 3 projetos. Para cada problema registrei severidade, arquivo e linha exatos e por que ele importa. Sempre que possível, confirmei o problema na aplicação rodando (ex.: login com SQL Injection, cartão aparecendo no log). Na mesma etapa criei um **smoke test por projeto** ([`scripts/`](scripts/)). Ele registra o comportamento original (o *baseline*) e é a régua da Fase 3: 22/22, 8/8 e 32/32 chamadas corretas antes da refatoração.

| Projeto | Stack | Arquivos / linhas | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python 3 + Flask 3.1 + sqlite3 (SQL cru) | 4 / ~780 | 4 | 4 | 4 | 3 | **15** |
| 2 — ecommerce-api-legacy | Node.js + Express 4 + sqlite3 em memória (callbacks) | 3 / ~180 | 4 | 4 | 5 | 3 | **16** |
| 3 — task-manager-api | Python 3 + Flask 3.0 + Flask-SQLAlchemy | 13 / ~1.150 | 3 | 3 | 7 | 3 | **16** |

As tabelas abaixo resumem cada problema. Os arquivos e linhas exatos de cada item estão em [`docs/analise-manual.md`](docs/analise-manual.md).

### Projeto 1 — code-smells-project (API de E-commerce)

| Sev. | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | SQL Injection (SQL montado por concatenação) | Comprovado: login com `admin@loja.com' --` entra como admin sem senha |
| CRITICAL | `/admin/query` executa SQL arbitrário e `/admin/reset-db` apaga o banco, ambos sem autenticação | Qualquer cliente lê todas as senhas ou destrói os dados |
| CRITICAL | `SECRET_KEY` fixa no código e devolvida pelo `/health` | Segredo no git e exposto publicamente |
| CRITICAL | Senhas em texto puro, gravadas e retornadas pela API | Vazamento direto das credenciais de todos os usuários |
| HIGH | Modo debug ligado e servidor ouvindo em `0.0.0.0` | O debugger do Werkzeug permite executar código remotamente |
| HIGH | Regra de negócio no model; SQL dentro do controller | Camadas misturadas, regra impossível de testar isoladamente |
| HIGH | Uma única conexão SQLite global compartilhada entre threads | Condições de corrida; conexão, schema e seed misturados |
| HIGH | Notificações (e-mail/SMS) acopladas ao fluxo HTTP | Não dá para trocar nem testar esses efeitos colaterais |
| MEDIUM | Query N+1 em pedidos → itens → produto | O número de queries cresce com o volume de dados |
| MEDIUM | Funções e validações duplicadas | Correções precisam ser feitas em vários lugares |
| MEDIUM | Sem validação de entrada; `try/except` repetido que devolve `str(e)` | Erro 500 em input inválido e detalhes internos vazados |
| MEDIUM | Pedido criado sem transação | Estoque pode ficar negativo; pedido pode ficar sem itens |
| LOW | Magic numbers (faixas de desconto, status) | Regras de negócio escondidas no código |
| LOW | `print` usado como log | Sem níveis de log; e-mails de usuários aparecem no log |
| LOW | Nomes ruins (`id` sombreando o built-in, `cursor2`) e imports mortos | Legibilidade |

### Projeto 2 — ecommerce-api-legacy (LMS com checkout)

| Sev. | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | God Class `AppManager` (conexão, schema, seed, rotas, pagamento e relatório na mesma classe) | Nenhuma separação de camadas; nada é testável |
| CRITICAL | Credenciais fixas no código (senha do banco, chave *live* do gateway, SMTP) | Segredos versionados no git |
| CRITICAL | Número do cartão e chave do gateway escritos no log | Comprovado no baseline; viola a PCI-DSS |
| CRITICAL | "Hash" de senha em Base64 truncado e senha padrão `123456` | Na prática, as senhas ficam em texto puro |
| HIGH | Relatório financeiro e exclusão de usuário sem autenticação | Qualquer cliente lê dados financeiros ou apaga usuários |
| HIGH | Regra de negócio na rota, com 5 níveis de callbacks | Fluxo de pagamento ilegível e não testável |
| HIGH | Checkout sem transação | Matrícula pode ficar gravada sem o pagamento |
| HIGH | Estado global mutável (`globalCache`, `totalRevenue`) | Vazamento de memória e dado global enganoso |
| MEDIUM | Query N+1 no relatório | 1 + C + 2×M queries por relatório |
| MEDIUM | DELETE sem integridade referencial, sempre responde 200 | Dados órfãos (`"Unknown"`) no relatório |
| MEDIUM | `err` dos callbacks ignorado | Uma falha no banco derruba o processo em vez de responder 500 |
| MEDIUM | Validação de entrada fraca | Dados inválidos chegam ao banco |
| MEDIUM | `npm audit` mostra 13 vulnerabilidades (2 critical) | Dependências desatualizadas |
| LOW | Nomes crípticos (`u`, `cc`, `c_id`) | Legibilidade (o payload é mantido por compatibilidade) |
| LOW | Magic numbers; erros às vezes em texto, às vezes em JSON | Contrato da API inconsistente |
| LOW | `self = this` misturado com arrow functions; import morto | Confusão sobre o escopo de `this` |

### Projeto 3 — task-manager-api (Task Manager, já parcialmente organizado)

| Sev. | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | `SECRET_KEY` e credenciais SMTP fixas no código | Segredos versionados no git |
| CRITICAL | Senha em MD5 sem salt, e o hash é devolvido em login e consultas | Comprovado: o hash aparece na resposta do `/login` |
| CRITICAL | Token falso, nenhuma rota protegida, e `POST /users` aceita `role: "admin"` | Qualquer pessoa se cadastra como admin |
| HIGH | Rotas "gordas": validam, consultam, calculam e serializam | Ter as pastas `models/` e `routes/` não é o mesmo que seguir MVC |
| HIGH | Código pronto que ninguém usa (`is_overdue()`, validadores, `NotificationService`) | Várias implementações paralelas da mesma regra |
| HIGH | Debug ligado, configuração fixa no código, sem app factory | Debugger exposto; não dá para configurar ambientes |
| MEDIUM | Queries N+1 (`Query.get` para cada task) | Desempenho piora com o volume de dados |
| MEDIUM | Regra de "atrasada" duplicada 6 vezes | Regras divergentes |
| MEDIUM | `priority` em string ou `title: null` geram erro 500 | Erro de input vira erro de servidor |
| MEDIUM | `except:` genérico que engole exceções | Esconde bugs (inclusive `SystemExit`) |
| MEDIUM | APIs deprecated: `datetime.utcnow()` e `Query.get()` | Vão quebrar em versões futuras do Python e do SQLAlchemy |
| MEDIUM | Relatório com 12 `count()` separados e todas as tasks carregadas em memória | Deveria ser um `GROUP BY` no banco |
| MEDIUM | Integridade referencial feita à mão nas rotas | A cascata deveria estar declarada no model |
| LOW | Imports não usados | Ruído |
| LOW | Magic numbers e listas de status repetidas | Já existiam constantes, mas não eram usadas |
| LOW | Código verboso (`if x: return True else: return False`, `type(x) == list`) | Legibilidade |

## B) Construção da Skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                              # 159 linhas: o "prompt" com as 3 fases, regras invioláveis e formatos de saída
└── references/
    ├── project-analysis.md               # Fase 1: heurísticas de linguagem, framework, banco, domínio e arquitetura
    ├── anti-patterns-catalog.md          # Fase 2: 26 anti-patterns com sinais de detecção, falsos positivos e severidade
    ├── audit-report-template.md          # Fase 2: formato obrigatório do relatório
    ├── mvc-guidelines.md                 # Fase 3: camadas, regra de dependência, estruturas-alvo, contrato, protocolo de validação
    └── refactoring-playbook.md           # Fase 3: 17 transformações (T01–T17) com antes/depois em Python e JavaScript (T16: autenticação real; T02/T17: defaults seguros)
```

### Decisões de design

1. **O `SKILL.md` diz o que fazer; as referências trazem o conhecimento.** O `SKILL.md` descreve o processo e as regras. Cada arquivo de referência só é lido na fase em que é necessário (tabela "quando ler"). Assim o contexto fica enxuto: o playbook de 769 linhas não é carregado durante a análise.
2. **Regras invioláveis no topo do `SKILL.md`:**
   - Nada é alterado antes do "y".
   - Nenhum finding sem arquivo e linha que o agente tenha lido.
   - Lista de pastas e arquivos ignorados.
   - Preservação do contrato da API.
   - Monolito é decomposto; projeto parcialmente organizado é melhorado de forma incremental.
   - Nenhum comando git.
   - Relatório no idioma do projeto.
3. **Pausa obrigatória com frase exata.** A Fase 2 termina com `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e a instrução "PARE AQUI". Qualquer resposta diferente de `y` não modifica nada.
4. **Relatório salvo pela própria skill.** O argumento opcional `$ARGUMENTS` (`/refactor-arch ../reports/audit-project-N.md`) indica onde gravar o relatório da Fase 2. É a única escrita permitida antes da confirmação.
5. **Validação objetiva, não "parece que funciona".** A Fase 3 captura um *baseline* (status HTTP e JSON de cada endpoint) **antes** de mexer no código. Depois da refatoração, repete as mesmas requisições e compara status e chaves do JSON. Também sobe a app com `python -W default` ou `node --trace-deprecation` para pegar avisos de deprecated e audita de novo os sinais CRITICAL/HIGH. A regra final é "nunca marque ✓ em algo que você não executou e observou".
6. **Contrato da API versus segurança.** O `mvc-guidelines.md` separa:
   - Mudanças de segurança **permitidas e obrigatórias**, listadas na seção "Security Contract Changes" do resumo: remover `password` das respostas, trocar 500 por 400 em input inválido, remover `/admin/query`, **corrigir o AP-11** (token assinado com expiração, rotas protegidas por papel, papel definido pelo servidor), aplicar os **defaults seguros do AP-10** (debug off, bind `127.0.0.1`, CORS fechado sem `CORS_ORIGINS`), trocar 200 falso por 404 e corrigir órfãos com soft delete ou cascata.
   - Mudanças que **exigem decisão humana**: alterar regra de negócio, trocar banco ou major version do framework, trocar a autenticação por um provedor externo (OAuth/SSO), mudar o formato do corpo de erro. Elas aparecem em "Pending (requires human decision)". AP-10, AP-11 e qualquer outro CRITICAL/HIGH **nunca** vão para essa seção.
8. **A Recommendation é um compromisso (regra 9, v1.3).** O que a Recommendation de um finding promete é exatamente o que a Fase 3 entrega, com os mesmos valores e defaults. Se uma parte depende de decisão humana, a própria Recommendation já diz `Pending: <motivo>` (só em MEDIUM/LOW). A Fase 3 termina com uma **reconciliação Fase 2 × Fase 3**: relê o relatório finding por finding e confere no código que cada Recommendation foi cumprida.
7. **Matriz de acesso explícita.** Para corrigir o AP-11 de forma igual em qualquer stack, o `mvc-guidelines.md` classifica cada endpoint do inventário em **público** (health, login, cadastro, catálogo, checkout), **autenticado — dono ou admin** (dados do próprio usuário, pedidos em nome próprio) e **admin** (listar/excluir usuários, alterar papel, relatórios, escrita no catálogo, `/admin/*`). O T16 traz o código concreto em Python (`itsdangerous` + decorators `login_required`/`admin_required`) e em Node (HMAC com `crypto` + middleware), inclusive o caso de projeto sem login (credencial de admin definida no servidor via `ADMIN_TOKEN`).

### Catálogo de anti-patterns (26 itens)

| Severidade | Anti-patterns | Por que entraram |
|---|---|---|
| CRITICAL | AP-01 SQL/NoSQL Injection · AP-02 Segredos fixos no código · AP-03 Senha insegura · AP-04 Exposição de dados sensíveis · AP-05 Endpoint de execução arbitrária · AP-06 God Class/File | Falhas exploráveis e o problema arquitetural mais grave; todas apareceram na análise manual |
| HIGH | AP-07 Regra de negócio na rota · AP-08 Acesso a dados fora do Model · AP-09 Estado global mutável · AP-10 Configuração insegura · AP-11 Autenticação ausente ou falsa · AP-12 Escrita múltipla sem transação · AP-13 Efeitos colaterais acoplados / callback hell | Violações de MVC/SOLID e riscos de integridade dos dados |
| MEDIUM | AP-14 N+1 · AP-15 Duplicação · AP-16 Validação ausente · AP-17 Erros descentralizados · AP-18 APIs deprecated e dependências vulneráveis · AP-19 Agregação ineficiente · AP-20 Integridade referencial manual | Desempenho, robustez e manutenção |
| LOW | AP-21 Magic numbers · AP-22 `print`/`console.log` · AP-23 Nomes ruins · AP-24 Código morto · AP-25 Código não idiomático · AP-26 Respostas inconsistentes | Legibilidade |

Cada item tem **sinais de detecção concretos**, alguns encontráveis com grep (ex.: `f"SELECT`, `+ "' "`, `hashlib.md5`, `.query.get(`) e outros estruturais (ex.: "query dentro de `for`"). Também lista **falsos positivos** (ex.: concatenação só de constantes não é SQL Injection) e a **transformação do playbook** que corrige o problema. As **regras de calibração** permitem subir ou descer a severidade com justificativa escrita. Isso aconteceu de verdade:
- AP-16 subiu para HIGH no Projeto 2, porque o input sem validação derrubava o processo.
- AP-13 desceu para MEDIUM no Projeto 3, porque o código de notificação existia mas nunca era chamado.

O AP-18 traz uma tabela de APIs deprecated por stack (Python, SQLAlchemy, Flask/Werkzeug, Node/Express, callbacks legados).

### Como a skill se mantém agnóstica de tecnologia

- A **Fase 1 descobre a stack pelos manifestos** (`requirements.txt`, `package.json`, `go.mod`, `pom.xml`, ...) e pelos imports, em vez de assumir Flask ou Express.
- O **catálogo descreve conceitos** (ex.: "acesso a dados fora do Model") com sinais de exemplo de várias linguagens; nenhum item depende de um projeto específico.
- O **`mvc-guidelines.md` define papéis** (Config, Model, Service, Controller, View/Routes, Middleware, Composition root) e dá estruturas-alvo para Flask e Express. Para outras stacks, a regra é aplicar os mesmos papéis com a convenção da linguagem.
- O **playbook mostra cada transformação em Python e em JavaScript**.
- **A prova:** a mesma pasta foi copiada sem nenhuma alteração para os 3 projetos (`diff -r` sem diferenças) e funcionou em Python/SQL cru, Node/callbacks e Python/ORM já organizado.

### Desafios encontrados e iterações (v1 → v1.1)

| Problema observado | Onde | Correção |
|---|---|---|
| A skill **criou um branch git** (`refactor/mvc-architecture`) sem que o usuário pedisse | Projeto 1 | **Regra 7**: proibidos comandos git que alterem o repositório; versionar é decisão do usuário. Mantive o branch e trabalhei nele até o merge final |
| A verificação de deprecated foi só estática ("Nenhuma detectada" sem executar nada), porque o Flask não estava instalado | Projeto 1 | **Fase 2, passo 3**: verificação em tempo de execução **obrigatória**: venv temporário fora do projeto + `python -W default`; `npm audit` + `node --trace-deprecation` |
| Relatório escrito em inglês num projeto em português | Projeto 1 | **Regra 8**: relatório no idioma do projeto (só os rótulos do template ficam em inglês). Confirmado nos Projetos 2 e 3 |
| O servidor Flask não morria com um único `kill` (o reloader do modo debug cria um processo filho) | Validação | O protocolo de validação passou a incluir o comando para Windows e Linux que derruba todos os processos |
| Como refatorar o Projeto 3 sem "reescrever do zero" | Projeto 3 | Estratégia **incremental** no `mvc-guidelines.md`: manter `models/` e `routes/`, adicionar `config/`, `controllers/` e `middlewares/`, **reaproveitar** `is_overdue()` e helpers e eliminar as cópias |

#### Iteração v1.1 → v1.2 (após a revisão do professor)

| Problema observado | Onde | Correção |
|---|---|---|
| A skill classificava o AP-11 como HIGH na Fase 2, mas mandava a correção para "Pending" na Fase 3. Resultado: no Projeto 3 o login continuava devolvendo `fake-jwt-token-<id>` e o cadastro aceitava `role` do cliente (qualquer pessoa virava admin) | Projetos 1, 2 e 3 | **Catálogo (AP-11):** a nota agora manda **corrigir na Fase 3, nunca adiar**, e ganhou sinais novos (login sem credencial, token previsível, `user_id` do corpo usado como identidade). **`mvc-guidelines.md` §4:** a correção do AP-11 virou mudança de segurança permitida e obrigatória, com a matriz de acesso público / dono ou admin / admin e as checagens 401/403 no protocolo de validação. **T16:** padrão concreto de token assinado com expiração, middleware que relê o papel do banco, papel definido pelo servidor no cadastro/update e o caso `ADMIN_TOKEN` para projetos sem login. **`SKILL.md`:** passo 8 da Fase 3 dedicado ao AP-11, nova seção "Security Contract Changes" no resumo e item "Authentication enforced" na validação |

Depois da correção, a Fase 3 foi executada de novo nos 3 projetos (incremental sobre o código já refatorado, que só divergia da nova skill no AP-11), com os relatórios atualizados no finding AP-11 e os smoke tests ampliados com as checagens de autorização.

#### Iteração v1.2 → v1.3 (após a segunda revisão do professor)

A segunda revisão mostrou o mesmo tipo de falha da primeira, em outro finding: o **HIGH #10 (AP-10)** do Projeto 1 recomendava `CORS_ORIGINS` "com default seguro", mas a Fase 3 manteve `"*"` como padrão ("preserva o comportamento aberto"). Em vez de corrigir só esse ponto, tratei a causa: **nada obrigava a Fase 3 a cumprir a Recommendation da Fase 2**. Revisei os 69 findings dos 3 relatórios contra o código e encontrei outras divergências do mesmo tipo.

| Problema observado | Onde | Correção |
|---|---|---|
| AP-10: Recommendation pedia defaults seguros, mas o código manteve `CORS_ORIGINS="*"` e `HOST=0.0.0.0` como padrão | P1 (#10) e P3 (#6) | **Catálogo (AP-10):** nota "corrigido com defaults seguros, nunca Pending"; um config que lê o ambiente mas tem default inseguro também é AP-10. **T02/T17:** tabela de defaults obrigatórios (debug off, `HOST=127.0.0.1`, **CORS fechado**: sem `CORS_ORIGINS` o `flask-cors` nem é registrado; `*` só se definido explicitamente) com código Python e Node. **`mvc-guidelines.md`:** CORS fechado virou mudança de segurança permitida e obrigatória, com checagem `Origin: http://evil.example` no protocolo de validação |
| Recommendations cumpridas só em parte, sem aparecer em "Pending" | P1 #16 (status de pedido inexistente → 200), P1 #20 (produto excluído deixava itens órfãos), P2 #11/#13 (e-mail, `c_id`, `card` e `:id` sem validar; `DELETE` inexistente → 200), P2 #16 (Recommendation pedia cascata, código mantinha os órfãos), P3 #11 (`color` sem validação), P3 #2 (senha mínima de 4) | **Regra 9 no `SKILL.md`:** a Recommendation é um compromisso; parte pendente só com `Pending: <motivo>` explícito e só em MEDIUM/LOW. **Reconciliação Fase 2 × Fase 3** obrigatória na validação, com linha própria no resumo. **AP-20:** o catálogo agora diz quando usar soft delete (filho é histórico) e quando usar cascata transacional (filho pertence ao pai), e o T09 traz os dois exemplos. **`mvc-guidelines.md`:** 200 falso → 404 virou mudança permitida |
| Itens que eram decisão humana de verdade, mas a Recommendation não dizia isso | P1 #13 (devolver estoque ao cancelar), P2 #22 (erro em texto → JSON), P3 #8 (disparar e-mails) | As Recommendations agora terminam com `Pending: <motivo>`, e são exatamente esses os itens da seção "Pendências" |
| A Fase 2 do Projeto 1 não tinha rodado a checagem em tempo de execução nem a auditoria de dependências (`pip-audit`) | P1 | **Fase 2, passo 3:** `pip-audit` obrigatório no venv temporário. Novo finding **#18 [MEDIUM] AP-18**: `flask 3.1.1` e `flask-cors 5.0.1` com vulnerabilidades conhecidas → atualizados para 3.1.3 e 6.0.0 |
| `npm audit` ainda mostrava 8 vulnerabilidades, deixadas como "pendência de major version" | P2 #14 | `sqlite3` atualizado para 6.0.1 (é driver, não framework; mesma API) e `qs` fixado via `overrides` → **0 vulnerabilidades** |

Depois da correção, rodei de novo a Fase 3 de forma incremental nos 3 projetos, os 3 relatórios foram revisados (Recommendations reescritas para dizer exatamente o que foi entregue; P1 ganhou o finding #18) e os smoke tests ganharam as checagens da v1.3. A validação final sobe cada app **sem nenhuma variável de ambiente**, para provar os defaults seguros.

Também vi a validação da própria skill funcionando: no Projeto 3, ela percebeu ao testar que parte do finding #15 estava errada (o ORM já limpava `category_id` ao apagar uma categoria) e **corrigiu o relatório** em vez de manter um achado falso.

## C) Resultados

### Resumo das auditorias (Fase 2)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Análise manual | Relatório |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | 6 | 7 | 7 | 6 | **26** | 15 | [audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | 4 | 7 | 5 | 6 | **22** | 16 | [audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api | 3 | 4 | 8 | 6 | **21** | 16 | [audit-project-3.md](reports/audit-project-3.md) |

Em todos os projetos a skill encontrou **mais findings que a análise manual**. Todos os CRITICAL e HIGH da análise manual aparecem nos relatórios. O número é maior porque o catálogo é mais granular: por exemplo, "senha em texto puro" e "senha exposta na resposta" viram AP-03 e AP-04.

### Critérios de aceite

| Critério | P1 | P2 | P3 |
|---|---|---|---|
| Fase 1 detecta a stack corretamente | ✅ Python/Flask 3.1, sqlite3 | ✅ Node.js/Express 4, sqlite3 | ✅ Python/Flask 3.0 + SQLAlchemy, domínio Task Manager |
| Fase 2 encontra ≥ 5 findings | ✅ 26 | ✅ 22 | ✅ 21 |
| Fase 2 tem ≥ 1 CRITICAL ou HIGH | ✅ 13 | ✅ 11 | ✅ 7 |
| Fase 3: a aplicação funciona após a refatoração | ✅ smoke 49/49 (22 do baseline + 19 de autorização + 8 da v1.3) | ✅ smoke 22/22 (8 do baseline + 5 de autorização + 9 da v1.3) | ✅ smoke 55/55 (32 do baseline + 17 de autorização + 6 da v1.3) |
| Fase 3: AP-11 corrigido (sem pendência) | ✅ token assinado no login, matriz de acesso | ✅ rotas admin com `ADMIN_TOKEN` | ✅ token assinado, papel definido pelo servidor |
| Fase 3: AP-10 com defaults seguros (sem pendência) | ✅ CORS fechado, bind `127.0.0.1`, debug off | ✅ bind `127.0.0.1` (o projeto não usa CORS) | ✅ CORS fechado, bind `127.0.0.1`, debug off |
| Fase 3: cada Recommendation entregue ou declarada `Pending` | ✅ 26/26 (1 `Pending` declarado) | ✅ 22/22 (1 `Pending` declarado) | ✅ 21/21 (1 `Pending` declarado) |

### Estrutura antes → depois

<table>
<tr><th>Projeto</th><th>Antes</th><th>Depois</th></tr>
<tr><td><b>1</b><br>monolito → MVC completo</td><td>

```
app.py
controllers.py
models.py
database.py
```
</td><td>

```
app.py               # create_app() (composition root)
database.py          # conexão por requisição (g)
errors.py
config/              settings.py, constants.py
models/              produto, usuario, pedido, sistema
services/            pedido, relatorio, usuario, notification, auth
controllers/         produto, usuario, pedido, relatorio,
                     sistema, validators
views/               routes.py, serializers.py
middlewares/         error_handler.py, auth.py
```
</td></tr>
<tr><td><b>2</b><br>God Class → MVC (Express)</td><td>

```
src/app.js
src/AppManager.js
src/utils.js
```
</td><td>

```
src/app.js           # composition root
src/config/          index.js, constants.js
src/database/        index.js (Promises, transaction())
src/models/          user, course, enrollment, payment,
                     auditLog, report
src/services/        checkout, report, user, paymentGateway
src/controllers/     checkout, report, user
src/routes/          index.js
src/middlewares/     errorHandler.js, auth.js
src/utils/           logger.js, password.js (scrypt)
```
</td></tr>
<tr><td><b>3</b><br>camadas só no nome → MVC incremental</td><td>

```
app.py
database.py
seed.py
models/    task, user, category
routes/    task, user, report
services/  notification_service (não usado)
utils/     helpers (não usado)
```
</td><td>

```
app.py               # create_app()
database.py
seed.py              # continua funcionando
config/              settings.py, constants.py      (novo)
models/              task, user, category           (mantido)
services/            task, user, category, report, auth,
                     notification (injetável)       (ampliado)
controllers/         task, user, category, report,
                     system, validators             (novo)
routes/              task, user, report, category,
                     system                         (mantido)
views/               serializers.py                 (novo)
middlewares/         error_handler.py, auth.py      (novo)
utils/               helpers.py, security.py        (reaproveitado)
```
</td></tr>
</table>

Os arquivos antigos que foram totalmente substituídos (`controllers.py`, `models.py`, `AppManager.js`, `utils.js`) foram **removidos**. Não ficaram duas implementações da mesma regra.

### Checklist de validação preenchido

Cada item foi conferido por mim de forma independente, além do resumo da própria skill: li o relatório, rodei o smoke test e testei os pontos de segurança.

| Item | P1 | P2 | P3 |
|---|---|---|---|
| **Fase 1 — Análise** | | | |
| Linguagem detectada corretamente | ✅ Python 3 | ✅ JavaScript (Node.js 20) | ✅ Python 3 |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4 | ✅ Flask 3.0 + Flask-SQLAlchemy |
| Domínio descrito corretamente | ✅ E-commerce (produtos, usuários, pedidos) | ✅ LMS com checkout (cursos, matrículas, pagamentos) | ✅ Task Manager (tasks, usuários, categorias) |
| Número de arquivos condiz com a realidade | ✅ 4 arquivos | ✅ 3 arquivos em `src/` | ✅ 13 arquivos `.py` |
| **Fase 2 — Auditoria** | | | |
| Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 25 | ✅ 22 | ✅ 21 |
| Detecção de APIs deprecated (se aplicável) | ✅ nenhuma API deprecated no código (Grep + `-W default` em tempo de execução); `pip-audit` achou `flask 3.1.1` e `flask-cors 5.0.1` vulneráveis (finding #18) | ✅ callbacks legados do sqlite3 + `npm audit` (13 vulnerabilidades); `--trace-deprecation` limpo | ✅ `datetime.utcnow()` e `Query.get()` encontrados no código e confirmados em tempo de execução |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3 — Refatoração** | | | |
| Estrutura de diretórios segue MVC | ✅ | ✅ | ✅ |
| Configuração em módulo próprio, sem valores fixos | ✅ `config/settings.py` + `.env.example`, defaults seguros | ✅ `src/config/` + `.env.example`, bind local | ✅ `config/settings.py` + `.env.example`, defaults seguros |
| Models abstraem os dados | ✅ `models/*_model.py` (queries parametrizadas) | ✅ `src/models/*Model.js` | ✅ `models/` (consultas e agregações) |
| Views/Routes separadas | ✅ `views/routes.py` + `serializers.py` | ✅ `src/routes/index.js` | ✅ `routes/*` + `views/serializers.py` |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ `middlewares/error_handler.py` | ✅ `src/middlewares/errorHandler.js` | ✅ `middlewares/error_handler.py` |
| Entry point claro | ✅ `app.py` (`create_app`) | ✅ `src/app.js` (`npm start`) | ✅ `app.py` (`create_app`) |
| Aplicação inicia sem erros | ✅ `python app.py` (sem variáveis de ambiente) | ✅ `npm start` | ✅ `python seed.py && python app.py` (sem variáveis de ambiente) |
| Endpoints originais respondem corretamente | ✅ 22/22 (com token do papel adequado) | ✅ 8/8 (receitas 997 e 994 iguais às originais; rotas admin com `ADMIN_TOKEN`) | ✅ 32/32 (com token do papel adequado) |
| Autenticação e autorização (AP-11) | ✅ 19/19 checagens | ✅ 5/5 checagens | ✅ 17/17 checagens |
| Defaults seguros e correções da v1.3 | ✅ 8/8 (CORS fechado, 404, soft delete) | ✅ 9/9 (validação, 404, cascata) | ✅ 6/6 (CORS fechado, senha mínima, cor) |
| Dependências sem vulnerabilidades conhecidas | ✅ `pip-audit`: nenhuma | ✅ `npm audit`: 0 | ✅ `pip-audit`: nenhuma |

**Verificações extras de segurança feitas depois da refatoração:**
- **P1:**
  - Login com SQL Injection → `401`.
  - `/admin/query` → `404` (removido).
  - `/admin/reset-db` sem token → `401`; com token de cliente → `403`; só admin reseta.
  - Login devolve token assinado em `dados.token`; rotas admin sem token → `401`, com token de cliente → `403`; token adulterado → `401`.
  - Cliente não cria pedido em nome de outro usuário nem lê pedidos/dados de outro usuário (`403`).
  - Cadastro com `"tipo":"admin"` → criado como `cliente`.
  - `/health` sem `secret_key`; `/usuarios/1` sem `senha`.
  - Preço em string → `400`.
  - Sem variáveis de ambiente: servidor em `127.0.0.1`, debug off e **nenhum** `Access-Control-Allow-Origin` para `Origin: http://evil.example`. Com `CORS_ORIGINS=http://ok.example`, só essa origem recebe o header.
  - `PUT /pedidos/9999/status` → `404` (antes `200`).
  - Produto excluído: some do catálogo (`404`), não pode ser pedido (`400`) e o histórico do pedido mantém o nome dele.
- **P2:**
  - Cartão inválido → `400`, e o servidor continua de pé.
  - O log mostra só o "cartão final 4444".
  - Nenhum segredo restante em `src/`.
  - Relatório financeiro e `DELETE /api/users/:id` sem credencial, com credencial errada ou adulterada → `401`; com `ADMIN_TOKEN` → `200`. Sem `ADMIN_TOKEN` configurado, a app avisa no boot e as rotas admin ficam desabilitadas.
  - `npm audit`: de 13 para **0** vulnerabilidades (`sqlite3` 6.0.1 + `qs` fixado via `overrides`).
  - E-mail inválido, `c_id: "abc"` e cartão com letras → `400`; `DELETE /api/users/abc` → `400`; usuário inexistente → `404`.
  - `DELETE /api/users/1` remove o usuário com suas matrículas e pagamentos: o relatório fica sem alunos `Unknown` (curso 1: receita 0; curso 2: 497).
- **P3:**
  - `/login` e `/users/1` sem `password`.
  - `/login` não devolve mais `fake-jwt-token-<id>`: o `token` é assinado (HMAC + expiração); `fake-jwt-token-1` e token adulterado → `401`.
  - Cadastro público com `"role":"admin"` → criado com `role: user`; o usuário criado recebe `403` em `GET /users`. Admin autenticado consegue criar `manager`.
  - Usuário comum: `403` em `GET /users`, `DELETE /users/1`, `/reports/summary`, escrita em categorias, dados de outro usuário e ao tentar mudar o próprio `role`.
  - Todos os hashes no banco em `scrypt`; hash MD5 legado migrado no login.
  - `"priority":"alta"` e `?priority=x` → `400` (antes eram `500`).
  - Log sem `DeprecationWarning`/`LegacyAPIWarning`.
  - Sem variáveis de ambiente: servidor em `127.0.0.1`, debug off, CORS fechado.
  - `color: "azul"` ou `"#12345"` → `400`; senha com menos de 8 caracteres no cadastro → `400` (login com as senhas do seed continua funcionando).

**Validação final (v1.2), além dos smoke tests:**
- **Original × atual, requisição por requisição:** subi o código do commit inicial e o atual e comparei status HTTP e estrutura do JSON (2 níveis). As rotas protegidas foram chamadas com o token do papel adequado.
  - P1: 17/23 iguais. As 6 diferenças são intencionais: `senha` e `secret_key`/`debug`/`db_path` removidos, `sucesso: false` acrescentado nos erros (mesmo status) e `token` acrescentado em `dados` no login.
  - P2: 6/6 iguais (rotas admin com `ADMIN_TOKEN`).
  - P3: 24/28 iguais. As 4 diferenças são a remoção de `password` das respostas.
  - **v1.3:** as requisições do baseline continuam com o mesmo status (parte "baseline" dos smoke tests). A única nova diferença de corpo é intencional: o texto do `DELETE /api/users/:id` no P2, que descrevia o defeito corrigido. Os novos 400/404 só aparecem em chamadas que antes eram inválidas (id inexistente, cor ou e-mail fora do formato, senha curta), e CORS só muda para navegadores em outra origem.
- **Casos de borda de autenticação (24/24):** token expirado (`TOKEN_MAX_AGE=2`) → 401; token assinado com outra `SECRET_KEY` → 401; requisição sem header → 401; promover ou rebaixar um usuário vale na hora, com o mesmo token (papel relido do banco); usuário desativado perde o acesso (401) e não consegue logar (403); usuário comum não altera o próprio `active` (403); `usuario_id` `"2"` (string) próprio → 201, de outro → 403; cadastro com token inválido → 401. Nenhum log com `Traceback` ou `DeprecationWarning`.

### Pendências (decisão humana)

A skill não aplica automaticamente mudanças que alteram regra de negócio ou infraestrutura. Desde a v1.3, **só fica pendente o que a própria Recommendation do relatório já declarava como `Pending: <motivo>`**, e nunca um CRITICAL/HIGH. AP-10 e AP-11 foram corrigidos nos 3 projetos. Ficaram para decisão humana:
- **Todos os projetos:** trocar o token próprio por um provedor de identidade externo (OAuth/SSO), se a empresa tiver um.
- **P1 (#13):** devolver o estoque quando um pedido é cancelado. O código original só escrevia "Devolver estoque." no log; executar a devolução é uma regra de negócio nova.
- **P2 (#22):** trocar o corpo de erro de texto puro para JSON. Isso quebraria clientes que já leem o texto.
- **P3 (#8):** disparar e-mails quando uma task é atribuída ou fica atrasada. O `NotificationService` está pronto e injetado, mas o código original nunca enviava e-mails, então é uma funcionalidade nova.

### Logs das aplicações rodando após a refatoração

Os logs completos estão em [`docs/logs/`](docs/logs/), um por projeto, com o smoke test e o log do servidor:
- [project-1-after.txt](docs/logs/project-1-after.txt)
- [project-2-after.txt](docs/logs/project-2-after.txt)
- [project-3-after.txt](docs/logs/project-3-after.txt)

Trechos:

```
$ python -W default app.py        # Projeto 1
WARNING [__main__] SECRET_KEY não definida; usando chave aleatória (apenas desenvolvimento).
INFO [__main__] Servidor iniciado em http://127.0.0.1:5000 (debug=False)
 * Debug mode: off
$ bash scripts/smoke-project-1.sh
Autorização (AP-11):
  OK   login devolve token assinado em dados.token
  OK   cadastro público com tipo=admin vira tipo=cliente
Correções v1.3 (AP-10 defaults seguros, AP-16 404, AP-20 soft delete):
  OK   CORS fechado por padrão (origem externa sem Access-Control-Allow-Origin)
  OK   histórico do pedido mantém o nome do produto excluído
Resultado: 49 OK, 0 FAIL

$ ADMIN_TOKEN=<aleatório> npm start   # Projeto 2
[WARN] PAYMENT_GATEWAY_KEY não definida; gateway de pagamento roda em modo simulado (apenas desenvolvimento).
[INFO] Frankenstein LMS rodando em http://127.0.0.1:3000...
[INFO] Processando pagamento de 997 com cartão final 4444 (gateway simulado)
$ ADMIN_TOKEN=<o mesmo> bash scripts/smoke-project-2.sh
  OK   GET /api/admin/financial-report -> 401
  OK   receitas do relatório conferem
  OK   exclusão em cascata: relatório sem alunos órfãos
Resultado: 22 OK, 0 FAIL

$ python seed.py && python -W default app.py   # Projeto 3
Seed concluído com sucesso!
 * Debug mode: off
INFO services.task_service: Task criada: 11
$ bash scripts/smoke-project-3.sh
Autorização (AP-11):
  OK   login devolve token assinado (sem fake-jwt-token)
  OK   cadastro público com role=admin vira role=user
Correções v1.3 (AP-10 defaults seguros, AP-03 senha mínima, AP-16 cor #RRGGBB):
  OK   CORS fechado por padrão (origem externa sem Access-Control-Allow-Origin)
Resultado: 55 OK, 0 FAIL
```

Nenhum dos três logs tem `Traceback` nem aviso de deprecated. Cada log termina com a auditoria de dependências (`pip-audit` / `npm audit`) sem vulnerabilidades conhecidas.

### Como a skill se comportou em stacks diferentes

- **Projeto 1 (monolito Python + SQL cru):** aplicou a estratégia de decomposição, separando dois arquivos "Deus" em seis camadas. O maior ganho foi em segurança: queries parametrizadas, hash de senha com migração dos dados existentes e remoção do endpoint de SQL arbitrário.
- **Projeto 2 (Node + callbacks):** a mesma skill, sem alterações, identificou Express e o padrão de callbacks, converteu para `async/await` e criou um helper `transaction()` sobre o sqlite3. Manteve os nomes ruins do payload (`usr`, `eml`, `c_id`), traduzindo-os só dentro do controller, para não quebrar clientes.
- **Projeto 3 (Flask já organizado):** reconheceu a "arquitetura em camadas só no nome" e usou a estratégia **incremental**: manteve `models/` e `routes/`, adicionou `controllers/`, `config/`, `middlewares/` e `views/`, e reaproveitou o código que existia mas não era usado. Também foi o único projeto com APIs deprecated de verdade, todas corrigidas.
- **Em comum:** em todos os projetos a skill respeitou a pausa da Fase 2, preservou o contrato (mesmo comando, porta, rotas e envelope de resposta) e reportou com honestidade o que não corrigiu.
- **AP-11 em stacks diferentes (v1.2):** o mesmo T16 gerou três soluções adequadas a cada projeto. P1 (SQL cru): token em `dados.token`, sem mudar as chaves de primeiro nível da resposta. P3 (ORM): o `token` substitui o `fake-jwt-token` na mesma chave e o papel passa a ser do servidor. P2 (Node, sem login): credencial de admin definida no servidor (`ADMIN_TOKEN`) e comparada em tempo constante.

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude --version`).
- Python 3.12+ (os testes foram feitos com 3.14) e Node.js 20+.
- `bash` e `curl` para os smoke tests (no Windows, o Git Bash serve).

### Executar a skill em cada projeto

A skill já está em `.claude/skills/refactor-arch/` de cada projeto. O argumento opcional indica onde salvar o relatório da Fase 2.

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch ../reports/audit-project-1.md"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch ../reports/audit-project-2.md"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch ../reports/audit-project-3.md"
```

Em cada projeto:
1. A skill imprime a **Fase 1** (stack e endpoints).
2. Imprime e salva a **Fase 2** (relatório) e pergunta `Proceed with refactoring (Phase 3)? [y/n]`.
3. Revise o relatório e responda `y` para refatorar, ou qualquer outra coisa para não alterar nada.
4. Ao final, a **Fase 3** imprime a nova estrutura, os findings tratados, as mudanças de contrato de segurança (incluindo a matriz de acesso do AP-11), as pendências e a validação.

> Para rodar a skill de novo sobre o código **original**, use o commit inicial (`git checkout 6d1ce62 -- <projeto>`), já que este repositório guarda a versão refatorada.

### Validar que a refatoração funcionou

Rode cada projeto e o seu smoke test. Os scripts repetem as requisições do baseline do código original (com o token do papel adequado, obtido via `POST /login`) e depois testam a autorização: 401 sem token, 403 sem papel e papel definido pelo servidor no cadastro.

```bash
# Projeto 1 (porta 5000) — banco é recriado no boot
cd code-smells-project
pip install -r requirements.txt
rm -f loja.db && python app.py &
bash ../scripts/smoke-project-1.sh          # esperado: 49 OK, 0 FAIL

# Projeto 2 (porta 3000) — banco em memória; reinicie o servidor entre execuções
cd ../ecommerce-api-legacy
npm install
export ADMIN_TOKEN=$(node -e "console.log(require('crypto').randomBytes(24).toString('hex'))")
npm start &
bash ../scripts/smoke-project-2.sh          # esperado: 22 OK, 0 FAIL (usa o mesmo ADMIN_TOKEN)

# Projeto 3 (porta 5000) — derrube o Projeto 1 antes
cd ../task-manager-api
pip install -r requirements.txt
python seed.py && python app.py &
bash ../scripts/smoke-project-3.sh          # esperado: 55 OK, 0 FAIL
```

As apps sobem em `127.0.0.1` (só local) e com CORS fechado por padrão. Use `HOST=0.0.0.0` para expor na rede e `CORS_ORIGINS=<origens>` para liberar um front-end de outra origem.

Para checar avisos de deprecated, suba com `python -W default app.py` ou `node --trace-deprecation src/app.js` e confirme que o log não tem `DeprecationWarning` nem `Traceback`. Segredos são opcionais em desenvolvimento: sem eles, a app gera uma chave aleatória e mostra um aviso. Em produção, configure as variáveis de ambiente listadas no `.env.example` de cada projeto.
