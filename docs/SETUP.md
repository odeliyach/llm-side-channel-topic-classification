# Setup & Installation Guide

## Requirements

- Python 3.8 or later
- pip (Python package installer)
- Internet connection (for Groq API access)

## Step 1: Clone the Repository

```bash
git clone https://github.com/odeliyach/llm-side-channel-topic-classification.git
cd llm-side-channel-topic-classification
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependency Overview:**
- `groq` – Python client for Groq API (LLM provider)
- `scikit-learn` – Machine learning library for classification
- `numpy` – Numerical computing
- `matplotlib` – Visualization

## Step 3: Obtain Groq API Key

This project uses the **Groq API** with the **Llama 4 Scout 17B** model.

### Get a Free API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign in with your Google account (or create a new account)
3. Navigate to the API Keys section
4. Click "Create API Key"
5. Copy your key (you'll use it in the next step)

**Free Tier Limits:**
- 1,500 requests/day (sufficient for this project)
- 15 requests/minute
- No credit card required

## Step 4: Configure API Access

### Option A: Environment Variable (Recommended)

Create a `.env` file in the repository root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GROQ_API_KEY=your_actual_api_key_here
```

Then, in your Python scripts, load it:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
```

Or use the existing pattern in `1_generate_data.py`:

```python
import os
api_key = os.environ.get("GROQ_API_KEY", "TOKEN")
```

### Option B: Direct Configuration (Development Only)

Edit `1_generate_data.py` and replace:

```python
API_KEY = "TOKEN"
```

with:

```python
API_KEY = "your_actual_api_key_here"
```

**⚠️ WARNING:** Never commit your API key to version control. If you accidentally commit it, you'll need to regenerate the key on the Groq console.

### Option C: Using python-dotenv

If you prefer automatic `.env` loading:

```bash
pip install python-dotenv
```

Then in your scripts:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
```

## Step 5: Verify Installation

Run a quick sanity check:

```bash
python -c "import groq; import sklearn; import numpy; import matplotlib; print('All dependencies installed successfully!')"
```

If successful, you should see:
```
All dependencies installed successfully!
```

## Step 6: Test Groq API Connection (Optional)

Create a test script `test_api.py`:

```python
import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="llama-2-70b-chat",
        messages=[{"role": "user", "content": "Hello, test message"}],
        stream=False,
    )
    print("✓ API connection successful!")
    print(f"Response: {response.choices[0].message.content[:100]}...")
except Exception as e:
    print(f"✗ API connection failed: {e}")
```

Run it:

```bash
python test_api.py
```

Expected output:
```
✓ API connection successful!
Response: Hello! I'm Claude, an AI assistant created by Anthropic...
```

## Running the Full Pipeline

Once setup is complete:

```bash
# 1. Collect data (takes ~10-15 minutes)
python 1_generate_data.py

# 2. Train and evaluate (takes ~30 seconds)
python 2_train_evaluate.py

# 3. View results
ls -la results/
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'groq'` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `Error: Invalid API key` | Missing or incorrect key | Check `GROQ_API_KEY` environment variable |
| `HTTPError 429: Too Many Requests` | Rate limit exceeded | The script includes 5-second delays; if exceeded, increase `REQUEST_DELAY` in `.env` |
| `FileNotFoundError: data/responses.json` | Phase 1 didn't complete | Run `python 1_generate_data.py` first |
| `Empty response from API` | Network issue or API down | Check your internet connection and Groq API status |

## Security Considerations

1. **Never commit `.env` file** — it's in `.gitignore` by default
2. **Use environment variables** — safer than hardcoding keys
3. **Rotate API keys** — if you suspect exposure, regenerate on Groq console
4. **Monitor API usage** — check the Groq console dashboard for unexpected activity

## Next Steps

Once setup is complete, proceed to:
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md) — Run the full experiment
- [METHODOLOGY.md](METHODOLOGY.md) — Understand the experimental design
- [RESULTS.md](RESULTS.md) — Interpret the results
