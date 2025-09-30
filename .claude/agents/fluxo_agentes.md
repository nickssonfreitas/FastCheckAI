# Fluxo de Agentes para Desenvolvimento de Software

Vou explicar o fluxo completo, mostrando como os 9 agentes se integram do início ao fim de um projeto.

## Visão Geral do Fluxo

```
[Ideia/Necessidade de Negócio]
           ↓
    ┌──────────────┐
    │ DISCOVERY    │ → requirements-analyst
    └──────────────┘
           ↓
    ┌──────────────┐
    │ STRATEGY     │ → product-manager
    └──────────────┘
           ↓
    ┌──────────────┐
    │ ARCHITECTURE │ → architect-specialist + api-designer
    └──────────────┘
           ↓
    ┌──────────────┐
    │ DESIGN       │ → frontarch-specialist (se frontend)
    └──────────────┘
           ↓
    ┌──────────────┐
    │ DEVELOPMENT  │ → python-expert-reviewer (code review contínuo)
    └──────────────┘
           ↓
    ┌──────────────┐
    │ QUALITY      │ → qa-automation-specialist
    └──────────────┘
           ↓
    ┌──────────────┐
    │ DEPLOYMENT   │ → devops-engineer
    └──────────────┘
           ↓
    ┌──────────────┐
    │ MONITORING   │ → project-analyzer (contínuo)
    └──────────────┘
```

## Fase 1: Discovery & Requirements

### Gatilho
- Nova feature request
- Novo projeto
- Requisitos vagos ou conflitantes

### Agente: `requirements-analyst`

**Entrada:**
- Ideia de negócio ou problema a resolver
- Stakeholders disponíveis para entrevista

**Processo:**
1. Conduz entrevista estruturada em 12 estágios
2. Coleta requisitos funcionais e não-funcionais
3. Identifica compliance (LGPD, GDPR, etc.)
4. Documenta riscos e dependências
5. Gera matriz de rastreabilidade

**Saída:**
- Catálogo de requisitos funcionais
- NFRs mensuráveis (performance, segurança, etc.)
- Stakeholder map
- Risk matrix
- Gap analysis

**Handoff para:** `product-manager` + `architect-specialist`

---

## Fase 2: Product Strategy & Prioritization

### Gatilho
- Requisitos validados disponíveis
- Necessidade de priorizar features
- Planejamento de sprint/roadmap

### Agente: `product-manager`

**Entrada:**
- Output do `requirements-analyst`
- Business objectives e OKRs
- Team capacity e constraints

**Processo:**
1. Valida alignment com objetivos de negócio
2. Aplica framework de priorização (RICE/MoSCoW)
3. Cria backlog priorizado com user stories
4. Define sprint goals e acceptance criteria
5. Gera roadmap trimestral

**Saída:**
- Product backlog priorizado
- User stories com BDD/Gherkin
- Sprint plan com DoR/DoD
- Roadmap com milestones
- Success metrics

**Handoff para:** `architect-specialist` (escopo técnico), `qa-automation-specialist` (acceptance criteria)

---

## Fase 3: Architecture & API Design

### Gatilho
- Feature/projeto priorizado
- Decisão técnica necessária
- Design de integrações

### Agentes: `architect-specialist` + `api-designer`

#### 3A. Arquitetura de Sistema (`architect-specialist`)

**Entrada:**
- Requisitos funcionais e NFRs
- Technical constraints
- Scope da feature/projeto

**Processo:**
1. Detecta modo (FULLSTACK/SOFTWARE/DATA)
2. Gera 2-5 alternativas de arquitetura
3. Scoring matrix com trade-offs
4. Recomendação justificada
5. ADR completo

**Saída:**
- ADR (Architectural Decision Record)
- Diagrama de arquitetura (C4)
- Technology stack recommendation
- Implementation roadmap
- Risk mitigation strategies

#### 3B. Design de APIs (`api-designer`)

**Entrada:**
- Functional requirements de integrações
- Bounded contexts definidos
- Data models

**Processo:**
1. Define paradigma (REST/GraphQL/gRPC)
2. Modela recursos e endpoints
3. Gera OpenAPI 3.1 spec completo
4. Define security (OAuth2, rate limiting)
5. Documenta versioning strategy

**Saída:**
- OpenAPI specification
- API documentation (Swagger UI)
- Authentication/authorization design
- Error handling patterns
- SDK generation strategy

**Handoff para:** `frontarch-specialist` (contratos frontend), `python-expert-reviewer` (implementação), `qa-automation-specialist` (contract tests)

---

## Fase 4: Frontend Architecture (se aplicável)

### Gatilho
- Feature com interface de usuário
- Novo projeto frontend
- Refatoração de UI

### Agente: `frontarch-specialist`

**Entrada:**
- User stories com acceptance criteria
- API contracts (do `api-designer`)
- Design mockups (se disponível)

**Processo:**
1. Define stack (React/Next.js/etc.)
2. Escolhe rendering strategy (CSR/SSR/SSG)
3. Define state management
4. Gera scaffold com best practices
5. Define quality gates (Lighthouse, A11y)

**Saída:**
- Project scaffold funcional
- Component architecture
- Design system tokens
- Performance budgets
- Accessibility standards

**Handoff para:** `python-expert-reviewer` (se backend em Python), `qa-automation-specialist` (E2E tests)

---

## Fase 5: Development & Code Review

### Gatilho
- Código implementado (qualquer chunk lógico)
- Pull request pronto
- Refatoração planejada

### Agente: `python-expert-reviewer`

**Entrada:**
- Código fonte implementado
- ADRs e architectural decisions
- Test coverage reports

**Processo:**
1. Detecta modo (QUICK/SECURITY/PERFORMANCE/ARCHITECTURE)
2. Valida quality gates (lint, types, tests)
3. Identifica vulnerabilidades (SAST)
4. Analisa performance bottlenecks
5. Verifica architectural adherence

**Saída:**
- Findings por severidade (Critical/High/Medium/Low)
- Code patches com before/after
- Security vulnerability report
- Performance optimization recommendations
- Prioritized action checklist

**Feedback loop:** Desenvolvedor corrige → novo review até aprovação

---

## Fase 6: Quality Assurance & Testing

### Gatilho
- Feature implementada
- Necessidade de test strategy
- Testes flaky ou lentos

### Agente: `qa-automation-specialist`

**Entrada:**
- Acceptance criteria (do `product-manager`)
- API contracts (do `api-designer`)
- Código implementado

**Processo:**
1. Design test pyramid (70/20/10)
2. Implementa E2E tests (Playwright)
3. Contract tests (Pact)
4. Performance tests (k6)
5. Integra quality gates no CI/CD

**Saída:**
- Test strategy document
- E2E test suite (Page Object Model)
- API contract tests
- Performance test scripts
- CI/CD pipeline configuration
- Test coverage reports

**Handoff para:** `devops-engineer` (CI/CD integration)

---

## Fase 7: Deployment & Operations

### Gatilho
- Feature aprovada em QA
- Setup de novo ambiente
- Configuração de infra

### Agente: `devops-engineer`

**Entrada:**
- Código aprovado em review
- Quality gates passed
- Deployment requirements

**Processo:**
1. Cria Dockerfile otimizado
2. Setup CI/CD pipeline
3. Configura Kubernetes/infra
4. Implementa monitoring
5. Define rollback strategy

**Saída:**
- Docker/Kubernetes configs
- CI/CD pipeline (GitHub Actions)
- Infrastructure as Code (Terraform)
- Monitoring setup (Prometheus/Grafana)
- Deployment runbook

---

## Fase 8: Monitoring & Analysis (Contínuo)

### Gatilho
- Milestone completado
- Sprint review
- Health check periódico

### Agente: `project-analyzer`

**Entrada:**
- Codebase completo
- Git history
- Quality metrics

**Processo:**
1. Analisa code quality metrics
2. Calcula technical debt
3. Avalia test coverage trends
4. Identifica security vulnerabilities
5. Gera relatório de saúde

**Saída:**
- Project health report
- Technical debt quantification
- Quality metrics dashboard
- Improvement recommendations
- Trend analysis

**Feedback para:** Todos os agentes (melhoria contínua)

---

## Fluxos Específicos de Uso

### Fluxo 1: Nova Feature Completa

```
User: "Precisamos adicionar autenticação OAuth ao sistema"

1. requirements-analyst
   → Coleta requisitos (quais providers? SSO? MFA?)
   → Output: NFRs de segurança, compliance LGPD

2. product-manager
   → Recebe requisitos
   → Prioriza (P0 - critical)
   → Define user stories com acceptance criteria
   → Output: Sprint plan

3. architect-specialist
   → Avalia alternativas (OAuth2 vs OIDC vs SAML)
   → Gera ADR
   → Output: Decisão técnica documentada

4. api-designer
   → Define endpoints de autenticação
   → Gera OpenAPI spec
   → Output: /auth/login, /auth/refresh, /auth/logout

5. python-expert-reviewer
   → Revisa implementação
   → Verifica security (secrets, JWT, OWASP)
   → Output: Aprovação com checklist

6. qa-automation-specialist
   → Cria testes E2E de login/logout
   → Contract tests para auth API
   → Output: Test suite

7. devops-engineer
   → Configura secrets management
   → Setup rate limiting
   → Output: Deploy seguro

8. project-analyzer
   → Valida cobertura de testes
   → Verifica vulnerabilidades
   → Output: Health check
```

### Fluxo 2: Bug em Produção

```
User: "API de agendamentos retornando 500 errors"

1. project-analyzer (diagnóstico)
   → Analisa logs e métricas
   → Identifica endpoint problemático

2. python-expert-reviewer (MODO-PERFORMANCE)
   → Analisa código do endpoint
   → Identifica N+1 query
   → Output: Patch otimizado

3. qa-automation-specialist
   → Adiciona regression test
   → Performance test para validar fix
   → Output: Test que falha com bug, passa com fix

4. devops-engineer
   → Hotfix deploy com rollback plan
   → Output: Deploy seguro
```

### Fluxo 3: Refatoração Arquitetural

```
User: "Monolito está lento, pensar em microservices?"

1. project-analyzer
   → Analisa codebase atual
   → Identifica bounded contexts
   → Quantifica technical debt

2. architect-specialist (MODO-SOFTWARE)
   → Avalia monolith vs microservices
   → Scoring matrix com trade-offs
   → ADR com recomendação

3. api-designer
   → Define contratos entre serviços
   → Strategy de API gateway
   → Output: Service mesh design

4. qa-automation-specialist
   → Contract tests entre serviços
   → Integration tests
   → Output: Test strategy para microservices

5. devops-engineer
   → Kubernetes setup
   → Service mesh (Istio)
   → Output: Infra for microservices
```

## Integração Entre Agentes

### Dependências de Input/Output

```
requirements-analyst
  ↓ (requisitos validados)
product-manager
  ↓ (backlog priorizado)
  ├→ architect-specialist (escopo técnico)
  └→ qa-automation-specialist (acceptance criteria)

architect-specialist
  ↓ (ADRs, tech stack)
  ├→ api-designer (bounded contexts)
  ├→ frontarch-specialist (constraints)
  └→ python-expert-reviewer (padrões a validar)

api-designer
  ↓ (OpenAPI specs)
  ├→ frontarch-specialist (contratos)
  ├→ qa-automation-specialist (contract tests)
  └→ devops-engineer (API gateway config)

python-expert-reviewer
  ↓ (code approved)
qa-automation-specialist
  ↓ (tests passing)
devops-engineer
  ↓ (deployed)
project-analyzer (monitoring)
```

## Quando Usar Cada Agente

**Decision Tree:**

```
Tenho uma ideia/problema de negócio
  → requirements-analyst (sempre começa aqui)

Tenho requisitos e preciso priorizar
  → product-manager

Preciso decidir tecnologia/arquitetura
  → architect-specialist

Preciso desenhar APIs
  → api-designer

Preciso implementar frontend
  → frontarch-specialist

Implementei código Python
  → python-expert-reviewer (sempre após código)

Preciso testar
  → qa-automation-specialist

Preciso fazer deploy
  → devops-engineer

Preciso analisar saúde do projeto
  → project-analyzer
```

## Resumo Prático

**Regras de ouro:**

1. **Sempre comece com requirements-analyst** para novos projetos/features
2. **Sempre passe por python-expert-reviewer** após qualquer código Python
3. **Sempre use qa-automation-specialist** antes de considerar "done"
4. **Use architect-specialist** para qualquer decisão técnica significativa
5. **Use project-analyzer** periodicamente (semanal/sprint review)