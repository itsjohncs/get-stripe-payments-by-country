#!/usr/bin/env python3

import os
import sys
import argparse
import warnings
import json

import stripe
import toml
from tqdm import tqdm
import dateparser

# A noisy warning caused by dateparser. More info at
# https://github.com/scrapinghub/dateparser/issues/1013
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, "
    "as this time zone supports the fold attribute",
)


# pylint: disable-next=too-few-public-methods
class Counters:
    def __init__(self):
        self.countries = {}

    def add(self, country, category, currency, value):
        currency_dict = self.countries.setdefault(country, {}).setdefault(
            category, {}
        )
        if currency in currency_dict:
            currency_dict[currency] += value
        else:
            currency_dict[currency] = value


def setup_stripe(target_mode):
    assert target_mode in {"live", "test"}

    with open(
        f"{os.environ['HOME']}/.config/stripe/config.toml", encoding="utf8"
    ) as f:
        config = toml.load(f)

    stripe.api_key = config["default"][f"{target_mode}_mode_api_key"]
    assert stripe.api_key

    stripe.max_network_retries = 2


def parse_datetime(txt):
    datetime = dateparser.parse(txt)
    if datetime is None:
        raise ValueError()

    return datetime


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        metavar="PERIOD_START",
        dest="period_start",
        type=parse_datetime,
        help="The start of the period to get payments for.",
    )
    parser.add_argument(
        metavar="PERIOD_END",
        dest="period_end",
        type=parse_datetime,
        help="The start of the period to get payments for.",
    )
    parser.add_argument("--live", action="store_true", help="Use the prod key, rather than the testing one.")

    return parser.parse_args(argv)


def main(period_start, period_end):
    counters = Counters()
    for payment in tqdm(
        stripe.PaymentIntent.list(
            created={"gte": period_start, "lte": period_end}, limit=100
        ).auto_paging_iter()
    ):
        for charge in payment["charges"]["data"]:
            country = charge["payment_method_details"]["card"]["country"]

            counters.add(
                country, "revenue", charge["currency"], charge["amount"]
            )
            counters.add(
                country,
                "captured",
                charge["currency"],
                charge["amount_captured"],
            )
            counters.add(
                country,
                "refunded",
                charge["currency"],
                charge["amount_refunded"],
            )

    json.dump(counters.countries, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    mode = "live" if args.live else "test"
    setup_stripe(mode)
    print(f"Getting {mode} data for {args.period_start} to {args.period_end}", file=sys.stderr)
    main(args.period_start, args.period_end)
