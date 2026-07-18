# Catálogo de Anti-Patterns (Fase 2)

Cada entrada tem: **sinal de detecção** (acionável, agnóstico), **por que importa**
e **severidade**. Use os sinais para varrer o código e produzir findings com
`arquivo:linha` exatos.

## Escala de severidade

- **CRITICAL** — falha grave de arquitetura ou segurança: expõe dados sensíveis,
  permite injeção/execução arbitrária, ou viola completamente a separação de
  responsabilidades (God Class com DB + lógica + roteamento juntos).
- **HIGH** — forte violação de MVC/SOLID que trava manutenção e testes: lógica de
  negócio pesada no controller, acoplamento sem injeção, estado global mutável.
- **MEDIUM** — padronização, duplicação ou performance: N+1, validação ausente,
  APIs deprecated, exposição moderada de dados.
- **LOW** — legibilidade: nomes ruins, magic numbers, duplicação pontual.

---

## CRITICAL

### AP-01 · SQL Injection
**Sinal:** input concatenado/interpolado dentro de `execute(...)` — `"... " + var`,
f-string ou template string com valor vindo de request. **Por quê:** permite ler,
alterar ou apagar dados arbitrários. **Fix:** playbook #1 (query parametrizada).

### AP-02 · Hardcoded Credentials / Secrets
**Sinal:** literais como `SECRET_KEY = "..."`, `password = "..."`, `pk_live_...`,
chaves de API, senhas de DB/SMTP no código. **Por quê:** vaza credencial no
versionamento; impossível rotacionar. **Fix:** playbook #2 (env var + módulo config).

### AP-03 · God Class / God Method
**Sinal:** um arquivo/classe concentra DB + rotas + lógica + validação de vários
domínios; arquivos muito longos (>250 linhas) fazendo tudo; um "Manager" que inicia
banco, define rotas e processa negócio. **Por quê:** impossível testar isolado;
qualquer mudança afeta tudo. **Fix:** playbook #3 (separar por domínio/camada).

### AP-04 · Arbitrary SQL / Command Endpoint
**Sinal:** rota que recebe `sql`/`query`/comando do body e executa direto; endpoints
administrativos destrutivos sem proteção (`/admin/query`, `/admin/reset-db`).
**Por quê:** RCE/SQLi total. **Fix:** remover o endpoint ou trocar por operação
específica e parametrizada.

---

## HIGH

### AP-05 · Business Logic / Orchestration in Controller
**Sinal:** o handler da rota monta queries, calcula regra de negócio, orquestra
pagamento/matrícula/notificação, ou formata dados. **Por quê:** borda HTTP vira
dono da regra; não reusável, não testável. **Fix:** playbook #4 (service layer;
controller fino que delega).

### AP-06 · Missing Transaction (writes múltiplos não-atômicos)
**Sinal:** vários `INSERT`/`UPDATE` sequenciais (criar pedido + itens + baixa de
estoque; matrícula + pagamento + log) sem transação. **Por quê:** falha no meio
deixa dados inconsistentes. **Fix:** playbook #5 (transação atômica).

### AP-07 · Mutable Global State
**Sinal:** `global x`, variável/objeto module-level mutável compartilhado
(`globalCache = {}`, conexão singleton global). **Por quê:** estado imprevisível,
vazamento entre requisições, difícil de testar. **Fix:** playbook #6 (encapsular /
injetar).

### AP-08 · Weak / Homemade Cryptography
**Sinal:** `md5(`, `sha1(` para senha; hashing caseiro (loop montando string
base64); senha em texto plano. **Por quê:** senhas trivialmente quebráveis. **Fix:**
playbook #7 (hash forte: werkzeug/bcrypt).

---

## MEDIUM

### AP-09 · N+1 Query
**Sinal:** query dentro de loop sobre resultados de outra query (`for row: execute(
SELECT ... WHERE id = row.x)`); `.get()`/`.query` por item numa lista. **Por quê:**
explosão de consultas; degradação linear. **Fix:** playbook #8 (join / eager / única).

### AP-10 · Callback Hell / ausência de async-await
**Sinal:** callbacks aninhados 3+ níveis; contadores manuais (`pending--`) para
coordenar assíncrono. **Por quê:** ilegível, propício a bugs de concorrência.
**Fix:** playbook #9 (async/await, promisify).

### AP-11 · Missing Input Validation
**Sinal:** acesso direto a `request`/`body`/`params` usado em query ou persistência
sem validar presença/tipo/faixa. **Por quê:** dados inválidos/hostis chegam ao core.
**Fix:** playbook #10 (validação na borda).

### AP-12 · Deprecated API
**Sinal:** uso de APIs obsoletas — recomende o equivalente moderno:
- Python: `datetime.utcnow()` → `datetime.now(datetime.UTC)`;
  `Model.query.get(id)` (SQLAlchemy 2.x legacy) → `db.session.get(Model, id)`;
  `sqlite3` verbose/APIs antigas.
- Node: `sqlite3` callbacks → `node:sqlite`/driver com promises; `crypto` inseguro;
  `new Buffer()` → `Buffer.from()`.
**Por quê:** quebra em versões futuras, sem suporte. **Fix:** playbook #11.

### AP-13 · Sensitive Data Exposure
**Sinal:** senha/token/cartão/secret em `print`/`console.log`, na response, ou em
`to_dict()` (ex.: `to_dict` retorna `password`); health check devolvendo `secret_key`.
**Por quê:** vaza dado sensível em logs e respostas. **Fix:** remover do output;
nunca logar segredo/PII.

---

## LOW

### AP-14 · Magic Numbers / Strings
**Sinal:** literais soltos sem nome (limites de tamanho, faixas de prioridade,
strings de status repetidas). **Por quê:** intenção obscura, mudança propensa a erro.
**Fix:** constantes nomeadas / enums.

### AP-15 · Duplicated Code
**Sinal:** blocos idênticos repetidos (ex.: cálculo de `overdue`, serialização de
task em vários handlers). **Por quê:** correção precisa ser feita em N lugares.
**Fix:** extrair função/método de domínio.

### AP-16 · Poor Naming
**Sinal:** nomes de 1 letra ou genéricos em código de negócio (`u`, `e`, `p`, `cc`,
`t`, `data`). **Por quê:** prejudica leitura e manutenção. **Fix:** nomes descritivos.

---

## Uso

Para cada projeto, varra por TODOS os sinais acima. Um projeto pode disparar o mesmo
anti-pattern em vários lugares — reporte cada ocorrência relevante com sua linha.
Priorize impacto arquitetural: garanta cobertura de pelo menos CRITICAL/HIGH quando
existirem, além de MEDIUM e LOW.
