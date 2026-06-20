# Contributing Guidelines

Thank you for your interest in contributing to this research project! We welcome contributions of all kinds: bug reports, documentation improvements, new features, and research extensions.

---

## How to Contribute

### 1. Report Issues

Found a bug or have a suggestion? Open a GitHub issue:

1. Check existing issues first (no duplicates)
2. Describe the problem clearly
3. Include steps to reproduce
4. Attach relevant logs or screenshots

**Issue Template:**
```
## Description
[Clear description of the issue]

## Steps to Reproduce
1. Run ...
2. Observe ...
3. Expected: ...

## Actual Result
[What happened instead]

## Environment
- Python version: 
- OS: 
- Groq API model used:
```

### 2. Suggest Enhancements

Have an idea? Open a discussion or feature request:

1. Explain the motivation
2. Describe the proposed solution
3. Discuss alternatives you've considered
4. Note any potential limitations

### 3. Submit Code Changes

Follow these steps to contribute code:

#### Step 1: Fork & Branch

```bash
git clone https://github.com/YOUR_USERNAME/llm-side-channel-topic-classification.git
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-new-topics` — new feature
- `bugfix/fix-api-timeout` — bug fix
- `docs/improve-setup-guide` — documentation
- `refactor/reorganize-code` — code cleanup

#### Step 2: Make Changes

- Write clear, commented code
- Follow PEP 8 style guidelines
- Update docstrings
- Add tests for new functionality

#### Step 3: Test Your Changes

```bash
# Run the full pipeline
python 1_generate_data.py
python 2_train_evaluate.py

# Check for obvious errors
python -m py_compile *.py
```

#### Step 4: Commit with Clear Messages

```bash
git add .
git commit -m "Brief description of changes"
```

**Commit message guidelines:**
- Use imperative mood ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Explain why the change was made, not just what

Example:
```
Improve feature extraction documentation

Add docstrings to explain histogram binning strategy
and rationale for each statistical feature.
```

#### Step 5: Push & Open PR

```bash
git push origin feature/your-feature-name
```

Then on GitHub, click "New Pull Request" and fill in the template.

**PR Template:**
```
## Description
[Summarize your changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code cleanup

## Related Issues
Closes #123

## Testing
[Describe how you tested the changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Comments added for non-obvious sections
- [ ] Documentation updated
- [ ] No new warnings generated
```

---

## Code Style

### Python Conventions

We follow **PEP 8** with these specifics:

- **Line length:** 100 characters (slightly more than PEP 8's 79)
- **Indentation:** 4 spaces
- **Imports:** Organize as: stdlib, third-party, local
- **Naming:**
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Docstring Format

Use Google-style docstrings:

```python
def extract_features(token_lengths: list) -> np.ndarray:
    """
    Extract statistical features from a token-length sequence.
    
    Args:
        token_lengths: List of token character lengths.
    
    Returns:
        Feature vector as a numpy array of shape (11,).
    
    Raises:
        ValueError: If token_lengths is empty.
    
    Example:
        >>> lengths = [3, 5, 2, 8]
        >>> features = extract_features(lengths)
        >>> features.shape
        (11,)
    """
```

---

## Research Contributions

### Extension Ideas

**Easy (good for beginners):**
- Add more prompts to existing topics
- Create new topic categories
- Improve visualization plots
- Write documentation on specific sections

**Medium:**
- Implement new classifiers (SVM, XGBoost)
- Add ablation studies (feature importance analysis)
- Extend to multilingual prompts
- Test generalization across LLM models

**Advanced:**
- Implement real traffic capture + analysis (Bonus 1)
- Develop text reconstruction model (Bonus 2)
- Implement defense mechanisms (padding, buffering)
- Test adversarial robustness

### Before Starting Major Work

1. Open an issue describing your idea
2. Wait for feedback from maintainers
3. Discuss implementation approach
4. Coordinate to avoid duplicate work

---

## Documentation Improvements

Good documentation is crucial. Help us improve:

- **README.md** — Getting started, quick reference
- **docs/SETUP.md** — Installation & configuration
- **docs/METHODOLOGY.md** — Experimental design details
- **docs/RESULTS.md** — Results interpretation
- **Code comments** — Explain non-obvious logic

---

## Conduct

We're committed to providing a welcoming, inclusive environment. Please:

- Be respectful and constructive
- Assume good intent
- Provide feedback kindly
- Welcome diverse perspectives

Unacceptable behavior (harassment, discrimination, etc.) will not be tolerated.

---

## Recognition

Contributors will be acknowledged:

- In the repository's [CHANGELOG.md](CHANGELOG.md)
- In pull request discussions
- In any publications using this code

---

## Questions?

- Open an issue for questions about contribution process
- Email repository maintainer for sensitive topics
- Check existing documentation first

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License (same as the project).

---

Thank you for contributing! 🎉
