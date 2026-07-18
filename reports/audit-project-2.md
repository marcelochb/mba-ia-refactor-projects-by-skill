================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:1-7
Description: Objeto `config` contém senha de banco (`dbPass`), chave de gateway de
pagamento (`paymentGatewayKey: "pk_live_..."`) e usuário SMTP hardcoded.
Impact: Segredos de produção versionados; comprometimento total de pagamento e DB.
Recommendation: Ler de variáveis de ambiente via módulo de config — playbook #2.

### [CRITICAL] God Class (DB + rotas + negócio no mesmo lugar)
File: src/AppManager.js:1-141
Description: `AppManager` cria as tabelas, popula seeds, define todas as rotas e
executa a lógica de checkout/relatório/exclusão num único arquivo/classe.
Impact: Impossível testar em isolamento; qualquer mudança afeta todo o sistema.
Recommendation: Separar em config/DB, models, controllers, routes — playbook #3.

### [CRITICAL] Exposição de dados sensíveis (cartão e chave em log)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`
loga o número do cartão do cliente e a chave do gateway.
Impact: PII financeira e segredo vazados em logs (violação grave de segurança).
Recommendation: Remover o log; nunca registrar cartão/segredo — ver AP-13.

### [HIGH] Lógica de negócio e orquestração no controller/rota
File: src/AppManager.js:28-78
Description: A rota de checkout orquestra criação de usuário, "processamento" de
pagamento, matrícula, pagamento e log de auditoria diretamente no handler.
Impact: Borda HTTP vira dona da regra de negócio; não reutilizável nem testável.
Recommendation: Extrair um CheckoutService; controller fino — playbook #4.

### [HIGH] Write múltiplo sem transação atômica
File: src/AppManager.js:50-63
Description: Checkout insere enrollment, payment e audit_log em callbacks encadeados
sem transação; falha no meio deixa dados inconsistentes.
Impact: Matrícula sem pagamento (ou vice-versa) em caso de erro parcial.
Recommendation: Envolver em transação (BEGIN/COMMIT/ROLLBACK) — playbook #5.

### [HIGH] Criptografia caseira / fraca de senha
File: src/utils.js:17-23
Description: `badCrypto` monta uma string base64 repetida e trunca em 10 chars —
não é hashing seguro; senha default `"123456"` quando ausente.
Impact: Senhas trivialmente quebráveis; sem salt.
Recommendation: Usar bcrypt/argon2 — playbook #7.

### [HIGH] Estado global mutável
File: src/utils.js:9-15
Description: `globalCache = {}` e `totalRevenue` module-level mutáveis, alterados por
`logAndCache`. Estado compartilhado entre requisições.
Impact: Comportamento imprevisível, vazamento entre requisições, difícil de testar.
Recommendation: Encapsular em serviço com escopo próprio — playbook #6.

### [MEDIUM] N+1 Query + Callback Hell no relatório financeiro
File: src/AppManager.js:80-129
Description: Para cada curso, consulta matrículas; para cada matrícula, consulta
usuário e pagamento — callbacks aninhados 4 níveis com contadores manuais
(`coursesPending--`, `enrPending--`).
Impact: Explosão de queries e código frágil/ilegível.
Recommendation: JOIN/agregação numa query + async/await — playbooks #8 e #9.

### [MEDIUM] Exclusão sem integridade referencial (registros órfãos)
File: src/AppManager.js:131-137
Description: DELETE de usuário não remove matrículas/pagamentos associados; a própria
resposta admite "ficaram sujos no banco".
Impact: Dados órfãos e inconsistentes.
Recommendation: Excluir em cascata dentro de transação (ou bloquear se houver vínculo).

### [MEDIUM] Validação de input fraca
File: src/AppManager.js:29-35
Description: Só verifica presença de alguns campos; não valida formato de email,
formato de cartão, tipos. Regra de pagamento baseada em `card.startsWith("4")`.
Impact: Dados inválidos entram no fluxo de pagamento/persistência.
Recommendation: Validação na borda reutilizável — playbook #10.

### [LOW] Nomes ruins / variáveis de 1 letra
File: src/AppManager.js:29-33
Description: `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, curso e cartão.
Impact: Prejudica leitura e manutenção.
Recommendation: Nomes descritivos.

### [LOW] Magic strings de status
File: src/AppManager.js:46-48
Description: `"PAID"`/`"DENIED"` e regra `startsWith("4")` embutidos como literais.
Impact: Intenção obscura; difícil de evoluir.
Recommendation: Constantes nomeadas.

### [LOW] Import não utilizado / API verbose desnecessária
File: src/AppManager.js:1-2
Description: `sqlite3.verbose()` em produção e `totalRevenue` importado sem uso.
Impact: Ruído e overhead desnecessário.
Recommendation: Remover verbose e imports mortos.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
