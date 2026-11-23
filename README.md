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
| 3 — task-manager-api | Python 3 + Flask 3.0 + Flask-SQLAlchemy | 15 / ~1.158 | 3 | 3 | 7 | 3 | **16** |

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

1. **O `SKILL.md` diz o que fazer; as referências trazem o conhecimento.** O `SKILL.md` descreve o processo e as regras. Cada arquivo de referência só é lido na fase em que é necessário (tabela "quando ler"). Assim o contexto fica enxuto: o playbook de 796 linhas não é carregado durante a análise.
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
7. **Matriz de acesso explícita.** Para corrigir o AP-11 de forma igual em qualquer stack, o `mvc-guidelines.md` classifica cada endpoint do inventário em **público** (health, login, cadastro, catálogo, checkout), **autenticado — dono ou admin** (dados do próprio usuário, pedidos em nome próprio) e **admin** (listar/excluir usuários, alterar papel, relatórios, escrita no catálogo, `/admin/*`). O T16 traz o código concreto em Python (`itsdangerous` + decorators `login_required`/`admin_required`) e em Node (HMAC com `crypto` + middleware), inclusive o caso de projeto sem login: `ADMIN_TOKEN` quando só há rotas administrativas a proteger, ou login com papéis quando um fluxo público também usa um dado do cliente como identidade (foi o caso do P2).
8. **A Recommendation é um compromisso (regra 9, v1.3).** O que a Recommendation de um finding promete é exatamente o que a Fase 3 entrega, com os mesmos valores e defaults. Se uma parte depende de decisão humana, a própria Recommendation já diz `Pending: <motivo>` (só em MEDIUM/LOW). A Fase 3 termina com uma **reconciliação Fase 2 × Fase 3**: relê o relatório finding por finding e confere no código que cada Recommendation foi cumprida.

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
- **A prova:** a mesma pasta foi copiada sem nenhuma alteração para os 3 projetos (`diff -r` sem diferenças) e, na execução final, rodou **do zero** sobre o código original dos 3 projetos (Python/SQL cru, Node/callbacks e Python/ORM já organizado) produzindo o código e os relatórios que estão neste repositório.

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

#### Execução final: a skill rodando do zero nos 3 projetos

Os dois comentários do professor pediam "rode a skill de novo". Até a v1.3, as iterações eram aplicadas de forma incremental sobre o código já refatorado. Para a entrega final, rodei a skill **exatamente como o professor rodaria**: uma sessão nova e não interativa do Claude Code (`claude -p "/refactor-arch ../reports/audit-project-N.md"`), sem nenhum contexto anterior, sobre uma cópia do **código original** (commit inicial) de cada projeto, respondendo `y` à pergunta da Fase 2 só depois de conferir que nenhum arquivo tinha sido alterado.

Duas execuções de teste no Projeto 1 revelaram brechas de instrução que o código incremental não tinha, mas a skill sozinha produzia:

| Problema observado na execução do zero | Correção na skill |
|---|---|
| A skill manteve `POST /admin/query` "só para admin e só `SELECT`" em vez de removê-lo; confirmei que, por ele, um admin lia os hashes de senha de todos os usuários | **Catálogo (AP-05), `mvc-guidelines.md` e T16:** rota que executa SQL/código vindo do cliente é **removida** (404), nunca "restringida" |
| A skill trocou a senha de desenvolvimento do admin por uma senha aleatória **escrita no log** | **Catálogo (AP-04):** senha/token gerados e logados contam como exposição de dados. **T16 e `mvc-guidelines.md`:** preservar as credenciais de desenvolvimento do seed original (com hash); nunca gerar e logar segredo |

Com a skill corrigida, rodei os 3 projetos do zero (US$ 14,50 e 58 minutos no total). **O código, os relatórios e os READMEs dos projetos neste repositório são a saída real dessa execução**, e as transcrições completas (Fases 1, 2 e 3) estão em [`docs/logs/skill-run-project-1.md`](docs/logs/skill-run-project-1.md), [`-2`](docs/logs/skill-run-project-2.md) e [`-3`](docs/logs/skill-run-project-3.md). Em todos:
- A Fase 2 **parou** em `Proceed with refactoring (Phase 3)? [y/n]` sem alterar nenhum arquivo do projeto.
- A Fase 3 validou boot, endpoints, autorização e defaults seguros, e reconciliou cada finding com o código (26/26, 23/23, 20/20).
- Durante a reconciliação, a skill **corrigiu o próprio relatório** onde o texto não batia com o entregue (nomes de arquivo no P1; no P3, a Recommendation do #8 não cobria a lista em memória citada no Impact). Os relatórios em `reports/` são essa versão final; a versão impressa na Fase 2 está nas transcrições.

Depois, **conferi cada saída de forma independente** (ver "Checklist de validação" abaixo). Fiz à mão uma única correção em texto gerado: o relatório do P3 contava 23 endpoints, e o original tem 22 (conferido pela lista de rotas do Flask). Também deixei explícito no T16 o critério que a skill usou no P2 (login com papéis em vez de `ADMIN_TOKEN` quando o checkout usa o e-mail do cliente como identidade).

## C) Resultados

Tudo nesta seção vem da **execução final da skill do zero** (ver B) e da minha verificação independente sobre o código que ela produziu.

### Resumo das auditorias (Fase 2)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Análise manual | Relatório |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | 6 | 7 | 7 | 6 | **26** | 15 | [audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | 5 | 8 | 4 | 6 | **23** | 16 | [audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api | 3 | 4 | 8 | 5 | **20** | 16 | [audit-project-3.md](reports/audit-project-3.md) |

Em todos os projetos a skill encontrou **mais findings que a análise manual**, e todos os CRITICAL e HIGH da análise manual aparecem nos relatórios. O número é maior porque o catálogo é mais granular: por exemplo, "senha em texto puro" e "senha exposta na resposta" viram AP-03 e AP-04. As regras de calibração foram usadas com justificativa escrita: AP-16 subiu para HIGH no P2 (input sem validação derrubava o processo) e AP-13 desceu para MEDIUM no P3 (a classe de notificação nunca era usada).

### Critérios de aceite

| Critério | P1 | P2 | P3 |
|---|---|---|---|
| Fase 1 detecta a stack corretamente | ✅ Python + Flask 3.1.1, sqlite3 (SQL cru) | ✅ Node.js 20 + Express 4, sqlite3 em memória | ✅ Python + Flask 3.0 + Flask-SQLAlchemy, domínio **Task Manager API** |
| Fase 2 encontra ≥ 5 findings | ✅ 26 | ✅ 23 | ✅ 20 |
| Fase 2 tem ≥ 1 CRITICAL ou HIGH | ✅ 13 | ✅ 13 | ✅ 7 |
| Fase 3: a aplicação funciona após a refatoração | ✅ smoke 50/50 | ✅ smoke 25/25 | ✅ smoke 54/54 |
| AP-11 corrigido (sem pendência) | ✅ token assinado no login, matriz de acesso | ✅ `POST /api/login` com papéis, rotas admin protegidas, checkout exige a senha do dono do e-mail | ✅ token assinado no lugar do `fake-jwt-token`, papel definido pelo servidor |
| AP-10 com defaults seguros (sem pendência) | ✅ CORS fechado, bind `127.0.0.1`, debug off | ✅ CORS fechado, bind `127.0.0.1` | ✅ CORS fechado, bind `127.0.0.1`, debug off |
| Cada Recommendation entregue ou declarada `Pending` | ✅ 26/26 | ✅ 23/23 | ✅ 20/20 |

### Estrutura antes → depois

<table>
<tr><th>Projeto</th><th>Antes</th><th>Depois (saída da skill)</th></tr>
<tr><td><b>1</b><br>camadas só no nome → MVC</td><td>

```
app.py
controllers.py
models.py
database.py
```
</td><td>

```
app.py               # composition root (create_app)
database.py          # conexão por requisição (g)
errors.py            # exceções de domínio
config/              settings.py, constants.py
models/              produto, usuario, pedido, sistema,
                     seed.py, passwords.py
services/            produto, usuario, pedido, relatorio,
                     auth, notification
controllers/         produto, usuario, pedido, relatorio,
                     sistema, validators
routes/              produto, usuario, pedido, sistema (Blueprints)
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
src/database/        index.js (Promises, transaction()),
                     schema.js, seed.js
src/models/          user, course, enrollment, payment,
                     auditLog, report
src/services/        checkout, report, user, auth,
                     paymentGateway, cache
src/controllers/     checkout, report, user, auth
src/routes/          index.js (matriz de acesso)
src/middlewares/     errorHandler.js, auth.js, cors.js
src/utils/           logger, password (scrypt), token,
                     validators, errors
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
config/              settings.py                    (novo)
models/              task, user, category           (mantido)
services/            task, user, category, report,
                     auth, notification (injetável) (ampliado)
controllers/         task, user, category, report,
                     validators, serializers        (novo)
routes/              task, user, report, category   (mantido)
middlewares/         error_handler.py, auth.py      (novo)
utils/               helpers.py, errors.py          (reaproveitado)
```
</td></tr>
</table>

Os arquivos antigos totalmente substituídos (`controllers.py` e `models.py` do P1; `AppManager.js` e `utils.js` do P2) foram **removidos** pela skill. Não ficaram duas implementações da mesma regra.

### Checklist de validação preenchido

Cada item foi conferido por mim de forma independente sobre a saída da skill, além do resumo que ela própria imprimiu: li os relatórios, rodei os smoke tests e conferi os pontos de segurança.

| Item | P1 | P2 | P3 |
|---|---|---|---|
| **Fase 1 — Análise** | | | |
| Linguagem detectada corretamente | ✅ Python (3.14.5 no ambiente) | ✅ JavaScript (Node.js v20.19.5) | ✅ Python (3.14.5 no ambiente) |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4 (4.22.1 resolvido) | ✅ Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 |
| Domínio descrito corretamente | ✅ E-commerce (produtos, usuários, pedidos, relatório de vendas) | ✅ LMS com checkout (usuários, cursos, matrículas, pagamentos) | ✅ Task Manager API (tasks, usuários, categorias, relatórios) |
| Número de arquivos condiz com a realidade | ✅ 4 arquivos, ~780 linhas | ✅ 3 arquivos em `src/`, ~180 linhas | ✅ 15 arquivos `.py`, ~1.158 linhas |
| **Fase 2 — Auditoria** | | | |
| Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ 241 referências, todas válidas no código original | ✅ 141 referências válidas | ✅ 313 referências válidas |
| Findings ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 26 | ✅ 23 | ✅ 20 |
| Detecção de APIs deprecated (se aplicável) | ✅ nenhuma no código (Grep + `python -W default`); `pip-audit` achou `flask 3.1.1` e `flask-cors 5.0.1` vulneráveis (#18) | ✅ callbacks legados do sqlite3; `npm audit` (sqlite3 5 + transitivas do Express); `--trace-deprecation` limpo | ✅ `datetime.utcnow()`, `Query.get()` e `backref=` (confirmados em tempo de execução); `pip-audit`: 22 vulnerabilidades em 5 pacotes |
| Pausa e pede confirmação antes da Fase 3 | ✅ nenhum arquivo alterado antes do `y` | ✅ idem | ✅ idem |
| **Fase 3 — Refatoração** | | | |
| Estrutura de diretórios segue MVC | ✅ | ✅ | ✅ |
| Configuração em módulo próprio, sem valores fixos | ✅ `config/settings.py` + `.env.example` | ✅ `src/config/` + `.env.example` | ✅ `config/settings.py` + `.env.example` |
| Models abstraem os dados | ✅ `models/*_model.py` (SQL 100% parametrizado) | ✅ `src/models/*Model.js` | ✅ `models/` (consultas e agregações) |
| Views/Routes separadas | ✅ `routes/` (Blueprints por domínio) | ✅ `src/routes/index.js` | ✅ `routes/*` + `controllers/serializers.py` |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ `middlewares/error_handler.py` | ✅ `src/middlewares/errorHandler.js` | ✅ `middlewares/error_handler.py` |
| Entry point claro | ✅ `app.py` (`create_app`) | ✅ `src/app.js` (`npm start`) | ✅ `app.py` (`create_app`) |
| Aplicação inicia sem erros | ✅ `python app.py`, sem variáveis de ambiente | ✅ `npm start` (com `ADMIN_PASSWORD` para o login do admin) | ✅ `python seed.py && python app.py`, sem variáveis de ambiente |
| Endpoints originais respondem corretamente | ✅ 22/22 do baseline; 18 das 19 rotas originais mantidas (`/admin/query` removido de propósito) | ✅ 5/5 do baseline; as 3 rotas originais mantidas | ✅ 32/32 do baseline; as 22 rotas originais mantidas |
| Autenticação e autorização (AP-11) | ✅ 18/18 checagens | ✅ 12/12 | ✅ 17/17 |
| Defaults seguros e correções | ✅ 10/10 (CORS fechado, `/admin/query` 404, 404, soft delete) | ✅ 8/8 (CORS fechado, validação, 404, cascata) | ✅ 5/5 (CORS fechado, cor `#RRGGBB`) |
| Dependências sem vulnerabilidades conhecidas | ✅ `pip-audit`: nenhuma | ✅ `npm audit`: 0 | ✅ `pip-audit`: nenhuma |

**Verificações independentes feitas sobre a saída da skill:**
- **Smoke tests** ([`scripts/`](scripts/)): repetem as requisições do baseline do código original com o token do papel adequado e depois testam autorização, defaults seguros e as correções. O do P2 foi adaptado ao contrato que a skill entregou (login do admin em `POST /api/login`, em vez do `ADMIN_TOKEN` da versão anterior).
- **Boot sem nenhuma variável de ambiente:** bind em `127.0.0.1`, debug desligado e **nenhum** `Access-Control-Allow-Origin` para `Origin: http://evil.example`. Com `CORS_ORIGINS` definido, só a origem configurada é liberada (verificado pela skill).
- **Rotas:** comparei a lista de rotas do Flask (método + path) do original com a refatorada. No P1, só `POST /admin/query` sumiu (removido de propósito, AP-05); no P3, as 22 rotas são idênticas.
- **Referências dos relatórios:** as 695 referências `arquivo:linha` apontam para linhas existentes no código original; amostras conferidas linha a linha.
- **Segredos e logs:** nenhum segredo fixo no código; nenhum log com senha (no P2, a senha do admin vem de `ADMIN_PASSWORD` e não aparece no log); o cartão aparece mascarado (`**** 4444`).
- **Dependências:** instaladas do zero a partir dos manifestos gerados (venv novo / `npm ci`): `pip-audit` sem vulnerabilidades e `npm audit` com 0.

### Pendências (decisão humana)

A skill não aplica automaticamente mudanças que alteram regra de negócio. Só fica pendente o que a própria Recommendation do relatório declara como `Pending: <motivo>`, e nunca um CRITICAL/HIGH. AP-10 e AP-11 foram corrigidos nos 3 projetos. Ficaram para decisão humana:
- **P1 (#16):** devolver o estoque quando um pedido é cancelado e definir quais transições de status são permitidas. O comportamento original foi mantido.
- **P2:** nenhuma.
- **P3 (#8):** ligar notificações a eventos (ex.: e-mail ao atribuir uma task), um efeito que o código original nunca teve, e persistir o histórico de notificações, que exige uma tabela nova. O serviço está pronto e injetado.

### Logs das aplicações rodando após a refatoração

- **Transcrições completas da skill** (Fases 1, 2 e 3): [skill-run-project-1.md](docs/logs/skill-run-project-1.md), [skill-run-project-2.md](docs/logs/skill-run-project-2.md), [skill-run-project-3.md](docs/logs/skill-run-project-3.md).
- **Aplicações rodando + smoke test + auditoria de dependências:** [project-1-after.txt](docs/logs/project-1-after.txt), [project-2-after.txt](docs/logs/project-2-after.txt), [project-3-after.txt](docs/logs/project-3-after.txt).

Trechos:

```
$ rm -f loja.db && python -W default app.py        # Projeto 1, sem variáveis de ambiente
WARNING __main__: SECRET_KEY não definida; usando chave aleatória (tokens expiram a cada reinício).
 * Debug mode: off
 * Running on http://127.0.0.1:5000
$ bash scripts/smoke-project-1.sh
Defaults seguros e correções (AP-10, AP-05, AP-16 404, AP-20 soft delete):
  OK   POST /admin/query -> 404
  OK   CORS fechado por padrão (origem externa sem Access-Control-Allow-Origin)
  OK   histórico do pedido mantém o nome do produto excluído
Resultado: 50 OK, 0 FAIL

$ ADMIN_PASSWORD=<aleatória> npm start              # Projeto 2
[INFO] LMS API rodando em http://127.0.0.1:3000 (CORS: fechado)
[INFO] Processando pagamento de 497 com cartão **** 4444: PAID
$ ADMIN_PASSWORD=<a mesma> bash scripts/smoke-project-2.sh
  OK   GET /api/admin/financial-report -> 403
  OK   POST /api/checkout -> 401
  OK   exclusão em cascata: relatório sem alunos órfãos
Resultado: 25 OK, 0 FAIL

$ python seed.py && python -W default app.py        # Projeto 3, sem variáveis de ambiente
 * Debug mode: off
 * Running on http://127.0.0.1:5000
$ bash scripts/smoke-project-3.sh
  OK   login devolve token assinado (sem fake-jwt-token)
  OK   cadastro público com role=admin vira role=user
Resultado: 54 OK, 0 FAIL
```

Nenhum dos três logs tem `Traceback` nem aviso de deprecated, e cada um termina com a auditoria de dependências sem vulnerabilidades conhecidas.

### Como a skill se comportou em stacks diferentes

- **Projeto 1 (Python + SQL cru, camadas só no nome):** decompôs os arquivos "Deus" em config, models, services, controllers, routes e middlewares. Os maiores ganhos foram de segurança: queries 100% parametrizadas, hash de senha com migração automática de um banco antigo, remoção do endpoint de SQL arbitrário e token assinado com matriz de acesso.
- **Projeto 2 (Node + callbacks, God Class):** a mesma skill, sem alterações, identificou Express e o padrão de callbacks, converteu para `async/await` com um helper `transaction()`, manteve os nomes ruins do payload (`usr`, `eml`, `c_id`) traduzindo-os só no controller, e percebeu um problema que a análise manual não pegou: o checkout aceitava o e-mail de outra pessoa como identidade. Por isso criou login com papéis em vez de só proteger as rotas admin.
- **Projeto 3 (Flask já organizado):** reconheceu a "arquitetura em camadas só no nome" e aplicou a estratégia **incremental**: manteve `models/` e `routes/`, acrescentou `config/`, `controllers/` e `middlewares/`, e reaproveitou o código que existia mas não era usado. Foi o único com APIs deprecated de verdade (`utcnow`, `Query.get`, `backref`), todas corrigidas.
- **Em comum:** respeitou a pausa da Fase 2 sem tocar em nenhum arquivo, preservou o contrato (comando, porta, rotas, nomes de campos e envelope de resposta), aplicou os mesmos defaults seguros nas 3 stacks e corrigiu o próprio relatório quando a reconciliação encontrou divergência.
- **Ponto de atenção honesto:** o resumo da Fase 3 do P3 saiu em inglês, apesar da regra 8 (o relatório saiu em português); e cada execução do zero toma pequenas decisões diferentes (nomes de arquivo, onde fica o serializer). Por isso a validação final é sempre feita por testes e pela reconciliação, não pela comparação de texto.

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

> Para rodar a skill de novo sobre o código **original**, use o commit inicial (`git checkout 6d1ce62 -- <projeto>`), já que este repositório guarda a versão refatorada. Foi assim que a execução final foi feita: em uma cópia do original, com `claude -p` em uma sessão nova (transcrições em `docs/logs/skill-run-project-N.md`).

### Validar que a refatoração funcionou

Rode cada projeto e o seu smoke test. Os scripts repetem as requisições do baseline do código original (com o token do papel adequado, obtido pelo login de cada projeto) e depois testam a autorização (401 sem token, 403 sem papel, papel definido pelo servidor), os defaults seguros e as correções.

```bash
# Projeto 1 (porta 5000) — banco é recriado no boot
cd code-smells-project
pip install -r requirements.txt
rm -f loja.db && python app.py &
bash ../scripts/smoke-project-1.sh          # esperado: 50 OK, 0 FAIL

# Projeto 2 (porta 3000) — banco em memória; reinicie o servidor entre execuções
cd ../ecommerce-api-legacy
npm install
export ADMIN_PASSWORD=$(node -e "console.log(require('crypto').randomBytes(18).toString('hex'))")
npm start &
bash ../scripts/smoke-project-2.sh          # esperado: 25 OK, 0 FAIL (usa a mesma ADMIN_PASSWORD)

# Projeto 3 (porta 5000) — derrube o Projeto 1 antes
cd ../task-manager-api
pip install -r requirements.txt
python seed.py && python app.py &
bash ../scripts/smoke-project-3.sh          # esperado: 54 OK, 0 FAIL
```

As apps sobem em `127.0.0.1` (só local) e com CORS fechado por padrão. Use `HOST=0.0.0.0` para expor na rede e `CORS_ORIGINS=<origens>` para liberar um front-end de outra origem.

Para checar avisos de deprecated, suba com `python -W default app.py` ou `node --trace-deprecation src/app.js` e confirme que o log não tem `DeprecationWarning` nem `Traceback`. Segredos são opcionais em desenvolvimento: sem eles, a app gera uma chave aleatória e mostra um aviso. Em produção, configure as variáveis de ambiente listadas no `.env.example` de cada projeto.
