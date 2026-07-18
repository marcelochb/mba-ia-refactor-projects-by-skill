# Análise de Projeto (Fase 1)

Heurísticas para detectar linguagem, framework, banco de dados e mapear a
arquitetura atual — de forma agnóstica de stack.

## 1. Detecção de linguagem e framework

Comece pelos **manifests de dependências** (fonte mais confiável):

| Manifest | Linguagem | Como ler |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | libs + versões pinadas |
| `package.json` | Node.js | `dependencies` / `devDependencies` |
| `go.mod` | Go | módulos |
| `pom.xml`, `build.gradle` | Java/Kotlin | dependências |
| `composer.json` | PHP | requires |
| `Gemfile` | Ruby | gems |

Se não houver manifest, use a **extensão dominante** dos arquivos-fonte
(`.py`, `.js`/`.ts`, `.go`, `.java`, `.rb`, `.php`).

**Identificação do framework** pela dependência + imports:

- Python: `flask` → Flask; `fastapi` → FastAPI; `django` → Django.
- Node: `express` → Express; `@nestjs/*` → NestJS; `fastify` → Fastify; `koa` → Koa.
- Confirme lendo o entry point (import/require do framework, criação do `app`).

Extraia a **versão** do manifest quando disponível (ex.: `flask==3.1.1`,
`"express": "^4.18.2"`).

## 2. Detecção de banco de dados

Procure por sinais em imports, drivers e uso:

- SQL cru: `sqlite3`, `psycopg2`, `mysql`, `pg`, `better-sqlite3`.
- ORM: `flask_sqlalchemy`/`sqlalchemy`, `sequelize`, `typeorm`, `prisma`, `mongoose`.
- **Tabelas/entidades:** leia `CREATE TABLE ...`, classes de model
  (`class X(db.Model)`, `@Entity`), ou schemas. Liste os nomes das tabelas/entidades.
- Banco em memória (`:memory:`) vs. arquivo/servidor — relevante para validação.

## 3. Mapeamento da arquitetura atual

Classifique o nível de organização — isso define o quanto a Fase 3 vai mexer:

- **Monolítico (sem camadas):** tudo em poucos arquivos; rotas, lógica, queries e
  validação misturadas. Ex.: um único arquivo com `add_url_rule`/`app.get` + SQL inline.
- **Parcialmente organizado:** já existem pastas como `models/`, `routes/`,
  `services/`, `utils/`, mas com responsabilidades vazando (lógica de negócio na
  rota, model expondo dado sensível, service com credenciais).
- **Camadas claras:** separação real Model/Controller/Service/Route. (Raro nos
  projetos-alvo; ainda assim pode ter problemas de segurança/qualidade.)

Para o mapeamento, responda:

- Onde estão as **rotas/endpoints**? (roteamento explícito, decorators, blueprints)
- Onde está a **lógica de negócio**? (misturada na rota? num "manager"/"god class"?)
- Onde estão o **acesso a dados** e as **queries**?
- Onde está a **configuração** (secrets, portas, conexões)?
- Há **entry point** claro (`app.py`, `src/app.js`, `main`)?

## 4. Identificação do domínio

Deduza o domínio pelos nomes de tabelas, rotas e entidades (ex.: `produtos`,
`pedidos`, `usuarios` → E-commerce; `courses`, `enrollments`, `payments` → LMS/checkout;
`tasks`, `categories` → Task Manager). Descreva em uma frase.

## 5. Contagem de arquivos

Conte os arquivos-fonte reais analisados (exclua `node_modules/`, `.venv/`,
`__pycache__/`, `.git/`, arquivos gerados). É o número que vai no resumo da Fase 1.
