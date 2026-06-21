# Data Directory

This directory contains data generated during the experiment.

---

## Files

### `responses.json` (Generated at Runtime)

**Format:** JSON file containing all collected API responses

**Structure:**
```json
[
  {
    "topic": "poetry",
    "prompt_index": 1,
    "prompt": "What makes a poem different from other forms of writing?",
    "token_lengths": [14, 8, 10, 5, 12, 9, 7, 3, ...],
    "num_chunks": 42
  },
  {
    "topic": "python_code",
    "prompt_index": 1,
    "prompt": "Write a Python function to sort a list.",
    "token_lengths": [7, 12, 3, 8, 2, 14, 6, ...],
    "num_chunks": 56
  },
  ...
]
```

**Size:** ~50-100 KB (75 responses)

**Generation:** Run `python 1_generate_data.py`

**Note:** Not tracked by git (in `.gitignore`) because it's generated at runtime.

---

## How Data is Collected

1. **Prompt Definition** — See `1_generate_data.py` for topic definitions
2. **API Call** — Query Groq API in streaming mode
3. **Token Length Recording** — Measure each chunk size, discard actual text
4. **Label Assignment** — Assign topic based on which prompt was sent
5. **JSON Output** — Save all responses to `responses.json`

---

## Important Notes

### No Actual Text is Stored

For privacy and to simulate the eavesdropper's constraints, we record **only token-length sequences**, never the actual response text.

Example:
- ✅ We record: `[14, 8, 10, 5, 12, ...]`
- ❌ We do NOT record: `"The poem is a beautiful form of literary expression..."`

### Train/Test Split is Prompt-Based

When training the classifier in Phase 2, we split by **prompt index**, not randomly by response.

This prevents subtle data leakage: if the same prompt appears in both train and test, the model may exploit the prompt structure rather than learning topic patterns.

### Reproducibility

To reproduce results with the same data:
1. Use a fixed random seed (set in `1_generate_data.py`)
2. Use the same Groq model and API configuration
3. Run the full pipeline in order: Phase 1 → Phase 2

Results may vary slightly due to:
- API response variability
- Random seed initialization in classifiers
- Cross-validation fold randomization

---

## Sample Data Format

### Minimal Example

```json
[
  {
    "topic": "poetry",
    "prompt_index": 0,
    "prompt": "What makes a poem different from other forms of writing?",
    "token_lengths": [14, 8, 10, 5, 12, 9, 7, 3, 11, 6],
    "num_chunks": 10
  }
]
```

### Full Example (Single Response)

```json
{
  "topic": "python_code",
  "prompt_index": 2,
  "prompt": "Explain the difference between list comprehensions and generator expressions in Python.",
  "token_lengths": [
    7, 12, 3, 8, 2, 14, 6, 9, 4, 11,
    5, 13, 2, 10, 8, 6, 15, 3, 7, 4,
    9, 6, 11, 2, 8, 13, 5, 10, 7, 12,
    3, 6, 9, 4, 14, 8, 2, 11, 5, 10,
    6, 13, 7, 3, 9, 2, 12, 8, 4, 11,
    6, 10, 5, 15, 3, 9, 7, 2, 13, 8
  ],
  "num_chunks": 60
}
```

---

## Data Validation

After running Phase 1, validate the data:

```bash
# Check file exists
ls -lh responses.json

# Check JSON validity
python -m json.tool responses.json > /dev/null && echo "✓ Valid JSON"

# Count responses per topic
python -c "
import json
with open('responses.json') as f:
    data = json.load(f)
    topics = {}
    for r in data:
        t = r['topic']
        topics[t] = topics.get(t, 0) + 1
    for topic, count in sorted(topics.items()):
        print(f'{topic}: {count}')
"

# Expected output:
# cooking: 15
# legal: 15
# medical_advice: 15
# poetry: 15
# python_code: 15
```

---

## Storage & Privacy

- **Location:** Local `data/` directory
- **Scope:** Only token lengths (no sensitive content)
- **Sharing:** Safe to share; contains no text
- **Retention:** Can be deleted anytime; will be regenerated on next Phase 1 run
- **Backup:** Not necessary; easily reproducible

---

## Using the Data Programmatically

```python
import json

# Load responses
with open('data/responses.json') as f:
    responses = json.load(f)

# Iterate over responses
for response in responses:
    topic = response['topic']
    token_lengths = response['token_lengths']
    num_chunks = response['num_chunks']
    print(f"{topic}: {num_chunks} chunks, mean length {sum(token_lengths)/len(token_lengths):.1f}")

# Filter by topic
poetry_responses = [r for r in responses if r['topic'] == 'poetry']
print(f"Found {len(poetry_responses)} poetry responses")

# Extract features (used by Phase 2)
from phase2_functions import extract_features  # Pseudo-import
X = [extract_features(r['token_lengths']) for r in responses]
y = [r['topic'] for r in responses]
```

---

## Questions?

See [REPRODUCIBILITY.md](../REPRODUCIBILITY.md) for instructions on generating this data, or [METHODOLOGY.md](../docs/METHODOLOGY.md) for details on how data is collected.
