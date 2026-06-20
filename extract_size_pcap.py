from scapy.all import rdpcap, UDP, IPv6, IP
import sys
GAP = 0.5  # seconds separating responses

if len(sys.argv) != 2:
    print("Usage: python gemini_packet_sizes.py <capture.pcapng>")
    sys.exit(1)

pcap_file = sys.argv[1]
packets = rdpcap(pcap_file)

responses = []

current = []
last_time = None

for pkt in packets:

    if UDP not in pkt:
        continue

    udp = pkt[UDP]

    # only server -> client traffic
    if udp.sport != 443:
        continue

    if IPv6 in pkt:
        src = pkt[IPv6].src
    elif IP in pkt:
        src = pkt[IP].src
    else:
        continue

    ts = float(pkt.time)

    if last_time is not None and ts - last_time > GAP:
        if current:
            responses.append(current)
        current = []

    current.append(len(bytes(udp.payload)))
    last_time = ts

if current:
    responses.append(current)

for i, r in enumerate(responses):
    print(
        f"Response {i+1}: "
        f"{len(r)} chunks, "
        f"lengths sample: {r[:8]}"
    )