import json
import math


def normalize_token_lengths(
    input_file="data/responses_gemini_2.json",
    output_file="data/responses_gemini_2_normalized.json",
    max_value=50,
):
    """
    Compress Gemini packet sizes into the range [1, max_value]
    using logarithmic scaling.

    Example:
        31   -> 2
        39   -> 3
        250  -> 26
        500  -> 35
        1000 -> 47
        1220 -> 50
    """

    with open(input_file, "r") as f:
        responses = json.load(f)

    # global maximum
    max_len = max(
        max(r["token_lengths"])
        for r in responses
        if r["token_lengths"]
    )

    log_max = math.log1p(max_len)

    for r in responses:

        normalized = []

        for x in r["token_lengths"]:

            value = int(
                round(
                    math.log1p(x) / log_max * max_value
                )
            )

            value = max(1, min(max_value, value))

            normalized.append(value)

        r["token_lengths"] = normalized

    with open(output_file, "w") as f:
        json.dump(responses, f, indent=2)

    print(f"Saved normalized file to {output_file}")


if __name__ == "__main__":
    normalize_token_lengths()