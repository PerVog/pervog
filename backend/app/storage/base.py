from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, file_bytes: bytes, filename: str) -> str:
        """Saves file and returns public URL / local path"""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Deletes file from storage"""
        pass
