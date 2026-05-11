# Analysis Pipeline

## Two-Phase Scan Model

PDFy uses a hybrid scan model:

- `Fast scan`: synchronous or near-synchronous checks that return an initial result quickly
- `Advanced scan`: queued analysis that augments the result with deeper findings

## Fast Scan Responsibilities

The fast scan should produce the first usable verdict and include:

- file hash and basic fingerprinting
- metadata extraction
- suspicious PDF keyword detection
- quick structural anomaly checks
- URL and IP extraction
- initial severity scoring
- an initial verdict summary

## Advanced Scan Responsibilities

Advanced analysis runs after the fast verdict and may include:

- deep object enumeration and extraction
- stream decompression and inspection
- embedded JavaScript extraction and heuristic review
- obfuscation pattern checks such as suspicious `eval`, `unescape`, or encoded payload usage
- embedded file detection
- exploit-pattern detection against known suspicious techniques
- optional external enrichment such as VirusTotal hash reputation checks

## Scan Lifecycle

1. Receive upload request and retention preference.
2. Persist a scan record.
3. Store the uploaded file temporarily for processing.
4. Run fast analysis and publish initial findings.
5. Queue advanced tasks when applicable.
6. Append advanced findings to the same scan record.
7. Generate a structured report payload.
8. Delete or expire the source file according to retention policy.

## Failure Behavior

- Invalid or malformed PDFs should produce a completed scan with an error-aware result, not a silent failure.
- Advanced job failures should not erase fast-scan findings.
- Third-party enrichment failures should be non-fatal and reported separately from core analysis results.
