# LLM Side-Channel Topic Classification

## Overview

This project demonstrates a side-channel attack on Large Language Models (LLMs) by classifying conversation topics using only token-length sequences. When LLM responses are streamed token-by-token over encrypted HTTPS connections, an eavesdropper can observe packet sizes (without accessing content) and infer the topic being discussed.

**Research Foundation:** "What Was Your Prompt? A Remote Keylogging Attack on AI Assistants" — Weiss et al., USENIX Security 2024

## Project Structure

```
├── 1_generate_data.py          # Collect token-length sequences from Groq API
├── 2_train_evaluate.py         # Extract features and train classifiers
├── data/                       # Collected responses (generated at runtime)
│   ├── responses.json
│   └── 1_output.txt            # Data collection logs
├── results/                    # Model outputs (generated at runtime)
│   ├── run1_overfitting/       # First experimental run (overfitting analysis)
│   └── run2_final/             # Final validated run with correct results
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## Setup & Installation

### Prerequisites

- Python 3.8 or later
- pip (Python package installer)
- Groq API key (free, from [console.groq.com](https://console.groq.com))

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `groq` — Python client for Groq API
- `scikit-learn` — Machine learning library
- `numpy` — Numerical computing
- `matplotlib` — Visualization

### Step 2: Get Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Create a free account (Google sign-in available)
3. Generate an API key in the API Keys section
4. Copy your key for the next step

**Free Tier:** 1,500 requests/day, 15 requests/minute (sufficient for this project)

### Step 3: Configure API Access

Set your API key as an environment variable:

```bash
export GROQ_API_KEY="your_api_key_here"
```

**⚠️ Never commit your API key to version control.** The `.env` file is already in `.gitignore`.

## Usage

### Phase 1: Collect Training Data

```bash
python 1_generate_data.py
```

**What it does:**
- Queries the LLM with 75 prompts (5 topics × 15 prompts each)
- Topics: Poetry, Python Code, Medical Advice, Cooking, Legal
- Records token-length sequences for each streaming response
- Applies 5-second rate limiting between requests
- Saves results to `data/responses.json`

**Expected output:**
```
Starting data collection...
Topics: ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']
Total prompts: 75

[Topic: poetry]
  (1/75) prompt 1: What makes a poem different from...
  → 42 chunks, lengths: [14, 8, 10, 5, 12, 9, 7, 3]
  ...
Saved 75 responses to data/responses.json
```

**Time estimate:** ~10-15 minutes (dominated by API latency)

### Phase 2: Train & Evaluate Classifiers

```bash
python 2_train_evaluate.py
```

**What it does:**
1. Loads responses from `data/responses.json`
2. Extracts statistical features (mean, std, histogram bins)
3. Trains Logistic Regression and Random Forest classifiers
4. Evaluates using 5-fold stratified group cross-validation
5. Generates confusion matrices and feature importance plots

**Expected output:**
```
Loaded 75 responses.

============================================================
Experiment: 2 Topics (Poetry vs. Python Code)
============================================================

Logistic Regression:
  CV accuracy: 0.833 ± 0.149
  Per-fold:    ['1.00', '0.67', '0.67', '1.00', '0.83']

Random Forest:
  CV accuracy: 0.800 ± 0.125

============================================================
Experiment: 5 Topics
============================================================

Logistic Regression:
  CV accuracy: 0.440 ± 0.090
  
Random Forest:
  CV accuracy: 0.440 ± 0.090
```

**Output files:**
- `results/confusion_2_topics.png` — Confusion matrix (2-topic)
- `results/confusion_5_topics.png` — Confusion matrix (5-topic)
- `results/importance_2_topics.png` — Feature importance (2-topic)
- `results/importance_5_topics.png` — Feature importance (5-topic)
- `results/comparison_2v5_topics.png` — Accuracy comparison

**Time estimate:** ~30 seconds

---

## Experimental Results

### Accuracy Summary

| Classifier | 2-Topic Baseline | 5-Topic Baseline | 2-Topic Accuracy | 5-Topic Accuracy |
|---|---|---|---|---|
| **Logistic Regression** | 50% | 20% | **83.3%** | **44.0%** |
| **Random Forest** | 50% | 20% | 80.0% | 44.0% |

### Key Findings

1. **2-Topic Case (Poetry vs. Code):**
   - Accuracy significantly exceeds random baseline (50%)
   - Poetry uses varied, shorter tokens
   - Code uses specific symbols and syntax
   - These differences are clearly distinguishable

2. **5-Topic Case:**
   - Accuracy above random baseline (20%)
   - Medical/legal content produces longer, more complex tokens
   - Real-world attack is harder but still feasible

3. **Feature Importance:**
   - Mean and maximum token length are most discriminative
   - Distribution histogram provides complementary signal
   - Response verbosity contributes but isn't dominant

---

## Methodology

### Data Collection

- **15 prompts per topic** (75 total) — diverse phrasings to prevent overfitting to specific prompt structures
- **Streaming mode** — replicates real attack where adversary intercepts packets in real-time
- **Token lengths only** — simulates eavesdropper constraints (encrypted HTTPS, packet sizes observable)

**Topics:**
- **Poetry:** Poetic forms, techniques, literary history
- **Python Code:** Algorithms, language features, best practices
- **Medical Advice:** Diseases, treatments, anatomy
- **Cooking:** Techniques, food science, recipes
- **Legal:** Legal concepts, contracts, procedures

### Feature Engineering

From each token-length sequence, we extract a fixed-size feature vector:

1. **Summary Statistics:**
   - Mean, std, min, max, median token length
   - Total number of chunks (response verbosity)

2. **Distribution Histogram:**
   - Normalized histogram over 5 bins: [1-2], [3-5], [6-10], [11-15], [16+] characters
   - Captures shape independent of response length

**Why this approach:** With ~75 samples, neural networks would overfit. Hand-crafted statistical features are interpretable and require far less data.

### Cross-Validation Strategy

We use **StratifiedGroupKFold** to prevent data leakage:
- **Stratification:** Each fold maintains class proportions
- **Group splitting:** All responses from the same prompt index go to either train OR test (never split)
- **Result:** Honest evaluation of topic classification ability

---

## Security & Ethics

### API Key Security

**Never commit your API key to version control.**
- Keys in `.gitignore` by default
- Use environment variables, not hardcoded values
- If accidentally committed, regenerate immediately on [console.groq.com](https://console.groq.com)

### Research Ethics

This project is for educational and research purposes only. It demonstrates:
- Fundamental privacy risks in streaming LLM APIs
- Importance of traffic analysis defenses
- Value of responsible disclosure in security research

### Potential Defenses

- Packet padding to fixed sizes
- Buffering tokens before sending
- Traffic morphing with dummy packets
- Variable-size chunking (not token-aligned)

---

## Limitations

1. **Simulated, Not Real Attack:** We measure API chunk lengths, not encrypted packet sizes
2. **Single LLM Only:** Trained on Groq/Llama; won't transfer to GPT-4 without retraining
3. **English-Only:** No multilingual evaluation
4. **Limited Topics:** Only 5 categories (real attacks could target 50+)
5. **Controlled Environment:** No network noise, jitter, or compression
6. **Small Dataset:** 75 responses total

## Running the Complete Pipeline

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
export GROQ_API_KEY="your_key_here"

# 3. Collect data (~10-15 minutes)
python 1_generate_data.py

# 4. Train and evaluate (~30 seconds)
python 2_train_evaluate.py

# 5. View results
ls -la results/run2_final/
```

**Total runtime:** ~10-15 minutes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: groq` | Run `pip install -r requirements.txt` |
| `Error: Invalid API key` | Set `export GROQ_API_KEY="..."` |
| `Empty response from API` | Check internet; increase `DELAY_SECONDS` in phase 1 |
| `FileNotFoundError: data/responses.json` | Run `python 1_generate_data.py` first |

## References

- **Weiss et al.** "What Was Your Prompt? A Remote Keylogging Attack on AI Assistants" — USENIX Security 2024
- **Groq API:** https://console.groq.com
- **Scikit-learn:** https://scikit-learn.org
- **Numpy:** https://numpy.org
- **Matplotlib:** https://matplotlib.org

## License

MIT License — See LICENSE file for details.
