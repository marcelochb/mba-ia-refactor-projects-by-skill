# Skill `refactor-arch` — Refatoração Arquitetural Automatizada

Skill agnóstica de tecnologia que audita e refatora uma codebase de backend para o
padrão **MVC**, em três fases sequenciais: **análise → auditoria (com confirmação) →
refatoração (com validação)**. Foi construída e executada em três projetos legados de
stacks diferentes (2× Python/Flask e 1× Node/Express).

- Skill: `<projeto>/.claude/skills/refactor-arch/`
- Relatórios de auditoria: `reports/audit-project-{1,2,3}.md`
- Código refatorado: commitado em cada projeto

---

## A) Análise Manual

Antes de construir a skill, os três projetos foram lidos manualmente para entender os
problemas que ela precisaria detectar. Abaixo, os achados de maior impacto por projeto,
classificados por severidade. Os relatórios completos gerados pela skill estão em
`reports/`.

### Projeto 1 — `code-smells-project` (Python/Flask, E-commerce)

| # | Problema | Severidade | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | SQL Injection (concatenação de input em query) | CRITICAL | `models.py` (várias linhas, ex.: 28, 109-110) | Todas as queries concatenam valores; o login concatena email/senha — permite ler/alterar dados e burlar autenticação. |
| 2 | Credenciais/segredos hardcoded | CRITICAL | `app.py:7`; `controllers.py:289` | `SECRET_KEY` no código e devolvida no `/health`; segredo versionado e exposto. |
| 3 | God Module (multi-domínio sem camadas) | CRITICAL | `models.py:1-314`, `controllers.py:1-292` | Dados + negócio + formatação juntos; impossível testar isolado. |
| 4 | Endpoint de SQL arbitrário / reset destrutivo | CRITICAL | `app.py:47-78` | `/admin/query` executa SQL do body; `/admin/reset-db` apaga tudo — sem auth. |
| 5 | Write múltiplo sem transação | HIGH | `models.py:133-169` | Criação de pedido + itens + baixa de estoque sem atomicidade. |
| 6 | Exposição de dados sensíveis | MEDIUM | `models.py:83,99`; `controllers.py:289` | Senha do usuário e secret_key retornadas nas respostas. |
| 7 | N+1 Query | MEDIUM | `models.py:187-231` | Query por pedido e por item ao montar a listagem. |
| 8 | Magic numbers / notificações via print | LOW | `models.py:257-262`; `controllers.py:208-210` | Faixas de desconto soltas; "envio" de email/SMS via `print`. |

### Projeto 2 — `ecommerce-api-legacy` (Node/Express, LMS com checkout)

| # | Problema | Severidade | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | Segredos hardcoded (chave de gateway, senhas) | CRITICAL | `src/utils.js:1-7` | `paymentGatewayKey: "pk_live_..."`, senha de DB e SMTP no código. |
| 2 | God Class | CRITICAL | `src/AppManager.js:1-141` | Uma classe faz DB, rotas e todo o negócio. |
| 3 | Cartão e chave logados no console | CRITICAL | `src/AppManager.js:45` | `console.log` do número do cartão do cliente e da chave do gateway. |
| 4 | Negócio/orquestração na rota + sem transação | HIGH | `src/AppManager.js:28-78` | Checkout orquestra usuário/pagamento/matrícula em callbacks sem atomicidade. |
| 5 | Criptografia caseira de senha | HIGH | `src/utils.js:17-23` | `badCrypto` (base64 repetido, truncado) — não é hash seguro. |
| 6 | Estado global mutável | HIGH | `src/utils.js:9-15` | `globalCache`/`totalRevenue` compartilhados entre requisições. |
| 7 | N+1 + callback hell no relatório | MEDIUM | `src/AppManager.js:80-129` | Consultas aninhadas por curso/matrícula/usuário com contadores manuais. |
| 8 | Delete sem integridade (órfãos) / nomes ruins | MEDIUM / LOW | `src/AppManager.js:131-137`, `:29-33` | Exclusão deixa matrículas/pagamentos órfãos; variáveis `u`, `e`, `cc`. |

### Projeto 3 — `task-manager-api` (Python/Flask, Task Manager, parcialmente organizado)

| # | Problema | Severidade | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | MD5 na senha + hash exposto | CRITICAL | `models/user.py:16-32` | MD5 sem salt e `to_dict()` inclui `password` — vaza em `/users` e `/login`. |
| 2 | Config/secret hardcoded | HIGH | `app.py:11-13` | `SECRET_KEY` e URI no código, apesar de `python-dotenv` nas deps. |
| 3 | Negócio dentro das rotas (sem controllers) | HIGH | `routes/*.py` | Rotas montam serialização e regra; camada `services/` sequer usada. |
| 4 | N+1 na listagem/relatórios | MEDIUM | `routes/task_routes.py:41-57`; `report_routes.py:53-68` | `User.query.get`/`Category.query.get` por task. |
| 5 | Cálculo de `overdue` duplicado | MEDIUM | 5 locais (models + 4 rotas) | Mesma lógica reescrita, apesar de existir `Task.is_overdue()`. |
| 6 | APIs deprecated | MEDIUM | `models/*.py`, `routes/*.py` | `Model.query.get` (legacy) e `datetime.utcnow()` (deprecado no 3.12). |
| 7 | `except:` genérico / logs via print | LOW | `routes/*.py` | Erros silenciados; logging via `print`. |
| 8 | Imports mortos / booleanos verbosos | LOW | `app.py:7`, `models/user.py:34-38` | `os, sys, json` sem uso; `if/else` retornando True/False. |

---

## B) Construção da Skill

### Decisões de design

O `SKILL.md` é **leve**: contém só a `description` (gatilho semântico), o escopo de
uso, os princípios e o índice das 3 fases. Todo o conhecimento pesado fica em
**arquivos de referência carregados sob demanda** (lazy), um por área:

```
.claude/skills/refactor-arch/
├── SKILL.md
└── references/
    ├── project-analysis.md        # heurísticas de detecção de stack e mapeamento
    ├── anti-patterns-catalog.md   # catálogo (16 anti-patterns) + APIs deprecated
    ├── audit-report-template.md   # formato do relatório da Fase 2
    ├── mvc-architecture.md        # regras das camadas MVC alvo
    └── refactoring-playbook.md    # 12 transformações antes/depois (Python + Node)
```

Esse desenho reduz a pressão sobre a janela de contexto: a IA lê o índice leve
primeiro e só abre o arquivo da fase em que está.

### Anti-patterns incluídos (e por quê)

O catálogo tem **16 anti-patterns** distribuídos por severidade, escolhidos por
cobrirem os problemas reais dos três projetos e serem genéricos o bastante para outras
codebases:

- **CRITICAL:** SQL Injection, Hardcoded Secrets, God Class, Arbitrary SQL/Command Endpoint.
- **HIGH:** Business Logic in Controller, Missing Transaction, Mutable Global State, Weak/Homemade Crypto.
- **MEDIUM:** N+1 Query, Callback Hell, Missing Validation, **Deprecated API**, Sensitive Data Exposure.
- **LOW:** Magic Numbers, Duplicated Code, Poor Naming.

A detecção de **APIs deprecated** foi incluída explicitamente (requisito do desafio),
com o equivalente moderno recomendado (ex.: `datetime.utcnow()` → `datetime.now(UTC)`,
`Model.query.get` → `db.session.get`, `new Buffer` → `Buffer.from`).

### Como a skill é agnóstica de tecnologia

- Cada anti-pattern é descrito por **sinal de detecção conceitual**, não por sintaxe
  de uma linguagem.
- A Fase 1 **detecta a stack** (manifests, imports, drivers) antes de qualquer
  transformação.
- O playbook traz exemplos **paralelos em Python e Node** para cada padrão; a skill
  escolhe o dialeto conforme a stack detectada.
- As guidelines de MVC descrevem **responsabilidades de camada**, deixando os nomes de
  diretório se adaptarem à convenção da linguagem.

### Desafios e como foram resolvidos

- **Projeto já organizado (projeto 3):** a skill não podia "recriar tudo". A guideline
  de MVC inclui uma seção de *adaptação ao contexto* — preservar o que já respeita as
  camadas e só mover o que está no lugar errado. Na prática, mantivemos `models/` e
  `routes/`, adicionamos `controllers/`/`config/` e afinamos as rotas.
- **Não regredir endpoints:** cada refatoração foi validada rodando a aplicação e
  exercendo os endpoints originais (baseline antes, verificação depois).
- **Segurança sem sair do escopo:** correções ficaram no que o desafio pede (config
  sem hardcoded, queries parametrizadas, hash forte, remoção de endpoint perigoso),
  sem introduzir dependências ou features fora do exercício.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 | 3 | 3 | 3 | **13** |
| 2 — ecommerce-api-legacy | Node/Express | 3 | 4 | 3 | 3 | **13** |
| 3 — task-manager-api | Python/Flask | 1 | 3 | 4 | 4 | **12** |

### Antes / depois da estrutura

**Projeto 1 (monolito → MVC completo):**

```
Antes                        Depois
app.py                       app.py (entrypoint) + src/
models.py (God)              ├── config/ (settings, database)
controllers.py               ├── models/ (produto, usuario, pedido)
database.py (global)         ├── views/routes.py
                             ├── controllers/ (produto, usuario, pedido, health)
                             ├── services/ (notificacao)
                             └── middlewares/ (validation, error_handler)
```

**Projeto 2 (God Class → MVC completo):**

```
Antes                        Depois (src/)
src/app.js                   ├── config/ (index, database c/ Promises)
src/AppManager.js (God)      ├── models/ (user, course, enrollment, payment, auditLog)
src/utils.js (config+cache)  ├── controllers/ (checkout, report, user)
                             ├── routes/index.js
                             ├── services/ (checkout, payment, crypto, cache, report, user)
                             └── middlewares/ (validation, errorHandler)
```

**Projeto 3 (parcial → MVC reforçado):**

```
Antes                        Depois
models/ routes/              models/ (mantido, corrigido)
services/ utils/             routes/ (afinadas — só roteiam)
app.py (config hardcoded)    + config/ (settings)
                             + controllers/ (task, user, report)
                             + middlewares/ (validation, error_handler)
                             app.py (composition root: create_app)
```

### Checklist de validação (preenchido para os 3 projetos)

Legenda: ✅ atendido nos 3 projetos.

**Fase 1 — Análise**
- ✅ Linguagem detectada corretamente (Python / JavaScript)
- ✅ Framework detectado (Flask / Express)
- ✅ Domínio descrito (E-commerce / LMS-checkout / Task Manager)
- ✅ Número de arquivos analisados condiz com a realidade

**Fase 2 — Auditoria**
- ✅ Relatório segue o template definido nas referências
- ✅ Cada finding tem arquivo e linhas exatos
- ✅ Findings ordenados por severidade (CRITICAL → LOW)
- ✅ Mínimo de 5 findings (12–13 por projeto)
- ✅ Detecção de APIs deprecated incluída (projeto 3 e projeto 2)
- ✅ Confirmação pedida antes da Fase 3

**Fase 3 — Refatoração**
- ✅ Estrutura de diretórios em MVC
- ✅ Config extraída para módulo (sem hardcoded)
- ✅ Models abstraindo dados
- ✅ Views/Routes separadas
- ✅ Controllers concentram o fluxo
- ✅ Error handling centralizado
- ✅ Entry point claro (composition root)
- ✅ Aplicação inicia sem erros
- ✅ Endpoints originais respondem corretamente

### Evidências de execução (após refatoração)

**Projeto 1** — endpoints respondendo e correções ativas:
```
/produtos 200 | /login OK | /relatorios/vendas OK | /health OK (sem secret_key)
/produtos/1%20OR%201=1 -> 404  (SQLi neutralizado)
/admin/query -> 404            (endpoint perigoso removido)
/usuarios e /login -> sem campo "senha"
criar pedido -> transação OK | listar pedidos -> JOIN (sem N+1)
```

**Projeto 2** — 3 endpoints OK e sem vazamento:
```
POST /api/checkout (card 4xxx) -> 200 | (card 5xxx) -> 400 Pagamento recusado
GET  /api/admin/financial-report -> 200 (JOIN único)
DELETE /api/users/1 -> remove em cascata (revenue 1994 -> 997, sem órfãos)
Log do servidor: cartão e paymentGatewayKey NÃO aparecem
```

**Projeto 3** — 20 endpoints em 200 e segurança corrigida:
```
/ /health /tasks /tasks/:id /tasks/search /tasks/stats
/users /users/:id /users/:id/tasks /reports/summary /reports/user/:id /categories  -> 200
POST/PUT/DELETE de tasks, users e categories -> 201/200
login senha correta -> 200 (sem "password" no payload) | senha errada -> 401
título curto -> 400 (error handler central) | sem warnings de deprecation
```

### Como a skill se comportou em stacks diferentes

- **Python monolítico (P1):** transformação mais profunda — criou todas as camadas.
- **Node God Class (P2):** além de separar camadas, aplicou async/await, transação e
  hash forte; mostrou o playbook funcionando no dialeto JS.
- **Python parcial (P3):** adaptou-se ao que já existia, reforçando a arquitetura sem
  reescrever o que já estava correto — validando o requisito de agnosticismo e de
  adaptação ao contexto.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- **Projeto 1 e 3 (Python/Flask):** Python 3.12+.
- **Projeto 2 (Node/Express):** Node.js 18+.

### Invocar a skill em cada projeto

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

A skill executa a Fase 1 (análise), imprime o relatório da Fase 2 e **pede
confirmação** antes de refatorar (Fase 3).

### Validar que a refatoração funcionou

**Projeto 1 (Python/Flask):**
```bash
cd code-smells-project
pip install -r requirements.txt
python app.py          # sobe em http://localhost:5000
curl localhost:5000/produtos
curl localhost:5000/health
```

**Projeto 2 (Node/Express):**
```bash
cd ecommerce-api-legacy
npm install
npm start               # sobe em http://localhost:3000
curl localhost:3000/api/admin/financial-report
```

**Projeto 3 (Python/Flask):**
```bash
cd task-manager-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py          # popula dados de exemplo
python app.py           # sobe em http://localhost:5000
curl localhost:5000/tasks
curl localhost:5000/reports/summary
```

> Configuração sensível (SECRET_KEY, chaves) agora é lida de variáveis de ambiente.
> Cada projeto traz um `.env.example` — copie para `.env` e ajuste os valores.
