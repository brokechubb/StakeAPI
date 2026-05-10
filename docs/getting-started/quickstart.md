---
layout: default
title: Quick Start
parent: Getting Started
nav_order: 3
---

# Quick Start
{: .fs-9 }

Your first API call in under 60 seconds.
{: .fs-6 .fw-300 }

---

## Prerequisites

- Python 3.8+
- `pip install stakeapi`
- A stake.com or stake.us access token (see [Authentication](authentication.md))

---

## stake.us — Simplest Setup

```python
import asyncio
from stakeapi import StakeAPI

ACCESS_TOKEN = "your_stake_us_token"

async def main():
    async with StakeAPI(access_token=ACCESS_TOKEN, base_url="https://stake.us") as client:

        # Balance
        balance = await client.get_user_balance()
        for currency, amount in balance["available"].items():
            if amount > 0:
                print(f"  {currency}: {amount}")

        # Profile
        profile = await client.get_user_profile()
        print(f"User: {profile['user']['name']}")

        # Recent games
        recent = await client.get_user_recent_games(limit=5)
        for game in recent["user"]["recentGameList"]:
            print(f"  Played: {game['name']}")

asyncio.run(main())
```

---

## stake.com — With Cloudflare Cookie

```python
import asyncio
from stakeapi import StakeAPI

ACCESS_TOKEN  = "your_stake_com_token"
CF_CLEARANCE  = "your_cf_clearance_cookie"
USER_AGENT    = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."

async def main():
    async with StakeAPI(
        access_token=ACCESS_TOKEN,
        cf_clearance=CF_CLEARANCE,
        user_agent=USER_AGENT,
        base_url="https://stake.com",
    ) as client:
        balance = await client.get_user_balance()
        print(balance)

asyncio.run(main())
```

---

## Common Patterns

### Run multiple requests concurrently

```python
import asyncio
from stakeapi import StakeAPI

async def main():
    async with StakeAPI(access_token="token", base_url="https://stake.us") as client:
        balance, faucet, sessions = await asyncio.gather(
            client.get_user_balance(),
            client.get_faucet(),
            client.get_user_sessions(),
        )
        print(balance, faucet, sessions)

asyncio.run(main())
```

### Paginate transactions

```python
async def all_transactions(client, page_size=50):
    offset, results = 0, []
    while True:
        data = await client.get_transactions(offset=offset, limit=page_size)
        page = data["user"]["transaction"]
        results.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return results
```

### Filter transactions by type

```python
rakeback_txs = await client.get_transactions(types=["rakeback"])
drops = await client.get_transactions(types=["bonusDrop", "chatTip"])
```

---

## Error Handling

```python
from stakeapi import StakeAPI
from stakeapi.exceptions import AuthenticationError, RateLimitError, StakeAPIError

async with StakeAPI(access_token="token", base_url="https://stake.us") as client:
    try:
        balance = await client.get_user_balance()
    except AuthenticationError:
        print("Invalid or expired token")
    except RateLimitError:
        print("Rate limited — slow down")
    except StakeAPIError as e:
        if "403" in str(e):
            print("Cloudflare blocked — need cf_clearance cookie")
        else:
            print(f"API error: {e}")
```

---

## What's Next?

- [Authentication](authentication.md) — Cloudflare bypass, Playwright cookie extraction
- [API Reference: Client](../api-reference/client.md) — All methods with parameters
- [API Reference: Endpoints](../api-reference/endpoints.md) — Raw GraphQL query constants
- [GraphQL Queries Guide](../guides/graphql-queries.md) — Writing custom queries
