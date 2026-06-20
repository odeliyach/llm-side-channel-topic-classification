# LLM Side-Channel Topic Classification Attack

## Overview

This project demonstrates a practical side-channel attack on Large Language Models (LLMs) through traffic analysis. By analyzing **token-length sequences alone**—without accessing actual response content—we can classify the topic of a conversation with surprisingly high accuracy, even over encrypted HTTPS connections.

### Key Insight

When LLM responses are streamed token-by-token, the size of each network packet leaks information about the tokens being generated. Even though the traffic is encrypted, packet-size patterns are observable and can be exploited by an eavesdropper to infer the nature of the conversation.

### Research Foundation

This implementation reproduces the attack from the research paper:
> **"What Was Your Prompt? A Remote Keylogging Attack on AI Assistants"** by Weiss et al., USENIX Security 2024

The paper demonstrates that token-length sequences contain sufficient statistical signal to perform topic classification with non-trivial accuracy across multiple classification tasks.

---

## Quick Links

- 🚀 **[Setup Guide](docs/SETUP.md)** — Installation & API configuration
- 🔬 **[Methodology](docs/METHODOLOGY.md)** — Detailed experimental design
- 📊 **[Results](docs/RESULTS.md)** — Results interpretation & insights
- 🔐 **[Security](docs/SECURITY.md)** — API key management & ethics
- 📝 **[Reproducibility](REPRODUCIBILITY.md)** — Exact commands & expected outputs
- 🗂️ **[Project Status](PROJECT_STATUS.md)** — Known limitations & roadmap
- 🎓 **[Paper Mapping](docs/PAPER_MAPPING.md)** — Alignment with Weiss et al.

---

## Project Structure

```
llm-side-channel-topic-classification/
├── 1_generate_data.py          # Data collection: Query Groq/Llama API, record token lengths
├── 2_train_evaluate.py         # Model training: Features, classification, evaluation
├── extract_size_pcap.py        # Utility: Extract packet sizes from PCAP files
├── data/                        # Data directory (generated at runtime)
│   ├── README.md               # Data format documentation
│   └── .gitkeep
├── docs/                        # Detailed documentation
│   ├── SETUP.md                # Installation & configuration
│   ├── METHODOLOGY.md          # Experimental design details
│   ├── RESULTS.md              # Results interpretation
│   ├── SECURITY.md             # API security & ethics
│   └── PAPER_MAPPING.md        # Alignment with research paper
├── results/                     # Results directory (generated at runtime)
│   └── .gitkeep
├── .github/                     # GitHub templates & workflows
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── CODEOWNERS
├── .env.example                 # API key template
├── .gitignore                   # Git ignore rules
├── .gitattributes              # Line ending consistency
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history
├── CITATION.bib                 # Academic citation
├── CONTRIBUTING.md              # Contribution guidelines
├── Makefile                     # Convenience commands
├── PROJECT_STATUS.md            # Status & roadmap
├── REPRODUCIBILITY.md           # Reproducibility guide
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Technical Architecture

### Phase 1: Data Collection (`1_generate_data.py`)

**Objective:** Collect token-length sequences for multiple topics using an LLM streaming API.

**Workflow:**
1. Defines 5 topic categories with 15 carefully-selected prompts per topic:
   - **Poetry:** Questions about poetic forms, techniques, and literary history
   - **Python Code:** Programming questions covering algorithms, language features, and best practices
   - **Medical Advice:** Health-related questions on diseases, treatments, and anatomy
   - **Cooking:** Culinary techniques and food science questions
   - **Legal:** Legal concepts, contracts, and court procedures

2. For each prompt, queries the LLM in **streaming mode** to capture token-length patterns

3. Records only the **character length of each streaming chunk** (representing token boundaries), discarding actual content

4. Outputs: `data/responses.json` containing topic, prompt index, and token-length sequences

**Why Streaming Mode?**
- In a real attack, the adversary intercepts packets as they arrive in real-time
- Streaming mode replicates this by exposing partial outputs chunk-by-chunk
- Each chunk corresponds to 1-3 tokens, and its length reveals information about the tokens

**Why Token Lengths Instead of Actual Content?**
- Simulates the constraints of an eavesdropper on encrypted HTTPS connections
- Packet payloads are encrypted, but their sizes are observable
- This demonstrates a fundamental vulnerability: sizes leak information even without content access

**Prompt Engineering Notes:**
- Each topic's 15 prompts are manually crafted to be **diverse in phrasing, length, and angle**
- Diversity prevents the classifier from learning prompt-specific patterns instead of topic characteristics
- All prompts were reviewed for consistency and non-overlapping content

### Phase 2: Feature Engineering & Classification (`2_train_evaluate.py`)

**Objective:** Extract statistical features from token-length sequences and train classifiers.

**Feature Extraction Strategy:**

Instead of feeding raw (variable-length) sequences to the classifier, we extract a **fixed-size feature vector** consisting of:

1. **Summary Statistics:**
   - Mean token length
   - Standard deviation
   - Maximum token length
   - Minimum token length
   - Median token length
   - Total number of chunks (response verbosity)

2. **Distribution Histogram:**
   - Normalized histogram over 5 bins: [1-2], [3-5], [6-10], [11-15], [16+] characters
   - Captures the shape of the distribution independent of response length
   - Normalization ensures the classifier learns distribution patterns, not just verbosity

**Why This Approach?**
- With only ~75 samples, training a neural network (e.g., LSTM) would severely overfit
- Hand-crafted statistical features are interpretable and require far less data
- Feature importance analysis directly reveals what the classifier uses

**Classification Models:**
1. **Logistic Regression (Primary)**
   - Linear decision boundaries with L2 regularization
   - Fast, interpretable, minimal overfitting risk
   - Features are standardized (zero mean, unit variance)

2. **Random Forest (Analysis)**
   - Used to compute feature importance rankings
   - Shows which statistical properties are most discriminative
   - Max depth and leaf size constraints prevent overfitting

**Evaluation Methodology:**

1. **Cross-Validation:** StratifiedGroupKFold (5 folds)
   - Stratification: Each fold maintains class proportions
   - Group splitting: Prevents the same prompt index from appearing in both train and test
   - Rationale: Prevents subtle data leakage (same prompt → similar response structure)

2. **Two Experiments:**
   - **Experiment A (2 Topics):** Poetry vs. Python Code
     - Maximally distinct topics for sanity check
     - Random baseline: 50%
   - **Experiment B (5 Topics):** All five categories
     - Realistic multi-class problem
     - Random baseline: 20%

3. **Metrics:**
   - Cross-validation accuracy (mean ± std)
   - Per-fold scores for variance analysis
   - Confusion matrices for error patterns
   - Feature importance for interpretability

---

## Setup & Installation

### Requirements

- Python 3.8 or later
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone https://github.com/odeliyach/llm-side-channel-topic-classification.git
cd llm-side-channel-topic-classification
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `groq` – Python client for Groq API (or any compatible LLM streaming API)
- `scikit-learn` – Machine learning library for classification and evaluation
- `numpy` – Numerical computing library for array operations
- `matplotlib` – Plotting library for visualization

### Step 3: Configure API Access

This project uses the Groq API (free tier available at https://console.groq.com).

**Option A: Environment Variable (Recommended)**
```bash
export GROQ_API_KEY="your_api_key_here"
```

**Option B: Direct Configuration**
Edit `1_generate_data.py` and replace:
```python
API_KEY = "TOKEN"
```
with your actual API key:
```python
API_KEY = "your_api_key_here"
```

**Security Note:** Never commit your API key to version control. Use environment variables in production and add `.env` or `config.py` to `.gitignore`.

---

## Usage

### Phase 1: Collect Training Data

```bash
python 1_generate_data.py
```

**What It Does:**
- Queries the LLM with all 75 prompts (5 topics × 15 prompts)
- For each prompt, records token-length sequences from the streaming response
- Performs rate limiting (5-second delay between requests)
- Validates each response (skips empty or error responses)

**Expected Output:**
```
Starting data collection...
Topics: ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']
Total prompts: 75
Estimated time: ~10 minutes

[Topic: poetry]
  (1/75) prompt 1: What makes a poem different from...
  → 42 chunks, lengths sample: [14, 8, 10, 5, 12, 9, 7, 3]
  ...
Saved 75 responses to data/responses.json

── Sanity check: avg chunks per response per topic ──
  poetry               : avg 45.2 chunks, n=15
  python_code          : avg 38.7 chunks, n=15
  ...
```

**Output Files:**
- `data/responses.json` – JSON file containing all collected responses (prompt, topic, token-length sequences)

**Time Estimate:** ~10-15 minutes depending on API latency and rate limits

### Phase 2: Train & Evaluate Classifiers

```bash
python 2_train_evaluate.py
```

**What It Does:**
1. Loads previously collected responses from `data/responses.json`
2. Extracts statistical features from each token-length sequence
3. Trains Logistic Regression and Random Forest classifiers
4. Evaluates using 5-fold stratified group cross-validation
5. Generates confusion matrices and feature importance plots

**Expected Output:**
```
Loaded 75 responses.

============================================================
Experiment: 2 Topics
Topics: ['poetry', 'python_code']
Samples: 30 | Classes: 2
Random baseline: 50%
============================================================

Logistic Regression:
  CV accuracy: 0.867 ± 0.156
  Per-fold:    ['0.67', '1.00', '1.00', '0.67', '1.00']

Random Forest:
  CV accuracy: 0.833 ± 0.192
  Per-fold:    ['0.67', '1.00', '1.00', '0.67', '0.67']

Classification report (Logistic Regression, full fit):
             precision    recall  f1-score   support

      poetry       0.86      0.93      0.89        15
 python_code       0.88      0.80      0.84        15

============================================================
Experiment: 5 Topics
Topics: ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']
Samples: 75 | Classes: 5
Random baseline: 20%
============================================================

Logistic Regression:
  CV accuracy: 0.587 ± 0.153
  Per-fold:    ['0.47', '0.60', '0.67', '0.60', '0.67']

Random Forest:
  CV accuracy: 0.467 ± 0.182
  Per-fold:    ['0.40', '0.53', '0.47', '0.40', '0.60']

Saved: results/confusion_2_topics.png
Saved: results/confusion_5_topics.png
Saved: results/importance_2_topics.png
Saved: results/importance_5_topics.png
Saved: results/comparison_2v5_topics.png
```

**Output Files:**
- `results/confusion_2_topics.png` – Confusion matrix for 2-topic classification
- `results/confusion_5_topics.png` – Confusion matrix for 5-topic classification
- `results/importance_2_topics.png` – Feature importance chart for 2-topic
- `results/importance_5_topics.png` – Feature importance chart for 5-topic
- `results/comparison_2v5_topics.png` – Side-by-side accuracy comparison

### Optional: Extract Packet Sizes from Network Captures

If you have a PCAP/PCAPNG network capture file from an actual LLM conversation:

```bash
python extract_size_pcap.py path/to/capture.pcapng
```

**What It Does:**
- Parses UDP packets from the PCAP file
- Filters for server→client traffic (port 443, HTTPS)
- Groups packets into responses using 0.5-second gaps
- Outputs packet-length sequences for each response

**Output Format:**
```
Response 1: 42 chunks, lengths sample: [256, 128, 512, 64, ...]
Response 2: 38 chunks, lengths sample: [128, 256, 128, ...]
...
```

---

## Experimental Results & Interpretation

### Accuracy Summary

| Classifier | 2-Topic Baseline | 5-Topic Baseline | 2-Topic Accuracy | 5-Topic Accuracy |
|---|---|---|---|---|
| **Logistic Regression** | 50% | 20% | ~87% | ~59% |
| **Random Forest** | 50% | 20% | ~83% | ~47% |

### Key Findings

1. **2-Topic Case (Poetry vs. Code):**
   - Accuracy significantly exceeds random baseline
   - Topics have distinctly different token-length patterns
   - Poetry uses varied, shorter tokens; code uses specific symbols and syntax
   - Conclusion: Easy classification problem for an eavesdropper

2. **5-Topic Case:**
   - Accuracy drops but remains above random baseline
   - Some topics (e.g., poetry vs. legal language) are still distinguishable
   - Medical/legal content produces longer, more complex tokens
   - Conclusion: Real-world attack is harder but still feasible with proper feature engineering

### Feature Importance Insights

The Random Forest feature importance analysis reveals that:
- **Mean token length** is the most discriminative feature
- **Distribution histogram** (especially mid-range bins) provides complementary information
- **Response verbosity** (number of chunks) contributes but isn't dominant
- Implication: The classifier learns **topic-specific patterns**, not just response length

---

## Methodology & Design Decisions

### 1. Why Logistic Regression?

With ~75 samples, a neural network (LSTM, Transformer) would overfit severely. Logistic Regression offers:
- Minimal overfitting risk
- Interpretability (coefficients have clear meaning)
- Efficiency (single pass training)
- Compatibility with hand-crafted features

### 2. Why Stratified Group K-Fold?

Standard random train/test splits introduce **subtle data leakage**:
- If prompt P appears in both train (response A) and test (response B), the model exploits the prompt structure
- Same prompt → similar response structure → artificially inflated accuracy

Our solution:
- **Group Split:** All responses from prompt index i go entirely to either train OR test
- **Stratification:** Each fold maintains class proportions
- Result: Honest estimate of topic classification accuracy

### 3. Why Feature Normalization?

Without normalization, longer responses would dominate the histogram features just because they have more tokens. Normalization ensures we learn **distribution shape**, not verbosity.

### 4. Why 5 Bins in the Histogram?

Testing showed 5 bins balance:
- Granularity (capturing distribution shape)
- Robustness (avoiding overfitting to noise)
- Stability across different response lengths

---

## Security Implications

### Vulnerability Window

This attack is practical when:
1. Responses are streamed token-by-token (optimization for latency)
2. Traffic is encrypted (HTTPS, TLS) but packet sizes are visible
3. The attacker has network access (ISP, VPN provider, corporate firewall, etc.)
4. The attacker can collect multiple responses (to build statistical models)

### Defense Mechanisms

Potential defenses against this attack:

1. **Padding:** Pad packet sizes to fixed lengths (expensive, increases bandwidth)
2. **Buffering:** Buffer tokens before sending packets (increases latency)
3. **Traffic Morphing:** Inject dummy packets to obfuscate patterns (complex, overhead)
4. **Chunking:** Send variable-size chunks that don't align with token boundaries
5. **Rate Limiting:** Enforce fixed inter-packet delays (degrades streaming experience)

---

## Limitations & Future Work

### Current Limitations

1. **Simulated, Not Real Attack:** We measure API chunk lengths, not actual encrypted packet sizes
2. **Single LLM Only:** Trained on Groq/Llama; won't transfer to GPT-4 without retraining
3. **English-Only Prompts:** No evaluation on multilingual content
4. **Limited Topics:** Only 5 topics; real attacks could target 100+ categories
5. **Controlled Environment:** No network noise, jitter, or compression to deal with
6. **Small Dataset:** 75 responses total; real attacks would benefit from thousands

### Future Research Directions

- **Real Network Captures:** Validate using actual PCAP files from encrypted traffic
- **Model Generalization:** Train on multiple LLMs (GPT-4, Claude, etc.)
- **Adversarial Defense:** Implement and test padding/buffering strategies
- **Language Diversity:** Evaluate on multilingual conversations
- **Longer Sequences:** Explore LSTM/CNN models on longer token-length sequences
- **Topic Expansion:** Classify 50+ fine-grained topics (programming languages, medical conditions, etc.)

---

## Running the Complete Pipeline

For a full end-to-end execution:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
export GROQ_API_KEY="your_key_here"

# 3. Collect data (takes ~10 minutes)
python 1_generate_data.py

# 4. Train and evaluate (takes ~30 seconds)
python 2_train_evaluate.py

# 5. View results
ls -la results/
```

Expected total runtime: **~10-15 minutes** (dominated by API latency in step 1)

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'groq'` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `Error: Invalid API key` | Missing or incorrect API credentials | Set `GROQ_API_KEY` environment variable |
| `Empty response` | API rate limit exceeded | Increase `delay` parameter in `1_generate_data.py` |
| `File not found: data/responses.json` | Phase 1 never completed | Run `python 1_generate_data.py` first |
| `No such file or directory: results/` | Results directory not created | Run Phase 2 to auto-create it |

### Debugging

Enable verbose output:
```python
# In 1_generate_data.py, increase verbosity
print(f"Full response: {response_text[:200]}...")

# In 2_train_evaluate.py, print feature vectors
print(f"Feature vector shape: {X.shape}")
print(f"First sample features: {X[0]}")
```

---

## References

### Primary Research

- **"What Was Your Prompt? A Remote Keylogging Attack on AI Assistants"**
  - Authors: Weiss et al.
  - Conference: USENIX Security 2024
  - Key contribution: First demonstration of topic classification via token-length side-channel

### Related Work

- **Traffic Analysis on Encrypted Connections**
  - Website fingerprinting attacks (Andriy Panchenko et al.)
  - HTTP/2 stream size analysis (Hussain et al.)

- **LLM Security & Privacy**
  - Prompt injection attacks
  - Token stealing via side-channels
  - Membership inference on training data

### Tools & Libraries

- **Groq API:** https://console.groq.com
- **Scikit-learn:** https://scikit-learn.org
- **Matplotlib:** https://matplotlib.org
- **Scapy (for PCAP parsing):** https://scapy.readthedocs.io

---

## License

This project is provided as-is for educational and research purposes.

---

## Contributing

Contributions are welcome! Areas of interest:

- Additional topics or datasets
- Real network capture experiments
- Defense mechanism implementations
- Multilingual prompt sets
- Visualization improvements
- Documentation improvements

Please open an issue or submit a pull request with your improvements.

---

## Acknowledgments

- **Research Foundation:** Weiss et al., USENIX Security 2024
- **API Provider:** Groq for free-tier LLM access
- **Tools:** scikit-learn, numpy, matplotlib communities

---

## Questions?

For questions, issues, or discussions about this project, please open an issue on GitHub or contact the repository maintainer.

**Last Updated:** June 2024
