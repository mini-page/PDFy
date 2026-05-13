from fastapi import APIRouter, File, UploadFile

from app.services.deep_scan import run_deep_scan, run_fast_scan

router = APIRouter(prefix="/analyze")


@router.post("/fast")
async def analyze_fast(file: UploadFile = File(...)):
    payload = await file.read()
    return run_fast_scan(payload, file.filename or "upload.pdf")


@router.post("/deep")
async def analyze_deep(file: UploadFile = File(...)):
    payload = await file.read()
    return run_deep_scan(payload, file.filename or "upload.pdf")
