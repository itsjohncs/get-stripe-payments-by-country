#!/usr/bin/env python3

import json
import sys
import functools
import numbers

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


def add_dicts(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        result = dict(a)
        for k, v in b.items():
            if k in result:
                result[k] = add_dicts(result[k], v)
            else:
                result[k] = v

        return result
    elif isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        return a + b
    else:
        raise TypeError("a and b do not have compatible types")


def main():
    data = json.load(sys.stdin)
    print(
        "EU: ",
        functools.reduce(
            add_dicts, (v for k, v in data.items() if k in EU_COUNTRY_CODES)
        ),
    )
    print("UK: ", data["GB"])


if __name__ == "__main__":
    main()
