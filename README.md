# PDFy: PDF Malware Analysis API

<p align="center">
  <strong>Fast, comprehensive PDF malware scanning with instant results</strong>
</p>

## Overview

PDFy is a powerful web service for analyzing PDF files for malicious content. It provides multiple interfaces (REST API, Web UI, TUI) for scanning PDFs and detecting malware, suspicious keywords, embedded scripts, and other security threats.

### Key Features

- **Fast Scanning** - Quick analysis using keyword matching and heuristic detection
- **Deep Analysis** - Advanced PDF parsing with pikepdf for metadata, embedded files, and JavaScript detection
- **IOC Extraction** - Automatically extracts URLs, IP addresses, and email addresses
- **Multi-Interface** - REST API, Web UI, and Terminal interfaces
- **Risk Scoring** - Comprehensive scoring with confidence levels

## Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| [Product Vision](docs/product/vision.md) | Product scope, goals, and release intent |
| [System Architecture](docs/architecture/system-overview.md) | High-level system boundaries and components |
| [Analysis Pipeline](docs/architecture/analysis-pipeline.md) | Scan lifecycle and analysis stages |

### API & Development

| Document | Description |
|----------|-------------|
| [API Contracts](docs/api/contracts.md) | REST API surface and payload definitions |
| [Scan Result Schema](docs/schemas/scan-result-schema.md) | Result data structures |
| [Design Spec](docs/superpowers/specs/2026-05-11-pdf-malware-scanner-design.md) | Product design and implementation details |
| [Production Plan](docs/superpowers/plans/2026-05-11-pdfy-production-mvp.md) | MVP implementation roadmap |

### Operations & Security

| Document | Description |
|----------|-------------|
| [Privacy & Security](docs/security/privacy.md) | Data retention, deletion, and privacy policies |
| [Deployment Guide](docs/operations/deployment.md) | Environment setup and deployment |
| [ADR Decisions](docs/decisions/ADR-0001-platform-architecture.md) | Technical architecture decisions |

## Installation

```bash
# Install dependencies
pip install -e ./services/analyzer

# Install API dependencies
pip install -e ./apps/api
```

## Quick Start

### Start the API Server

```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Usage Options

#### 1. Web Interface

Open `apps/web/index.html` in your browser for a user-friendly PDF analysis interface.

#### 2. REST API

```bash
# Analyze a PDF file
curl -X POST http://localhost:8000/analyze/fast \
  -F "file=@sample.pdf"
```

#### 3. Terminal Interface (TUI)

```bash
# If TUI is implemented
python -m apps.tui.main
```

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze/fast` | POST | Quick analysis with keyword/IOC detection |
| `/analyze/deep` | POST | Deep scan with PDF metadata and JavaScript analysis |
| `/health` | GET | API health check |

### Response Format

```json
{
  "file_name": "document.pdf",
  "sha256": "abc123...",
  "keyword_hits": ["Suspicious keyword"],
  "iocs": {
    "urls": ["http://example.com"],
    "ips": ["192.168.1.1"],
    "emails": ["test@example.com"]
  },
  "summary": {
    "verdict": "suspicious",
    "score": 65,
    "confidence": "high"
  }
}
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov
```

## Project Structure

```
PDFy/
├── apps/
│   ├── api/          # FastAPI REST API
│   ├── web/         # Web interface (HTML/JS)
│   └── tui/         # Terminal interface
├── services/
│   └── analyzer/    # PDF analysis engine
├── docs/            # Documentation
└── README.md        # This file
```

## Security

See [Privacy & Security Documentation](docs/security/privacy.md) for:
- Data retention policies
- Automatic deletion schedules
- Abuse prevention measures

## License

See project repositories for licensing information.