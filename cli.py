#!/usr/bin/env python3
"""
CLI entry point for the Simplified Trading Bot (Binance Futures Testnet).

Examples
--------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000

Stop-limit order (bonus):
    python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 \\
        --price 58000 --stop-price 58500
"""

import argparse
import sys

from bot.client import BinanceClientError, get_futures_testnet_client
from bot.logging_config import logger
from bot.orders import place_order
from bot.validators import ValidationError, build_order_request


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET, LIMIT, or STOP orders on Binance Futures Testnet."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"])
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP", "market", "limit", "stop"],
        help="Order type. STOP is a bonus stop-limit order.",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.01")
    parser.add_argument(
        "--price", required=False, default=None, help="Limit price (required for LIMIT/STOP)"
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        required=False,
        default=None,
        help="Trigger price (required for STOP orders only)",
    )
    return parser.parse_args(argv)


def print_report(result: dict) -> None:
    print("\n=== Order Request ===")
    for key, value in result["request"].items():
        print(f"  {key}: {value}")

    if result["success"]:
        print("\n=== Order Response ===")
        for key, value in result["response"].items():
            print(f"  {key}: {value}")
        print("\n✅ SUCCESS: order placed on Binance Futures Testnet.\n")
    else:
        print("\n=== Error ===")
        print(f"  {result['error']}")
        print("\n❌ FAILED: order was not placed.\n")


def main(argv=None) -> int:
    args = parse_args(argv)

    try:
        order = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n❌ Invalid input: {exc}\n")
        return 1

    try:
        client = get_futures_testnet_client()
    except BinanceClientError as exc:
        logger.error("Could not create client: %s", exc)
        print(f"\n❌ Configuration error: {exc}\n")
        return 1

    result = place_order(client, order)
    print_report(result)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
