"""
Unit tests for bot.validators. These don't touch the network, so they can
run anywhere (including CI) as a quick sanity check on input handling.

Run with:
    python -m pytest tests/
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.validators import ValidationError, build_order_request  # noqa: E402


def test_valid_market_order():
    order = build_order_request("btcusdt", "buy", "market", "0.01")
    assert order.symbol == "BTCUSDT"
    assert order.side == "BUY"
    assert order.order_type == "MARKET"
    assert order.quantity == 0.01
    assert order.price is None


def test_valid_limit_order():
    order = build_order_request("BTCUSDT", "SELL", "LIMIT", "0.5", price="60000")
    assert order.order_type == "LIMIT"
    assert order.price == 60000.0


def test_limit_order_requires_price():
    with pytest.raises(ValidationError):
        build_order_request("BTCUSDT", "SELL", "LIMIT", "0.5")


def test_stop_order_requires_price_and_stop_price():
    with pytest.raises(ValidationError):
        build_order_request("BTCUSDT", "SELL", "STOP", "0.5", price="58000")


def test_invalid_side_rejected():
    with pytest.raises(ValidationError):
        build_order_request("BTCUSDT", "HOLD", "MARKET", "0.01")


def test_invalid_symbol_rejected():
    with pytest.raises(ValidationError):
        build_order_request("btc/usdt", "BUY", "MARKET", "0.01")


def test_invalid_order_type_rejected():
    with pytest.raises(ValidationError):
        build_order_request("BTCUSDT", "BUY", "SWAP", "0.01")


def test_negative_quantity_rejected():
    with pytest.raises(ValidationError):
        build_order_request("BTCUSDT", "BUY", "MARKET", "-1")


def test_non_numeric_quantity_rejected():
    with pytest.raises(ValidationError):
        build_order_request("BTCUSDT", "BUY", "MARKET", "abc")