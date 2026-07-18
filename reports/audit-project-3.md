================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask (Flask-SQLAlchemy)
Files:   13 analyzed | ~1158 lines of code

## Summary
CRITICAL: 1 | HIGH: 3 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Criptografia fraca de senha (MD5) + exposição do hash
File: models/user.py:27-32, models/user.py:16-25
Description: `set_password`/`check_password` usam `hashlib.md5`; além disso `to_dict()`
inclui o campo `password`, então o hash MD5 vaza em `/users`, `/users/<id>`, `/login`
e nas respostas de criação/atualização.
Impact: Senhas quebráveis (MD5 sem salt) e hash exposto publicamente — falha grave.
Recommendation: Trocar por `werkzeug.security` (pbkdf2/scrypt) e remover `password`
da serialização — playbook #7 e AP-13.

### [HIGH] Configuração e secret hardcoded no entry point
File: app.py:11-13
Description: `SECRET_KEY = 'super-secret-key-123'` e a URI do banco hardcoded no
`app.py`; sem uso de variáveis de ambiente (apesar de `python-dotenv` estar nas deps).
Impact: Segredo versionado; impossível variar config por ambiente.
Recommendation: Módulo de config lendo env vars — playbook #2.

### [HIGH] Lógica de negócio dentro das rotas (controllers ausentes)
File: routes/task_routes.py:11-63, 85-154, routes/report_routes.py:12-101
Description: As rotas montam serialização, calculam `overdue`, orquestram validações e
regras diretamente; não há camada de controller nem uso da camada `services/`.
Impact: Camada de rota faz papel de controller+service; difícil testar e reutilizar.
Recommendation: Introduzir controllers finos + services; rota só roteia — playbook #4.

### [HIGH] Autenticação simulada / token falso
File: routes/user_routes.py:185-211
Description: O `/login` retorna `'token': 'fake-jwt-token-' + str(user.id)` — token
previsível e não assinado; qualquer um forja o token de qualquer usuário.
Impact: Controle de acesso inexistente; escalonamento trivial.
Recommendation: Emitir JWT assinado (com expiração) ou marcar claramente como não-auth.
(Correção mínima: parar de expor credenciais no payload de login.)

### [MEDIUM] N+1 Query na listagem de tasks e em relatórios
File: routes/task_routes.py:41-57, routes/report_routes.py:53-68
Description: Para cada task, faz `User.query.get` e `Category.query.get`; no relatório,
para cada usuário roda uma query de tasks separada.
Impact: Explosão de consultas conforme o volume cresce.
Recommendation: Eager load / JOIN — playbook #8.

### [MEDIUM] Cálculo de `overdue` duplicado
File: models/task.py:50-60, routes/task_routes.py:30-39, 71-80, routes/user_routes.py:171-180, routes/report_routes.py:34-43
Description: A mesma lógica de "atrasada" é reescrita à mão em 5 lugares, apesar de
existir `Task.is_overdue()` no model.
Impact: Correção precisa ser replicada; risco de divergência.
Recommendation: Reutilizar `Task.is_overdue()` em todos os pontos — playbook #12.

### [MEDIUM] API deprecated (SQLAlchemy 2.x / datetime)
File: models/user.py:14, models/task.py:15-16, routes/task_routes.py:42,51 (e outros)
Description: Uso de `Model.query.get(id)` (legacy no SQLAlchemy 2.x) e
`datetime.utcnow()` (deprecado no Python 3.12).
Impact: Warnings e quebra em versões futuras.
Recommendation: `db.session.get(Model, id)` e `datetime.now(datetime.UTC)` — playbook #11.

### [MEDIUM] Validação de input espalhada e duplicada
File: routes/task_routes.py:85-144 vs. utils/helpers.py:57-108
Description: Validação repetida inline nas rotas de task (create/update) enquanto
`utils/helpers.process_task_data` faz quase o mesmo, mas não é usado.
Impact: Duplicação e inconsistência entre create e update.
Recommendation: Centralizar validação reutilizável — playbook #10.

### [LOW] Except genérico engolindo erros
File: routes/task_routes.py:62-63, routes/user_routes.py:130-132, routes/report_routes.py:186-188
Description: `except:` sem tipo, retornando "Erro interno" e escondendo a causa real.
Impact: Depuração difícil; erros silenciados.
Recommendation: Capturar exceções específicas e centralizar tratamento.

### [LOW] Logs via print
File: routes/task_routes.py:149,219, routes/user_routes.py:83,89,147
Description: `print(...)` para logging de ações e erros.
Impact: Sem níveis, polui stdout, não configurável.
Recommendation: Módulo de logging.

### [LOW] Imports não utilizados
File: app.py:7 (os, sys, json), routes/task_routes.py:7 (json, os, sys, time), utils/helpers.py:3-7
Description: Vários imports que não são usados.
Impact: Ruído e confusão sobre dependências reais.
Recommendation: Remover imports mortos.

### [LOW] Método booleano verboso
File: models/user.py:34-38, models/task.py:38-48
Description: `is_admin`/`validate_status`/`validate_priority` usam if/else para
retornar True/False onde a expressão já é booleana.
Impact: Verbosidade desnecessária.
Recommendation: Retornar a expressão diretamente.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
