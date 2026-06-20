# Project Status & Roadmap

Current status, known limitations, and future work.

---

## Current Status: ✅ Feature Complete

**Version:** 0.1.0 (Initial Release)

**Date:** June 2024

**Presented:** June 29, 2024 (USENIX Security 2024 Seminar)

---

## What Works

- ✅ Data collection from Groq/Llama API in streaming mode
- ✅ Feature extraction from token-length sequences
- ✅ Logistic Regression & Random Forest classification
- ✅ Cross-validation with proper train/test splits
- ✅ Visualization (confusion matrices, feature importance)
- ✅ Comprehensive documentation
- ✅ 2-topic classification: ~87% accuracy (Poetry vs. Code)
- ✅ 5-topic classification: ~59% accuracy (all topics)

---

## Known Limitations

### Limitation 1: Simulated vs. Real Traffic ⚠️

**Status:** Acknowledged, not resolved

**Description:** We measure API chunk lengths, not actual encrypted packet sizes

**Impact:** API chunks may batch tokens; real packets include encryption overhead

**Resolution:** Bonus 1 (not yet done) — use Wireshark to capture real traffic

**Priority:** Medium (code is correct; validation is the question)

---

### Limitation 2: Single LLM ⚠️

**Status:** Acknowledged, not addressed

**Description:** Trained on Llama 4 Scout 17B; won't transfer to GPT-4 or Claude without retraining

**Impact:** Different LLMs use different tokenizers (tiktoken, SentencePiece, etc.)

**Resolution:** Would need to train separate classifiers for each LLM

**Priority:** Medium (expected behavior; documented)

---

### Limitation 3: Small Dataset ⚠️

**Status:** Acknowledged, acceptable for course project

**Description:** 75 responses vs. 1.5M in the paper

**Impact:** Higher variance, overfitting risk, lower expected accuracy

**Resolution:** Could increase to 300-500 responses for better generalization

**Priority:** Low (75 is sufficient for proof-of-concept)

---

### Limitation 4: Predefined Topics ⚠️

**Status:** Acknowledged, intentional

**Description:** Hand-picked 5 topics (poetry, code, medical, cooking, legal)

**Impact:** May have cherry-picked easy-to-separate topics

**Resolution:** Test with random/diverse topics; measure performance degradation

**Priority:** Low (limitations are discussed in presentation)

---

### Limitation 5: English-Only ⚠️

**Status:** Acknowledged

**Description:** All prompts in English; no multilingual evaluation

**Impact:** Results may not generalize to non-English LLM interactions

**Resolution:** Would require generating prompts in multiple languages

**Priority:** Low (out of scope for initial project)

---

### Limitation 6: No Defense Evaluation ⚠️

**Status:** Acknowledged, discussed

**Description:** We discuss defense mechanisms (padding, buffering) but don't implement them

**Impact:** No empirical validation of defenses

**Resolution:** Implement padding + test classifier robustness

**Priority:** Low (could be future work)

---

## What Remains (Bonus Work)

### Bonus 1: Real Traffic Validation 🔬

**Goal:** Capture real encrypted traffic and validate packet-size patterns

**Approach:**
1. Run Wireshark while making Groq/Claude API calls
2. Extract packet sizes from PCAP files
3. Compare to API-reported token lengths
4. Show correlation — the leak is real

**Estimated Time:** 2-4 hours

**Status:** Not started

**Priority:** High (would significantly strengthen paper)

---

### Bonus 2: Text Reconstruction 🔬

**Goal:** Fine-tune a seq2seq model (e.g., T5) to reconstruct text from token lengths

**Approach:**
1. Generate synthetic token-length sequences with labels
2. Fine-tune T5 encoder-decoder
3. Measure reconstruction accuracy (character-level or BLEU)
4. Compare to paper's reported ~29% accuracy

**Estimated Time:** 4-6 hours

**Status:** Not started

**Priority:** Medium (matches paper's advanced capability, but harder)

---

### Bonus 3: Defense Mechanisms 🛡️

**Goal:** Implement and test defenses (padding, buffering, chunking)

**Approach:**
1. Implement padding: Add dummy tokens to fixed-length packets
2. Train classifier on padded sequences
3. Measure accuracy drop (is defense effective?)
4. Benchmark latency/bandwidth overhead

**Estimated Time:** 3-5 hours

**Status:** Not started

**Priority:** Low (research direction, not core requirement)

---

### Bonus 4: Model Generalization 📊

**Goal:** Train on one LLM, test on another

**Approach:**
1. Collect responses from GPT-4, Claude, Gemini (if APIs available)
2. Train classifier on Llama; test on GPT-4
3. Report transfer accuracy
4. Fine-tune and retrain on GPT-4

**Estimated Time:** 6-8 hours (depends on API access)

**Status:** Not started

**Priority:** Low (ambitious, requires multiple API keys)

---

## Known Bugs

**None reported.** Code has been tested end-to-end on the full pipeline.

---

## Recent Changes (CHANGELOG)

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**v0.1.0 (June 2024)**
- Initial release
- Full data collection + classification pipeline
- Comprehensive documentation
- Professional repository structure

---

## How to Help

### For Researchers
- Test on different LLMs (GPT-4, Claude, Gemini)
- Implement Bonus 1 (real traffic validation)
- Extend to multilingual content
- Test on different topic sets

### For Developers
- Refactor code into modular `src/` directory
- Add unit tests (`tests/`)
- Implement CI/CD workflows
- Improve error handling

### For Documentarians
- Expand guides with screenshots
- Create video tutorials
- Write blog post about the research
- Create FAQ section

---

## Roadmap

### Short Term (Weeks 1-2)
- [ ] Finalize documentation
- [ ] Create CITATION.bib
- [ ] Add Makefile
- [ ] Create GitHub issue templates

### Medium Term (Weeks 3-4)
- [ ] Bonus 1: Real traffic validation
- [ ] Unit tests
- [ ] Refactor to `src/` directory
- [ ] CI/CD workflows

### Long Term (Weeks 5+)
- [ ] Bonus 2: Text reconstruction
- [ ] Multi-LLM support
- [ ] Defense mechanism implementations
- [ ] Publish supplementary results

---

## Contact & Questions

**Lead Researchers:**
- Odeliya Chindrich
- Alin Prătescu

**GitHub:** [@odeliyach](https://github.com/odeliyach)

**Questions?** Open an issue or contact via email.

---

## Acknowledgments

- **Research Foundation:** Weiss et al., USENIX Security 2024
- **API Provider:** Groq for free-tier LLM access
- **Tools:** scikit-learn, numpy, matplotlib communities
- **Institution:** [Your University/Organization]

---

**Last Updated:** June 2024
