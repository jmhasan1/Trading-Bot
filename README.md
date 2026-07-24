# Simplified Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured CLI application for placing MARKET, LIMIT, and (bonus)
STOP orders on the Binance Futures Testnet, built with `python-binance`.

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py            # Binance client wrapper (testnet, auth)
│   ├── orders.py             # Order placement logic + response summarizing
│   ├── validators.py         # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py     # Rotating file + console logging setup
├── tests/
│   └── test_validators.py    # Unit tests for validation logic
├── logs/
│   └── trading_bot.log       # Generated at runtime (requests/responses/errors)
├── cli.py                    # CLI entry point (argparse)
├── requirements.txt
├── .env.example
└── README.md
```

Client/API layer (`bot/client.py`, `bot/orders.py`) is kept separate from
the command layer (`cli.py`) so the same order logic could be reused by a
future script, scheduler, or UI without touching argument parsing.

## Setup

1. **Create a Binance Futures Testnet account**
   Register at https://testnet.binancefuture.com and log in.

2. **Generate API credentials**
   In the testnet dashboard, generate an API Key + Secret.

3. **Clone this repo and install dependencies**
   ```bash
   git clone <your-repo-url>
   cd trading_bot
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure credentials**
   ```bash
   cp .env.example .env
   # then edit .env and paste your testnet API key/secret
   ```
   The app reads `BINANCE_API_KEY` and `BINANCE_API_SECRET` from `.env`
   (via `python-dotenv`) or from real environment variables — it never
   asks for keys on the command line, so they don't end up in shell
   history or log files.

## How to Run

**Market order (BUY):**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit order (SELL):**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

**Stop-limit order (bonus order type):**
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 \
    --price 58000 --stop-price 58500
```

Each run prints:
- the order request summary (symbol, side, type, quantity, price if any)
- the order response (`orderId`, `status`, `executedQty`, `avgPrice`)
- a clear ✅ success / ❌ failure message

All requests, responses, and errors are also appended to `logs/trading_bot.log`.

## Running Tests

```bash
python -m pytest tests/
```
These cover the validation layer (bad symbols, missing prices, invalid
sides/types, non-numeric or negative quantities) without needing network
access or live credentials.

## Error Handling

- **Invalid input** (bad symbol format, unsupported side/type, non-numeric
  or non-positive quantity, missing price for LIMIT/STOP) is caught by
  `bot/validators.py` before any network call is made, and reported with a
  specific message.
- **API errors** (e.g. insufficient testnet balance, bad precision,
  invalid symbol on the exchange) are caught around the
  `futures_create_order` call and logged with the exchange's error detail.
- **Network failures** (timeouts, DNS issues, connection resets) are caught
  as a generic exception in `orders.py` so the CLI never crashes silently —
  it always prints a message and exits with a non-zero status on failure.

## Assumptions

- This targets **USDT-M Futures** (not Coin-M or Spot), per the task.
- Only `BUY`/`SELL` sides and `MARKET`/`LIMIT`/`STOP` order types are
  supported, matching the core requirement plus one bonus order type.
- LIMIT and STOP orders use `timeInForce=GTC` (Good-Til-Cancelled) since
  the task didn't specify a time-in-force policy.
- Quantity precision/step size and price tick size are assumed to already
  match the symbol's exchange filters (e.g. `0.01` for BTCUSDT); the bot
  does not auto-round to `LOT_SIZE`/`PRICE_FILTER` since that wasn't listed
  as a requirement, but this would be the first enhancement for production
  use (via `client.futures_exchange_info()`).
- Credentials are provided via `.env`, never hard-coded or passed as CLI
  arguments, to avoid leaking them into shell history or logs.

## Log Files

`logs/trading_bot.log` accumulates every run's requests/responses/errors,
including the sample MARKET and LIMIT order log entries required for
submission (see the `logs/` folder in this repo for those samples).