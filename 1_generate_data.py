"""
1_generate_data.py
------------------
Queries Gemini in streaming mode and records only token lengths per response.
This simulates the eavesdropper's view: we see packet sizes (= token lengths),
not the actual text content.

Why streaming mode?
    In a real attack, the adversary intercepts packets as they arrive.
    Each packet carries one (or a few) tokens. Streaming mode replicates
    this: we get chunks as they're generated and measure their length
    before discarding the text.

Why Gemini 1.5 Flash?
    Free tier (1,500 req/day), supports streaming, easy SDK.
    Note: Gemini uses a SentencePiece tokenizer, different from GPT-4's
    tiktoken. A classifier trained here won't transfer to GPT-4 traffic
    without retraining — acknowledged as a limitation.
"""

import json
import time
import os
import google.generativeai as genai

# ── API key ──────────────────────────────────────────────────────────────────
# Replace with your key from https://aistudio.google.com
# Do NOT commit this to GitHub — use an environment variable in production.
API_KEY = "GEMINI-TOKEN"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ── Prompts ───────────────────────────────────────────────────────────────────
# 15 prompts per topic, deliberately varied in framing, length, and angle.
# Why varied? If all prompts in a topic look similar, Gemini responds
# similarly — and the classifier learns prompt style, not topic structure.
# These were reviewed manually to ensure no duplicates across topics.

PROMPTS = {
    "poetry": [
        "What makes a poem different from other forms of writing?",
        "Explain the concept of meter and rhythm in poetry.",
        "What is the difference between a sonnet and a haiku?",
        "How do poets use imagery to convey emotion?",
        "Describe the history of free verse poetry.",
        "What techniques do slam poets use to engage audiences?",
        "Compare Romantic poetry to Modernist poetry.",
        "How does alliteration function in a poem?",
        "What is the role of the volta in a Shakespearean sonnet?",
        "Explain what an ode is and give an example of its structure.",
        "Why do some poems use unconventional punctuation or capitalization?",
        "What distinguishes lyric poetry from narrative poetry?",
        "How has poetry been used historically as a form of protest?",
        "Describe the structure and purpose of a villanelle.",
        "What does it mean for a poem to have a speaker versus an author?",
    ],
    "python_code": [
        "How do you implement a binary search algorithm in Python?",
        "Explain how Python decorators work with a code example.",
        "What is the difference between a list and a tuple in Python?",
        "How do you handle exceptions in Python using try/except?",
        "Write a Python function to check if a string is a palindrome.",
        "How does Python's garbage collection work?",
        "Explain the difference between shallow copy and deep copy in Python.",
        "How do you read and write JSON files in Python?",
        "What are Python generators and how do they differ from regular functions?",
        "Explain how Python's multiprocessing module differs from threading.",
        "How do you implement a stack data structure in Python?",
        "What is the purpose of __init__ and __repr__ in a Python class?",
        "How do you use list comprehensions with conditional filtering?",
        "Explain what a context manager is and how to write one.",
        "How do you sort a list of dictionaries by a specific key in Python?",
    ],
    "medical_advice": [
        "What are the early symptoms of type 2 diabetes?",
        "How does high blood pressure damage the cardiovascular system over time?",
        "What is the difference between bacterial and viral infections?",
        "Explain how the immune system responds to a vaccine.",
        "What causes migraines and how are they typically treated?",
        "How does the liver process alcohol and what happens with chronic use?",
        "What are the symptoms and treatment options for hypothyroidism?",
        "Explain the difference between an MRI and a CT scan.",
        "What is the role of cholesterol in cardiovascular disease?",
        "How do anti-inflammatory medications work at the cellular level?",
        "What are the warning signs of a stroke and what should you do?",
        "How does sleep deprivation affect the immune system?",
        "What is the difference between Type 1 and Type 2 diabetes?",
        "How do antibiotics work and why is antibiotic resistance a problem?",
        "What are the risk factors for developing osteoporosis?",
    ],
    "cooking": [
        "What is the Maillard reaction and why does it matter in cooking?",
        "How do you properly caramelize onions?",
        "What is the difference between baking soda and baking powder?",
        "How do you make a basic béchamel sauce from scratch?",
        "What techniques are used to make meat more tender?",
        "How does fermentation work in bread making?",
        "What is the correct way to season a cast iron pan?",
        "Explain the difference between braising and stewing.",
        "How do you make a proper stock, and what makes it gelatinous?",
        "What is the purpose of resting meat after cooking?",
        "How do you temper chocolate correctly?",
        "What is the difference between julienne, brunoise, and chiffonade cuts?",
        "How does salt affect the texture of vegetables when cooking?",
        "What makes a good emulsion in salad dressings?",
        "Explain how to properly cook pasta al dente.",
    ],
    "legal": [
        "What is the difference between civil law and criminal law?",
        "Explain what habeas corpus means and why it is significant.",
        "What is the doctrine of precedent in common law systems?",
        "How does intellectual property law protect software?",
        "What is the difference between a contract and a memorandum of understanding?",
        "Explain the concept of due process in legal proceedings.",
        "What constitutes a breach of fiduciary duty?",
        "How does the statute of limitations affect legal claims?",
        "What is the difference between libel and slander?",
        "Explain the legal concept of mens rea in criminal law.",
        "What rights does a defendant have during a criminal trial?",
        "How does arbitration differ from litigation?",
        "What is the legal definition of negligence and how is it proven?",
        "Explain what a non-disclosure agreement covers and its limits.",
        "What is the difference between an injunction and a restraining order?",
    ],
}

# ── Data collection ───────────────────────────────────────────────────────────

def get_token_lengths(prompt: str) -> list[int]:
    """
    Query Gemini in streaming mode and return a list of chunk lengths.

    Each chunk from the streaming API corresponds to a small number of tokens.
    We record len(chunk.text) — the character length — and discard the text.
    This is what an eavesdropper observes: not content, just sizes.

    INTERVIEW NOTE: In a real network attack, you'd capture packet payload
    sizes instead. Here we use the API directly because we're simulating
    the attack, not actually sniffing traffic. The lengths are equivalent
    because vendors don't pad or compress before encryption (per the paper).
    """
    lengths = []
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                # Record length only — the text itself is discarded
                lengths.append(len(chunk.text))
    except Exception as e:
        print(f"  [ERROR] API call failed: {e}")
        return []
    return lengths


def collect_all_data(prompts: dict, output_path: str, delay: float = 1.5):
    """
    Loop over all topics and prompts, collect token-length sequences,
    and save to a JSON file.

    delay: seconds between requests to avoid hitting the rate limit
           (Gemini free tier: 15 requests/minute).

    Why save raw sequences now and extract features later?
    Separating data collection from feature engineering means we can
    re-run the classifier with different features without re-querying
    the API. Good engineering practice and cheaper on API calls.
    """
    dataset = []
    total = sum(len(p) for p in prompts.values())
    count = 0

    for topic, topic_prompts in prompts.items():
        print(f"\n[Topic: {topic}]")
        for i, prompt in enumerate(topic_prompts):
            count += 1
            print(f"  ({count}/{total}) prompt {i+1}: {prompt[:60]}...")

            lengths = get_token_lengths(prompt)

            if not lengths:
                print("  Skipping — empty response.")
                continue

            dataset.append({
                "topic": topic,
                "prompt_index": i,       # used for train/test split by prompt
                "prompt": prompt,
                "token_lengths": lengths,
            })

            print(f"  → {len(lengths)} chunks, lengths sample: {lengths[:8]}")
            time.sleep(delay)  # rate limiting

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"\nSaved {len(dataset)} responses to {output_path}")
    return dataset


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    output_path = "data/responses.json"

    print("Starting data collection...")
    print(f"Topics: {list(PROMPTS.keys())}")
    print(f"Total prompts: {sum(len(v) for v in PROMPTS.values())}")
    print(f"Estimated time: ~{sum(len(v) for v in PROMPTS.values()) * 1.5 / 60:.1f} minutes\n")

    data = collect_all_data(PROMPTS, output_path)

    # Quick sanity check: print average sequence length per topic
    print("\n── Sanity check: avg chunks per response per topic ──")
    from collections import defaultdict
    topic_lengths = defaultdict(list)
    for item in data:
        topic_lengths[item["topic"]].append(len(item["token_lengths"]))
    for topic, lens in topic_lengths.items():
        print(f"  {topic:20s}: avg {sum(lens)/len(lens):.1f} chunks, n={len(lens)}")
