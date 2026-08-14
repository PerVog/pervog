import os
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.storage.storage_manager import StorageManager
from app.ai.services.crop_validator import CropValidator, CropStorageError

client = TestClient(app)

def test_phase0_crop_storage_and_validation(tmp_path):
    # Phase 0.4 Test: Create 3 synthetic test crops (top, middle, bottom sections)
    full_img = Image.new("RGB", (300, 600), (200, 200, 200))
    
    top_crop = full_img.crop((50, 20, 250, 200))
    mid_crop = full_img.crop((50, 200, 250, 420))
    bot_crop = full_img.crop((50, 420, 250, 580))

    storage_mgr = StorageManager()
    analysis_id = "test_phase0"

    url_top = storage_mgr.save_region_crop(analysis_id, "region_1", top_crop)
    url_mid = storage_mgr.save_region_crop(analysis_id, "region_2", mid_crop)
    url_bot = storage_mgr.save_region_crop(analysis_id, "region_3", bot_crop)

    assert url_top == "/storage/crops/analysis_test_phase0_region_1.png"
    assert url_mid == "/storage/crops/analysis_test_phase0_region_2.png"
    assert url_bot == "/storage/crops/analysis_test_phase0_region_3.png"

    # Verify file existence on disk
    path_top = os.path.join(os.getcwd(), "storage", "crops", "analysis_test_phase0_region_1.png")
    path_mid = os.path.join(os.getcwd(), "storage", "crops", "analysis_test_phase0_region_2.png")
    path_bot = os.path.join(os.getcwd(), "storage", "crops", "analysis_test_phase0_region_3.png")

    assert os.path.exists(path_top)
    assert os.path.exists(path_mid)
    assert os.path.exists(path_bot)

    # Phase 0.2 validation
    assert CropValidator.validate_region_crop(url_top, "region_1") is True
    assert CropValidator.validate_region_crop(url_mid, "region_2") is True
    assert CropValidator.validate_region_crop(url_bot, "region_3") is True

    # STEP 2 Verification: HTTP GET via FastAPI static mount returns 200 OK
    res_top = client.get(url_top)
    assert res_top.status_code == 200
    assert res_top.headers["content-type"] in ["image/png", "image/x-png"]
    assert len(res_top.content) > 0
