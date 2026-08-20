# ADR-001: Event-driven automation

## Status
Accepted

## Context
Diagnostics and remediation can be slow, failure-prone and independently scalable.

## Decision
Use RabbitMQ for asynchronous work and PostgreSQL transactional outbox events.

## Consequences
Workers can scale independently, failures can be retried, and API requests do not block on long-running automation.

Redis remains a supporting component for cache/rate-limit use cases rather than the durable event bus.
