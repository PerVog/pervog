"""
Test upload and analyze route integration using FastAPI TestClient.
"""

from fastapi.testclient import TestClient
from PIL import Image
import io
import os
from app.main import app

client = TestClient(app)

def test_fastapi_upload_and_analyze_endpoints():
    # 1. Test image upload endpoint POST /api/wardrobe/upload
    img = Image.new("RGB", (200, 400), (30, 30, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    upload_res = client.post(
        "/api/wardrobe/upload",
        files={"file": ("test_suit.jpg", buf, "image/jpeg")}
    )

    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    data = upload_res.json()
    assert "image_url" in data
    image_url = data["image_url"]
    assert image_url.startswith("/uploads/")

    # 2. Test analysis endpoint POST /api/wardrobe/analyze?image_url=...
    analyze_res = client.post(f"/api/wardrobe/analyze?image_url={image_url}")
    assert analyze_res.status_code == 200, f"Analyze failed: {analyze_res.text}"
    res_data = analyze_res.json()
    assert res_data.get("success") is True
    assert "items" in res_data
