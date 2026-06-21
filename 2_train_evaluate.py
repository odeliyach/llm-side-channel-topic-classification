"""
2_train_evaluate.py
-------------------
Loads token-length sequences from data/responses.json,
extracts statistical features, trains classifiers, and evaluates them.

Runs two experiments:
    A) 2-topic classification: poetry vs. python_code
    B) 5-topic classification: all topics

Why two experiments?
    The 2-topic case is a controlled sanity check under ideal conditions.
    The 5-topic case is more realistic — a real attacker doesn't know
    which two topics to compare. Comparing accuracy between them shows
    how the attack degrades as the problem becomes harder.

INTERVIEW NOTE: We use Logistic Regression, not a neural net.
    With ~75 samples, a neural net would overfit badly.
    Well-engineered features + simple classifier is the right call
    when data is scarce. Feature importance is also interpretable,
    which helps us explain *why* the classifier works.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay
)
from sklearn.preprocessing import LabelEncoder

# ── Feature extraction ────────────────────────────────────────────────────────

def extract_features(token_lengths: list[int]) -> np.ndarray:
    """
    Convert a raw token-length sequence into a fixed-size feature vector.

    Why these features?
        Different topics have structurally different token-length distributions.
        Poetry: short, rhythmic sequences. Code: many 1-2 char tokens (symbols).
        Medical/Legal: long tokens (technical terminology).
        Rather than feeding raw sequences (variable length) to the classifier,
        we summarize the distribution — this is more robust and interpretable.

    INTERVIEW NOTE: This is the core design decision. A neural net (e.g., LSTM)
        could consume raw sequences, but with 75 samples it would overfit.
        Feature engineering is the right trade-off here.
    """
    arr = np.array(token_lengths, dtype=float)

    # Summary statistics — capture the "typical" token size for this topic
    mean_len   = np.mean(arr)
    std_len    = np.std(arr)
    max_len    = np.max(arr)
    min_len    = np.min(arr)
    median_len = np.median(arr)
    seq_len    = len(arr)           # total number of chunks (response verbosity)

    # Histogram over token lengths 1-20, normalized to sum to 1.
    # This captures the full shape of the distribution, not just summary stats.
    # Normalization makes it independent of response length.
    # INTERVIEW NOTE: Without normalization, long responses would dominate
    # just because they have more tokens — we'd be learning length, not pattern.
    hist,_ = np.histogram(arr, bins=[1, 3, 6, 11, 16, 22], density=False)
    hist_normalized = hist / (hist.sum() + 1e-8)  # avoid div-by-zero

    features = np.concatenate([
        [mean_len, std_len, max_len, min_len, median_len, seq_len],
        hist_normalized,
    ])
    return features


def build_dataset(data: list[dict], topics: list[str]):
    """
    Filter data to the selected topics and build X, y, groups arrays.

    groups: the prompt_index for each sample, used to split by prompt
    (not by response) in cross-validation. This prevents the same prompt
    from appearing in both train and test — a subtle form of data leakage.

    INTERVIEW NOTE: If we split randomly by response, the model could
        see response A from prompt P in training and response B from the
        same prompt P in test. Since same prompt → similar response structure,
        this inflates accuracy. Splitting by prompt_index avoids this.
    """
    X, y, groups = [], [], []
    for item in data:
        if item["topic"] not in topics:
            continue
        features = extract_features(item["token_lengths"])
        X.append(features)
        y.append(item["topic"])
        groups.append(item["prompt_index"])

    return np.array(X), np.array(y), np.array(groups)


# ── Training and evaluation ───────────────────────────────────────────────────

def train_and_evaluate(X, y, groups, topic_names: list[str], experiment_name: str):
    """
    Train Logistic Regression and Random Forest classifiers.
    Uses StratifiedGroupKFold so:
        - Each fold has roughly equal class proportions (stratified)
        - Prompts from the same index never span train/test (group split)

    Why cross-validation instead of a single train/test split?
        With ~75 samples, a single split is noisy. CV gives a more
        stable accuracy estimate by averaging over multiple splits.
    """
    print(f"\n{'='*60}")
    print(f"Experiment: {experiment_name}")
    print(f"Topics: {topic_names}")
    print(f"Samples: {len(y)} | Classes: {len(set(y))}")
    print(f"Random baseline: {1/len(set(y)):.0%}")
    print('='*60)

    # Encode string labels to integers (required by sklearn)
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # StratifiedGroupKFold: stratified by class, grouped by prompt
    cv = StratifiedGroupKFold(n_splits=5)
    # Pre‑fit a scaler on the whole dataset (for full fit)
    results = {}
    for clf_name, clf in [
        ("Logistic Regression", make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))),
        ("Random Forest", RandomForestClassifier(n_estimators=100, random_state=42)),
    ]:
        scores = cross_val_score(clf, X, y_enc, cv=cv, groups=groups, scoring="accuracy")
        results[clf_name] = scores
        print(f"\n{clf_name}:")
        print(f"  CV accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
        print(f"  Per-fold:    {[f'{s:.2f}' for s in scores]}")

    # Full fit on all data for confusion matrix and feature importance
    # Full fit for Logistic Regression (using scaled data)
    lr_regularized = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=1000, random_state=42))
    lr_regularized.fit(X, y_enc)
    y_pred = lr_regularized.predict(X)

    # Random Forest (no scaling needed)
    rf = RandomForestClassifier(n_estimators=100, max_depth=3, min_samples_leaf=3, random_state=42)
    rf.fit(X, y_enc)

    print(f"\nClassification report (Logistic Regression, full fit):")
    print(classification_report(y_enc, y_pred, target_names=le.classes_))

    # Save confusion matrix
    os.makedirs("results", exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    cm = confusion_matrix(y_enc, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=le.classes_)
    disp.plot(ax=ax, colorbar=False)
    ax.set_title(f"Confusion Matrix — {experiment_name}\n(Logistic Regression, full fit)")
    plt.tight_layout()
    fname = f"results/confusion_{experiment_name.lower().replace(' ', '_')}.png"
    plt.savefig(fname, dpi=150)
    plt.close()
    print(f"Saved: {fname}")

    # Feature importance from Random Forest
    # INTERVIEW NOTE: RF feature importance tells us which statistical
    # properties of the length sequence matter most. If seq_len (response
    # length) dominates, it means we might just be learning verbosity,
    # not actual topic patterns — a key methodological concern.
    feature_names = [
        "mean", "std", "max", "min", "median", "seq_len",
    ] + [f"hist_bin_{i}" for i in range(1, 22)]

    importances = rf.feature_importances_
    top_idx = np.argsort(importances)[::-1][:10]

    print("\nTop 10 features (Random Forest importance):")
    for i in top_idx:
        print(f"  {feature_names[i]:15s}: {importances[i]:.4f}")

    # Save feature importance plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(10), importances[top_idx])
    ax.set_xticks(range(10))
    ax.set_xticklabels([feature_names[i] for i in top_idx], rotation=30, ha="right")
    ax.set_title(f"Feature Importance — {experiment_name}")
    ax.set_ylabel("Importance")
    plt.tight_layout()
    fname = f"results/importance_{experiment_name.lower().replace(' ', '_')}.png"
    plt.savefig(fname, dpi=150)
    plt.close()
    print(f"Saved: {fname}")

    return {clf: scores.mean() for clf, scores in results.items()}


# ── Summary comparison plot ───────────────────────────────────────────────────

def plot_comparison(results_2topic: dict, results_5topic: dict):
    """
    Bar chart comparing 2-topic vs 5-topic accuracy for each classifier.
    Always includes the random baseline so the audience understands
    what 'chance level' looks like.
    """
    clf_names = list(results_2topic.keys())
    x = np.arange(len(clf_names))
    width = 0.3

    fig, ax = plt.subplots(figsize=(7, 5))
    bars1 = ax.bar(x - width/2, [results_2topic[c] for c in clf_names],
                   width, label="2-topic", color="#4C72B0")
    bars2 = ax.bar(x + width/2, [results_5topic[c] for c in clf_names],
                   width, label="5-topic", color="#DD8452")

    # Random baselines
    ax.axhline(0.5,  color="#4C72B0", linestyle="--", linewidth=1, alpha=0.6, label="Random (2-topic, 50%)")
    ax.axhline(0.2,  color="#DD8452", linestyle="--", linewidth=1, alpha=0.6, label="Random (5-topic, 20%)")

    ax.set_xticks(x)
    ax.set_xticklabels(clf_names)
    ax.set_ylabel("CV Accuracy")
    ax.set_title("2-Topic vs. 5-Topic Classification Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend()

    # Annotate bars with values
    for bar in list(bars1) + list(bars2):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("results/comparison_2v5_topics.png", dpi=150)
    plt.close()
    print("\nSaved: results/comparison_2v5_topics.png")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Load collected data
    with open("data/responses.json") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} responses.")

    # ── Experiment A: 2 topics ─────────────────────────────────────────────
    # Poetry vs. Python code — maximally distinct, serves as a sanity check.
    # If accuracy is low here, something is wrong with the pipeline.
    X2, y2, g2 = build_dataset(data, topics=["poetry", "python_code"])
    res_2 = train_and_evaluate(X2, y2, g2,
                               topic_names=["poetry", "python_code"],
                               experiment_name="2 Topics")

    # ── Experiment B: 5 topics ─────────────────────────────────────────────
    # All topics — more realistic scenario, harder classification problem.
    # We expect accuracy to drop; the question is by how much.
    X5, y5, g5 = build_dataset(data, topics=["poetry", "python_code",
                                              "medical_advice", "cooking", "legal"])
    res_5 = train_and_evaluate(X5, y5, g5,
                               topic_names=["poetry", "python_code",
                                            "medical_advice", "cooking", "legal"],
                               experiment_name="5 Topics")

    # ── Comparison plot ────────────────────────────────────────────────────
    plot_comparison(res_2, res_5)

    print("\n── Final summary ──")
    print(f"{'Classifier':<25} {'2-topic':>10} {'5-topic':>10}")
    print("-" * 47)
    for clf in res_2:
        print(f"{clf:<25} {res_2[clf]:>10.3f} {res_5[clf]:>10.3f}")
    print(f"\nRandom baseline:          {'0.500':>10} {'0.200':>10}")
