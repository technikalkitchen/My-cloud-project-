import json
import urllib.request
import urllib.error
import time

BASE_URL = 'https://www.bitstamp.net/api/v2/ohlc/{pair}/?step=86400&limit=10'
PAIRS = ['btcusdt', 'btcusd', 'ethusd', 'ethbtc', 'solusd']

def test_pair(pair):
    url = BASE_URL.format(pair=pair)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            ohlc = data.get('data', {}).get('ohlc', [])
            if ohlc:
                return f"✅ OK (count={len(ohlc)})"
            return "⚠️ OK but empty"
    except urllib.error.HTTPError as e:
        return f"❌ HTTP {e.code}"
    except Exception as e:
        return f"❌ ERROR: {str(e)[:50]}"

def main():
    print('=== Bitstamp Diagnostic (5 pairs) ===')
    for p in PAIRS:
        print(f"Testing {p:10s} ... ", end='', flush=True)
        res = test_pair(p)
        print(res)
        time.sleep(1)
    print('=== Diagnostic Complete ===')

if __name__ == '__main__':
    main()
