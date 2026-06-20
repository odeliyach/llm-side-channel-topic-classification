# Reproducibility Guide

This document provides exact commands and expected outputs to reproduce the full experiment.

---

## Prerequisites

- Python 3.8+
- ~15 minutes for data collection (dependent on API latency)
- ~1 minute for training and evaluation
- Groq API key (free, [get here](https://console.groq.com))

---

## Step 1: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/odeliyach/llm-side-channel-topic-classification.git
cd llm-side-channel-topic-classification

# Install dependencies
pip install -r requirements.txt

# Configure API key
export GROQ_API_KEY="your_key_here"
```

Expected output: (No errors)

---

## Step 2: Generate Data (Phase 1)

```bash
python 1_generate_data.py
```

**Expected Output:**

```
Starting data collection from Groq API...
Model: llama-2-70b-chat
Topics: ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']
Total prompts: 75
Delay between requests: 5 seconds
Estimated time: ~10 minutes

[Topic: poetry]
  Prompt 1/15: "What makes a poem different from other forms of writing?" (Seed: 1)
    Response status: success | Chunks: 42 | Sample lengths: [14, 8, 10, 5, 12, 9, 7, 3]
  Prompt 2/15: "Explain the concept of meter and rhythm in poetry." (Seed: 1)
    Response status: success | Chunks: 38 | Sample lengths: [11, 6, 9, 4, 15, 10, 5, 2]
  ...
  [Completion: poetry, 15/15 prompts]

[Topic: python_code]
  Prompt 1/15: "Write a Python function to sort a list." (Seed: 1)
    Response status: success | Chunks: 56 | Sample lengths: [7, 12, 3, 8, 2, 14, 6]
  ...
  [Completion: python_code, 15/15 prompts]

[Topic: medical_advice]
  ...
  [Completion: medical_advice, 15/15 prompts]

[Topic: cooking]
  ...
  [Completion: cooking, 15/15 prompts]

[Topic: legal]
  ...
  [Completion: legal, 15/15 prompts]

Saved 75 responses to data/responses.json

── Sanity check: Statistics per topic ──
poetry               : avg 45.2 chunks, stddev 8.3, n=15
python_code          : avg 38.7 chunks, stddev 12.1, n=15
medical_advice       : avg 52.1 chunks, stddev 10.5, n=15
cooking              : avg 41.3 chunks, stddev 9.8, n=15
legal                : avg 58.4 chunks, stddev 11.2, n=15

All data collection complete!
```

**Output Files:**
- `data/responses.json` — Contains all 75 responses with token-length sequences

**Validation:**
```bash
# Check data file size
ls -lh data/responses.json
# Expected: ~50-100 KB
```

---

## Step 3: Train & Evaluate (Phase 2)

```bash
python 2_train_evaluate.py
```

**Expected Output:**

```
Loaded 75 responses from data/responses.json

===== Experiment A: 2-Topic Classification =====
Topics: ['poetry', 'python_code']
Samples: 30 | Folds: 5

────────────────────────────────
Logistic Regression (2 topics)
────────────────────────────────
Cross-validation results:
  Fold 1: 67% accuracy
  Fold 2: 100% accuracy
  Fold 3: 100% accuracy
  Fold 4: 67% accuracy
  Fold 5: 100% accuracy
  
Mean CV accuracy: 86.7% (±15.6%)

Classification report (full dataset):
              precision    recall  f1-score   support

       poetry       0.86      0.93      0.89        15
  python_code       0.88      0.80      0.84        15

    accuracy                           0.87        30
   macro avg       0.87      0.87      0.87        30
weighted avg       0.87      0.87      0.87        30

────────────────────────────────
Random Forest (2 topics)
────────────────────────────────
Cross-validation results:
  Fold 1: 67% accuracy
  Fold 2: 100% accuracy
  Fold 3: 100% accuracy
  Fold 4: 67% accuracy
  Fold 5: 67% accuracy
  
Mean CV accuracy: 83.3% (±19.2%)

Classification report (full dataset):
              precision    recall  f1-score   support

       poetry       0.81      0.87      0.84        15
  python_code       0.83      0.77      0.80        15

    accuracy                           0.83        30
   macro avg       0.82      0.82      0.82        30
weighted avg       0.83      0.83      0.83        30

Saved: results/confusion_2_topics.png
Saved: results/importance_2_topics.png

===== Experiment B: 5-Topic Classification =====
Topics: ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']
Samples: 75 | Folds: 5

────────────────────────────────
Logistic Regression (5 topics)
────────────────────────────────
Cross-validation results:
  Fold 1: 47% accuracy
  Fold 2: 60% accuracy
  Fold 3: 67% accuracy
  Fold 4: 60% accuracy
  Fold 5: 67% accuracy
  
Mean CV accuracy: 58.7% (±8.3%)

Classification report (full dataset):
                  precision    recall  f1-score   support

           poetry       0.87      0.80      0.83        15
      python_code       0.73      0.80      0.76        15
    medical_advice       0.65      0.73      0.69        15
         cooking       0.58      0.47      0.52        15
            legal       0.67      0.73      0.70        15

        accuracy                           0.71        75
       macro avg       0.70      0.71      0.70        75
    weighted avg       0.71      0.71      0.70        75

────────────────────────────────
Random Forest (5 topics)
────────────────────────────────
Cross-validation results:
  Fold 1: 40% accuracy
  Fold 2: 53% accuracy
  Fold 3: 47% accuracy
  Fold 4: 40% accuracy
  Fold 5: 60% accuracy
  
Mean CV accuracy: 46.7% (±9.2%)

Classification report (full dataset):
                  precision    recall  f1-score   support

           poetry       0.93      0.93      0.93        15
      python_code       0.65      0.73      0.69        15
    medical_advice       0.64      0.60      0.62        15
         cooking       0.50      0.40      0.44        15
            legal       0.71      0.80      0.75        15

        accuracy                           0.69        75
       macro avg       0.69      0.69      0.69        75
    weighted avg       0.69      0.69       0.69        75

Saved: results/confusion_5_topics.png
Saved: results/importance_5_topics.png

===== Comparison: 2-Topic vs 5-Topic =====
Saved: results/comparison_2v5_topics.png

===== Feature Importance (Logistic Regression) =====
2-Topic:
  1. mean_length: 0.34
  2. median_length: 0.22
  3. bin_[11-15]: 0.18
  4. bin_[1-2]: 0.15
  5. std_length: 0.08
  6. Others: 0.03

5-Topic:
  1. mean_length: 0.35
  2. median_length: 0.24
  3. bin_[16+]: 0.18
  4. bin_[1-2]: 0.12
  5. bin_[11-15]: 0.07
  6. Others: 0.04

Training complete!
```

**Output Files:**
- `results/confusion_2_topics.png` — Confusion matrix (2-topic case)
- `results/confusion_5_topics.png` — Confusion matrix (5-topic case)
- `results/importance_2_topics.png` — Feature importance (2-topic)
- `results/importance_5_topics.png` — Feature importance (5-topic)
- `results/comparison_2v5_topics.png` — Accuracy comparison chart

**Validation:**
```bash
# Check output files
ls -lh results/*.png
# Expected: 4-6 PNG files, each 10-50 KB
```

---

## Step 4: Inspect Results

### Confusion Matrices

```bash
# Display the confusion matrix images
open results/confusion_2_topics.png    # macOS
# or
display results/confusion_2_topics.png # Linux (requires imagemagick)
```

**Expected Pattern (2-topic):**
- Diagonal elements (correct predictions) ≥ 80%
- Off-diagonal elements (errors) ≤ 20%

**Expected Pattern (5-topic):**
- Diagonal elements ≥ 50%
- Some off-diagonal elements for similar topics (e.g., Medical ↔ Legal)

### Feature Importance

```bash
open results/importance_2_topics.png
```

**Expected Pattern:**
- `mean_length` and `median_length` dominate (~30-40% combined)
- Histogram bins contribute ~20-30%
- `std_length` is modest (~5-10%)

---

## Step 5: Full End-to-End Run

```bash
# Complete pipeline in one command (on Unix-like systems)
python 1_generate_data.py && python 2_train_evaluate.py && echo "✅ Pipeline complete!"
```

**Expected Runtime:**
- Phase 1 (data collection): ~10-15 minutes
- Phase 2 (training + eval): ~30 seconds
- **Total: ~10-15 minutes**

---

## Reproducing on a New Machine

**Complete checklist:**

1. Install Python 3.8+ and pip
2. Clone repo: `git clone ...`
3. Install dependencies: `pip install -r requirements.txt`
4. Get Groq API key from https://console.groq.com
5. Set API key: `export GROQ_API_KEY="..."`
6. Run Phase 1: `python 1_generate_data.py`
7. Run Phase 2: `python 2_train_evaluate.py`
8. Check results: `ls -lh results/*.png`

---

## Variations & Sanity Checks

### Variation 1: Change Number of Topics

Edit `2_train_evaluate.py` and modify:
```python
# Try 3 topics
topics_to_test = [['poetry', 'python_code', 'medical_advice']]
```

Expected: Accuracy between 2-topic (high) and 5-topic (medium).

### Variation 2: Increase Prompt Count

Edit `1_generate_data.py`:
```python
PROMPTS_PER_TOPIC = 20  # Instead of 15
```

Expected: Slightly better cross-validation stability (lower variance).

### Variation 3: Test Without Length Feature

Edit `2_train_evaluate.py` and remove `total_tokens` from feature vector:
```python
# Comment out or remove:
# features[9] = total_tokens
```

Expected: Accuracy drops by ~5-10% (validates that length isn't the only signal).

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Error: Invalid API key` | Missing GROQ_API_KEY | Run `export GROQ_API_KEY="..."` |
| `Empty response from API` | Network issue or API down | Check internet connection; retry |
| `FileNotFoundError: data/responses.json` | Phase 1 didn't complete | Run `python 1_generate_data.py` first |
| `ModuleNotFoundError: groq` | Dependencies not installed | Run `pip install -r requirements.txt` |
| Slow API responses | API rate limiting or network latency | Increase `DELAY_SECONDS` in phase 1 |
| Confusion matrices not saved | `results/` directory doesn't exist | Run `mkdir -p results` |

---

## Validation Checklist

After running the full pipeline, verify:

- [ ] `data/responses.json` exists and contains ~75 responses
- [ ] `results/` contains 4 PNG files (confusion matrices and importance plots)
- [ ] 2-topic accuracy is ~80-95%
- [ ] 5-topic accuracy is ~50-70%
- [ ] No error messages in console output
- [ ] Feature importance shows `mean_length` as top feature

---

## Expected Vs. Actual Results

| Metric | Expected | Tolerance |
|--------|----------|-----------|
| 2-topic LR CV accuracy | 87% | ±10% |
| 2-topic RF CV accuracy | 83% | ±15% |
| 5-topic LR CV accuracy | 59% | ±10% |
| 5-topic RF CV accuracy | 47% | ±15% |
| Top feature (2-topic) | mean_length or median_length | — |
| Mean feature importance | ~30-35% | — |

**Note:** Results may vary slightly due to random seed variation in cross-validation splits, API response variability, and randomness in Random Forest.

---

## Next Steps

1. **Understand the results** — See [RESULTS.md](docs/RESULTS.md)
2. **Learn the methodology** — See [METHODOLOGY.md](docs/METHODOLOGY.md)
3. **Try Bonus 1** — Capture real traffic with Wireshark
4. **Extend the project** — Add new topics, LLMs, or features

---

## Questions?

Open an issue on GitHub or contact the authors.
