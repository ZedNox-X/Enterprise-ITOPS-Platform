# Enterprise IT Operations Automation Platform.

A production-oriented Python reference architecture for enterprise IT operations.
The platform demonstrates.

- FastAPI REST APIs
- PostgreSQL + SQLAlchemy 2
- RabbitMQ event-driven processing
- Redis for caching/rate limiting primitives
- Transactional Outbox pattern
- Idempotent job processing
- Retry + dead-letter workflow
- RBAC and JWT-ready authentication boundaries
- Audit logging
- OpenTelemetry-ready observability
- Docker Compose local environment
- Kubernetes manifests
- GitHub Actions CI
- pytest unit/integration test structure
- Ruff, mypy, Bandit and pip-audit
- Clean architecture / domain-driven service boundaries

> This is a portfolio/reference implementation. Device remediation is intentionally simulated and does not execute destructive commands on real machines.
<img width="1536" height="1024" alt="Enterprise-ITOPS-Platform" src="https://github.com/user-attachments/assets/4ec329a9-f684-4f13-b1bc-ef22015a626d" />

## Architecture

```text
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │   REST / OpenAPI     │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
             Devices API      Incidents API     Automation API
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    ▼
                              PostgreSQL
                                    │
                              Outbox Events
                                    │
                                    ▼
                               RabbitMQ
                         ┌──────────┼──────────┐
                         ▼          ▼          ▼
                    Diagnostic  Remediation  Notification
                      Worker       Worker       Worker
                         │
                         ▼
                    Redis / Cache

             Observability: OpenTelemetry → Prometheus/Grafana
```

## Repository layout

```text
enterprise-itops-platform/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── domain/
│   ├── repositories/
│   ├── services/
│   ├── workers/
│   └── main.py
├── tests/
├── infrastructure/
│   └── kubernetes/
├── .github/workflows/
├── docs/adr/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Quick start

Requirements: Python 3.12+, Docker and Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

API:
- `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Run tests locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check .
mypy app
bandit -r app
```

## Example API flow

Create a device:

```bash
curl -X POST http://localhost:8000/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{"hostname":"laptop-001","platform":"windows","status":"online"}'
```

Create an incident:

```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{"device_id":"<DEVICE_ID>","title":"Authentication failure","severity":"high"}'
```

Request diagnostics:

```bash
curl -X POST \
  http://localhost:8000/api/v1/incidents/<INCIDENT_ID>/diagnose
```

Request remediation with an idempotency key:

```bash
curl -X POST \
  http://localhost:8000/api/v1/incidents/<INCIDENT_ID>/remediate \
  -H "X-Idempotency-Key: demo-001"
```

## Design decisions

### RabbitMQ vs Redis

RabbitMQ is used for reliable asynchronous work because the platform needs durable queues, acknowledgements, routing and dead-letter handling.

Redis is reserved for low-latency ephemeral workloads such as caching and rate limiting.

### Idempotency

The platform does not assume exactly-once delivery. It uses at-least-once delivery with:

1. Idempotency keys
2. Unique database constraints
3. Safe state transitions
4. Idempotent worker operations

### Worker failure

Messages are acknowledged only after successful processing. Failed work can be retried and ultimately routed to a dead-letter queue.

### Distributed transactions

The platform avoids distributed database transactions. Business state and its outbox event are committed in one PostgreSQL transaction. A publisher subsequently forwards the event to RabbitMQ.

### Security

The service layer defines RBAC boundaries, request validation, audit events and idempotency controls. Production deployment should place the API behind an OIDC/OAuth2 identity provider and gateway/WAF.

### 100,000-device scale

The API is stateless and can scale horizontally. Workers scale independently based on queue depth. PostgreSQL uses pooling and indexing, while high-volume audit/diagnostic tables can be partitioned. Observability uses request IDs, job IDs and trace IDs.

## Production hardening roadmap

- OIDC integration with Entra ID/Keycloak
- mTLS between services
- Kubernetes HPA/KEDA
- PostgreSQL HA
- RabbitMQ cluster/quorum queues
- Secrets Manager/Vault integration
- OpenTelemetry Collector
- Prometheus/Grafana dashboards
- Contract tests
- Full E2E environment
- Policy-as-code for privileged automation
- Approval workflow for destructive actions

## License

MIT
