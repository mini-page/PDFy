# PDFy Production MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-leaning anonymous PDF malware scanning MVP with a Next.js website, a Python analyzer, fast synchronous scanning, queued advanced analysis, and immediate-delete-by-default retention.

**Architecture:** Use a pnpm monorepo with `apps/web` for the public product, `services/analyzer` for FastAPI-based PDF analysis, and `workers/jobs` for Redis-backed advanced scan and cleanup workers. Persist scan state in Postgres, store temporary files in S3-compatible storage, and keep schemas shared through a TypeScript contracts package.

**Tech Stack:** Next.js, TypeScript, Vitest, Prisma, Postgres, Redis, MinIO, FastAPI, Python 3.12, pypdf, pytest, RQ, pnpm, uv, Docker Compose

---

## Planned File Structure

- `package.json`: root scripts for workspace dev, lint, test, and formatting
- `pnpm-workspace.yaml`: workspace membership for `apps/*` and `packages/*`
- `turbo.json`: task orchestration for web and shared TypeScript packages
- `.gitignore`: ignore Next build output, Python caches, env files, and local object storage
- `docker-compose.yml`: local Postgres, Redis, MinIO, analyzer, and worker dependencies
- `apps/web/`: Next.js app for upload, scan status, and report views
- `apps/web/prisma/schema.prisma`: Postgres schema for scans, findings, and retention metadata
- `packages/contracts/`: shared Zod schemas and TypeScript types for scan payloads
- `services/analyzer/`: FastAPI service for fast and advanced PDF analysis
- `workers/jobs/`: RQ worker entrypoints for advanced scans and cleanup tasks
- `docs/`: living product, architecture, API, security, and operations docs

### Task 1: Bootstrap The Monorepo And Local Services

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `turbo.json`
- Create: `.gitignore`
- Create: `docker-compose.yml`
- Create: `apps/web/package.json`
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/app/api/health/route.ts`
- Create: `apps/web/tests/api/health.test.ts`
- Create: `services/analyzer/pyproject.toml`
- Create: `services/analyzer/app/main.py`
- Create: `services/analyzer/tests/test_health.py`

- [ ] **Step 1: Create the root workspace manifests and scripts**

```json
{
  "name": "pdfy",
  "private": true,
  "packageManager": "pnpm@10.0.0",
  "scripts": {
    "dev:web": "pnpm --filter web dev",
    "test:web": "pnpm --filter web test",
    "lint:web": "pnpm --filter web lint",
    "typecheck:web": "pnpm --filter web typecheck"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
```

```yaml
packages:
  - apps/*
  - packages/*
```

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "lint": {},
    "test": {},
    "typecheck": {}
  }
}
```

- [ ] **Step 2: Write failing health checks for the web app and analyzer**

```ts
import { describe, expect, it } from "vitest";

import { GET } from "@/app/api/health/route";

describe("GET /api/health", () => {
  it("returns an ok status payload", async () => {
    const response = await GET();
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body).toEqual({ status: "ok", service: "web" });
  });
});
```

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "analyzer"}
```

- [ ] **Step 3: Run tests to verify the new workspace fails before implementation**

Run: `pnpm --dir apps/web test`
Expected: FAIL with module or route resolution errors because the web health route is not implemented yet

Run: `uv run --project services/analyzer pytest services/analyzer/tests/test_health.py -q`
Expected: FAIL because the FastAPI app entrypoint does not exist yet

- [ ] **Step 4: Implement the minimal health routes and local dependency configuration**

```ts
export async function GET() {
  return Response.json({ status: "ok", service: "web" });
}
```

```python
from fastapi import FastAPI

app = FastAPI(title="PDFy Analyzer")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "analyzer"}
```

```toml
[project]
name = "pdfy-analyzer"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115.0",
  "httpx>=0.28.0",
  "pydantic>=2.9.0",
  "pytest>=8.3.0",
  "uvicorn>=0.34.0"
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 5: Add local infra defaults for Postgres, Redis, and MinIO**

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: pdfy
      POSTGRES_PASSWORD: pdfy
      POSTGRES_DB: pdfy
    ports: ["5432:5432"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    ports: ["9000:9000", "9001:9001"]
```

- [ ] **Step 6: Run tests again to verify the workspace baseline passes**

Run: `pnpm --dir apps/web test`
Expected: PASS for `health.test.ts`

Run: `uv run --project services/analyzer pytest services/analyzer/tests/test_health.py -q`
Expected: PASS with `1 passed`

- [ ] **Step 7: Commit**

```bash
git add package.json pnpm-workspace.yaml turbo.json .gitignore docker-compose.yml apps/web services/analyzer
git commit -m "chore: bootstrap workspace and service health checks"
```

### Task 2: Add Shared Contracts And Scan Persistence

**Files:**
- Create: `packages/contracts/package.json`
- Create: `packages/contracts/tsconfig.json`
- Create: `packages/contracts/src/scan.ts`
- Create: `packages/contracts/src/index.ts`
- Create: `apps/web/prisma/schema.prisma`
- Create: `apps/web/src/lib/db.ts`
- Create: `apps/web/src/lib/env.ts`
- Create: `apps/web/tests/contracts/scan-contracts.test.ts`

- [ ] **Step 1: Write failing TypeScript contract and persistence tests**

```ts
import { describe, expect, it } from "vitest";

import { createScanInputSchema, retentionModeSchema } from "@pdfy/contracts";

describe("scan contracts", () => {
  it("defaults upload requests to immediate deletion", () => {
    const parsed = createScanInputSchema.parse({});

    expect(parsed.retentionMode).toBe("delete_immediately");
  });

  it("allows only supported retention modes", () => {
    expect(retentionModeSchema.safeParse("temporary_cache").success).toBe(true);
    expect(retentionModeSchema.safeParse("forever").success).toBe(false);
  });
});
```

- [ ] **Step 2: Run the contract tests to verify they fail before schemas exist**

Run: `pnpm --dir apps/web vitest run tests/contracts/scan-contracts.test.ts`
Expected: FAIL with package import errors because `@pdfy/contracts` is not implemented yet

- [ ] **Step 3: Implement shared Zod schemas for scan creation, status, and reports**

```ts
import { z } from "zod";

export const retentionModeSchema = z.enum([
  "delete_immediately",
  "temporary_cache"
]);

export const createScanInputSchema = z.object({
  retentionMode: retentionModeSchema.default("delete_immediately"),
  enableEnrichment: z.boolean().default(true)
});

export const scanStatusSchema = z.enum([
  "queued_fast_scan",
  "running_fast_scan",
  "completed_fast_scan",
  "queued_advanced_scan",
  "running_advanced_scan",
  "completed",
  "failed",
  "expired"
]);
```

```ts
export * from "./scan";
```

- [ ] **Step 4: Add the initial Prisma schema for scans and findings**

```prisma
model Scan {
  id              String   @id @default(cuid())
  sha256          String
  fileName        String
  storageKey      String?
  retentionMode   String
  status          String
  verdict         String?
  score           Int?
  enableEnrichment Boolean @default(true)
  expiresAt       DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  findings        Finding[]
}

model Finding {
  id        String   @id @default(cuid())
  scanId    String
  category  String
  severity  String
  title     String
  detail    Json
  createdAt DateTime @default(now())
  scan      Scan     @relation(fields: [scanId], references: [id], onDelete: Cascade)
}
```

- [ ] **Step 5: Wire the Prisma client and environment validation**

```ts
import { PrismaClient } from "@prisma/client";

declare global {
  var prisma: PrismaClient | undefined;
}

export const db =
  global.prisma ??
  new PrismaClient({
    log: ["warn", "error"]
  });

if (process.env.NODE_ENV !== "production") {
  global.prisma = db;
}
```

```ts
import { z } from "zod";

export const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  ANALYZER_BASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  S3_ENDPOINT: z.string().url()
});
```

- [ ] **Step 6: Run the contract tests and Prisma validation**

Run: `pnpm --dir apps/web vitest run tests/contracts/scan-contracts.test.ts`
Expected: PASS

Run: `pnpm --dir apps/web prisma validate`
Expected: `The schema at prisma/schema.prisma is valid`

- [ ] **Step 7: Commit**

```bash
git add packages/contracts apps/web/prisma apps/web/src/lib/db.ts apps/web/src/lib/env.ts apps/web/tests/contracts
git commit -m "feat: add shared scan contracts and persistence schema"
```

### Task 3: Implement The Fast Analyzer Engine

**Files:**
- Create: `services/analyzer/app/models.py`
- Create: `services/analyzer/app/services/hash_utils.py`
- Create: `services/analyzer/app/services/fast_scan.py`
- Create: `services/analyzer/app/services/pdf_extract.py`
- Create: `services/analyzer/app/routes/analyze.py`
- Create: `services/analyzer/tests/test_fast_scan.py`

- [ ] **Step 1: Write failing analyzer tests for hashes, keywords, and IOC extraction**

```python
from app.services.fast_scan import run_fast_scan


def test_fast_scan_detects_javascript_and_url() -> None:
    pdf_bytes = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /OpenAction 2 0 R >>
endobj
2 0 obj
<< /S /JavaScript /JS (app.alert('x'); var u='http://bad.test') >>
endobj
trailer << /Root 1 0 R >>
%%EOF
"""

    result = run_fast_scan(pdf_bytes, "malicious.pdf")

    assert result.summary.verdict in {"suspicious", "malicious"}
    assert "/JavaScript" in result.keyword_hits
    assert "http://bad.test" in result.iocs.urls
```

- [ ] **Step 2: Run pytest to verify the analyzer logic fails before implementation**

Run: `uv run --project services/analyzer pytest services/analyzer/tests/test_fast_scan.py -q`
Expected: FAIL because `run_fast_scan` and the scan models do not exist yet

- [ ] **Step 3: Implement the fast scan models and deterministic heuristics**

```python
from pydantic import BaseModel, Field


class IocSet(BaseModel):
    urls: list[str] = Field(default_factory=list)
    ips: list[str] = Field(default_factory=list)


class ScanSummary(BaseModel):
    verdict: str
    score: int
    confidence: str


class FastScanResult(BaseModel):
    file_name: str
    sha256: str
    keyword_hits: list[str]
    iocs: IocSet
    summary: ScanSummary
```

```python
import hashlib


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
```

```python
import re

SUSPICIOUS_KEYWORDS = [
    b"/JavaScript",
    b"/JS",
    b"/OpenAction",
    b"/EmbeddedFile"
]

URL_RE = re.compile(rb"https?://[^\s<>()]+")
IP_RE = re.compile(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b")
```

- [ ] **Step 4: Implement the fast scan service and HTTP endpoint**

```python
from app.models import FastScanResult, IocSet, ScanSummary
from app.services.hash_utils import sha256_bytes
from app.services.pdf_extract import IP_RE, SUSPICIOUS_KEYWORDS, URL_RE


def run_fast_scan(pdf_bytes: bytes, file_name: str) -> FastScanResult:
    keyword_hits = [
        keyword.decode("utf-8") for keyword in SUSPICIOUS_KEYWORDS if keyword in pdf_bytes
    ]
    urls = sorted({match.decode("utf-8") for match in URL_RE.findall(pdf_bytes)})
    ips = sorted({match.decode("utf-8") for match in IP_RE.findall(pdf_bytes)})
    score = min(100, len(keyword_hits) * 20 + len(urls) * 15 + len(ips) * 10)
    verdict = "malicious" if score >= 80 else "suspicious" if score >= 40 else "clean"

    return FastScanResult(
        file_name=file_name,
        sha256=sha256_bytes(pdf_bytes),
        keyword_hits=keyword_hits,
        iocs=IocSet(urls=urls, ips=ips),
        summary=ScanSummary(verdict=verdict, score=score, confidence="medium")
    )
```

```python
from fastapi import APIRouter, File, UploadFile

from app.services.fast_scan import run_fast_scan

router = APIRouter(prefix="/analyze")


@router.post("/fast")
async def analyze_fast(file: UploadFile = File(...)):
    payload = await file.read()
    return run_fast_scan(payload, file.filename or "upload.pdf")
```

- [ ] **Step 5: Register the router in `app/main.py`**

```python
from fastapi import FastAPI

from app.routes.analyze import router as analyze_router

app = FastAPI(title="PDFy Analyzer")
app.include_router(analyze_router)
```

- [ ] **Step 6: Run analyzer tests again**

Run: `uv run --project services/analyzer pytest services/analyzer/tests/test_fast_scan.py -q`
Expected: PASS

Run: `uv run --project services/analyzer pytest -q`
Expected: PASS for health and fast scan tests

- [ ] **Step 7: Commit**

```bash
git add services/analyzer/app services/analyzer/tests/test_fast_scan.py
git commit -m "feat: add fast PDF analysis engine"
```

### Task 4: Build Upload Creation And Fast Scan Persistence

**Files:**
- Create: `apps/web/src/lib/storage.ts`
- Create: `apps/web/src/lib/analyzer-client.ts`
- Create: `apps/web/src/lib/scans/create-scan.ts`
- Create: `apps/web/src/lib/scans/get-scan.ts`
- Create: `apps/web/app/api/scans/route.ts`
- Create: `apps/web/app/api/scans/[scanId]/route.ts`
- Create: `apps/web/tests/api/create-scan.test.ts`

- [ ] **Step 1: Write failing tests for upload validation and default retention**

```ts
import { describe, expect, it } from "vitest";

import { createScan } from "@/src/lib/scans/create-scan";

describe("createScan", () => {
  it("defaults to immediate deletion when no retention mode is provided", async () => {
    const result = await createScan({
      fileName: "sample.pdf",
      contentType: "application/pdf",
      bytes: new Uint8Array([37, 80, 68, 70])
    });

    expect(result.retentionMode).toBe("delete_immediately");
  });

  it("rejects non-pdf uploads", async () => {
    await expect(
      createScan({
        fileName: "sample.exe",
        contentType: "application/octet-stream",
        bytes: new Uint8Array([1, 2, 3])
      })
    ).rejects.toThrow("Only PDF files are allowed");
  });
});
```

- [ ] **Step 2: Run the new test to verify it fails before the orchestration code exists**

Run: `pnpm --dir apps/web vitest run tests/api/create-scan.test.ts`
Expected: FAIL because `createScan` is not implemented yet

- [ ] **Step 3: Implement the analyzer client and storage adapter interface**

```ts
export async function runFastScan(file: File): Promise<FastScanResult> {
  const form = new FormData();
  form.set("file", file);

  const response = await fetch(`${process.env.ANALYZER_BASE_URL}/analyze/fast`, {
    method: "POST",
    body: form
  });

  if (!response.ok) {
    throw new Error("Fast scan request failed");
  }

  return fastScanResultSchema.parse(await response.json());
}
```

```ts
export type StoredObject = {
  storageKey: string;
};

export async function putTemporaryObject(input: {
  bytes: Uint8Array;
  fileName: string;
}): Promise<StoredObject> {
  return { storageKey: `uploads/${crypto.randomUUID()}-${input.fileName}` };
}
```

- [ ] **Step 4: Implement `createScan` with validation, persistence, and fast-scan orchestration**

```ts
import { createScanInputSchema } from "@pdfy/contracts";

export async function createScan(input: {
  fileName: string;
  contentType: string;
  bytes: Uint8Array;
  retentionMode?: "delete_immediately" | "temporary_cache";
  enableEnrichment?: boolean;
}) {
  if (input.contentType !== "application/pdf") {
    throw new Error("Only PDF files are allowed");
  }

  const parsed = createScanInputSchema.parse({
    retentionMode: input.retentionMode,
    enableEnrichment: input.enableEnrichment
  });

  const file = new File([input.bytes], input.fileName, { type: input.contentType });
  const fastScan = await runFastScan(file);
  const stored = await putTemporaryObject({ bytes: input.bytes, fileName: input.fileName });

  return db.scan.create({
    data: {
      fileName: input.fileName,
      sha256: fastScan.sha256,
      storageKey: stored.storageKey,
      retentionMode: parsed.retentionMode,
      status: "completed_fast_scan",
      verdict: fastScan.summary.verdict,
      score: fastScan.summary.score,
      enableEnrichment: parsed.enableEnrichment
    }
  });
}
```

- [ ] **Step 5: Implement the route handlers**

```ts
export async function POST(request: Request) {
  const form = await request.formData();
  const file = form.get("file");

  if (!(file instanceof File)) {
    return Response.json({ error: "Missing file" }, { status: 400 });
  }

  const scan = await createScan({
    fileName: file.name,
    contentType: file.type,
    bytes: new Uint8Array(await file.arrayBuffer())
  });

  return Response.json({
    scanId: scan.id,
    status: scan.status,
    retentionMode: scan.retentionMode,
    resultUrl: `/scans/${scan.id}`
  });
}
```

- [ ] **Step 6: Run web tests and Prisma migration generation**

Run: `pnpm --dir apps/web vitest run tests/api/create-scan.test.ts`
Expected: PASS

Run: `pnpm --dir apps/web prisma migrate dev --name init_scans`
Expected: migration created successfully

- [ ] **Step 7: Commit**

```bash
git add apps/web/app/api/scans apps/web/src/lib/storage.ts apps/web/src/lib/analyzer-client.ts apps/web/src/lib/scans apps/web/tests/api/create-scan.test.ts apps/web/prisma
git commit -m "feat: add upload creation and fast scan persistence"
```

### Task 5: Build The Website Scanner And Result Pages

**Files:**
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/app/scans/[scanId]/page.tsx`
- Create: `apps/web/src/components/upload-form.tsx`
- Create: `apps/web/src/components/scan-summary.tsx`
- Create: `apps/web/src/components/finding-list.tsx`
- Create: `apps/web/tests/ui/upload-form.test.tsx`

- [ ] **Step 1: Write failing UI tests for retention defaults and result rendering**

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { UploadForm } from "@/src/components/upload-form";

describe("UploadForm", () => {
  it("defaults the retention choice to immediate deletion", () => {
    render(<UploadForm />);

    expect(screen.getByLabelText(/delete immediately after analysis/i)).toBeChecked();
  });
});
```

- [ ] **Step 2: Run the UI test to verify it fails before components exist**

Run: `pnpm --dir apps/web vitest run tests/ui/upload-form.test.tsx`
Expected: FAIL because the upload components are not implemented yet

- [ ] **Step 3: Implement a minimal, functional scanner homepage**

```tsx
"use client";

import { useState } from "react";

export function UploadForm() {
  const [retentionMode, setRetentionMode] = useState("delete_immediately");

  return (
    <form className="scanner-form">
      <label>
        <input
          type="radio"
          name="retention"
          value="delete_immediately"
          checked={retentionMode === "delete_immediately"}
          onChange={() => setRetentionMode("delete_immediately")}
        />
        Delete immediately after analysis
      </label>
      <label>
        <input
          type="radio"
          name="retention"
          value="temporary_cache"
          checked={retentionMode === "temporary_cache"}
          onChange={() => setRetentionMode("temporary_cache")}
        />
        Keep a temporary cached result
      </label>
      <input type="file" name="file" accept="application/pdf" />
      <button type="submit">Scan PDF</button>
    </form>
  );
}
```

```tsx
import { UploadForm } from "@/src/components/upload-form";

export default function HomePage() {
  return (
    <main>
      <h1>PDFy</h1>
      <p>Analyze uploaded PDFs for suspicious structure, JavaScript, and network indicators.</p>
      <UploadForm />
    </main>
  );
}
```

- [ ] **Step 4: Implement the result page and reusable summary components**

```tsx
export function ScanSummary(props: {
  verdict: string;
  score: number;
  retentionMode: string;
}) {
  return (
    <section>
      <h2>{props.verdict.toUpperCase()}</h2>
      <p>Risk score: {props.score}</p>
      <p>Retention: {props.retentionMode}</p>
    </section>
  );
}
```

```tsx
import { getScan } from "@/src/lib/scans/get-scan";
import { ScanSummary } from "@/src/components/scan-summary";

export default async function ScanPage({
  params
}: {
  params: Promise<{ scanId: string }>;
}) {
  const { scanId } = await params;
  const scan = await getScan(scanId);

  return <ScanSummary verdict={scan.verdict!} score={scan.score!} retentionMode={scan.retentionMode} />;
}
```

- [ ] **Step 5: Run UI tests and basic route rendering**

Run: `pnpm --dir apps/web vitest run tests/ui/upload-form.test.tsx`
Expected: PASS

Run: `pnpm --dir apps/web test`
Expected: PASS for contract, API, UI, and health tests

- [ ] **Step 6: Commit**

```bash
git add apps/web/app/page.tsx apps/web/app/scans apps/web/src/components apps/web/tests/ui/upload-form.test.tsx
git commit -m "feat: add scanner homepage and result pages"
```

### Task 6: Add Advanced Analysis Scheduling And Worker Processing

**Files:**
- Create: `services/analyzer/app/services/advanced_scan.py`
- Create: `services/analyzer/app/routes/jobs.py`
- Create: `services/analyzer/tests/test_advanced_scan.py`
- Create: `workers/jobs/pyproject.toml`
- Create: `workers/jobs/worker.py`
- Create: `workers/jobs/tests/test_cleanup_job.py`
- Modify: `apps/web/src/lib/scans/create-scan.ts`
- Modify: `apps/web/prisma/schema.prisma`

- [ ] **Step 1: Write failing tests for advanced scheduling and persisted status transitions**

```python
from app.services.advanced_scan import summarize_advanced_findings


def test_advanced_scan_flags_embedded_file_keyword() -> None:
    pdf_bytes = b"%PDF-1.4 /EmbeddedFile /OpenAction /JS"

    result = summarize_advanced_findings(pdf_bytes)

    assert "embedded_file" in result.categories
```

```ts
import { describe, expect, it, vi } from "vitest";

import { createScan } from "@/src/lib/scans/create-scan";

describe("createScan advanced queueing", () => {
  it("marks advanced analysis as queued after fast scan succeeds", async () => {
    const scan = await createScan({
      fileName: "sample.pdf",
      contentType: "application/pdf",
      bytes: new Uint8Array([37, 80, 68, 70])
    });

    expect(scan.status).toBe("queued_advanced_scan");
  });
});
```

- [ ] **Step 2: Run the new tests to verify they fail before advanced processing exists**

Run: `uv run --project services/analyzer pytest services/analyzer/tests/test_advanced_scan.py -q`
Expected: FAIL because advanced scan helpers do not exist yet

Run: `pnpm --dir apps/web vitest run tests/api/create-scan.test.ts`
Expected: FAIL because the scan status still stops at `completed_fast_scan`

- [ ] **Step 3: Extend the Prisma schema with advanced status and report timestamps**

```prisma
model Scan {
  id               String   @id @default(cuid())
  sha256           String
  fileName         String
  storageKey       String?
  retentionMode    String
  status           String
  verdict          String?
  score            Int?
  advancedStatus   String   @default("queued")
  reportGeneratedAt DateTime?
  enableEnrichment Boolean  @default(true)
  expiresAt        DateTime?
  createdAt        DateTime @default(now())
  updatedAt        DateTime @updatedAt
  findings         Finding[]
}
```

- [ ] **Step 4: Implement analyzer scheduling and worker entrypoints**

```python
def summarize_advanced_findings(pdf_bytes: bytes) -> dict[str, list[str]]:
    categories: list[str] = []
    if b"/EmbeddedFile" in pdf_bytes:
        categories.append("embedded_file")
    if b"/OpenAction" in pdf_bytes and b"/JS" in pdf_bytes:
        categories.append("open_action_javascript")
    return {"categories": categories}
```

```python
from redis import Redis
from rq import Queue

redis = Redis.from_url("redis://localhost:6379/0")
queue = Queue("advanced-scans", connection=redis)


def enqueue_advanced_scan(scan_id: str, storage_key: str) -> str:
    job = queue.enqueue("workers.jobs.worker.run_advanced_scan_job", scan_id, storage_key)
    return job.id
```

```python
from minio import Minio
from psycopg import connect


def run_advanced_scan_job(scan_id: str, storage_key: str) -> None:
    storage = Minio(
        "localhost:9000",
        access_key="minio",
        secret_key="minio123",
        secure=False
    )
    response = storage.get_object("pdfy", storage_key)
    payload = response.read()
    response.close()
    response.release_conn()

    findings = summarize_advanced_findings(payload)

    with connect("postgresql://pdfy:pdfy@localhost:5432/pdfy") as conn:
        with conn.cursor() as cur:
            for category in findings["categories"]:
                cur.execute(
                    """
                    insert into "Finding" ("id", "scanId", "category", "severity", "title", "detail", "createdAt")
                    values (gen_random_uuid()::text, %s, %s, %s, %s, %s::jsonb, now())
                    """,
                    (
                        scan_id,
                        category,
                        "medium",
                        f"Advanced finding: {category}",
                        '{"source":"advanced_scan"}'
                    )
                )

            cur.execute(
                """
                update "Scan"
                set "advancedStatus" = %s,
                    "status" = %s,
                    "reportGeneratedAt" = now(),
                    "updatedAt" = now()
                where "id" = %s
                """,
                ("completed", "completed", scan_id)
            )
        conn.commit()
```

```toml
[project]
name = "pdfy-jobs"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "minio>=7.2.0",
  "psycopg[binary]>=3.2.0",
  "pytest>=8.3.0",
  "redis>=5.0.0",
  "rq>=1.16.0"
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 5: Update `createScan` so fast scans queue advanced work**

```ts
const scan = await db.scan.create({
  data: {
    fileName: input.fileName,
    sha256: fastScan.sha256,
    storageKey: stored.storageKey,
    retentionMode: parsed.retentionMode,
    status: "queued_advanced_scan",
    advancedStatus: "queued",
    verdict: fastScan.summary.verdict,
    score: fastScan.summary.score,
    enableEnrichment: parsed.enableEnrichment
  }
});

await scheduleAdvancedScan({
  scanId: scan.id,
  storageKey: stored.storageKey
});

return scan;
```

- [ ] **Step 6: Run migration and advanced-analysis tests**

Run: `pnpm --dir apps/web prisma migrate dev --name add_advanced_status`
Expected: migration created successfully

Run: `uv run --project services/analyzer pytest -q`
Expected: PASS for health, fast scan, and advanced scan tests

Run: `pnpm --dir apps/web test`
Expected: PASS with scan creation asserting `queued_advanced_scan`

- [ ] **Step 7: Commit**

```bash
git add services/analyzer workers/jobs apps/web/src/lib/scans/create-scan.ts apps/web/prisma/schema.prisma apps/web/tests/api/create-scan.test.ts
git commit -m "feat: add advanced scan scheduling and worker processing"
```

### Task 7: Implement Report Retrieval, Cleanup, And Retention Enforcement

**Files:**
- Create: `apps/web/app/api/scans/[scanId]/report/route.ts`
- Create: `apps/web/app/scans/[scanId]/report/page.tsx`
- Create: `apps/web/src/lib/scans/get-scan-report.ts`
- Create: `workers/jobs/cleanup.py`
- Create: `workers/jobs/tests/test_retention_cleanup.py`
- Create: `apps/web/tests/report/get-scan-report.test.ts`
- Modify: `docs/api/contracts.md`
- Modify: `docs/security/privacy.md`
- Modify: `docs/runbooks/retention-cleanup.md`

- [ ] **Step 1: Write failing tests for report payloads and retention cleanup**

```python
from workers.jobs.cleanup import should_delete_scan_file


def test_delete_immediately_scans_are_removed_after_processing() -> None:
    assert should_delete_scan_file("delete_immediately", expires_at=None) is True
```

```ts
import { describe, expect, it } from "vitest";

import { getScanReport } from "@/src/lib/scans/get-scan-report";

describe("getScanReport", () => {
  it("returns a structured report with summary and IOC sections", async () => {
    const report = await getScanReport("scan_123");

    expect(report).toHaveProperty("summary");
    expect(report).toHaveProperty("iocs");
  });
});
```

- [ ] **Step 2: Run the new tests to verify they fail before implementation**

Run: `uv run --project workers/jobs pytest workers/jobs/tests/test_retention_cleanup.py -q`
Expected: FAIL because cleanup helpers do not exist yet

Run: `pnpm --dir apps/web vitest run tests/report/get-scan-report.test.ts`
Expected: FAIL because `getScanReport` does not exist yet

- [ ] **Step 3: Implement cleanup logic and retention decision helpers**

```python
from datetime import datetime, timezone
from minio import Minio
from psycopg import connect


def should_delete_scan_file(retention_mode: str, expires_at: datetime | None) -> bool:
    if retention_mode == "delete_immediately":
        return True
    if expires_at is None:
        return False
    return expires_at <= datetime.now(timezone.utc)


def run_cleanup_job() -> None:
    with connect("postgresql://pdfy:pdfy@localhost:5432/pdfy") as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select "id", "storageKey", "retentionMode", "expiresAt"
                from "Scan"
                where "status" <> 'expired'
                """
            )
            rows = cur.fetchall()

        storage = Minio(
            "localhost:9000",
            access_key="minio",
            secret_key="minio123",
            secure=False
        )

        for scan_id, storage_key, retention_mode, expires_at in rows:
            if not should_delete_scan_file(retention_mode, expires_at):
                continue

            if storage_key:
                storage.remove_object("pdfy", storage_key)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    update "Scan"
                    set "storageKey" = null,
                        "status" = %s,
                        "updatedAt" = now()
                    where "id" = %s
                    """,
                    ("expired", scan_id)
                )
        conn.commit()
```

- [ ] **Step 4: Implement report retrieval in the web app**

```ts
export async function getScanReport(scanId: string) {
  const scan = await db.scan.findUniqueOrThrow({
    where: { id: scanId },
    include: { findings: true }
  });

  return {
    scanId: scan.id,
    summary: {
      verdict: scan.verdict,
      score: scan.score
    },
    findings: scan.findings,
    iocs: {
      urls: scan.findings
        .flatMap((finding) => finding.detail.urls ?? []),
      ips: scan.findings
        .flatMap((finding) => finding.detail.ips ?? [])
    },
    mitigations: [
      "Open suspicious PDFs only in isolated environments.",
      "Block sender or hosting infrastructure if indicators are confirmed malicious."
    ]
  };
}
```

```ts
export async function GET(
  _request: Request,
  context: { params: Promise<{ scanId: string }> }
) {
  const { scanId } = await context.params;
  return Response.json(await getScanReport(scanId));
}
```

- [ ] **Step 5: Update docs to match implemented retention and report behavior**

```md
- `GET /api/scans/:scanId/report` returns summary, findings, IOCs, and mitigation guidance.
- `delete_immediately` remains the default retention mode for all anonymous scans.
```

- [ ] **Step 6: Run cleanup, report, and docs verification**

Run: `uv run --project workers/jobs pytest workers/jobs/tests/test_retention_cleanup.py -q`
Expected: PASS

Run: `pnpm --dir apps/web test`
Expected: PASS with report retrieval coverage

Run: `rg -n "delete_immediately|temporary_cache" docs apps/web services/analyzer workers/jobs`
Expected: consistent retention terminology across code and docs

- [ ] **Step 7: Commit**

```bash
git add apps/web/app/api/scans apps/web/app/scans workers/jobs docs/api/contracts.md docs/security/privacy.md docs/runbooks/retention-cleanup.md
git commit -m "feat: add report retrieval and retention cleanup"
```

### Task 8: Add Enrichment Flags, Deployment Hardening, And End-To-End Verification

**Files:**
- Create: `apps/web/.env.example`
- Create: `services/analyzer/.env.example`
- Create: `workers/jobs/.env.example`
- Create: `apps/web/tests/e2e/scan-flow.spec.ts`
- Modify: `docs/operations/deployment.md`
- Modify: `README.md`

- [ ] **Step 1: Write a failing end-to-end test for the anonymous scan flow**

```ts
import { expect, test } from "@playwright/test";

test("anonymous user can upload a pdf and see a fast-scan verdict", async ({ page }) => {
  await page.goto("/");
  await page.setInputFiles('input[type="file"]', "tests/fixtures/sample.pdf");
  await page.getByRole("button", { name: "Scan PDF" }).click();

  await expect(page.getByText(/risk score/i)).toBeVisible();
});
```

- [ ] **Step 2: Run the end-to-end test to verify the flow is still incomplete**

Run: `pnpm --dir apps/web playwright test tests/e2e/scan-flow.spec.ts`
Expected: FAIL until upload wiring, routing, and test fixtures are complete

- [ ] **Step 3: Add production-oriented env examples and enrichment toggles**

```env
DATABASE_URL=postgresql://pdfy:pdfy@localhost:5432/pdfy
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=pdfy
ANALYZER_BASE_URL=http://localhost:8000
VT_API_KEY=
ENABLE_ENRICHMENT=true
```

- [ ] **Step 4: Wire enrichment as an optional advanced-scan feature flag**

```python
def should_run_enrichment(enable_enrichment: bool, vt_api_key: str | None) -> bool:
    return enable_enrichment and bool(vt_api_key)
```

```ts
const enableEnrichment = process.env.ENABLE_ENRICHMENT === "true";
```

- [ ] **Step 5: Update deployment docs and the project README**

```md
## Local Development

1. Start infrastructure with `docker compose up -d`.
2. Install frontend dependencies with `pnpm install`.
3. Sync Python dependencies with `uv sync --project services/analyzer` and `uv sync --project workers/jobs`.
4. Run the web app, analyzer, and worker in separate terminals.
```

- [ ] **Step 6: Run the full verification suite**

Run: `pnpm --dir apps/web test`
Expected: PASS

Run: `pnpm --dir apps/web playwright test`
Expected: PASS

Run: `uv run --project services/analyzer pytest -q`
Expected: PASS

Run: `uv run --project workers/jobs pytest -q`
Expected: PASS

Run: `docker compose config`
Expected: valid compose configuration

- [ ] **Step 7: Commit**

```bash
git add apps/web/.env.example services/analyzer/.env.example workers/jobs/.env.example apps/web/tests/e2e docs/operations/deployment.md README.md
git commit -m "chore: harden deployment and verify end-to-end flow"
```

## Self-Review Notes

- Spec coverage:
  - website-first architecture: Tasks 1, 4, 5
  - fast scan: Tasks 3 and 4
  - advanced queued analysis: Task 6
  - retention and cleanup: Task 7
  - optional enrichment: Task 8
  - living documentation: Tasks 7 and 8
- Type consistency:
  - Keep `retentionMode` values exactly `delete_immediately` and `temporary_cache`.
  - Keep scan status values aligned with `@pdfy/contracts`.
