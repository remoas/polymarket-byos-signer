# BYOS Signer (FastAPI)

Run your own copy-trading signer with one click on Railway.

Deploy on Railway:

[Deploy on Railway](https://railway.app/new/template?template=https://github.com/remoas/polymarket-byos-signer)

## Environment
- RPC_URL: Polygon RPC
- PRIVATE_KEY: Wallet private key (holds USDC and trades)
- BYOS_AUTH: Optional shared secret for the bot
- FEE_WALLET: Service fee wallet (pre-filled by template)
- FEE_BPS: Fee in basis points (default 100 = 1.00%)
- MIN_FEE_USD: Minimum fee in USD to transfer

## Endpoints
- GET /health → { status: ok }
- POST /place → executes a trade (via Gamma orders if configured) and sends fee in USDC

## Local run
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## Deploy on Railway
- Create a new project from this folder; set environment variables.
- Railway will give you a public URL like https://your-app.up.railway.app
- In Telegram bot: /link_signer → paste that URL
