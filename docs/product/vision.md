# Product Vision

## Summary

PDFy is a website-first PDF malware scanning product that lets users upload a PDF, receive a fast initial verdict, and optionally receive richer findings from background analysis. The first release is anonymous by default and optimized for practical public use with minimal friction.

## Goals

- Provide a fast, understandable security verdict for uploaded PDFs.
- Detect suspicious PDF structures, JavaScript behaviors, embedded objects, URLs, IPs, and exploit indicators through static analysis.
- Support a two-phase analysis model: immediate fast scan plus deeper queued analysis.
- Keep operational costs and abuse exposure controlled by defaulting to immediate deletion after analysis.
- Build the analysis core so it can support both the website and future clients without architectural rewrite.

## Non-Goals For MVP

- User accounts, billing, or multi-tenant workspaces
- Behavioral detonation or live document execution
- Large-scale enterprise case management
- Long-term file storage by default

## MVP User Flow

1. User visits the scanner homepage.
2. User uploads a PDF and chooses whether to opt into short-lived cached retention.
3. System runs fast analysis and returns an initial verdict quickly.
4. Advanced analysis continues in the background when applicable.
5. User reviews the report and optional deeper findings.
6. Stored files and retained reports expire automatically according to retention settings.

## Retention Principle

- Default behavior: delete uploaded files immediately after analysis completes.
- Optional behavior: short-lived cached retention for temporary revisit access.
- Initial cache target: up to 6 hours, with tighter limits allowed later if operations require it.
