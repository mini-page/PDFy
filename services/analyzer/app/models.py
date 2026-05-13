
from typing import Optional, List, Dict, Any

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
    # Optional fields for deep scan
    metadata: Optional[Dict[str, Any]] = None
    embedded_files: Optional[List[Dict[str, Any]]] = None
    javascript: Optional[List[str]] = None
