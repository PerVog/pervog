import os
import uuid
from app.storage.base import StorageProvider
from app.config import settings

class LocalStorageProvider(StorageProvider):
    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(self.upload_dir, unique_name)
        
        with open(filepath, "wb") as f:
            f.write(file_bytes)
            
        # Return URL relative route served by FastAPI static mount
        return f"/uploads/{unique_name}"

    def delete_file(self, file_path: str) -> bool:
        if file_path.startswith("/uploads/"):
            relative = file_path.replace("/uploads/", "")
            full_path = os.path.join(self.upload_dir, relative)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        return False
