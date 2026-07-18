---
name: refactor-arch
description: Use ao auditar e refatorar uma codebase de backend para o padrão MVC. Detecta linguagem, framework e arquitetura; identifica anti-patterns e code smells com arquivo:linha e severidade; gera relatório de auditoria; e reestrutura em Models/Views(Routes)/Controllers validando que a aplicação segue funcionando. Agnóstica de stack (Python/Flask, Node/Express e outras). Não use para tarefas de frontend/UI nem para perguntas conceituais sem refatorar código.
---

# refactor-arch — Refatoração Arquitetural para MVC

Skill de 3 fases que audita e refatora um projeto de backend para o padrão MVC,
independente da linguagem ou framework. Cada fase é sequencial: analisar →
auditar (com confirmação humana) → refatorar (com validação).

## Princípios

- **Agnóstica de tecnologia.** Raciocine por conceito, não por sintaxe. Detecte a
  stack primeiro; só então escolha o dialeto concreto das transformações.
- **Evidência exata.** Todo achado tem `arquivo:linha` e severidade. "Código ruim"
  não é achado; "query SQL concatenando input em `models.py:28`" é.
- **Humano no comando.** A Fase 3 nunca começa sem confirmação explícita na Fase 2.
- **Fail secure e sem regressão.** A refatoração preserva os endpoints originais e
  não pode deixar a aplicação sem bootar.
- **Adapte a profundidade ao contexto.** Um monolito num arquivo exige transformação
  diferente de um projeto que já tem camadas parciais.

## Fases

### Fase 1 — Análise

Detecte stack e mapeie a arquitetura atual. Consulte
`references/project-analysis.md` para as heurísticas de detecção (manifests,
extensões, imports, sinais de banco de dados e mapeamento de arquitetura).

Imprima um resumo no formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <libs relevantes>
Domain:        <domínio da aplicação>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas detectadas>
================================
```

### Fase 2 — Auditoria

Cruze o código contra `references/anti-patterns-catalog.md` (≥8 anti-patterns com
sinais de detecção e severidade, incluindo APIs deprecated). Gere o relatório
seguindo `references/audit-report-template.md`: findings ordenados de CRITICAL a
LOW, cada um com arquivo, linhas, descrição, impacto e recomendação.

Ao final, **PARE e peça confirmação** antes de modificar qualquer arquivo:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Só avance para a Fase 3 com um `y` explícito.

### Fase 3 — Refatoração

Reestruture o projeto para MVC seguindo `references/mvc-architecture.md`
(responsabilidades de cada camada) e aplique as transformações concretas de
`references/refactoring-playbook.md` (≥8 padrões antes/depois por stack).

Depois de refatorar, **valide**:

1. A aplicação inicia sem erros (boot).
2. Os endpoints originais continuam respondendo.

Imprima o resumo final com a nova estrutura de diretórios e o resultado da
validação:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios MVC>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Referências

Leia sob demanda, conforme a fase:

- `references/project-analysis.md` — detecção de stack e mapeamento (Fase 1)
- `references/anti-patterns-catalog.md` — catálogo de anti-patterns (Fase 2)
- `references/audit-report-template.md` — formato do relatório (Fase 2)
- `references/mvc-architecture.md` — regras do MVC alvo (Fase 3)
- `references/refactoring-playbook.md` — transformações antes/depois (Fase 3)
