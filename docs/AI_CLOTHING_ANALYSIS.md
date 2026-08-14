# AI Clothing & Wearable Attribute Detection Module

## 1. Overview
The AI Clothing Analysis module provides a **₹0-cost, fully local vision pipeline** for classifying uploaded clothing images, extracting structured fashion attributes, and calculating formality scores without relying on paid APIs.

---

## 2. Models & Architecture

- **Primary Model**: Hugging Face `patrickjohncyh/fashion-clip` (or `openai/clip-vit-base-patch32`).
- **Alternative Model**: `Marqo/marqo-fashionCLIP` configurable via `FASHION_MODEL=marqo`.
- **Color Engine**: OpenCV (`cv2`) + PIL + NumPy K-Means Clustering (`ColorAnalyzerService`).
- **Formality Engine**: Rule-based `FormalityService` producing a normalized 0–10 score.
- **Hierarchical Classification**: `ClothingAnalysisService` (Region Slicing $\rightarrow$ Category $\rightarrow$ Subcategory $\rightarrow$ Style $\rightarrow$ Fit $\rightarrow$ Material $\rightarrow$ Occasion).

---

## 3. Configuration & Environment Variables

Set in environment or `.env`:

```env
FASHION_MODEL=fashionclip
CONFIDENCE_THRESHOLD=0.55
```

---

## 4. API Usage

### Single Image Analysis
`POST /api/ai/analyze-clothing`
- **Body**: `multipart/form-data` with `file`
- **Response**: `FullClothingAnalysisResponse` schema with confidence scores and `needs_confirmation` thresholding.

### Batch Analysis
`POST /api/ai/analyze-batch`
- **Body**: `multipart/form-data` with multiple `files`

---

## 5. Dataset Export

Run the export script to produce dataset files in JSON and CSV format:

```bash
python scripts/export_fashion_dataset.py
```

Produces:
- `fashion_dataset.json`
- `fashion_dataset.csv`

---

## 6. Model Evaluation

Run the accuracy benchmark test suite:

```bash
pytest tests/test_ai_evaluation.py -v
```

Outputs category, color, style, pattern, material, fit, and occasion accuracy scores.
