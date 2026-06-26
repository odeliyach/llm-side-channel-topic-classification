from scapy.all import rdpcap, TCP, IPv6, IP

SERVER = "2001:4860:482d:200::"

packets = rdpcap("../tcp-stream.pcap")

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

    if SERVER not in (src, dst):
        continue

    payload = len(bytes(tcp.payload))

    if payload == 0:
        continue

    direction = "S2C" if src == SERVER else "C2S"

    events.append({
        "time": float(pkt.time),
        "dir": direction,
        "len": payload
    })

events.sort(key=lambda x: x["time"])

SERVER = "2001:4860:482d:200::"
IDLE = 3.0      # seconds

responses = []
current = []

last_time = None

for e in events:

    if e["dir"] != "S2C":
        continue

    if last_time is None:
        current.append(e)
        last_time = e["time"]
        continue

    if e["time"] - last_time > IDLE:
        responses.append(current)
        current = []

    current.append(e)
    last_time = e["time"]

if current:
    responses.append(current)

print(len(responses))

for i, response in enumerate(responses):

    lengths = [pkt["len"] for pkt in response]

    print(f"Response {i+1}")
    print(f" -> {len(lengths)} chunks")
    print(f" -> lengths sample: {lengths[:8]}")
    print(f" -> total bytes: {sum(lengths)}")
    print()
