# Template do Relatório de Auditoria (Fase 2)

Gere o relatório **exatamente** com a estrutura abaixo (Markdown). Substitua os `<placeholders>`. Não remova seções; se uma estiver vazia, escreva "None".

## Regras de preenchimento

1. **Ordenação:** todos os CRITICAL, depois HIGH, MEDIUM e LOW. Dentro da mesma severidade, ordene pelo ID do catálogo.
2. **Localização exata:** `File:` sempre no formato `caminho/relativo.ext:linha` ou `caminho/relativo.ext:inicio-fim`. Múltiplas ocorrências: separe por vírgula; se forem muitas (> 8), liste as 8 mais relevantes e acrescente "(+N ocorrências: ...)" com as linhas restantes.
3. **Descrição concreta:** cite o trecho ou o valor problemático (ex.: "`SECRET_KEY` = `'minha-chave-...'`"). Nada genérico como "código ruim".
4. **Impact:** consequência real para segurança, manutenção, testes ou performance.
5. **Recommendation:** ação concreta + referência à transformação do playbook (`→ T0X`).
6. **Contagem:** o `Summary` e o `Total` devem bater com o número de findings listados.
7. Numere os findings sequencialmente (`#1`, `#2`, ...) para que possam ser referenciados na Fase 3.

## Template

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta do projeto>
Stack:   <Linguagem + Framework (versão)>
Files:   <N> analyzed | ~<L> lines of code
Date:    <AAAA-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| 1 | CRITICAL | <AP-XX Nome> | <arquivo:linha> |
| ... | ... | ... | ... |

## Findings

### #1 [CRITICAL] <AP-XX — Nome do anti-pattern>
File: <arquivo:linha[, arquivo:linha]>
Description: <o que foi encontrado, citando o trecho>
Impact: <consequência>
Recommendation: <ação concreta> (→ T0X)

### #2 [HIGH] <AP-XX — Nome>
File: ...
Description: ...
Impact: ...
Recommendation: ...

<... demais findings, em ordem de severidade ...>

## Deprecated APIs
| API | Location | Modern replacement | Evidence |
|---|---|---|---|
| <API obsoleta> | <arquivo:linha, ...> | <substituto> | <ex.: DeprecationWarning em runtime / changelog / npm audit> |

<ou "None detected" se não houver>

## Architecture Notes
- Current architecture: <classificação da Fase 1 + evidência>
- Refactoring strategy: <"monolith decomposition" ou "incremental layering"> — <por quê>
- Contract constraints: <campos/rotas que devem ser preservados, ex.: payload `usr`, `eml`>

================================
Total: <N> findings
================================
```

## Exemplo de finding bem escrito

```markdown
### #1 [CRITICAL] AP-01 — SQL Injection
File: models.py:28, models.py:47-50, models.py:109-111
Description: Queries montadas por concatenação de strings com dados do request, ex.: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`.
Impact: Login pode ser burlado com `email = "admin@loja.com' --"`; permite ler, alterar e apagar qualquer tabela.
Recommendation: Usar queries parametrizadas (`?` + tupla de parâmetros) em todo o acesso a dados, concentrado na camada Model (→ T01).
```
