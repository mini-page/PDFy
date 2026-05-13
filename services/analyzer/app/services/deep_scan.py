import io
from typing import Any

import pikepdf

from app.models import FastScanResult, IocSet, ScanSummary
from app.services.hash_utils import sha256_bytes
from app.services.pdf_extract import IP_RE, SUSPICIOUS_KEYWORDS, URL_RE


def run_fast_scan(pdf_bytes: bytes, file_name: str) -> FastScanResult:
    keyword_hits = [
        keyword.decode("utf-8")
        for keyword in SUSPICIOUS_KEYWORDS
        if keyword in pdf_bytes
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
        summary=ScanSummary(verdict=verdict, score=score, confidence="medium"),
    )


def run_deep_scan(pdf_bytes: bytes, file_name: str) -> FastScanResult:
    result = run_fast_scan(pdf_bytes, file_name)

    try:
        pdf = pikepdf.Pdf.open(io.BytesIO(pdf_bytes))

        metadata: dict[str, Any] = {}
        if pdf.docinfo:
            for key, value in pdf.docinfo.items():
                key_str = str(key).replace("/", "")
                metadata[key_str] = str(value)
        result.metadata = metadata if metadata else None

        embedded_files: list[dict[str, Any]] = []
        if pdf.encrypted is False:
            for obj in pdf.objects:
                if isinstance(obj, pikepdf.Dictionary):
                    if obj.get("/Type") == "/EmbeddedFile":
                        ef_data = {"subtype": str(obj.get("/Subtype", ""))}
                        if "/F" in obj:
                            ef_data["filename"] = str(obj["/F"])
                        embedded_files.append(ef_data)
        result.embedded_files = embedded_files if embedded_files else None

        javascript: list[str] = []
        pdf_str = pdf_bytes.decode("latin-1", errors="ignore")
        js_patterns = [b"/JavaScript", b"/JS", b"/OpenAction", b"/AA"]
        for pattern in js_patterns:
            if pattern in pdf_bytes:
                if pattern == b"/JavaScript":
                    javascript.append("JavaScript action detected")
                elif pattern == b"/JS":
                    javascript.append("JS action detected")
                elif pattern == b"/OpenAction":
                    javascript.append("OpenAction detected")
                elif pattern == b"/AA":
                    javascript.append("Automatic action detected")
        result.javascript = javascript if javascript else None

    except Exception:
        pass

    return result
