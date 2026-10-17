# TEST001 MVP — Stage 2.2

## Contents
- `scripts/test001.py`: command-line entry point.
- `.github/workflows/test001_manual.yml`: manually triggered GitHub Actions workflow.
- `data/test001/universe.json`: 125 unique fixed symbols; each asset contains only `symbol`.
- `app/market/test001/runner.py`: accepts a missing `coingecko_id` and writes `null` in results.

## Local usage

Install `requests`, then run from this directory:

```bash
python -m pip install requests
python scripts/test001.py --limit-assets 2
```

Run the full universe with the default five exchanges and both timeframes:

```bash
python scripts/test001.py
```

Optional arguments:
- `--universe PATH`
- `--output PATH`
- `--exchanges binance,okx,bitstamp,coinbase,crypto_com`
- `--timeframes 5m,1h`
- `--limit-assets N`
- `--stop-on-exchange-error`

The workflow is started from **Actions → TEST001 Manual Run → Run workflow**. It uploads `data/test001/results.json` as the `test001-results` artifact when available. The workflow performs live public API requests; no live API test was run while preparing this bundle.
