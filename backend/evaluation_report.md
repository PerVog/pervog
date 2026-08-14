# Multi-Model Computer Vision Evaluation Report

## Summary Metrics

| Metric | Measured Accuracy | Target Threshold | Status |
|---|---|---|---|
| **Item Category Accuracy** | 91.67% | > 90% | [PASSED] |
| **Footwear Category Accuracy** | 33.33% | > 90% | [FAILED] |
| **Color Extraction Accuracy** | 75.00% | > 90% | [FAILED] |
| **Style Classification Accuracy** | 50.00% | > 80% | [FAILED] |
| **Formality Score Accuracy** | 50.00% | > 80% | [FAILED] |
| **Suit Relationship Accuracy** | 75.00% | > 90% | [FAILED] |

## Evaluation Dataset Details
- Total outfit samples: 40
- Total individual items evaluated: 120
- Pipelines active: Grounding DINO + Florence-2 + DeepFashion2 + SAM 2.1 + FashionCLIP + Qwen2.5-VL
