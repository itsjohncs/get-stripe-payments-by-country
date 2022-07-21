#!/usr/bin/env python3

import json
import sys
import functools
import numbers
import operator

import pycountry

EU_COUNTRY_CODES = {
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "EL",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
}


def add_dicts(a, b, op = operator.add):
    if isinstance(a, dict) and isinstance(b, dict):
        result = dict(a)
        for k, v in b.items():
            if k in result:
                result[k] = add_dicts(result[k], v, op)
            else:
                result[k] = v

        return result
    elif isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        return op(a, b)
    else:
        raise TypeError("a and b do not have compatible types")


def main(exchange_rate):
    data = json.load(sys.stdin)

    print(
        "EU: ",
        functools.reduce(
            add_dicts, (v for k, v in data.items() if k in EU_COUNTRY_CODES)
        ),
    )
    for k, v in data.items():
        if k not in EU_COUNTRY_CODES:
            continue

        # Net including all currencies
        net_all = add_dicts(v["captured"], v["refunded"], operator.sub)
        assert "usd" in net_all and len(net_all) == 1

        net_euros = (net_all["usd"] / 100.0) / exchange_rate

        print(f"\t{pycountry.countries.get(alpha_2=k).name}: {net_euros:.2f} EUR")

    print("UK: ", data["GB"])


if __name__ == "__main__":
    exchange_rate = float(sys.argv[1])
    print(f"Using 1 EUR = {exchange_rate} USD")
    main(exchange_rate)
