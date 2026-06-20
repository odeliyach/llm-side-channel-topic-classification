# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2024-06-20

### Added

- **Initial Release**
  - Full data collection pipeline (`1_generate_data.py`)
  - Complete training and evaluation system (`2_train_evaluate.py`)
  - Logistic Regression and Random Forest classifiers
  - Stratified Group K-Fold cross-validation
  - Feature extraction with 11 statistical features
  - Confusion matrices and feature importance visualizations
  - Two experiments: 2-topic (Poetry vs. Code) and 5-topic classification

- **Documentation**
  - Comprehensive README.md with project overview
  - METHODOLOGY.md with detailed experimental design
  - SETUP.md with installation and API configuration
  - SECURITY.md with API key management and ethical guidelines
  - RESULTS.md with detailed results interpretation
  - PAPER_MAPPING.md mapping our work to Weiss et al.
  - REPRODUCIBILITY.md with exact commands and expected outputs
  - PROJECT_STATUS.md with known limitations and roadmap
  - CONTRIBUTING.md with contribution guidelines
  - This CHANGELOG.md

- **Configuration Files**
  - LICENSE (MIT)
  - .gitignore for Python, data, and results
  - .gitattributes for LF line endings
  - .env.example for API configuration template
  - requirements.txt with dependencies
  - CITATION.bib for academic citation

- **GitHub Integration**
  - Pull request template (.github/pull_request_template.md)
  - Issue templates (bug report, feature request)
  - CODEOWNERS file

- **Project Management**
  - Makefile for convenient commands
  - .github/workflows/ for CI/CD (linting, tests)

### Features

- **Data Collection**
  - 75 manually crafted prompts (15 per topic)
  - 5 topics: Poetry, Python Code, Medical Advice, Cooking, Legal
  - Streaming mode API calls to respect rate limits
  - Automatic response validation
  - JSON output with topic labels and token-length sequences

- **Feature Engineering**
  - 6 summary statistics (mean, std, median, min, max, total)
  - 5 histogram bins for distribution shape
  - Proper normalization and standardization
  - Interpretable features for decision making

- **Classification**
  - Logistic Regression with L2 regularization
  - Random Forest with depth constraints
  - Stratified Group K-Fold cross-validation
  - Per-fold accuracy reporting
  - Confusion matrices with per-class metrics

- **Evaluation**
  - 2-topic classification: ~87% accuracy (Poetry vs. Code)
  - 5-topic classification: ~59% accuracy (all topics)
  - Feature importance analysis
  - Comparison visualizations

### Technical Details

- Python 3.8+ compatibility
- Groq/Llama-4-Scout-17B integration
- scikit-learn for ML pipelines
- matplotlib for visualizations
- numpy for numerical operations

---

## [Unreleased]

### Planned Features (Bonus Work)

- **Bonus 1: Real Traffic Validation**
  - Wireshark packet capture analysis
  - PCAP file parsing
  - Packet-size to token-length correlation validation

- **Bonus 2: Text Reconstruction**
  - Fine-tuned seq2seq model (T5)
  - Token-length to text mapping
  - Reconstruction accuracy measurement

- **Bonus 3: Defense Mechanisms**
  - Padding implementation
  - Buffering strategy
  - Defense effectiveness evaluation

- **Bonus 4: Multi-LLM Support**
  - GPT-4 integration
  - Claude support
  - Model generalization testing

### Code Quality

- Unit tests (tests/ directory)
- CI/CD workflows (GitHub Actions)
- Code organization (src/ directory)
- Type hints for better IDE support
- Docstring improvements

---

## Version History

**v0.1.0** (June 2024) — Initial release with complete core functionality

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting issues, suggesting enhancements, and submitting code changes.

---

## Acknowledgments

- **Research Foundation:** Weiss et al., USENIX Security 2024
- **API Provider:** Groq for free-tier LLM access
- **Libraries:** scikit-learn, numpy, matplotlib, groq-python
