"""
3_pairwise_heatmap.py
----------------------
Extends 2_train_evaluate.py: instead of only running 2-topic and 5-topic
experiments, this runs EVERY pairwise combination of topics (5 topics ->
C(5,2) = 10 pairs) and plots a 5x5 heatmap where cell (i, j) = CV accuracy
distinguishing topic i from topic j.

Why this is useful:
    The 5-topic accuracy (0.44) tells you the average difficulty, but hides
    which specific topic pairs are easy vs. hard to tell apart. The heatmap
    answers: is "poetry vs. cooking" easy and "poetry vs. legal" hard, or
    is poetry just uniformly weak against everything?

This reuses extract_features() and build_dataset() unchanged from
2_train_evaluate.py — no new feature engineering, just a different slicing
of the same data.
"""

import json
import itertools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

# Reuse the exact feature extraction + dataset builder from the main script.
from importlib import import_module
main = import_module("2_train_evaluate")
extract_features = main.extract_features
build_dataset = main.build_dataset

TOPICS = ["poetry", "python_code", "medical_advice", "cooking", "legal"]


def pairwise_accuracy(data: list[dict], topic_a: str, topic_b: str) -> float:
    """
    Build a 2-topic dataset for (topic_a, topic_b) and return mean CV
    accuracy using the same model/CV setup as the main script
    (Logistic Regression inside a StandardScaler pipeline,
    StratifiedGroupKFold grouped by prompt_index).
    """
    X, y, groups = build_dataset(data, topics=[topic_a, topic_b])

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, random_state=42),
    )

    # n_splits=5 needs at least 5 distinct groups per class; with 15 prompts
    # per topic this is fine. If you ever reduce prompts per topic, lower
    # n_splits accordingly.
    cv = StratifiedGroupKFold(n_splits=5)
    scores = cross_val_score(clf, X, y_enc, cv=cv, groups=groups, scoring="accuracy")
    return scores.mean()


def build_pairwise_matrix(data: list[dict], topics: list[str]) -> np.ndarray:
    n = len(topics)
    matrix = np.full((n, n), np.nan)

    for i, j in itertools.combinations(range(n), 2):
        acc = pairwise_accuracy(data, topics[i], topics[j])
        matrix[i, j] = acc
        matrix[j, i] = acc  # symmetric
        print(f"  {topics[i]:15s} vs {topics[j]:15s}: {acc:.3f}")

    return matrix


def plot_heatmap(matrix: np.ndarray, topics: list[str], out_path: str):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0.5, vmax=1.0)

    ax.set_xticks(range(len(topics)))
    ax.set_yticks(range(len(topics)))
    ax.set_xticklabels(topics, rotation=30, ha="right")
    ax.set_yticklabels(topics)

    # Annotate each cell with its accuracy (diagonal left blank — not a real pair)
    for i in range(len(topics)):
        for j in range(len(topics)):
            if i == j:
                ax.text(j, i, "—", ha="center", va="center", color="gray")
            else:
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center",
                         color="black", fontsize=10)

    ax.set_title("Pairwise Topic Classification Accuracy\n(Logistic Regression, 5-fold CV)")
    fig.colorbar(im, ax=ax, label="CV Accuracy")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    with open("data/responses_100.json") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} responses.")

    print("\nRunning all pairwise topic comparisons...")
    matrix = build_pairwise_matrix(data, TOPICS)

    import os
    os.makedirs("results", exist_ok=True)
    plot_heatmap(matrix, TOPICS, "results/pairwise_heatmap.png")

    # Quick summary: easiest and hardest pair
    n = len(TOPICS)
    pairs = [(matrix[i, j], TOPICS[i], TOPICS[j])
             for i, j in itertools.combinations(range(n), 2)]
    pairs.sort()
    print(f"\nHardest pair to separate: {pairs[0][1]} vs {pairs[0][2]} ({pairs[0][0]:.3f})")
    print(f"Easiest pair to separate: {pairs[-1][1]} vs {pairs[-1][2]} ({pairs[-1][0]:.3f})")
