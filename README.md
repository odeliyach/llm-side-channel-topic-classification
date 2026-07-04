# LLM Side-Channel Topic Classification

Reproducing the topic classification attack from **"What Was Your Prompt? A Remote Keylogging Attack on AI Assistants"** (Weiss et al., USENIX Security 2024).

Week 9 experiment — ML Security Seminar.

## What this does

LLM responses are streamed token by token. Even over encrypted HTTPS, the size of each streamed chunk leaks the length of the token inside it. An eavesdropper who can't read the content can still see a sequence like `[3, 5, 12, 2, 8, ...]`.

This project shows that sequence alone is enough to classify the topic of the conversation, with no access to the actual text. We start with the base experiment (75 responses, 15 per topic) and then scale it up to 500 responses (100 per topic) to check whether the result holds up with more data.

## Project structure

```
scripts/
  1_generate_data.py            Collects the original 75-response dataset (15 prompts/topic) via streaming
  2_train_evaluate.py           Extracts features, trains classifiers, evaluates (StandardScaler + C=0.1 regularization)
  2_train_evaluate_original.py  Earlier, unregularized version — kept only to reproduce the overfitting comparison at scale (see below)
  3_pairwise_heatmap.py         Extends 2_train_evaluate.py: CV accuracy for every topic pair, plotted as a 5x5 heatmap
  5_build_prompts_no_api.py     Generates 85 new prompts/topic (100 total/topic) with zero API calls, for the 500-response run
  6_collect_responses_100.py    Collects streaming responses for the 100-prompt pool -> data/responses_100.json
  extract_size_pcap.py          Extracts packet sizes from a real PCAP capture (Bonus 1)
  normalization.py              Log-scales real Gemini packet sizes so they're comparable to API chunk lengths (Bonus 1)

data/
  README.md                     Data format notes
  generation_log.txt            Terminal output from running scripts/1_generate_data.py
  responses.json                75-response dataset (15/topic), from scripts/1_generate_data.py
  prompts_candidate_100.json    100-prompt-per-topic pool, from scripts/5_build_prompts_no_api.py
  responses_100.json            500-response dataset (100/topic), from scripts/6_collect_responses_100.py
  reponses_gemini_2.txt, responses_gemini_catched.txt   Raw real-traffic captures used for Bonus 1

results/
  run1_overfitting_75_promts/         First run, 75 responses — full-fit accuracy far above CV accuracy (overfitting signal)
  run2_75_prompts/                    Fixed run, 75 responses — the numbers used in the original presentation
  500_prompts_run/                    500 responses, regularized model (C=0.1) — the main scaled-up result
  500_promts_c=1_run/                 Same 500 responses, weaker regularization (C=1) — isolates whether regularization strength still matters at this scale
  500_promts_overfitting_check_run/   Same 500 responses run through the ORIGINAL unregularized script — checks whether the overfitting seen at 75 samples shrinks with more data
  bonus_1/                            Real packet capture of a Gemini conversation (Bonus 1), outputs 1-3
```

## Setup

```bash
pip install -r requirements.txt
```

Get a free API key at [console.groq.com](https://console.groq.com), then either:
- set it as an environment variable: `export GROQ_API_KEY="your_key"`, or
- copy `.env.example` to `.env` and fill it in

We originally planned to use Gemini, but its free tier was cut to 20 requests/day during the project, which isn't enough for our prompt volume. We switched to Llama 4 Scout via Groq (1,000 requests/day free, supports streaming).

## Running

**Base experiment (75 responses, ~10 min, 75 API calls):**
```bash
python scripts/1_generate_data.py
python scripts/2_train_evaluate.py
```

**Pairwise topic difficulty heatmap:**
```bash
python scripts/3_pairwise_heatmap.py
```

**Scaled-up experiment (500 responses, ~45-90 min, 500 API calls):**
```bash
python scripts/5_build_prompts_no_api.py   # builds the 100-prompt-per-topic pool, no API calls
python scripts/6_collect_responses_100.py  # collects the 500 responses, resumable if it crashes mid-run
python scripts/2_train_evaluate.py         # point it at data/responses_100.json
```

## Experiments

- **2 topics:** Poetry vs. Python code — the most structurally distinct pair, used as a sanity check
- **5 topics:** Poetry, Python code, medical advice, cooking, legal — the realistic, harder setting

## Results

### 75-response run (`results/run2_75_prompts/`)

| Classifier          | 2-topic CV accuracy | 5-topic CV accuracy |
|----------------------|:---:|:---:|
| Logistic Regression | 83.3% | 44.0% |
| Random Forest       | 80.0% | 44.0% |
| Random baseline     | 50% | 20% |

### 500-response run (`results/500_prompts_run/`)

| Classifier          | 2-topic CV accuracy | 5-topic CV accuracy |
|----------------------|:---:|:---:|
| Logistic Regression | 90.5% | 52.4% |
| Random Forest       | 93.5% | 49.2% |
| Random baseline     | 50% | 20% |

Both sample sizes land well above chance in both settings, and accuracy actually improves at 500 responses rather than degrading, which suggests the 75-sample result wasn't a fluke of a small dataset. Accuracy still drops substantially from 2 to 5 topics in both cases, which is expected: the realistic open-ended classification problem is harder than the best-case sanity check.

Python code remains the easiest topic to identify at both scales (near-perfect recall, its tokenizer pattern is very distinctive). Poetry stays the hardest in the 5-topic setting, frequently confused with cooking and legal text; see `results/500_promts_overfitting_check_run/` and the pairwise heatmap (`scripts/3_pairwise_heatmap.py`) for which specific topic pairs drive that confusion.

The top feature at both scales is `seq_len` / `max` (sequence length and maximum token length), which is worth discussing as a limitation, see below.

### Regularization at scale: `500_promts_c=1_run/` vs `500_prompts_run/`

At 75 samples, regularization (C=0.1) mattered: it was part of fixing the overfitting seen in `run1_overfitting_75_promts/`. At 500 samples, comparing C=0.1 (`500_prompts_run/`, 52.4% 5-topic LR) against C=1 (`500_promts_c=1_run/`, 51.0% 5-topic LR) shows almost no difference. This is a useful finding for the presentation: regularization strength stops being the deciding factor once there's enough data, the model isn't starved for signal anymore.

### Does the overfitting signal from 75 samples persist at 500? (`500_promts_overfitting_check_run/`)

We reran the *original*, unregularized script (`scripts/2_train_evaluate_original.py`) on the 500-response dataset to see if the full-fit-vs-CV accuracy gap from `run1_overfitting_75_promts/` (100% full-fit vs. 83% CV) shows up again. At 500 samples the gap is much smaller (about 55% full-fit vs. 51-59% CV depending on classifier), which supports the diagnosis that the original gap was a small-sample artifact rather than a flaw in the feature set itself.

## Methodology notes

- **Train/test split is grouped by prompt index, not by response.** If the same prompt appeared in both train and test, the model could learn the prompt's structure rather than the topic's. Splitting by prompt index prevents this.
- **Features are statistics over the token-length sequence**, not the raw sequence: mean, std, max, min, median, sequence length, and a normalized histogram. With ~75 samples, a model that consumes raw sequences (e.g. an LSTM) would overfit; hand-crafted features on top of a linear classifier are more appropriate here. This assumption is tested directly by the 500-response run above.
- **Tokenizer dependence:** the classifier is trained and evaluated only on Llama/Groq responses. A different LLM (e.g. GPT-4) uses a different tokenizer, so token-length distributions would differ. A real attacker would need to know or infer which LLM they're targeting.
- **Simulated, not sniffed (for the main dataset):** we collect token lengths via the API's streaming mode rather than real packet capture. `scripts/extract_size_pcap.py` and `scripts/normalization.py` validate this against real Gemini traffic instead (Bonus 1, see `results/bonus_1/`), though the chunk-to-packet mapping isn't one-to-one in practice.

## Limitations

- Prompts were written by us (with LLM assistance for diversity, and mechanically via `scripts/5_build_prompts_no_api.py` for the 500-response run); topic and prompt selection could bias results
- Only 5, deliberately distinct topics — harder, more similar topic pairs (e.g. medical vs. legal) show meaningfully lower accuracy, see the pairwise heatmap
- Single LLM (Llama 4 Scout); doesn't necessarily generalize to other models' tokenizers

## References

- Weiss et al., *"What Was Your Prompt? A Remote Keylogging Attack on AI Assistants,"* USENIX Security 2024
