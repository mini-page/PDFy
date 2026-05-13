# PDFy Documentation

This repository uses the `docs/` directory as a living source of truth during development.

Current documentation map:

- `superpowers/plans/`: implementation plans derived from approved specs
- `superpowers/specs/`: approved product specs and design documents
- `product/vision.md`: product scope, goals, non-goals, release intent
- `architecture/system-overview.md`: high-level system boundaries and component responsibilities
- `architecture/analysis-pipeline.md`: scan lifecycle, fast-path checks, advanced analysis jobs
- `api/contracts.md`: API surface and payload contracts
- `security/privacy.md`: retention defaults, deletion behavior, privacy and abuse posture
- `operations/deployment.md`: environment layout and deployment requirements
- `decisions/`: ADR-style records for major technical choices
- `runbooks/`: operational procedures for scheduled jobs and incidents
- `schemas/`: core result and risk data structures

Maintenance rules:

- Update docs in the same change as code whenever behavior, contracts, or architecture changes.
- Add a decision record for major product or technical direction changes.
- Keep this directory focused on current truth, not historical drift.
