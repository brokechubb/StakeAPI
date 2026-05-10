---
layout: default
title: Authentication
parent: Getting Started
nav_order: 2
---

# Authentication
{: .fs-9 }

How to authenticate with the Stake.com and Stake.us APIs.
{: .fs-6 .fw-300 }

---

## Overview

There are two domains with different authentication requirements:

| Domain | What you need |
|:-------|:-------------|
| **stake.us** | `access_token` only |
| **stake.com** | `access_token` + `cf_clearance` cookie + matching `user_agent` |

---

## Getting Your Access Token

1. Log in to stake.com (or stake.us) in your browser
2. Open DevTools — F12 or Ctrl+Shift+I
3. Go to the **Network** tab
4. Perform any action (check balance, browse games)
5. Find a request to `/_api/graphql`
6. Open its **Headers** tab and find `x-access-token`

The token is a 96-character hex string:
```
27a1afc27e2ae8b8...
```

### Extract from a copied cURL command

```python
from stakeapi.auth import AuthManager

curl = 'curl "https://stake.com/_api/graphql" -H "x-access-token: abc123..."'
token = AuthManager.extract_access_token_from_curl(curl)
```

---

## stake.us — Simple Setup

```python
import asyncio
import os
from stakeapi import StakeAPI

async def main():
    async with StakeAPI(
        access_token=os.getenv("STAKE_US_TOKEN"),
        base_url="https://stake.us",
    ) as client:
        balance = await client.get_user_balance()
        print(balance)

asyncio.run(main())
```

---

## stake.com — Cloudflare Bypass

stake.com runs Cloudflare's JS challenge, which blocks all non-browser HTTP clients. You need a valid `cf_clearance` cookie obtained by a real browser.

### Get `cf_clearance` from your browser

1. Log in to stake.com in Chrome/Firefox
2. Open DevTools → **Application** tab → **Cookies** → `https://stake.com`
3. Copy the `cf_clearance` value
4. Copy the exact User-Agent from DevTools → **Network** tab → any request headers

```python
async with StakeAPI(
    access_token="your_token",
    cf_clearance="Ivka2quxBBmVvv...",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
    base_url="https://stake.com",
) as client:
    balance = await client.get_user_balance()
```

{: .warning }
> `cf_clearance` expires after ~4 hours and is bound to the User-Agent that solved the challenge. The `user_agent` parameter must exactly match the browser that obtained the cookie.

### Headless servers — extract via Playwright

For servers without a browser, use Playwright to solve the CF challenge:

```python
from playwright.async_api import async_playwright

async def get_cf_clearance():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://stake.com")
        await page.wait_for_load_state("networkidle")  # CF challenge resolves here
        cookies = await page.context.cookies("https://stake.com")
        cf = next(c for c in cookies if c["name"] == "cf_clearance")
        ua = await page.evaluate("navigator.userAgent")
        await browser.close()
        return cf["value"], ua

cf_clearance, user_agent = await get_cf_clearance()
```

Headless Chrome 147 passes stake.com's CF challenge with no stealth plugins.

---

## Environment Variables

```bash
# .env
STAKE_US_TOKEN=your_stake_us_token
STAKE_COM_TOKEN=your_stake_com_token
CF_CLEARANCE=your_cf_clearance_cookie
USER_AGENT=Mozilla/5.0 ...
```

```python
import os
from dotenv import load_dotenv
from stakeapi import StakeAPI

load_dotenv()

async with StakeAPI(
    access_token=os.getenv("STAKE_US_TOKEN"),
    base_url="https://stake.us",
) as client:
    pass
```

{: .warning }
> Never commit `.env` or any file containing tokens to version control.

---

## Token Lifecycle

| Property | Detail |
|:---------|:-------|
| Format | 96-character hex string |
| Scope | Full account access |
| Expiry | Session-based (days to weeks) |
| `cf_clearance` expiry | ~4 hours |

---

## Handling Expired Tokens

```python
from stakeapi import StakeAPI
from stakeapi.exceptions import AuthenticationError

async with StakeAPI(access_token="your_token") as client:
    try:
        balance = await client.get_user_balance()
    except AuthenticationError:
        print("Token expired — get a new one from your browser DevTools")
```
