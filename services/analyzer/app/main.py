from fastapi import FastAPI

app = FastAPI(title="PDFy Analyzer")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "analyzer"}
