# ADR-002: Idempotent automation

## Status
Accepted

Automation requests use caller-provided idempotency keys backed by a database uniqueness constraint.

This prevents retries or duplicate HTTP requests from creating duplicate automation jobs.
