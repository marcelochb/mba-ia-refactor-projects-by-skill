================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] SQL Injection (concatenação de input em query)
File: models.py:28, 48-49, 58-60, 68, 92, 109-110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 224, 280, 289-297
Description: Praticamente todas as queries concatenam valores diretamente na string
SQL (`"... WHERE id = " + str(id)`, INSERT/UPDATE montados com `+`, busca com
`LIKE '%" + termo + "%'`). O login em `models.py:109-110` concatena email e senha.
Impact: Permite ler, alterar ou apagar qualquer dado do banco e burlar o login.
Recommendation: Queries parametrizadas com placeholders `?` — playbook #1.

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7, controllers.py:289
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` no código; o health check
ainda devolve a secret_key na resposta HTTP.
Impact: Segredo versionado e exposto; impossível rotacionar sem redeploy.
Recommendation: Ler de variável de ambiente via módulo de config — playbook #2.

### [CRITICAL] God Module (múltiplos domínios sem camadas)
File: models.py:1-314, controllers.py:1-292
Description: `models.py` concentra acesso a dados, regra de negócio (cálculo de
total de pedido, desconto de relatório) e formatação para 4 domínios. `controllers.py`
mistura validação, negócio e efeitos colaterais.
Impact: Impossível testar em isolamento; qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio — playbook #3.

### [CRITICAL] Arbitrary SQL / Endpoint destrutivo sem proteção
File: app.py:47-57 (/admin/reset-db), app.py:59-78 (/admin/query)
Description: `/admin/query` executa qualquer SQL recebido no body; `/admin/reset-db`
apaga todas as tabelas. Ambos sem autenticação.
Impact: Execução arbitrária de SQL e destruição total dos dados por qualquer cliente.
Recommendation: Remover os endpoints (ou substituir por operações específicas e
protegidas).

### [HIGH] Lógica de negócio e efeitos colaterais no controller
File: controllers.py:188-220 (criar_pedido), controllers.py:237-255
Description: O controller de pedido dispara "notificações" (email/SMS/push) via
`print` e concentra fluxo que deveria estar em service/model.
Impact: Borda HTTP vira dona da regra; não reutilizável nem testável.
Recommendation: Controller fino delegando a service/model — playbook #4.

### [HIGH] Write múltiplo sem transação atômica
File: models.py:133-169 (criar_pedido)
Description: Cria pedido, insere itens e dá baixa de estoque em INSERTs/UPDATEs
sequenciais com um único commit ao final, sem transação explícita; um erro no meio
deixa dados inconsistentes.
Impact: Pedido/itens/estoque podem ficar dessincronizados.
Recommendation: Envolver em transação atômica — playbook #5.

### [HIGH] Estado global mutável (conexão singleton)
File: database.py:4-10
Description: Conexão de banco mantida em variável global `db_connection` compartilhada
entre requisições (`check_same_thread=False`).
Impact: Estado compartilhado imprevisível, difícil de testar e propenso a corrida.
Recommendation: Encapsular acesso a dados / conexão por escopo — playbook #6.

### [MEDIUM] N+1 Query
File: models.py:187-199, 219-231
Description: Ao montar pedidos, para cada pedido roda uma query de itens e, para cada
item, outra query buscando o nome do produto.
Impact: Explosão de consultas conforme cresce o volume.
Recommendation: JOIN / query única — playbook #8.

### [MEDIUM] Validação de input espalhada e ausente
File: controllers.py:24-58, 146-165, 188-201
Description: Validações repetidas com `if not ...` dentro de cada handler, sem camada
reutilizável; alguns campos entram sem validação de tipo.
Impact: Duplicação e risco de dados inválidos chegarem ao core.
Recommendation: Validação na borda reutilizável — playbook #10.

### [MEDIUM] Exposição de dados sensíveis
File: models.py:83, 99 (senha em to-dict de usuário), controllers.py:289
Description: Listagem/detalhe de usuário retorna a senha; health check devolve
secret_key, debug e ambiente.
Impact: Vaza credencial e configuração sensível na resposta.
Recommendation: Nunca serializar senha/segredo; remover do output.

### [LOW] Magic numbers / strings
File: models.py:257-262 (faixas de desconto 10000/5000/1000), controllers.py:52
Description: Limiares e listas de categorias válidas embutidos como literais.
Impact: Intenção obscura; mudança propensa a erro.
Recommendation: Constantes nomeadas.

### [LOW] Notificações via print
File: controllers.py:208-210, 248-250, e prints de log espalhados
Description: "Envio" de email/SMS/push e logs feitos com `print`.
Impact: Não é logging real; polui stdout; sem níveis.
Recommendation: Logging apropriado / remover efeitos falsos.

### [LOW] Código de serialização duplicado
File: models.py:12-21, 31-40, 79-86, 95-102, 304-313
Description: O mesmo dicionário de produto/usuário é remontado à mão em várias funções.
Impact: Correção precisa ser replicada em vários pontos.
Recommendation: Método de serialização único por entidade — playbook #12.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
