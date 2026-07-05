"""
extract_final.py
----------------
Extracts exactly 20 responses per topic (80 total) from tcp-100-stream.pcap.
Medical_advice is excluded — its timestamp was missing from the Gemini HTML export
and it overlaps with the python_code window, making clean separation impossible.

Topics and UTC time windows (capture was UTC, Gemini HTML was UTC+3):
  poetry       13:55 – 14:00 UTC  (16:55–17:00 local)
  python_code  14:00 – 14:06 UTC  (17:00–17:06 local)
  cooking      14:06 – 14:12 UTC  (17:06–17:12 local)
  legal        14:12 – 14:20 UTC  (17:12–17:20 local)

Segmentation: within each window, take the top-19 largest inter-packet gaps
as response boundaries → exactly 20 responses per topic.
This avoids the global threshold problem (no clean valley in the full distribution)
and uses ground-truth time windows instead of fragile i//20 positional labeling.
"""

from scapy.all import rdpcap, TCP, IPv6
import datetime, json, numpy as np

PCAP_PATH = "../../tcp-100-stream.pcap"
SERVER_PREFIX = "2001:4860:4826:200:"
N_PER_TOPIC = 20

# ── Load S2C payload events ───────────────────────────────────────────────────
print("Loading pcap...")
pcap = rdpcap(PCAP_PATH)

events = []
for pkt in pcap:
    if TCP not in pkt or IPv6 not in pkt:
        continue
    if not pkt[IPv6].src.startswith(SERVER_PREFIX):
        continue
    payload = len(bytes(pkt[TCP].payload))
    if payload == 0:
        continue
    events.append((float(pkt.time), payload, pkt[TCP].dport))

events.sort()
print(f"S2C payload packets: {len(events)}")

# ── Auto-detect capture date from pcap ───────────────────────────────────────
capture_date = datetime.datetime.utcfromtimestamp(events[0][0]).strftime("%Y-%m-%d")
print(f"Capture date (UTC): {capture_date}")

def utc_boundary(hhmm):
    h, m = map(int, hhmm.split(":"))
    return datetime.datetime.strptime(
        f"{capture_date} {hhmm}", "%Y-%m-%d %H:%M"
    ).timestamp()

# ── Topic windows (UTC) ───────────────────────────────────────────────────────
WINDOWS = [
    ("poetry",      utc_boundary("13:55"), utc_boundary("14:00")),
    ("python_code", utc_boundary("14:00"), utc_boundary("14:06")),
    ("cooking",     utc_boundary("14:06"), utc_boundary("14:12")),
    ("legal",       utc_boundary("14:12"), utc_boundary("14:20")),
]

# ── Segment each window independently ────────────────────────────────────────
all_responses = []

for topic, t_start, t_end in WINDOWS:
    w = [(t, p, port) for t, p, port in events if t_start <= t < t_end]

    gaps = [(i, w[i][0] - w[i-1][0]) for i in range(1, len(w))]
    top_n = sorted(gaps, key=lambda x: -x[1])[:N_PER_TOPIC - 1]
    boundaries = set(idx for idx, _ in top_n)

    # Margin check
    cutoff = sorted(top_n, key=lambda x: x[1])[0][1]
    next_g = sorted(gaps, key=lambda x: -x[1])[N_PER_TOPIC - 1][1]
    print(f"\n{topic}: {len(w)} packets in window")
    print(f"  Boundary cutoff: {cutoff:.3f}s | next rejected: {next_g:.3f}s | "
          f"margin: {cutoff - next_g:.3f}s")

    # Build responses
    responses = []
    cur = []
    for i, (t, p, port) in enumerate(w):
        if i in boundaries and cur:
            responses.append(cur)
            cur = []
        cur.append((t, p, port))
    if cur:
        responses.append(cur)

    assert len(responses) == N_PER_TOPIC, \
        f"Expected {N_PER_TOPIC}, got {len(responses)} for {topic}"

    for resp in responses:
        t0     = resp[0][0]
        chunks = [p for _, p, _ in resp]
        all_responses.append({
            "topic":       topic,
            "start_utc":   datetime.datetime.utcfromtimestamp(t0).strftime("%H:%M:%S"),
            "start_local": datetime.datetime.utcfromtimestamp(t0 + 3*3600).strftime("%H:%M:%S"),
            "tcp_port":    resp[0][2],
            "token_lengths": chunks,
            "total_bytes": sum(chunks),
            "n_chunks":    len(chunks),
        })

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n── Final dataset: {len(all_responses)} responses ──")
print(f"{'#':>4} {'Topic':<15} {'UTC':>10} {'Local':>10} {'Chunks':>7} {'Bytes':>8}")
for i, r in enumerate(all_responses):
    print(f"  {i+1:3d}  {r['topic']:<15} {r['start_utc']:>10}  "
          f"{r['start_local']:>10}  {r['n_chunks']:>7}  {r['total_bytes']:>8}")

print(f"\nTotal: {len(all_responses)} responses across {len(WINDOWS)} topics")

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = "../data/responses_gemini_verified.json"
import os; os.makedirs("data", exist_ok=True)
with open(out_path, "w") as f:
    json.dump(all_responses, f, indent=2)
print(f"Saved: {out_path}")