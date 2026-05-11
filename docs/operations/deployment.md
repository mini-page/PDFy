# Deployment Notes

## Deployment Shape

The initial production-leaning MVP should support separate deployment units for:

- web application
- analyzer service
- worker service
- Postgres
- Redis
- object storage

## Environment Concerns

- Distinct environment variables for storage, database, queue, and enrichment providers
- Separate service credentials with least privilege
- Configurable retention windows
- Configurable feature flags for third-party enrichment

## Operational Priorities

- reliable upload handling
- observable scan status transitions
- cleanup jobs that actually delete expired files
- graceful degradation when advanced analysis or external enrichment is unavailable

## Initial Deployment Expectations

- support local development with containerized dependencies
- support production deployment without restructuring the codebase
- keep analyzer and worker boundaries explicit from the beginning
