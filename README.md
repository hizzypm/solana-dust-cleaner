# Solana Dust Cleaner & Rent Reclaimer

A simple, open-source Python tool that helps you reclaim locked SOL from empty token accounts across one or multiple wallets.

## What it does

- Scans your Solana wallet(s) for empty SPL token accounts
- Closes those empty accounts to reclaim the ~0.002 SOL rent
- Optionally burns spam tokens/NFTs before closing
- Shows a clear summary of how much SOL you can recover
- Dry-run mode by default (safe)

## Features

- Multi-wallet support (put keypairs in a folder)
- Dry-run by default
- Clean colored CLI output
- Works with any RPC (Helius, QuickNode, public, etc.)
- Reclaims rent from empty token accounts

## Installation

```bash
git clone https://github.com/hizzypm/solana-dust-cleaner.git
cd solana-dust-cleaner
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. Put your wallet keypairs (JSON format) inside a `keys/` folder
2. Copy `.env.example` to `.env` and set your RPC URL (optional)
3. Run:

```bash
# Dry run (recommended first)
python reclaim_dust.py

# Actually close accounts and reclaim SOL
python reclaim_dust.py --execute
```

## Safety

- Always run in dry-run mode first
- Never share your private keys
- This tool only closes **empty** accounts
- Use at your own risk

## Roadmap

- [ ] Burn spam NFTs before closing
- [ ] Pump.fun creator rewards claim
- [ ] Telegram notifications
- [ ] Web UI

---

Built for the community. Star it if it helped you reclaim SOL.
