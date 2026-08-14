import os
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from PIL import Image
import io
from app.ai.services.clothing_analysis import ClothingAnalysisService
from app.ai.models.schemas import FullClothingAnalysisResponse
from app.storage.local_storage import LocalStorageProvider

router = APIRouter(prefix="/ai", tags=["AI Clothing Analysis"])
storage = LocalStorageProvider()
service = ClothingAnalysisService()

@router.post("/analyze-clothing", response_model=FullClothingAnalysisResponse)
async def analyze_clothing_image(file: UploadFile = File(...)):
    """Analyzes uploaded clothing image using multi-model CV vision pipeline."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG, JPEG, WEBP)")
    
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file format")

    result = service.analyze(image)
    return result

@router.get("/debug/analysis/{analysis_id}")
def get_debug_analysis(analysis_id: str):
    """Debug API returning full physical region details, crop hashes, masks, and model evidence (PART 32)."""
    debug_runs_dir = "debug_runs"
    if not os.path.exists(debug_runs_dir):
        raise HTTPException(status_code=404, detail="No debug runs available")

    # Find matching debug run directory
    runs = sorted(os.listdir(debug_runs_dir), reverse=True)
    target_dir = None
    for run in runs:
        final_path = os.path.join(debug_runs_dir, run, "final.json")
        if os.path.exists(final_path):
            with open(final_path, "r") as f:
                data = json.load(f)
                if data.get("analysis_id") == analysis_id or analysis_id == "latest":
                    target_dir = os.path.join(debug_runs_dir, run)
                    break

    if not target_dir:
        raise HTTPException(status_code=404, detail=f"Analysis ID '{analysis_id}' not found")

    with open(os.path.join(target_dir, "final.json"), "r") as f:
        final_data = json.load(f)

    detections = []
    det_path = os.path.join(target_dir, "detections.json")
    if os.path.exists(det_path):
        with open(det_path, "r") as f:
            detections = json.load(f)

    return {
        "analysis_id": analysis_id,
        "debug_run_dir": target_dir,
        "original_image": f"/storage/{os.path.join(target_dir, 'original.jpg')}",
        "detections_image": f"/storage/{os.path.join(target_dir, 'detections.jpg')}",
        "raw_detections": detections,
        "physical_regions": final_data.get("items", []),
        "overall_outfit": final_data.get("overall_outfit", {})
    }

@router.post("/analyze-batch")
async def analyze_clothing_batch(files: List[UploadFile] = File(...)):
    """Batch analysis endpoint for dataset generation."""
    batch_results = []
    for file in files:
        contents = await file.read()
        try:
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            analysis = service.analyze(image)
            batch_results.append({
                "filename": file.filename,
                "analysis": analysis.model_dump()
            })
        except Exception as e:
            batch_results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {
        "success": True,
        "total_analyzed": len(batch_results),
        "results": batch_results
    }
