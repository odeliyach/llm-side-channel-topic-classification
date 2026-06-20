# Security & API Management

This document covers security best practices, API key management, rate limiting, and ethical considerations for side-channel research.

---

## API Key Security

### Never Commit Your Key

API keys are secrets. If committed to GitHub, anyone can use your quota or run up costs.

**Prevention:**
1. Keys are in `.gitignore` by default
2. Use environment variables, not hardcoded values
3. If you accidentally commit a key, regenerate it immediately on [console.groq.com](https://console.groq.com)

### Safe Configuration Methods

#### Method 1: Environment Variable (Recommended)

```bash
export GROQ_API_KEY="your_key_here"
python 1_generate_data.py
```

#### Method 2: `.env` File (Local Development)

```bash
cp .env.example .env
# Edit .env and add your key
cat .env
# GROQ_API_KEY=your_key_here
```

Then in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
```

#### Method 3: Secrets Management (Production)

For deployed systems, use a secrets manager:
- AWS Secrets Manager
- HashiCorp Vault
- GitHub Secrets (for CI/CD)
- Azure Key Vault

### Rotating API Keys

If you suspect a key is compromised:

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Delete the old key
3. Create a new key
4. Update your environment variable or `.env` file
5. Restart any running services

---

## Rate Limiting & Quota Management

### Free Tier Limits

- **Requests per day:** 1,500
- **Requests per minute:** 15
- **No credit card required**

### Respecting Rate Limits

Our `1_generate_data.py` includes a **5-second delay** between requests:

```python
DELAY_SECONDS = 5  # 12 requests per minute, well under 15 req/min limit
```

This leaves room for variability and other users sharing the free tier.

### Monitoring Usage

Check your quota on [console.groq.com/usage](https://console.groq.com/usage):
- Daily request count
- API response times
- Error rates

### If Rate Limits Are Exceeded

1. **Immediate:** Wait 60 seconds, then retry
2. **Persistent issue:** Increase `DELAY_SECONDS` in `1_generate_data.py`
3. **Solution:** Upgrade to a paid plan if you need higher limits

### Estimated Quota for This Project

- **Data Collection (Phase 1):** 75 requests
- **Testing:** ~20 requests
- **Total:** ~95 requests (6% of daily free tier)

You can run the full pipeline **multiple times per day** within free tier limits.

---

## Data Privacy

### What We Collect

- **Token-length sequences only** (no actual text)
- **Topic labels** (assigned by us, not from API)
- **Metadata:** response IDs, timestamps

### What We Don't Collect

- Actual LLM response text
- User information
- Conversation history
- PII or sensitive data

### Data Storage

- **Local only:** All data is stored in `data/` directory on your machine
- **No external uploads:** We don't send data anywhere
- **Encryption:** None needed since we record only lengths, not content

### GDPR / Privacy Compliance

This project:
- ✅ Collects only non-sensitive data
- ✅ Uses fictional prompts (no real user conversations)
- ✅ Doesn't require user consent (no user data involved)
- ✅ No data sharing with third parties

---

## Ethical Considerations

### Side-Channel Attacks as Research

This project studies a vulnerability disclosed responsibly in peer-reviewed research (Weiss et al., USENIX Security 2024). We:

1. **Don't sniff real traffic** — we use API-based simulation
2. **Don't attack real users** — we generate synthetic prompts
3. **Document limitations** — acknowledge differences from real attacks
4. **Propose defenses** — discuss padding, buffering, rate limiting

### Responsible Disclosure

The paper was published after disclosure to affected parties (OpenAI, Microsoft). These companies have since patched the vulnerability.

### Ethical Use

Only use this project for:
- ✅ Academic research and learning
- ✅ Security research and defense
- ✅ Understanding LLM vulnerabilities

Do not use for:
- ❌ Attacking real users or systems
- ❌ Sniffing actual encrypted traffic without authorization
- ❌ Commercial exploitation

---

## Defense Mechanisms

This attack can be mitigated with:

1. **Padding:** Pad packet sizes to fixed lengths (cost: bandwidth)
2. **Buffering:** Buffer tokens before sending packets (cost: latency)
3. **Traffic Morphing:** Inject dummy packets to obfuscate patterns (cost: overhead)
4. **Chunking:** Send variable-size chunks that don't align with token boundaries
5. **Rate Limiting:** Enforce fixed inter-packet delays (cost: user experience)

Research into practical defenses is an open problem.

---

## Code Security

### Dependencies

All dependencies are from reputable sources:
- `groq` — Official Python client for Groq API
- `scikit-learn` — Industry-standard ML library
- `numpy`, `matplotlib` — Standard scientific Python stack

We recommend:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Checking for Vulnerabilities

```bash
pip install safety
safety check
```

### Input Validation

The scripts validate API responses:
- Reject empty or malformed responses
- Log errors without crashing
- Retry on transient failures (with backoff)

---

## Incident Response

### If an API Key is Compromised

1. **Immediately:** Regenerate the key on Groq console
2. **Check usage:** Review recent API calls for unauthorized activity
3. **Notify:** If you're on an account with others, inform them
4. **Document:** Note the incident date and actions taken

### If the Repository is Compromised

1. **Audit:** Check `.env` file for exposed keys (shouldn't be, it's in `.gitignore`)
2. **Regenerate:** All API keys
3. **Notify:** Repository collaborators

### Reporting Security Issues

If you discover a vulnerability in this project:

1. **Do not** open a public GitHub issue
2. **Email** the repository maintainer privately
3. **Include:** Description, reproduction steps, potential impact
4. **Timeline:** We'll respond within 48 hours

---

## Compliance Checklist

- [x] No API keys in source code
- [x] API keys in `.gitignore`
- [x] `.env` file in `.gitignore`
- [x] Rate limiting respected (5-second delays)
- [x] Quota monitoring documented
- [x] Data privacy assured (no actual text stored)
- [x] Ethical use guidelines provided
- [x] Defense mechanisms acknowledged
- [x] Incident response plan documented

---

## Questions?

For security questions or to report a vulnerability, contact the repository maintainer at your earliest convenience.
