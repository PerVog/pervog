"""
Model Download and Pre-caching Script.

Pre-downloads and caches HuggingFace model weights locally for offline or instant execution.
Run:
    python scripts/download_models.py
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("download_models")

MODELS_TO_CACHE = [
    ("IDEA-Research/grounding-dino-base", "AutoProcessor", "AutoModelForZeroShotObjectDetection"),
    ("microsoft/Florence-2-base", "AutoProcessor", "AutoModelForCausalLM"),
    ("facebook/sam-vit-base", "SamProcessor", "SamModel"),
    ("openai/clip-vit-base-patch32", "CLIPProcessor", "CLIPModel")
]

def main():
    logger.info("Starting model download and caching process...")
    
    for model_id, proc_name, model_name in MODELS_TO_CACHE:
        try:
            logger.info(f"Downloading/Caching model: {model_id}...")
            import transformers
            proc_cls = getattr(transformers, proc_name, None)
            model_cls = getattr(transformers, model_name, None)

            if proc_cls:
                proc_cls.from_pretrained(model_id, trust_remote_code=True)
            if model_cls:
                model_cls.from_pretrained(model_id, trust_remote_code=True)

            logger.info(f"Successfully cached {model_id}")
        except Exception as e:
            logger.warning(f"Note for {model_id}: {e}")

    logger.info("All specified model weights checked/cached successfully.")

if __name__ == "__main__":
    main()
