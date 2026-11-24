#!/usr/bin/env python3
"""
Solana Dust Cleaner & Rent Reclaimer
Scans wallets for empty SPL token accounts and shows reclaimable SOL.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Style, init
from tabulate import tabulate
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.keypair import Keypair

init(autoreset=True)
load_dotenv()

TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

def load_keypair(path: Path) -> Keypair:
    with open(path, "r") as f:
        secret = json.load(f)
    if isinstance(secret, list):
        return Keypair.from_bytes(bytes(secret))
    elif isinstance(secret, dict) and "secretKey" in secret:
        return Keypair.from_bytes(bytes(secret["secretKey"]))
    else:
        raise ValueError("Unknown keypair format")

def get_sol_balance(client: Client, pubkey: Pubkey) -> float:
    try:
        resp = client.get_balance(pubkey)
        return resp.value / 1_000_000_000
    except Exception:
        return 0.0

def get_empty_token_accounts(client: Client, owner: Pubkey):
    try:
        opts = TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)
        resp = client.get_token_accounts_by_owner(owner, opts)
        empty = []
        for acc in resp.value:
            # Token account data: amount is u64 at offset 64
            data = acc.account.data
            if len(data) >= 72:
                amount = int.from_bytes(data[64:72], "little")
                if amount == 0:
                    empty.append({
                        "pubkey": str(acc.pubkey),
                        "lamports": acc.account.lamports
                    })
        return empty
    except Exception as e:
        print(f"{Fore.RED}  RPC error: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Solana Dust Cleaner - Find & reclaim rent from empty token accounts")
    parser.add_argument("--execute", action="store_true", help="(Coming soon) Actually close accounts")
    args = parser.parse_args()

    rpc_url = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
    keys_dir = Path(os.getenv("KEYS_DIR", "keys"))

    if not keys_dir.exists():
        print(f"{Fore.RED}Error: '{keys_dir}' folder not found.")
        print(f"{Fore.YELLOW}Create a 'keys/' folder and add your wallet JSON keypairs.")
        sys.exit(1)

    print(f"{Fore.CYAN}Solana Dust Cleaner")
    print(f"{Fore.CYAN}RPC: {rpc_url}")
    print(f"{Fore.CYAN}Mode: {'EXECUTE' if args.execute else 'DRY-RUN (scan only)'}\n")

    client = Client(rpc_url)
    key_files = list(keys_dir.glob("*.json"))

    if not key_files:
        print(f"{Fore.YELLOW}No .json keypairs found in {keys_dir}/")
        print("Put your Solana wallet keypair JSON files there and run again.")
        sys.exit(0)

    total_reclaimable = 0.0
    table_data = []

    for key_file in key_files:
        try:
            keypair = load_keypair(key_file)
            pubkey = keypair.pubkey()
            balance = get_sol_balance(client, pubkey)
            empty_accounts = get_empty_token_accounts(client, pubkey)
            reclaimable = sum(a["lamports"] for a in empty_accounts) / 1_000_000_000

            print(f"{Fore.GREEN}{key_file.name}")
            print(f"  Address: {pubkey}")
            print(f"  SOL Balance: {balance:.6f}")
            print(f"  Empty accounts: {len(empty_accounts)}")
            print(f"  Reclaimable: {reclaimable:.6f} SOL\n")

            total_reclaimable += reclaimable
            table_data.append([
                key_file.name[:15],
                f"{balance:.4f}",
                len(empty_accounts),
                f"{reclaimable:.6f}"
            ])

        except Exception as e:
            print(f"{Fore.RED}Failed {key_file.name}: {e}\n")

    print(f"{Fore.CYAN}{'='*60}")
    if table_data:
        print(tabulate(table_data, headers=["Wallet", "SOL", "Empty", "Reclaimable"], tablefmt="rounded_outline"))
    print(f"\n{Fore.GREEN}Total Reclaimable: {total_reclaimable:.6f} SOL")
    print(f"{Fore.YELLOW}(Each empty token account holds ~0.002039 SOL)")

    if args.execute:
        print(f"\n{Fore.YELLOW}Execute mode is not fully implemented yet.")
        print("Use this scan first. Full close logic coming in next version.")
    else:
        print(f"\n{Fore.CYAN}Dry-run complete. Add --execute when close logic is ready.")

if __name__ == "__main__":
    main()
