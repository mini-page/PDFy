# System Overview

## Architecture Summary

PDFy uses a website-first architecture with a Next.js frontend and a Python-based analysis backend. The frontend handles uploads, user-facing scan views, and report presentation. The backend handles PDF parsing, threat analysis, enrichment, and background jobs.

## Major Components

- `apps/web` (planned): Next.js application for upload, status, and report pages
- `services/analyzer` (planned): Python analysis service for PDF parsing and rule execution
- `workers/jobs` (planned): background workers for advanced analysis, enrichment, and cleanup
- `Redis`: transient queueing, job orchestration, and short-lived status coordination
- `Postgres`: scan records, findings summaries, status history, and retention metadata
- `S3-compatible object storage`: temporary storage for uploaded PDFs and report artifacts

## Responsibility Split

### Next.js web layer

- Validate uploads at the product boundary
- Create scan records
- Serve result pages and scan status
- Expose a stable API for web clients
- Enforce retention choices at request creation time

### Python analyzer

- Parse PDF structure
- Extract metadata and suspicious keywords
- Identify URLs, IPs, embedded objects, and JavaScript
- Apply heuristics for obfuscation and exploit indicators
- Produce normalized findings and risk signals

### Background workers

- Run deeper analysis tasks that should not block the initial response
- Perform optional third-party hash reputation lookups
- Generate report artifacts
- Enforce expiry and deletion jobs

## Trust Boundaries

- Public uploads enter through the web layer only.
- Analyzer and worker execution stay behind internal service boundaries.
- Third-party enrichment is optional and must be clearly separated from core analysis because it can disclose hashes or indicators externally.

## Growth Path

This architecture is intentionally reusable for a future public website expansion, additional clients, or multi-user product layers without replacing the analysis engine.
