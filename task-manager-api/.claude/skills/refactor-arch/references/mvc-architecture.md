# Guidelines de Arquitetura MVC (Fase 3)

Regras do padrão MVC alvo. Descrevem responsabilidades por camada, de forma
agnóstica de linguagem. A Fase 3 reestrutura o projeto para caber neste modelo.

## Camadas e responsabilidades

### Config
Toda configuração fora do código: secrets, portas, strings de conexão, chaves.
Lidos de variáveis de ambiente (com defaults seguros para dev). **Nada de valores
sensíveis hardcoded.** Módulo dedicado (`config/settings.py`, `src/config/index.js`).

### Models
Representam os dados e as regras que pertencem à entidade. Encapsulam acesso a
dados (queries parametrizadas ou ORM) e comportamento de domínio próprio da entidade
(ex.: `is_overdue()`, `check_password()`). **Não** conhecem HTTP nem `request`.
Um model por entidade/domínio.

### Views / Routes
A borda HTTP: definem os endpoints (path + método) e mapeiam para o controller
correspondente. Fazem parsing/serialização da requisição e resposta. **Não** contêm
regra de negócio nem acesso direto a dados. Em APIs, "View" = camada de rotas +
serialização da resposta JSON.

### Controllers
Orquestram o fluxo de cada operação: recebem os dados já validados, coordenam
models/services, decidem o status/resposta. **Controller fino** — não escreve SQL,
não guarda regra de negócio pesada; delega. Concentram o fluxo da aplicação.

### Services (quando houver orquestração de negócio)
Quando uma operação envolve várias entidades ou passos (ex.: checkout = pagamento +
matrícula + notificação + log), extraia para um service. O controller chama o
service; o service usa os models. Mantém o controller fino e a regra testável.

### Middlewares / Error handling
Tratamento de erro **centralizado**: um handler único converte exceções em respostas
consistentes, sem vazar stack trace ao cliente. Validação de input também pode viver
como middleware/camada na borda.

### Entry point (composition root)
Um ponto de entrada claro que monta a aplicação: carrega config, inicializa DB,
registra rotas e middlewares, sobe o servidor. Sem lógica de negócio.

## Estrutura de diretórios alvo

Adapte nomes à convenção da linguagem, mantendo as camadas:

```
src/ (ou raiz)
├── config/              # settings, env, conexões
├── models/              # uma entidade por arquivo
├── views/ (ou routes/)  # definição de rotas → controllers
├── controllers/         # fluxo por domínio
├── services/            # orquestração de negócio (quando necessário)
├── middlewares/         # error handler, validação
└── app entry point      # composition root
```

## Regra de fluxo

```
Request → Route/View → (validação) → Controller → Service? → Model → DB
                                                          ↑
                                              Error handler centralizado
```

## Adaptação ao contexto

- **Monolito (tudo num arquivo):** crie todas as camadas do zero, distribuindo o
  código por domínio.
- **Parcialmente organizado (já tem `models/`, `routes/`, `services/`):** preserve o
  que já respeita as camadas; mova a lógica que está no lugar errado (negócio na
  rota → controller/service; dado sensível no model → fora do `to_dict`); adicione
  o que falta (config sem hardcoded, controllers, error handler central).
- **Não invente escopo:** só as camadas necessárias para eliminar os findings e
  atingir MVC. Sem regressão nos endpoints.
