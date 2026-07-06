"""
4_generate_and_check_prompts.py
--------------------------------
Office-hours suggestion: before scaling data collection from 15 to ~100
prompts per topic, generate a larger prompt pool with an LLM and verify
the prompts are actually *diverse* (not just paraphrases of each other).
There's no point spending the Groq rate-limit budget on 500 streaming
calls if half the prompts are near-duplicates.

This script has two stages, run separately so you don't waste API calls
if the diversity check fails:

  STAGE 1 (generate_prompts):
      Ask an LLM to generate N new prompts per topic, seeded with the
      existing 15 PROMPTS per topic from 1_generate_data.py (so style/
      difficulty stays consistent), and save them to a JSON file.
      Uses the same Groq client/model as 1_generate_data.py — no new
      dependency.

  STAGE 2 (check_diversity):
      For each topic, embed all prompts (TF-IDF, no extra API calls
      needed) and compute pairwise cosine similarity. Flag prompt pairs
      above a similarity threshold as likely near-duplicates, and print
      a diversity score per topic. Only after this looks good should you
      run 1_generate_data.py-style collection on the new prompts.

Why TF-IDF and not an embedding API?
    Checking diversity is exploratory and can be re-run many times while
    you tune the generation prompt — using a free, local TF-IDF similarity
    avoids burning API quota just to sanity-check prompt wording.
"""

import json
import os
import time
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Reuse the existing seed prompts so the new ones match style/scope.
from importlib import import_module
gen_module = import_module("1_generate_data")
SEED_PROMPTS = gen_module.PROMPTS

API_KEY = "TOKEN"  # same key as 1_generate_data.py
client = Groq(api_key=API_KEY)

N_NEW_PER_TOPIC = 85  # 15 existing + 85 new = 100 per topic
GENERATION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # same as data collection


def generate_prompts_for_topic(topic: str, seed_prompts: list[str], n_new: int) -> list[str]:
    """
    Ask the LLM to produce n_new NEW prompts for a topic, explicitly
    instructed to avoid duplicating the seed prompts and to vary framing,
    length, and angle (same diversity goal as the original 15, per the
    comment in 1_generate_data.py).
    """
    seed_text = "\n".join(f"- {p}" for p in seed_prompts)

    instruction = f"""You are helping build a dataset of diverse questions about the topic: "{topic}".

Here are {len(seed_prompts)} existing example questions on this topic:
{seed_text}

Generate {n_new} NEW questions on the same topic ("{topic}") that:
- Are NOT duplicates or simple rewordings of the examples above
- Vary in length (some short, some longer/more detailed)
- Vary in framing (some "how", some "what", some "compare X vs Y", some "explain why")
- Cover different sub-aspects of the topic, not just the same angle repeated

Output ONLY the questions, one per line, no numbering, no extra text."""

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": instruction}],
        stream=False,
    )
    text = response.choices[0].message.content
    # Split into lines, strip empties and any stray numbering/bullets.
    lines = [l.strip().lstrip("-•0123456789. ") for l in text.split("\n")]
    prompts = [l for l in lines if l]
    return prompts


def generate_all_prompts(output_path: str = "data/prompts_candidate_100.json"):
    all_prompts = {}
    for topic, seeds in SEED_PROMPTS.items():
        print(f"\n[Topic: {topic}] Generating {N_NEW_PER_TOPIC} new prompts...")
        new_prompts = generate_prompts_for_topic(topic, seeds, N_NEW_PER_TOPIC)
        print(f"  Got {len(new_prompts)} new prompts.")
        all_prompts[topic] = seeds + new_prompts  # seed + new = full pool
        time.sleep(2)  # be polite to rate limits between topics

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_prompts, f, indent=2)
    print(f"\nSaved candidate prompt pool to {output_path}")
    return all_prompts


def check_diversity(prompts_path: str = "data/prompts_candidate_100.json",
                     similarity_threshold: float = 0.6):
    """
    For each topic, compute pairwise TF-IDF cosine similarity between all
    prompts. Reports:
      - average pairwise similarity per topic (lower = more diverse)
      - any prompt pairs above similarity_threshold (likely near-duplicates
        that should be manually reviewed/removed before spending API
        budget on data collection)
    """
    with open(prompts_path) as f:
        all_prompts = json.load(f)

    for topic, prompts in all_prompts.items():
        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(prompts)
        sim_matrix = cosine_similarity(X)

        # Exclude self-similarity (diagonal) from the average.
        n = len(prompts)
        mask = ~np.eye(n, dtype=bool)
        avg_sim = sim_matrix[mask].mean()

        print(f"\n[Topic: {topic}] n={n} prompts | avg pairwise similarity: {avg_sim:.3f}")

        # Flag near-duplicate pairs.
        flagged = []
        for i in range(n):
            for j in range(i + 1, n):
                if sim_matrix[i, j] > similarity_threshold:
                    flagged.append((sim_matrix[i, j], prompts[i], prompts[j]))

        flagged.sort(reverse=True)
        if flagged:
            print(f"  ⚠ {len(flagged)} pairs above similarity {similarity_threshold}:")
            for sim, p1, p2 in flagged[:5]:  # show top 5 worst offenders
                print(f"    sim={sim:.2f}")
                print(f"      A: {p1[:70]}")
                print(f"      B: {p2[:70]}")
        else:
            print(f"  No pairs above similarity {similarity_threshold} — looks diverse.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Run only the diversity check on an already-generated file,
        # e.g.: python 4_generate_and_check_prompts.py check
        check_diversity()
    else:
        # Default: generate, then immediately check.
        generate_all_prompts()
        check_diversity()
