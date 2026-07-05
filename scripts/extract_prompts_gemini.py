"""
Fixes the segmentation problem without needing a recapture.

Why: your threshold histogram showed NO clean valley (ratio ~1.06x), so any
fixed cutoff (0.45s or otherwise) will misclassify some boundaries. But you
know a strong prior: you sent exactly N_EXPECTED prompts, so there are
exactly N_EXPECTED-1 real boundaries. Instead of guessing a cutoff, we rank
ALL inter-packet gaps and take the top (N_EXPECTED-1) largest as boundaries.
This guarantees exactly N_EXPECTED responses and is robust even without a
clean separation, as long as real boundaries still tend to be larger than
intra-response gaps on average (a much weaker assumption than "there's a
clean cutoff").

We then flag suspicious responses (too few packets / too few bytes) so you
can manually eyeball the riskiest ones instead of trusting the whole set
blindly.
"""

from scapy.all import rdpcap, TCP, IPv6, IP
import json
import numpy as np

PCAP_PATH = "../tcp-filtered-100.pcap"
SERVER_PREFIX = "2001:4860:4826:200:"
N_EXPECTED = 100          # you sent exactly 100 prompts
TOPICS = ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']
PER_TOPIC = 20

packets = rdpcap(PCAP_PATH)
events = []
for pkt in packets:
    if TCP not in pkt:
        continue
    tcp = pkt[TCP]
    if IPv6 in pkt:
        src, dst = pkt[IPv6].src, pkt[IPv6].dst
    elif IP in pkt:
        src, dst = pkt[IP].src, pkt[IP].dst
    else:
        continue
    if not (src.startswith(SERVER_PREFIX) or dst.startswith(SERVER_PREFIX)):
        continue
    payload = len(bytes(tcp.payload))
    if payload == 0:
        continue
    direction = "S2C" if src.startswith(SERVER_PREFIX) else "C2S"
    events.append({"time": float(pkt.time), "dir": direction, "len": payload})

events.sort(key=lambda x: x["time"])
s2c = [e for e in events if e["dir"] == "S2C"]

# --- Compute gaps, keep index so we know WHERE each gap falls ---
gaps = []
for idx in range(1, len(s2c)):
    delta = s2c[idx]["time"] - s2c[idx - 1]["time"]
    gaps.append((idx, delta))  # boundary occurs BEFORE index idx

# Rank by gap size, descending; take top N_EXPECTED-1 as real boundaries
n_boundaries = N_EXPECTED - 1
top_boundaries = sorted(gaps, key=lambda x: -x[1])[:n_boundaries]
boundary_indices = set(idx for idx, _ in top_boundaries)

print(f"Total S2C packets: {len(s2c)}")
print(f"Selected {len(boundary_indices)} boundaries (top-{n_boundaries} largest gaps)\n")

# Show the smallest of the "selected" boundaries and largest of the "rejected"
# gaps, so you can see how close the cutoff point actually was
all_sorted = sorted(gaps, key=lambda x: -x[1])
cutoff_gap = all_sorted[n_boundaries - 1][1]
next_rejected = all_sorted[n_boundaries][1]
print(f"Smallest gap still selected as a boundary: {cutoff_gap:.4f}s")
print(f"Largest gap rejected (first non-boundary): {next_rejected:.4f}s")
print(f"Effective cutoff margin: {(cutoff_gap - next_rejected):.4f}s")
print("  (If this margin is tiny, the boundary right at the cutoff is a coin flip —")
print("   worth checking that specific response manually.)\n")

# --- Build responses using selected boundaries ---
responses = []
current = []
for i, e in enumerate(s2c):
    if i in boundary_indices and current:
        responses.append(current)
        current = []
    current.append(e["len"])
if current:
    responses.append(current)

print(f"Total responses formed: {len(responses)} (expected {N_EXPECTED})\n")

# --- Flag anomalies: unusually short responses (few packets / few bytes) ---
chunk_counts = np.array([len(r) for r in responses])
byte_totals = np.array([sum(r) for r in responses])

median_chunks = np.median(chunk_counts)
median_bytes = np.median(byte_totals)

print("Flagged responses (chunk count or byte total far below the group median):")
flagged = []
for i, (c, b) in enumerate(zip(chunk_counts, byte_totals)):
    if c < median_chunks * 0.3 or b < median_bytes * 0.15:
        flagged.append(i + 1)
        print(f"  Response {i+1}: {c} chunks, {b} bytes "
              f"(median in set: {median_chunks:.0f} chunks, {median_bytes:.0f} bytes)")
if not flagged:
    print("  None — all responses look like plausible full responses in size.")

print(f"\n{len(flagged)} response(s) flagged for manual review.")
print("These are the ones most likely to be a fragment merged/split incorrectly.")

# --- Save results with flags included ---
res = []
for i, response_lengths in enumerate(responses):
    topic_index = i // PER_TOPIC
    assigned_topic = TOPICS[topic_index] if topic_index < len(TOPICS) else "unknown"
    res.append({
        "topic": assigned_topic,
        "prompt_index": i + 1,
        "token_lengths": response_lengths,
        "total_bytes": sum(response_lengths),
        "flagged_suspicious": (i + 1) in flagged
    })

with open("data/responses_gemini_topN.json", "w") as f:
    json.dump(res, f, indent=2)

print("\nSaved to data/responses_gemini_topN.json")