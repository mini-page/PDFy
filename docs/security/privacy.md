# Security And Privacy

## Core Posture

PDFy analyzes potentially malicious files. The product should therefore minimize persistent storage, isolate analysis execution, and avoid unnecessary disclosure of user data.

## Retention Defaults

- Default retention mode: `delete_immediately`
- Optional retention mode: `temporary_cache`
- Temporary cache target: up to 6 hours

## Privacy Implications

- Immediate deletion reduces storage cost, blast radius, and casual abuse.
- Temporary cache should be opt-in and clearly explained in the UI.
- Third-party reputation lookups can disclose file hashes or indicators to external services and must therefore be optional and transparent.

## Abuse Controls To Design For

- file size limits
- MIME type and extension validation
- rate limiting at the upload boundary
- job concurrency limits
- retention cleanup enforcement
- safe handling of malformed or intentionally hostile PDFs

## Analyzer Safety Rules

- Static analysis is in scope for MVP.
- Live execution or detonation is out of scope for MVP.
- Analysis services should run in isolated environments with least-privilege access to storage and queues.
