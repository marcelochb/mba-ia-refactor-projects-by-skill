# Template do Relatório de Auditoria (Fase 2)

Formato padronizado do relatório impresso ao final da Fase 2 e salvo em
`reports/audit-project-N.md`. Findings **ordenados de CRITICAL a LOW**. Cada finding
tem título, `arquivo:linha(s)`, descrição, impacto e recomendação.

## Formato

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo>
Description: <o que foi encontrado, concreto>
Impact: <consequência de negócio/segurança/manutenção>
Recommendation: <transformação proposta — referencie o padrão do playbook>

### [CRITICAL] <...>
...

### [HIGH] <...>
...

### [MEDIUM] <...>
...

### [LOW] <...>
...

================================
Total: <n> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras

- **Ordenação:** todos os CRITICAL primeiro, depois HIGH, MEDIUM e LOW.
- **Localização exata:** sempre `arquivo:linha`. Se o problema é um bloco, use
  intervalo (`models.py:133-169`).
- **Uma linha de impacto** por finding, focada em consequência real (dado vazado,
  inconsistência, impossibilidade de testar), não em jargão.
- **Recomendação acionável:** aponte a transformação concreta (ex.: "query
  parametrizada — playbook #1").
- **Confirmação obrigatória:** o relatório termina SEMPRE com o prompt `[y/n]` e a
  Fase 3 só inicia com `y`.
- **Persistência:** o mesmo conteúdo é salvo em `reports/audit-project-N.md`.
