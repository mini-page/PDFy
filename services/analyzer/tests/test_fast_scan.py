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
