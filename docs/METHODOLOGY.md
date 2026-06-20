# Detailed Methodology

This document provides a comprehensive explanation of our experimental design, data collection, feature engineering, and evaluation methodology.

**Research Foundation:** "What Was Your Prompt? A Remote Keylogging Attack on AI Assistants" – Weiss et al., USENIX Security 2024

---

## What Are We Trying to Show?

LLM responses are streamed token-by-token over the network. Even over encrypted HTTPS traffic, an eavesdropper can observe the *size* of each token as it arrives — because the payload size of each packet maps directly to the number of characters in that token.

**Key Question:** Can you determine the topic of a conversation from only token-length sequences?

**Hypothesis:** Yes. Different topics produce structurally different token-length patterns:
- Poetry: short lines, rhythmic token lengths, frequent 1-token punctuation
- Python Code: indentation tokens (spaces), symbols (`:`, `()`, `=`), short identifiers
- Medical Advice: long technical terms, dense sentences, high mean token length
- Cooking: imperative short sentences, numbered steps, moderate length
- Legal/Contracts: very long dense sentences, formal connectives, high token count

---

## Data Collection (Phase 1)

### Prompt Design

- **15 prompts per topic** (75 total responses)
- Each prompt is deliberately **varied in framing, length, and angle**
- Variation prevents the classifier from memorizing prompt-specific patterns
- All prompts reviewed manually to ensure no unintended duplicates

**Topics and Example Prompts:**

1. **Poetry** (literary analysis, forms, history)
   - "What makes a poem different from other forms of writing?"
   - "Explain the concept of meter and rhythm in poetry."
   - "Compare Romantic poetry to Modernist poetry."

2. **Python Code** (algorithms, language features, best practices)
   - "Write a Python function to sort a list of integers."
   - "Explain the difference between list comprehensions and generator expressions."
   - "What are decorators in Python and how do they work?"

3. **Medical Advice** (diseases, treatments, anatomy)
   - "What are the symptoms of type 2 diabetes?"
   - "How should I treat a minor burn at home?"
   - "Explain what causes high blood pressure."

4. **Cooking** (techniques, food science, recipes)
   - "What's the difference between sautéing and stir-frying?"
   - "Explain the Maillard reaction in cooking."
   - "What are the benefits of sous-vide cooking?"

5. **Legal** (contracts, procedures, concepts)
   - "What is the difference between a tort and a crime?"
   - "Explain the concept of contract consideration."
   - "What does it mean to have standing in a lawsuit?"

### Why Streaming Mode?

- In a real attack, the adversary intercepts packets as they're generated
- Streaming mode simulates this by exposing partial outputs chunk-by-chunk
- Each chunk's length reveals information about the tokens
- **Limitation:** API chunks are not exactly 1-token; they may batch a few tokens. This is acknowledged as a difference from real network traffic.

### Data Recording

For each API response:
- **Token-length sequence:** `[3, 5, 12, 2, ...]` (only lengths, no content)
- **Topic label:** assigned automatically based on which prompt was sent
- **Response ID:** for tracking purposes

We **do not record the actual text** — this simulates the eavesdropper's constraints.

### API Details

- **Provider:** Groq
- **Model:** Llama 4 Scout 17B (llama-scout-2b or specified variant)
- **Rate Limiting:** 5-second delay between requests (respects free tier limits)
- **Expected Duration:** ~10-15 minutes for 75 requests

---

## Feature Engineering (Phase 2)

### Why Hand-Crafted Features?

With only ~75 samples, training a neural network (LSTM, Transformer) would severely overfit.

Instead, we extract **statistical features** that are:
- **Interpretable:** We can explain why each feature matters
- **Efficient:** Require minimal training data
- **Domain-motivated:** Based on linguistic intuition about token patterns

### Feature Extraction Pipeline

For each token-length sequence, we extract:

**1. Summary Statistics (6 features)**
- **Mean token length:** Average character count per token
- **Standard deviation:** Variability in token lengths
- **Median token length:** Middle value
- **Min token length:** Smallest token
- **Max token length:** Largest token
- **Total token count:** Response verbosity

**2. Distribution Histogram (5 features)**

We normalize the token-length distribution into bins:
- **[1-2]:** Very short tokens (single characters, punctuation, spaces)
- **[3-5]:** Short tokens (small words like "the", "and", code symbols)
- **[6-10]:** Medium tokens (common words)
- **[11-15]:** Long tokens (technical terms, compound words)
- **[16+]:** Very long tokens (rare, but present in medical/legal text)

Each bin is normalized by total token count, so we learn **distribution shape**, not verbosity.

### Why These Features?

- **Poetry** expects high frequency in [1-2] bin (short, rhythmic tokens)
- **Code** expects high frequency in [1-5] bin (spaces, operators, short identifiers)
- **Medical/Legal** expect high frequency in [11-15] and [16+] bins (technical terminology)
- **Cooking** is intermediate — mix of short imperatives and longer ingredient names

### Feature Normalization

All features are standardized (zero mean, unit variance) before classification. This prevents longer responses from dominating the histogram features.

---

## Classification Models

### Logistic Regression (Primary Classifier)

- **Why:** Simple, interpretable, minimal overfitting risk
- **Configuration:** L2 regularization, standardized features
- **Training:** Single pass, fast
- **Interpretability:** Coefficients show which features are most important

### Random Forest (Secondary, for Feature Importance)

- **Why:** Provides non-linear decision boundaries; feature importance rankings
- **Configuration:** Max depth constraint, leaf size limit (prevents overfitting)
- **Use:** Confirms feature importance findings from Logistic Regression

---

## Evaluation Methodology

### Cross-Validation Strategy: Stratified Group K-Fold

**Standard random train/test split problem:**
- If the same prompt appears in both train and test, the model exploits the prompt structure
- Example: Prompt P → Response A (train), Response B (test) → Similar structure → Inflated accuracy

**Our solution:**
1. **Group Split:** All responses from prompt index i go entirely to either train OR test
2. **Stratification:** Each fold maintains class proportions
3. **Result:** Honest estimate of topic classification accuracy without data leakage

**Configuration:** 5 folds, stratified by topic, grouped by prompt

### Two Experiments

**Experiment A: 2-Topic Classification (Poetry vs. Python Code)**
- Maximally distinct topics (sanity check)
- Easier problem — should achieve high accuracy
- Random baseline: 50%

**Experiment B: 5-Topic Classification (All topics)**
- Realistic multi-class problem
- Harder problem — real attacker doesn't know which topics to compare
- Random baseline: 20%

### Reported Metrics

For each experiment:
1. **Cross-validation accuracy:** mean ± standard deviation across folds
2. **Per-fold scores:** individual accuracy for each fold (shows variance)
3. **Confusion matrix:** reveals which topics get confused
4. **Precision/Recall:** per-class performance
5. **Feature importance:** which statistical features drive the classifier

---

## Methodological Concerns & Mitigations

### Concern 1: Prompt Selection Bias
**Question:** Are results specific to our writing style?

**Mitigation:** We deliberately varied prompts in framing, length, and angle. Ideally, we'd have an external party generate prompts, but LLM-generated diverse prompts are acceptable per the syllabus.

### Concern 2: Length Confound
**Question:** Does the classifier just learn response length, not topic patterns?

**Mitigation:**
- Feature importance analysis reveals which features drive the classifier
- We report ablation results: accuracy without the "total token count" feature
- If accuracy drops significantly, length is important; if not, distribution shape is the signal

### Concern 3: Train/Test Contamination
**Question:** Same prompt in train and test leaks information?

**Mitigation:** We split by prompt index, not randomly by response. All responses from a prompt are in exactly one fold.

### Concern 4: LLM Tokenizer Dependence
**Question:** Classifier trained on Groq/Llama won't transfer to GPT-4?

**Answer:** Correct. Each LLM uses a different tokenizer (tiktoken, SentencePiece, etc.), producing different token-length distributions. A real attacker would need to identify or infer which LLM they're eavesdropping on. We acknowledge this as a limitation.

### Concern 5: Small Dataset
**Question:** 75 samples has high variance?

**Answer:** Yes. The paper used 1.5M dialogues from UltraChat. We use 75 responses, which is much smaller. This is appropriate for a course project but acknowledged as a limitation.

### Concern 6: Cherry-Picked Topics
**Question:** Did we pick easy topics to inflate accuracy?

**Answer:** Possibly. Poetry vs. Code are structurally distinct, which makes 2-topic classification easier. The 5-topic experiment is harder and more realistic. We report both and discuss which topic pairs are harder to separate (e.g., Medical vs. Legal vs. Legal might be confused due to similar vocabulary).

---

## Reproducing the Experiment

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for exact commands and expected outputs.

---

## References

- **"What Was Your Prompt? A Remote Keylogging Attack on AI Assistants"**
  - Authors: Weiss et al.
  - Conference: USENIX Security 2024
  - DOI: [Check ACM DL](https://dl.acm.org/)

- **Related Work:**
  - Website fingerprinting (Andriy Panchenko et al.)
  - HTTP/2 stream size analysis (Hussain et al.)
  - LLM privacy attacks (membership inference, prompt extraction)
