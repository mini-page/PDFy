# ADR-0001: Website-First Architecture With Python Analysis Backend

## Status

Accepted

## Context

The product needs to start as a website-style PDF scanning experience and later expand without replacing the analysis core. Deep PDF malware analysis also aligns much better with Python-based tooling than a Node-only stack.

## Decision

Use:

- Next.js for the website and user-facing API layer
- Python services for PDF analysis
- queued background workers for advanced analysis and cleanup
- short-lived storage with immediate deletion as the default retention mode

## Consequences

- The product can evolve into a larger website platform without rewriting the analyzer.
- The analysis engine can use stronger PDF security tooling.
- Deployment is more complex than a single-process app, but the architecture matches long-term product needs.
