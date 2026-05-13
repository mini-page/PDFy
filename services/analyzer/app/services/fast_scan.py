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
