# Copy-Trading Signer – User Steps (No DevOps)

1) Deploy signer
- Click the project’s “Deploy on Railway” button
- Set these variables:
  - RPC_URL: Polygon RPC (Alchemy/Infura/Ankr recommended)
  - PRIVATE_KEY: Your wallet private key (holds USDC + gas)
  - BYOS_AUTH: A secret string (save it; you’ll use it in the bot)
  - FEE_WALLET/FEE_BPS/MIN_FEE_USD are prefilled
- Click Deploy; copy your app URL (e.g., https://your-signer.up.railway.app)

2) Link in Telegram bot
- /link_signer → paste your signer URL
- Paste your wallet address when asked
- /consent → /agree → /enable_copy

3) Trade
- Fund wallet with USDC and gas (MATIC)
- When a ping arrives, tap “Copy 1×” to execute via your signer

Troubleshooting
- /fee_info shows the fee terms and service wallet
- Ensure your RPC is reliable; switch providers if requests time out
- Keep BYOS_AUTH secret; the bot will include it on requests if configured
