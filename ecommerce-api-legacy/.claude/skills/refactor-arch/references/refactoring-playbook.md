# Playbook de Refatoração (Fase 3)

Padrões concretos de transformação, um por anti-pattern, com exemplos antes/depois
em Python e Node. Aplique o dialeto correspondente à stack detectada na Fase 1.

---

## #1 · SQL concatenado → query parametrizada (AP-01)

**Antes (Python):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```
**Depois:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

**Antes (Node):**
```js
db.get(`SELECT * FROM users WHERE email = '${email}'`, cb);
```
**Depois:**
```js
db.get("SELECT * FROM users WHERE email = ?", [email], cb);
```

Para filtros dinâmicos, construa a cláusula com placeholders e uma lista de params
(nunca concatene o valor).

---

## #2 · Secret hardcoded → env var + módulo de config (AP-02)

**Antes:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
**Depois (`config/settings.py`):**
```python
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```
```python
app.config["SECRET_KEY"] = settings.SECRET_KEY
```

**Node (`src/config/index.js`):**
```js
module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  port: process.env.PORT || 3000,
};
```

Documente as variáveis num `.env.example` (sem valores reais). O `.env` fica fora do
versionamento.

---

## #3 · God Class → separar por domínio/camada (AP-03)

Quebre o arquivo/classe único em: um **model por entidade** (acesso a dados +
regra da entidade), um **controller por domínio** (fluxo), e **rotas** apartadas.
O "Manager" que iniciava DB + rotas + negócio deixa de existir; o DB vira infra
(config/conexão), as rotas viram camada de view, o negócio vai para
controllers/services.

---

## #4 · Lógica de negócio no controller → service layer (AP-05)

**Antes:** o handler monta query, calcula total, dá baixa de estoque, envia
notificação.
**Depois:**
```python
# controllers/pedido_controller.py
def criar_pedido():
    dados = validar_pedido(request.get_json())   # validação na borda
    resultado = pedido_service.criar(dados)       # orquestração no service
    return jsonify(resultado), 201
```
O service coordena models; o controller só recebe → delega → responde.

---

## #5 · Writes múltiplos → transação atômica (AP-06)

**Antes:** vários `INSERT/UPDATE` soltos.
**Depois (Python):**
```python
try:
    db.execute("BEGIN")
    # inserts/updates ...
    db.commit()
except Exception:
    db.rollback()
    raise
```
Em ORM, use a sessão/transação do próprio ORM. Em Node, agrupe numa transação do
driver (`db.serialize` + `BEGIN`/`COMMIT`, ou `db.transaction`).

---

## #6 · Global mutável → estado encapsulado / injetado (AP-07)

**Antes:**
```js
let globalCache = {};
function logAndCache(k, v) { globalCache[k] = v; }
```
**Depois:** encapsule num módulo/instância com escopo claro (ex.: um `CacheService`
com seu próprio store), ou injete a dependência onde é usada, em vez de mutar um
objeto global compartilhado. Conexões de DB: crie/injete via config, não como
singleton global mutável.

---

## #7 · Hash caseiro/MD5 → hash forte (AP-08)

**Antes:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```
**Depois (Python):**
```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
# check: check_password_hash(self.password, pwd)
```
**Node:** use `bcrypt`/`argon2` em vez de hashing caseiro. Nunca armazene senha em
texto plano.

---

## #8 · N+1 → query única / join / eager (AP-09)

**Antes (Python):**
```python
for row in pedidos:
    itens = cursor.execute("SELECT * FROM itens WHERE pedido_id = " + str(row.id))
```
**Depois:** um `JOIN` (ou `WHERE pedido_id IN (...)`) para trazer tudo de uma vez, ou
`joinedload`/eager no ORM. Agrupe em memória depois da única consulta.

---

## #9 · Callback hell → async/await (AP-10)

**Antes:** callbacks aninhados 3+ níveis com contadores `pending--`.
**Depois (Node):** promisifique as chamadas do driver e use `async/await`:
```js
const row = await get("SELECT ...", [id]);
const items = await all("SELECT ... WHERE x = ?", [row.id]);
```
Elimina os contadores manuais e torna o fluxo linear.

---

## #10 · Validação ausente → validação na borda (AP-11)

Centralize a validação de input antes de tocar o core: verifique presença, tipo e
faixa; retorne 400 cedo. Extraia validadores reutilizáveis (ex.:
`validar_produto(dados)`), evitando `if not ...` repetidos espalhados.

---

## #11 · API deprecated → equivalente moderno (AP-12)

- `datetime.utcnow()` → `datetime.now(datetime.UTC)`
- `Model.query.get(id)` (SQLAlchemy legacy) → `db.session.get(Model, id)`
- Node `new Buffer(x)` → `Buffer.from(x)`; callbacks de driver → API com promises.

Troque o uso e ajuste os imports; verifique que o comportamento se mantém.

---

## #12 · Duplicação → método de domínio reutilizável (AP-15)

**Antes:** cálculo de `overdue` (ou serialização de entidade) repetido em vários
handlers.
**Depois:** um único método na entidade/model (`task.is_overdue()`, `task.to_dict()`)
usado por todos os pontos. Corrige-se em um lugar só.

---

## Ordem sugerida de aplicação

1. Extrair config (remove secrets do código).
2. Criar models por entidade (com queries parametrizadas / ORM correto).
3. Criar controllers/services (mover negócio para fora das rotas).
4. Separar rotas/views e registrar no entry point.
5. Adicionar error handler central + validação na borda.
6. Limpezas MEDIUM/LOW (N+1, deprecated, duplicação, nomes, magic numbers).
7. Validar: boot + endpoints.
