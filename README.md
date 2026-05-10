# StakeAPI

### UPDATED MAY 2026

An unofficial async Python wrapper for the stake.com / stake.us GraphQL API.

## Disclaimer

This is an unofficial wrapper, not affiliated with or endorsed by Stake.com or Stake.us. Use at your own risk and ensure compliance with all applicable laws and the platform's terms of service.

## Features

- Async/await with `aiohttp`
- All GraphQL operations verified against live stake.com and stake.us APIs
- Pydantic v2 models with camelCase alias support
- Cloudflare bypass via `cf_clearance` cookie + matching User-Agent
- stake.us works with access token only — no Cloudflare cookie required

## Installation

```bash
pip install stakeapi
```

## Quick Start

```python
import asyncio
from stakeapi import StakeAPI

async def main():
    # stake.us — access token only
    async with StakeAPI(
        access_token="your_token",
        base_url="https://stake.us",
    ) as client:
        balance = await client.get_user_balance()
        print(balance)

asyncio.run(main())
```

### stake.com (requires Cloudflare clearance)

stake.com blocks requests without a valid `cf_clearance` cookie. Get it from your browser's DevTools (Application → Cookies → `cf_clearance`) or extract it with Playwright:

```python
async with StakeAPI(
    access_token="your_token",
    cf_clearance="your_cf_clearance_cookie",
    user_agent="Mozilla/5.0 ... Chrome/147.0.0.0 ...",  # must match cookie
    base_url="https://stake.com",
) as client:
    balance = await client.get_user_balance()
```

## Getting Your Access Token

1. Log in to stake.com in your browser
2. Open DevTools (F12) → Network tab
3. Make any action that triggers a request to `/_api/graphql`
4. Find the `x-access-token` request header — that's your token

## API Methods

### User

| Method                                      | Description                             |
| ------------------------------------------- | --------------------------------------- |
| `get_user_balance()`                        | Available + vault balances per currency |
| `get_user_profile()`                        | Name, email, verification status        |
| `get_user_meta(name=None)`                  | Lightweight user info with balances     |
| `get_user_meta_extended(name, signup_code)` | Extended info including self-exclude    |
| `get_user_account_info()`                   | Name, email, createdAt                  |
| `get_user_kyc_status()`                     | KYC status (stake.com only)             |
| `get_user_sessions()`                       | Active sessions with IP and location    |
| `get_user_api_keys()`                       | API key list                            |
| `get_user_statistic()`                      | Per-currency wagering stats             |
| `get_user_seed_pair()`                      | Provably fair client/server seeds       |
| `is_user_tfa_enabled()`                     | 2FA status                              |
| `get_user_preferences()`                    | User preferences object                 |
| `get_user_recent_games(limit)`              | Recently played games                   |

### VIP / Reload / Faucet

| Method                  | Description                           |
| ----------------------- | ------------------------------------- |
| `get_vip_meta()`        | Balances + reload status combined     |
| `get_faucet()`          | Reload/faucet status                  |
| `get_active_rakeback()` | Rakeback info (permission-restricted) |
| `get_tip_list(limit)`   | User tip history                      |

### Currency / Config

| Method                                     | Description                                       |
| ------------------------------------------ | ------------------------------------------------- |
| `get_currency_configuration(is_acp)`       | Currency rates; `is_acp=True` for stake.us        |
| `get_conversion_rates(display_currencies)` | Fiat conversion rates (lowercase enum: `["usd"]`) |

### Bonuses / Promos

| Method                                | Description             |
| ------------------------------------- | ----------------------- |
| `check_bonus_code(code, coupon_type)` | Check code availability |
| `get_racing_list()`                   | Race/campaign list      |
| `get_campaign_balances()`             | User campaign balances  |

### Transactions / History

| Method                                   | Description                                        |
| ---------------------------------------- | -------------------------------------------------- |
| `get_transactions(offset, limit, types)` | Transaction history with optional type filter      |
| `get_deposits(offset, limit)`            | Deposit history                                    |
| `get_withdrawals(offset, limit)`         | Withdrawal history                                 |
| `get_my_bets(limit)`                     | Chat list (direct bet history unavailable via API) |

### Casino / Games

| Method                                    | Description                                   |
| ----------------------------------------- | --------------------------------------------- |
| `get_blackjack_active_bet()`              | Active BJ bet or null                         |
| `get_kurator_collection(collection_type)` | Game collection by enum type                  |
| `get_kurator_group(slug)`                 | Game group by slug (e.g. `"stake-originals"`) |

### Sports (stake.com only)

| Method                  | Description                            |
| ----------------------- | -------------------------------------- |
| `get_sport_list_menu()` | Sport list (region-locked on stake.us) |

### Social / Misc

| Method                             | Description                             |
| ---------------------------------- | --------------------------------------- |
| `get_active_races()`               | Active races                            |
| `get_notifications(offset, limit)` | Notification list                       |
| `get_public_chats()`               | Public chat entries                     |
| `get_banned_countries()`           | Banned countries (CSV in `value` field) |
| `get_player_count()`               | Player count by scope                   |
| `get_feature_flags()`              | Feature flag list                       |

### Mutations

| Method                                              | Description                |
| --------------------------------------------------- | -------------------------- |
| `claim_bonus_code(code, currency, turnstile_token)` | Claim a bonus code         |
| `claim_faucet(currency, turnstile_token)`           | Claim reload bonus         |
| `claim_rakeback()`                                  | Claim rakeback             |
| `create_vault_deposit(currency, amount)`            | Deposit to vault           |
| `rotate_seed_pair(seed)`                            | Rotate provably fair seeds |
| `blackjack_bet(amount, currency, identifier)`       | Place BJ bet               |
| `blackjack_next(action, identifier)`                | Hit/stand/double           |

> **Note:** `claim_bonus_code` and `claim_faucet` require a Cloudflare Turnstile token (sitekey `0x4AAAAAAAGD4gMGOTFnvupz`), which must be generated in a browser context.

## Custom GraphQL Queries

```python
async with StakeAPI(access_token="token", base_url="https://stake.us") as client:
    data = await client._graphql_request(
        query="""
        query UserSeedPair {
          user {
            id
            activeClientSeed { seed }
            activeServerSeed { seedHash nonce }
          }
        }
        """,
        operation_name="UserSeedPair",
    )
    print(data)
```

## Development

```bash
make install-dev   # install with dev deps
make format        # black + isort
make check         # lint + typecheck + tests
```

## License

MIT
