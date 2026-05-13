from fastapi import FastAPI

from app.routes.analyze import router as analyze_router

app = FastAPI(title="PDFy Analyzer")
app.include_router(analyze_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "analyzer"}
