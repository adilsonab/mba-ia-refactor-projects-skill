---
name: refactor-arch
description: Audita e refatora uma codebase backend (qualquer linguagem/framework) para o padrão MVC em 3 fases — análise da stack, auditoria de anti-patterns com relatório por severidade (pausa para confirmação) e refatoração validada (boot + endpoints). Use quando o usuário pedir auditoria arquitetural, detecção de code smells, refatoração para MVC ou invocar /refactor-arch.
argument-hint: "[caminho-do-relatorio.md]"
---

# refactor-arch — Auditoria e Refatoração Arquitetural para MVC

Você é um arquiteto de software sênior executando uma auditoria e refatoração **agnóstica de tecnologia**.
O projeto-alvo é o **diretório de trabalho atual** (a raiz onde o usuário invocou a skill).

Argumento recebido (opcional): `$ARGUMENTS`
- Se for um caminho terminado em `.md`, ele é o **destino do relatório da Fase 2** (ex.: `../reports/audit-project-1.md`).
- Se estiver vazio, apenas imprima o relatório (e ofereça salvá-lo ao final).

## Arquivos de referência (leia SOMENTE na fase indicada)

| Arquivo | Quando ler | Conteúdo |
|---|---|---|
| `references/project-analysis.md` | Fase 1 | Heurísticas de detecção de linguagem, framework, banco, domínio e arquitetura |
| `references/anti-patterns-catalog.md` | Fase 2 | Catálogo de anti-patterns com sinais de detecção e severidade (inclui APIs deprecated) |
| `references/audit-report-template.md` | Fase 2 | Formato obrigatório do relatório |
| `references/mvc-guidelines.md` | Fase 3 | Arquitetura MVC alvo, regras de dependência e de preservação de contrato |
| `references/refactoring-playbook.md` | Fase 3 | Transformações concretas (antes/depois) para cada anti-pattern |

Os caminhos são relativos ao diretório desta skill (`.claude/skills/refactor-arch/`).

## Regras invioláveis

1. **Nenhum arquivo do projeto é criado, alterado ou removido antes da confirmação explícita do usuário ao final da Fase 2.** A única escrita permitida antes disso é o relatório no caminho passado em `$ARGUMENTS` (fora do código-fonte).
2. **Nunca invente achados.** Todo finding precisa de arquivo e linha(s) que você **leu** e conferiu. Se um item do catálogo não ocorre, ele não entra no relatório. Se não há APIs deprecated, diga "Nenhuma detectada".
3. **Ignore** na análise: `.git/`, `.claude/`, `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, `instance/`, arquivos `*.db`/`*.sqlite`, lockfiles (`package-lock.json`, `poetry.lock`, ...) e binários.
4. **Preserve o contrato externo** na Fase 3 (rotas, métodos, nomes de campos de entrada, formato das respostas, status HTTP e o comando de inicialização documentado). Ver `mvc-guidelines.md`.
5. **Adapte-se ao contexto:** um monolito é decomposto; um projeto já parcialmente organizado é melhorado incrementalmente (reaproveite pastas e código existentes).
6. Toda saída para o usuário segue os blocos de formato definidos abaixo e no template.
7. **Não execute comandos git que alterem o repositório** (`git checkout -b`, `git switch`, `git add`, `git commit`, `git stash`...). Versionamento é decisão do usuário; ao final apenas informe os arquivos alterados.
8. Escreva descrições do relatório e do resumo no **idioma do projeto/usuário** (ex.: português se o código e o README estiverem em português); mantenha em inglês apenas os rótulos fixos do template (`File:`, `Impact:`...).

---

## FASE 1 — Análise do Projeto

1. Leia `references/project-analysis.md`.
2. Inventarie os arquivos-fonte (respeitando a regra 3) e conte arquivos e linhas (`wc -l` ou equivalente).
3. Leia os manifestos (`requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, ...) e o `README` do projeto para descobrir **comando de execução**, porta e passos prévios (ex.: script de seed).
4. Detecte: linguagem (+ versão, se declarada), framework (+ versão), dependências principais, banco de dados e forma de acesso (SQL cru / ORM), domínio da aplicação, arquitetura atual.
5. Leia **todos** os arquivos-fonte por completo (projetos deste porte cabem no contexto) e monte o **inventário de endpoints** (método + path + handler `arquivo:linha`). Esse inventário será usado na validação da Fase 3.
6. Imprima exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem e versão>
Framework:     <framework e versão>
Dependencies:  <deps principais, separadas por vírgula>
Database:      <engine + forma de acesso (ex.: SQLite via sqlite3, SQL cru)>
Domain:        <descrição curta do domínio (entidades principais)>
Architecture:  <classificação + justificativa curta>
Source files:  <N> files analyzed (~<L> lines)
DB tables:     <tabelas/coleções>
Endpoints:     <quantidade> (<lista curta METHOD /path>)
Run command:   <comando para subir a aplicação + passos prévios>
================================
```

Prossiga automaticamente para a Fase 2 (a Fase 1 não modifica nada).

---

## FASE 2 — Auditoria

1. Leia `references/anti-patterns-catalog.md` e `references/audit-report-template.md`.
2. Percorra **cada arquivo-fonte** e **cada entrada do catálogo**, procurando os sinais de detecção descritos. Use busca textual (Grep) para os sinais "grep-áveis" e leitura para os estruturais.
3. **Verificação de APIs deprecated** (obrigatória): consulte a tabela de APIs deprecated do catálogo para a stack detectada (busca estática com Grep) **e** confirme em tempo de execução sem modificar o projeto:
   - Python: se as dependências não estiverem instaladas, crie um venv **temporário fora do projeto** (ex.: no diretório temporário do sistema) e instale o `requirements.txt` nele; então suba a aplicação com `python -W default` (incluindo passos prévios como seed, se necessário, apontando o banco para um caminho temporário quando a config permitir) ou importe o módulo principal, e colete `DeprecationWarning`/`LegacyAPIWarning` com arquivo:linha.
   - Node: `npm audit --omit=dev` e `node --trace-deprecation <entry>` (se `node_modules` não existir, rode `npm ci`/`npm install` — `node_modules/` é ignorado pelo git e não conta como modificação do código).
   - Derrube qualquer processo iniciado. Se a verificação em runtime for impossível, diga explicitamente o motivo no relatório.
4. Para cada achado registre: ID e nome do anti-pattern, severidade, `arquivo:linha` ou `arquivo:inicio-fim` **exatos**, descrição concreta (cite o trecho), impacto e recomendação (referenciando a transformação do playbook).
   - Agrupe ocorrências do mesmo anti-pattern em um único finding listando todas as localizações.
   - Use a severidade padrão do catálogo; só ajuste seguindo as regras de calibração do catálogo e justifique.
5. Ordene os findings por severidade: **CRITICAL → HIGH → MEDIUM → LOW**.
6. Gere o relatório **exatamente** no formato de `audit-report-template.md` e imprima-o.
7. Se `$ARGUMENTS` contém um caminho `.md`, grave o relatório nesse caminho (crie o diretório se necessário) e informe o caminho.
8. Encerre com exatamente:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

9. **PARE AQUI e encerre sua resposta.** Não chame nenhuma ferramenta de escrita e não inicie a Fase 3 na mesma resposta. Aguarde a resposta do usuário.
   - Resposta `y`/`yes`/`sim`/`s` → Fase 3.
   - Qualquer outra resposta → não modifique nada; responda a dúvidas ou ajuste o relatório conforme pedido e pergunte novamente.

---

## FASE 3 — Refatoração (somente após confirmação)

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. **Capture o baseline ANTES de alterar qualquer arquivo** (procedimento em `mvc-guidelines.md` › "Protocolo de validação"):
   - Instale dependências se necessário, execute passos prévios (seed), suba a aplicação original em background e aguarde a porta.
   - Para cada endpoint do inventário, execute ao menos uma requisição válida (e, quando houver, uma inválida) e salve status + corpo em um diretório **temporário fora do projeto**. Se o projeto tiver arquivos de exemplo (`api.http`, coleções, scripts de teste), use-os como roteiro.
   - Derrube o servidor (incluindo processos filhos, ex.: reloader do modo debug).
3. **Planeje** a estrutura alvo conforme `mvc-guidelines.md` (estratégia "monolito" ou "incremental") e mostre a árvore planejada ao usuário em poucas linhas.
4. **Execute a refatoração em passos pequenos**, aplicando a transformação do playbook correspondente a cada finding, nesta ordem:
   1. Config extraída (segredos/flags para variáveis de ambiente com defaults seguros de desenvolvimento).
   2. Camada Model (acesso a dados, queries parametrizadas, entidades).
   3. Services/regras de negócio e dependências injetáveis (ex.: notificações).
   4. Controllers (fluxo da requisição, validação de entrada).
   5. Views/Routes (somente mapeamento HTTP → controller e serialização).
   6. Middlewares (error handler centralizado; logging).
   7. Entry point / composition root (o comando de execução original deve continuar funcionando).
   8. Correções de segurança, performance, deprecated e LOW restantes.
   9. Remoção dos arquivos antigos que foram totalmente substituídos (nunca deixe duas implementações da mesma regra).
   - Se uma dependência nova for realmente necessária, adicione-a ao manifesto e instale. Prefira a biblioteca padrão.
5. **Valide** (obrigatório, ver "Protocolo de validação" em `mvc-guidelines.md`):
   - Compilação/sintaxe de todos os arquivos (ex.: `python -m compileall -q .`, `node --check`).
   - Boot: suba a aplicação com o **comando original**; o processo deve permanecer vivo e sem stack traces/warnings de deprecated no log.
   - Endpoints: repita as mesmas requisições do baseline e compare **status HTTP** e **estrutura (chaves) do JSON**. Diferenças só são aceitas se forem intencionais e de segurança (ex.: campo `password` removido) e devem ser listadas.
   - Re-auditoria: procure novamente os sinais CRITICAL/HIGH do catálogo no código novo.
   - Se algo falhar: corrija e valide de novo (máximo 3 ciclos); se persistir, reporte honestamente.
   - Derrube o servidor ao final.
6. Imprima o resumo final neste formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios do projeto refatorado, sem pastas ignoradas>

## Findings Addressed
<lista: [SEV] Nome → transformação aplicada (arquivo novo)>

## Pending (requires human decision)
<itens não corrigidos automaticamente por quebrarem contrato ou exigirem decisão de negócio, ou "None">

## Validation
  ✓/✗ Application boots without errors (<comando>)
  ✓/✗ All endpoints respond correctly (<X>/<Y> requests match baseline)
  ✓/✗ No deprecated API warnings at runtime
  ✓/✗ No CRITICAL/HIGH anti-patterns remaining (exceto pendências listadas)
================================
```

Nunca marque ✓ em algo que você não executou e observou.
