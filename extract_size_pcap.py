from scapy.all import rdpcap, TCP, IPv6, IP
import json

SERVER_PREFIX = "2001:4860:4826:200:"

packets = rdpcap("../tcp-filtered-100.pcap")
events = []

for pkt in packets:
    if TCP not in pkt:
        continue

    tcp = pkt[TCP]

    if IPv6 in pkt:
        src = pkt[IPv6].src
        dst = pkt[IPv6].dst
    elif IP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst
    else:
        continue

    if not (src.startswith(SERVER_PREFIX) or dst.startswith(SERVER_PREFIX)):
        continue

    payload = len(bytes(tcp.payload))
    if payload == 0:
        continue

    direction = "S2C" if src.startswith(SERVER_PREFIX) else "C2S"

    events.append({
        "time": float(pkt.time),
        "dir": direction,
        "len": payload
    })

events.sort(key=lambda x: x["time"])

# --- THE CORRECTION LOGIC ---
# Instead of tracking C2S which gets compressed down to ~30 bytes,
# we look at the transmission silence window immediately prior to a burst.
responses = []
current_response = []
last_packet_time = None

# Filter to Server-to-Client bursts, dropping the 31/39 byte control signatures
s2c_clean_events = [e for e in events if e["dir"] == "S2C"]

for e in s2c_clean_events:
    if last_packet_time is None:
        current_response.append(e["len"])
        last_packet_time = e["time"]
        continue

    # Calculate the exact millisecond delta between stream allocations
    time_delta = e["time"] - last_packet_time

    # When your script steps to the next loop iteration, there is a clear local delay
    # as the model waits for input and generates the initial response block token.
    if time_delta > 0.45:  # 450ms is the standard network roundtrip/generation floor
        if current_response:
            responses.append(current_response)
        current_response = []

    current_response.append(e["len"])
    last_packet_time = e["time"]

if current_response:
    responses.append(current_response)

print(f"Total isolated responses found: {len(responses)}\n")

res = []
Topics = ['poetry', 'python_code', 'medical_advice', 'cooking', 'legal']

for i, response_lengths in enumerate(responses):
    # Dynamically match your 20-per-class balance structure
    topic_index = i // 20
    assigned_topic = Topics[topic_index] if topic_index < len(Topics) else "unknown"

    print(f"Response {i + 1} -> Topic: {assigned_topic}")
    print(f" -> {len(response_lengths)} chunks")
    print(f" -> Chunk sizes sample (first 10): {response_lengths[:10]}")
    print(f" -> Total bytes: {sum(response_lengths)}\n")

    res.append({
        "topic": assigned_topic,
        "prompt_index": i + 1,
        "token_lengths": response_lengths,
        "total_bytes": sum(response_lengths)
    })

with open("data/responses_gemini_3.json", "w") as f:
    json.dump(res, f, indent=2)