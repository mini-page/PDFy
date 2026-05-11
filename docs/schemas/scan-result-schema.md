# Scan Result Schema

## Summary

The result schema should stay stable across both fast and advanced scan phases.

## Core Fields

```json
{
  "scanId": "scan_123",
  "status": "completed",
  "retentionMode": "delete_immediately",
  "summary": {
    "verdict": "suspicious",
    "score": 67,
    "confidence": "medium"
  },
  "metadata": {},
  "findings": [],
  "iocs": {
    "urls": [],
    "ips": [],
    "hashes": []
  },
  "advancedAnalysis": {
    "status": "completed",
    "sections": []
  }
}
```

## Schema Rules

- `summary` must exist after fast scan completion.
- `advancedAnalysis` may be incomplete while background jobs are still running.
- `retentionMode` must always be explicit in the stored scan record.
