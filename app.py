import os
import time
import logging
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from web3 import Web3


RPC_URL = os.getenv("RPC_URL", "https://polygon-rpc.com")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "137"))
USDC_ADDRESS = os.getenv("USDC_ADDRESS", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
FEE_WALLET = os.getenv("FEE_WALLET", "0xYOURFEEWALLET")
FEE_BPS = int(os.getenv("FEE_BPS", "100"))
MIN_FEE_USD = float(os.getenv("MIN_FEE_USD", "0.50"))
BYOS_AUTH = os.getenv("BYOS_AUTH", "")
POLY_GAMMA_URL = os.getenv("POLY_GAMMA_URL", "https://gamma-api.polymarket.com")


app = FastAPI(title="BYOS Signer")
w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 20}))


class Order(BaseModel):
    leader_addr: str
    ratio: float
    side: str
    size: float
    limitPrice: float
    conditionId: Optional[str] = None
    timestamp: int


ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    }
]


def require_auth(header_auth: Optional[str]):
    if BYOS_AUTH and header_auth != BYOS_AUTH:
        raise HTTPException(status_code=401, detail="Unauthorized")


def send_usdc_fee(to_addr: str, usd_amount: float) -> Optional[str]:
    if usd_amount < MIN_FEE_USD:
        return None
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    token = w3.eth.contract(address=Web3.to_checksum_address(USDC_ADDRESS), abi=ERC20_ABI)
    # USDC has 6 decimals on Polygon
    amount = int(round(usd_amount * 10**6))
    tx = token.functions.transfer(Web3.to_checksum_address(to_addr), amount).build_transaction(
        {
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "chainId": CHAIN_ID,
            "maxFeePerGas": w3.to_wei("60", "gwei"),
            "maxPriorityFeePerGas": w3.to_wei("30", "gwei"),
        }
    )
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": int(time.time()),
        "fee_wallet": FEE_WALLET,
        "fee_bps": FEE_BPS,
        "min_fee_usd": MIN_FEE_USD,
    }


@app.post("/place")
def place(order: Order, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    # Compute notional in USD
    notional = float(order.size) * float(order.limitPrice)
    fee_usd = notional * FEE_BPS / 10_000

    # TODO: integrate Polymarket trade execution (Gamma API or smart contracts)
    # For now, call Gamma orders if provided, else return simulated id
    trade_tx = None
    try:
        import requests

        resp = requests.post(
            f"{POLY_GAMMA_URL.rstrip('/')}/orders",
            json={
                "side": order.side,
                "size": order.size,
                "price": order.limitPrice,
                "conditionId": order.conditionId,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            j = resp.json()
            trade_tx = j.get("txHash") or j.get("id")
    except Exception as e:
        logging.warning("Gamma order post failed: %s", e)

    fee_tx = None
    try:
        fee_tx = send_usdc_fee(FEE_WALLET, fee_usd)
    except Exception as e:
        logging.error("fee transfer failed: %s", e)

    return {
        "status": "OK",
        "orderId": f"order_{int(time.time())}",
        "txHash": trade_tx,
        "fee": {"status": "OK" if fee_tx else ("SKIPPED" if fee_usd < MIN_FEE_USD else "ERROR"), "tx": fee_tx},
    }


