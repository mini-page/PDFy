# API Contracts

## Design Principles

- Anonymous-first API for the MVP
- Stable scan identifiers instead of user accounts
- Separation between upload creation, status polling, and result retrieval

## Planned Endpoints

### `POST /api/scans`

Creates a scan request from an uploaded PDF.

Request shape:

```json
{
  "retentionMode": "delete_immediately",
  "enableEnrichment": true
}
```

Multipart payload should include:

- `file`: uploaded PDF

Response shape:

```json
{
  "scanId": "scan_123",
  "status": "queued_fast_scan",
  "retentionMode": "delete_immediately",
  "resultUrl": "/scans/scan_123"
}
```

### `GET /api/scans/:scanId`

Returns current scan status and summary fields.

Response shape:

```json
{
  "scanId": "scan_123",
  "status": "completed_fast_scan",
  "verdict": "suspicious",
  "score": 67,
  "advancedStatus": "running",
  "expiresAt": null
}
```

### `GET /api/scans/:scanId/report`

Returns the structured report payload used by the UI and export flows.

Response shape:

```json
{
  "scanId": "scan_123",
  "summary": {
    "verdict": "suspicious",
    "score": 67
  },
  "findings": [],
  "iocs": {
    "urls": [],
    "ips": []
  },
  "mitigations": []
}
```

## Status Vocabulary

- `queued_fast_scan`
- `running_fast_scan`
- `completed_fast_scan`
- `queued_advanced_scan`
- `running_advanced_scan`
- `completed`
- `failed`
- `expired`

## Contract Rules

- `delete_immediately` should be the default retention mode.
- `expiresAt` should be `null` when the file is deleted immediately after analysis.
- Advanced findings should be additive and must not replace the fast-scan summary structure.
