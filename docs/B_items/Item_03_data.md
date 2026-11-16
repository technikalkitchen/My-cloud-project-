# Item_03 — Test Data

> **Note:** `available_from` and `presence_status` are NOT in this file.
> They are calculated in **Item_13 (Bootstrap)** using `effective_start = max(exchange_start, listing_date)`.

## Source: `cmc_classify_2026-11-15.json`
**Description:** Classification of 125 universe assets based on CMC tags

### `classification_map`

- **BTC**: regular
- **ETH**: regular
- **USDT**: stablecoin
- **BNB**: regular
- **XRP**: regular
- **USDC**: stablecoin
- **SOL**: regular
- **TRX**: regular
- **ZEC**: regular
- **HYPE**: regular
- **XMR**: regular
- **DOGE**: regular
- **LEO**: regular
- **LINK**: regular
- **ADA**: regular
- **XLM**: regular
- **USDe**: stablecoin
- **BCH**: regular
- **NEAR**: regular
- **DAI**: stablecoin
- **UNI**: regular
- **LTC**: regular
- **CC**: regular
- **AVAX**: regular
- **SUI**: regular
- **USD1**: stablecoin
- **XAUt**: regular
- **GRAM**: regular
- **HBAR**: regular
- **PYUSD**: stablecoin
- **USDG**: stablecoin
- **RLUSD**: stablecoin
- **TAO**: regular
- **SHIB**: regular
- **CRO**: regular
- **QNT**: regular
- **OKB**: regular
- **PEPE**: regular
- **ENA**: regular
- **AAVE**: regular
- **ASTER**: regular
- **M**: regular
- **PAXG**: regular
- **ONDO**: regular
- **PUMP**: regular
- **U**: stablecoin
- **DOT**: regular
- **USDD**: stablecoin
- **SKY**: regular
- **MNT**: regular
- **WLFI**: regular
- **ICP**: regular
- **BGB**: regular
- **WLD**: regular
- **ARB**: regular
- **JST**: regular
- **MORPHO**: regular
- **ETC**: regular
- **GT**: regular
- **VVV**: regular
- **KCS**: regular
- **POL**: regular
- **ALGO**: regular
- **PI**: regular
- **KAS**: regular
- **INJ**: regular
- **RENDER**: regular
- **LIT**: regular
- **JUP**: regular
- **ATOM**: regular
- **NIGHT**: regular
- **XDC**: regular
- **FIL**: regular
- **ZRO**: regular
- **AERO**: regular
- **STX**: regular
- **CAKE**: regular
- **DASH**: regular
- **ETHFI**: regular
- **APT**: regular
- **FLR**: regular
- **币安人生**: regular
- **PYTH**: regular
- **TUSD**: stablecoin
- **RAY**: regular
- **NEXO**: regular
- **STABLE**: regular
- **EURC**: stablecoin
- **PIEVERSE**: regular
- **VET**: regular
- **TIA**: regular
- **CRV**: regular
- **PENGU**: regular
- **VIRTUAL**: regular
- **BTT**: regular
- **SEI**: regular
- **FET**: regular
- **TRUMP**: regular
- **SPX**: regular
- **BSV**: regular
- **KITE**: regular
- **FF**: regular
- **STRK**: regular
- **SUN**: regular
- **GNO**: regular
- **FDUSD**: stablecoin
- **XTZ**: regular
- **PENDLE**: regular
- **LDO**: regular
- **XPL**: regular
- **BONK**: regular
- **IMX**: regular
- **OP**: regular
- **LUNC**: regular
- **DCR**: regular
- **CFX**: regular
- **BEAM**: regular
- **GRT**: regular
- **AR**: regular
- **FLOKI**: regular
- **KAIA**: regular
- **COMP**: regular
- **KMNO**: regular
- **MON**: regular
- **NFT**: regular

### `stablecoins_list`

DAI, EURC, FDUSD, PYUSD, RLUSD, TUSD, U, USD1, USDC, USDD, USDG, USDT, USDe

### `wrapped_symbols_list`

_empty list_

### `support_asset_symbols_list`

USDT


---

## Source: `cmc_top125_fetch_2026-11-15.json`
**Description:** Universe selection: top 125 from CMC 150 (excludes 25 lowest ranks)

### `universe_symbols_list`

| rank | symbol | cmc_id | name | tags |
|---|---|---|---|---|
| 1 | BTC | 1 | Bitcoin | pow, layer-1 |
| 2 | ETH | 1027 | Ethereum | pos, smart-contracts, layer-1 |
| 3 | USDT | 825 | Tether USDt | stablecoin |
| 4 | BNB | 1839 | BNB | smart-contracts, layer-1 |
| 5 | XRP | 52 | XRP | - |
| 6 | USDC | 3408 | USDC | stablecoin |
| 7 | SOL | 5426 | Solana | pos, layer-1 |
| 8 | TRX | 1958 | TRON | layer-1 |
| 9 | ZEC | 1437 | Zcash | pow, privacy, layer-1 |
| 10 | HYPE | 32196 | Hyperliquid | defi, layer-1 |
| 11 | XMR | 328 | Monero | pow, privacy, layer-1 |
| 12 | DOGE | 74 | Dogecoin | pow, memes |
| 13 | LEO | 3957 | UNUS SED LEO | - |
| 14 | LINK | 1975 | Chainlink | defi, privacy, smart-contracts |
| 15 | ADA | 2010 | Cardano | pos, smart-contracts, layer-1 |
| 16 | XLM | 512 | Stellar | defi, smart-contracts |
| 17 | USDe | 29470 | Ethena USDe | stablecoin |
| 18 | BCH | 1831 | Bitcoin Cash | pow, layer-1 |
| 19 | NEAR | 6535 | NEAR Protocol | layer-1 |
| 20 | DAI | 4943 | Dai | defi, stablecoin |
| 21 | UNI | 7083 | Uniswap | defi |
| 22 | LTC | 2 | Litecoin | pow, privacy, layer-1 |
| 23 | CC | 37263 | Canton | privacy, smart-contracts, layer-1 |
| 24 | AVAX | 5805 | Avalanche | smart-contracts, layer-1 |
| 25 | SUI | 20947 | Sui | layer-1 |
| 26 | USD1 | 36148 | World Liberty Financial USD | stablecoin |
| 27 | XAUt | 5176 | Tether Gold | - |
| 28 | GRAM | 11419 | Gram (prev. Toncoin) | pos, layer-1 |
| 29 | HBAR | 4642 | Hedera | layer-1 |
| 30 | PYUSD | 27772 | PayPal USD | stablecoin |
| 31 | USDG | 33793 | Global Dollar | stablecoin |
| 32 | RLUSD | 34387 | Ripple USD | stablecoin |
| 33 | TAO | 22974 | Bittensor | layer-1 |
| 34 | SHIB | 5994 | Shiba Inu | memes |
| 35 | CRO | 3635 | Cronos | layer-1 |
| 36 | QNT | 3155 | Quant | defi |
| 37 | OKB | 3897 | OKB | layer-2 |
| 38 | PEPE | 24478 | Pepe | memes |
| 39 | ENA | 30171 | Ethena | defi |
| 40 | AAVE | 7278 | Aave | defi |
| 41 | ASTER | 36341 | Aster | defi |
| 42 | M | 35491 | MemeCore | memes, layer-1 |
| 43 | PAXG | 4705 | PAX Gold | - |
| 44 | ONDO | 21159 | Ondo | - |
| 45 | PUMP | 36507 | Pump.fun | - |
| 46 | U | 39120 | United Stables | stablecoin |
| 47 | DOT | 6636 | Polkadot | defi |
| 48 | USDD | 19891 | USDD | stablecoin |
| 49 | SKY | 33038 | Sky | defi |
| 50 | MNT | 27075 | Mantle | layer-2 |
| 51 | WLFI | 33251 | World Liberty Financial | defi |
| 52 | ICP | 8916 | Internet Computer | smart-contracts, layer-1 |
| 53 | BGB | 11092 | Bitget Token | - |
| 54 | WLD | 13502 | Worldcoin | defi |
| 55 | ARB | 11841 | Arbitrum | layer-2 |
| 56 | JST | 5488 | JUST | defi |
| 57 | MORPHO | 34104 | Morpho | defi |
| 58 | ETC | 1321 | Ethereum Classic | pow, smart-contracts, layer-1 |
| 59 | GT | 4269 | GateToken | - |
| 60 | VVV | 35509 | Venice Token | - |
| 61 | KCS | 2087 | KuCoin Token | - |
| 62 | POL | 28321 | Polygon (prev. MATIC) | layer-2 |
| 63 | ALGO | 4030 | Algorand | pos, smart-contracts, layer-1 |
| 64 | PI | 35697 | Pi | layer-1 |
| 65 | KAS | 20396 | Kaspa | pow, layer-1 |
| 66 | INJ | 7226 | Injective | pos, privacy, smart-contracts, layer-1 |
| 67 | RENDER | 5690 | Render | defi |
| 68 | LIT | 39125 | Lighter | defi |
| 69 | JUP | 29210 | Jupiter | defi |
| 70 | ATOM | 3794 | Cosmos | defi |
| 71 | NIGHT | 39064 | Midnight | privacy |
| 72 | XDC | 2634 | XDC Network | pos, smart-contracts, layer-1 |
| 73 | FIL | 2280 | Filecoin | layer-1 |
| 74 | ZRO | 26997 | LayerZero | defi |
| 75 | AERO | 29270 | Aero | defi |
| 76 | STX | 4847 | Stacks | smart-contracts, layer-2 |
| 77 | CAKE | 7186 | PancakeSwap | defi, smart-contracts |
| 78 | DASH | 131 | Dash | privacy |
| 79 | ETHFI | 29814 | ether.fi | defi |
| 80 | APT | 21794 | Aptos | layer-1 |
| 81 | FLR | 7950 | Flare | layer-1 |
| 82 | 币安人生 | 38590 | 币安人生 | memes |
| 83 | PYTH | 28177 | Pyth Network | defi |
| 84 | TUSD | 2563 | TrueUSD | stablecoin |
| 85 | RAY | 8526 | Raydium | defi |
| 86 | NEXO | 2694 | Nexo | - |
| 87 | STABLE | 38892 | Stable | layer-1 |
| 88 | EURC | 20641 | EURC | stablecoin |
| 89 | PIEVERSE | 38849 | Pieverse | - |
| 90 | VET | 3077 | VeChain | smart-contracts, layer-1 |
| 91 | TIA | 22861 | Celestia | layer-1 |
| 92 | CRV | 6538 | Curve DAO Token | defi |
| 93 | PENGU | 34466 | Pudgy Penguins | memes |
| 94 | VIRTUAL | 29420 | Virtuals Protocol | - |
| 95 | BTT | 16086 | BitTorrent [New] | defi |
| 96 | SEI | 23149 | Sei | layer-1 |
| 97 | FET | 3773 | Artificial Superintelligence Alliance | - |
| 98 | TRUMP | 35336 | OFFICIAL TRUMP | memes |
| 99 | SPX | 28081 | SPX6900 | memes |
| 100 | BSV | 3602 | Bitcoin SV | pow |
| 101 | KITE | 38828 | Kite | layer-1 |
| 102 | FF | 38482 | Falcon Finance | - |
| 103 | STRK | 22691 | Starknet | privacy, smart-contracts, layer-2 |
| 104 | SUN | 10529 | Sun [New] | - |
| 105 | GNO | 1659 | Gnosis | layer-1 |
| 106 | FDUSD | 26081 | First Digital USD | stablecoin |
| 107 | XTZ | 2011 | Tezos | pos, privacy, smart-contracts, layer-1 |
| 108 | PENDLE | 9481 | Pendle | defi |
| 109 | LDO | 8000 | Lido DAO | defi |
| 110 | XPL | 36645 | Plasma | layer-1 |
| 111 | BONK | 23095 | Bonk | memes |
| 112 | IMX | 10603 | Immutable | layer-2 |
| 113 | OP | 11840 | Optimism | layer-2 |
| 114 | LUNC | 4172 | Terra Classic | defi |
| 115 | DCR | 1168 | Decred | privacy, layer-1 |
| 116 | CFX | 7334 | Conflux | pow, defi, smart-contracts, layer-1 |
| 117 | BEAM | 28298 | Beam | - |
| 118 | GRT | 6719 | The Graph | defi |
| 119 | AR | 5632 | Arweave | layer-1 |
| 120 | FLOKI | 10804 | FLOKI | defi, memes |
| 121 | KAIA | 32880 | Kaia | layer-1 |
| 122 | COMP | 5692 | Compound | defi |
| 123 | KMNO | 30986 | Kamino | defi |
| 124 | MON | 30495 | Monad | defi, smart-contracts, layer-1 |
| 125 | NFT | 9816 | AINFT | - |

### `excluded_symbols_list`

| rank | symbol | cmc_id | name |
|---|---|---|---|
| 126 | ENS | 13855 | Ethereum Name Service |
| 127 | RUNE | 4157 | THORChain |
| 128 | AKT | 7431 | Akash Network |
| 129 | BAT | 1697 | Basic Attention Token |
| 130 | FLUID | 10508 | Fluid |
| 131 | ZBCN | 30636 | Zebec Network |
| 132 | CVX | 9903 | Convex Finance |
| 133 | JTO | 28541 | Jito |
| 134 | JASMY | 8425 | JasmyCoin |
| 135 | TWT | 5964 | Trust Wallet Token |
| 136 | TRAC | 2467 | OriginTrail |
| 137 | MET | 38353 | Meteora |
| 138 | ZAMA | 39332 | Zama |
| 139 | EIGEN | 30494 | EigenCloud |
| 140 | IOTA | 1720 | IOTA |
| 141 | SYRUP | 33824 | Maple Finance |
| 142 | CAP | 40531 | Cap |
| 143 | WIF | 28752 | dogwifhat |
| 144 | SOON | 36542 | SOON |
| 145 | GOMINING | 10180 | GoМining |
| 146 | TEL | 2394 | Telcoin |
| 147 | AXS | 6783 | Axie Infinity |
| 148 | MANA | 1966 | Decentraland |
| 149 | THETA | 2416 | Theta Network |
| 150 | XCN | 18679 | Onyxcoin |

### `source_file`

tests/evidence/cmc_top150_2026-11-08.json


---

