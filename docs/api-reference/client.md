---
layout: default
title: StakeAPI Client
parent: API Reference
nav_order: 1
---

# StakeAPI Client
{: .fs-9 }

Complete reference for the `StakeAPI` client class.
{: .fs-6 .fw-300 }

---

## Class: `StakeAPI`

The main client for interacting with the Stake.com/Stake.us GraphQL API.

**Import:**

```python
from stakeapi import StakeAPI
```

---

## Constructor

```python
StakeAPI(
    access_token: Optional[str] = None,
    session_cookie: Optional[str] = None,
    cf_clearance: Optional[str] = None,
    user_agent: Optional[str] = None,
    base_url: str = "https://stake.com",
    timeout: int = 30,
    rate_limit: int = 10,
)
```

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `access_token` | `Optional[str]` | `None` | `x-access-token` header value |
| `session_cookie` | `Optional[str]` | `None` | Session cookie |
| `cf_clearance` | `Optional[str]` | `None` | Cloudflare clearance cookie (stake.com only) |
| `user_agent` | `Optional[str]` | `None` | Must match the browser that obtained `cf_clearance` |
| `base_url` | `str` | `"https://stake.com"` | Use `"https://stake.us"` for stake.us |
| `timeout` | `int` | `30` | Request timeout in seconds |
| `rate_limit` | `int` | `10` | Max requests per second |

**stake.us** — only `access_token` required:

```python
client = StakeAPI(
    access_token="your_token",
    base_url="https://stake.us",
)
```

**stake.com** — requires `cf_clearance` + matching `user_agent`:

```python
client = StakeAPI(
    access_token="your_token",
    cf_clearance="your_cf_clearance_value",
    user_agent="Mozilla/5.0 ... Chrome/147.0.0.0 ...",
    base_url="https://stake.com",
)
```

---

## Context Manager

```python
async with StakeAPI(access_token="token", base_url="https://stake.us") as client:
    balance = await client.get_user_balance()
```

---

## User Methods

### `get_user_balance()`

Returns available and vault balances keyed by currency.

```python
balance = await client.get_user_balance()
# {"available": {"btc": 0.001, "sol": 4.0}, "vault": {"sol": 3.2}}
```

### `get_user_profile()`

Returns name, email, `hasEmailVerified`, `isMuted`, `isRainproof`, `isBanned`, `createdAt`.

### `get_user_meta(name=None)`

Lightweight user info with balances. Pass `name` to look up another user.

### `get_user_meta_extended(name=None, signup_code=False)`

Extended user info: `isMuted`, `isBanned`, `createdAt`, `campaignSet`, `selfExclude`.

### `get_user_account_info()`

Returns `id`, `name`, `email`, `createdAt`. No `country` field.

### `get_user_kyc_status()`

Returns `kycStatus`. Returns `null` on stake.us.

### `get_user_sessions()`

Returns `sessionList` entries with `id`, `sessionName`, `ip`, `active`, `country`, `city`, `createdAt`, `updatedAt`.

### `get_user_api_keys()`

Returns `apiKeys` entries with `id`, `ip`, `active`, `sessionName`, `type`, `createdAt`, `updatedAt`.

### `get_user_statistic()`

Returns per-currency `statistic` array: `id`, `betAmount`, `profit`, `amount`, `currency`.

### `get_user_seed_pair()`

Returns `activeClientSeed` (id, seed) and `activeServerSeed` (id, nonce, seedHash, nextSeedHash).

### `is_user_tfa_enabled()`

Returns `hasTfaEnabled` boolean.

### `get_user_preferences()`

Returns `preference { __typename }` only — field names not accessible.

### `get_user_recent_games(limit=10)`

Returns `recentGameList` entries with `id`, `name`, `slug`.

---

## VIP / Reload / Faucet Methods

### `get_vip_meta()`

Returns user balances and reload/faucet status (aliased as `reload`).

### `get_faucet()`

Returns `faucet` with `active`, `value`, `claimInterval`, `lastClaim`, `expireAt`.

### `get_active_rakeback()`

Returns rakeback info. Most accounts receive "You are not allowed to do that."

### `get_tip_list(limit=20)`

Returns `tipList` — `ChatTip` objects with `id`, `amount`, `currency`, `user`.

---

## Currency / Config Methods

### `get_currency_configuration(is_acp=False)`

Returns currency rates. Set `is_acp=True` for stake.us.

### `get_conversion_rates(display_currencies)`

```python
rates = await client.get_conversion_rates(["usd", "eur"])
```

`display_currencies` values must be **lowercase** (`"usd"`, not `"USD"`).

---

## Bonus / Promo Methods

### `check_bonus_code(code, coupon_type="drop")`

Returns `availabilityStatus`, `bonusValue`, `cryptoMultiplier`.

### `get_racing_list()`

Returns race list (`raceList`) with `id`, `name`.

### `get_campaign_balances()`

Returns `campaignBalances` list (usually empty).

---

## Transaction / History Methods

### `get_transactions(offset=0, limit=20, types=None)`

```python
# All transactions
txs = await client.get_transactions(limit=50)

# Filter by type
rakeback = await client.get_transactions(types=["rakeback"])
drops = await client.get_transactions(types=["bonusDrop", "chatTip"])
```

Returns `id`, `amount`, `currency`, `type`, `createdAt`.

### `get_deposits(offset=0, limit=20)`

Returns `WalletDeposit` objects: `id`, `amount`, `currency`, `status`, `createdAt`.

### `get_withdrawals(offset=0, limit=20)`

Returns `WalletWithdrawal` objects: `id`, `amount`, `currency`, `status`, `createdAt`.

### `get_my_bets(limit=20)`

Returns `chatList` entries. Direct bet history is not available via the user API.

---

## Casino / Game Methods

### `get_blackjack_active_bet()`

Returns the active blackjack bet or `null` if none.

### `get_kurator_collection(collection_type)`

Returns a game collection. `collection_type` must be a valid `GameKuratorCollectionEnum` value (enum values not publicly documented).

### `get_kurator_group(slug)`

```python
group = await client.get_kurator_group("stake-originals")
# {"slugKuratorGroup": {"id": "...", "name": "Stake Originals", "gameCount": 31}}
```

---

## Sports Methods

### `get_sport_list_menu()`

Returns `sportList` with `id`, `name`, `slug`. **stake.com only** — returns a connection error on stake.us.

---

## Social / Misc Methods

### `get_active_races()`

Returns `activeRaces` with `id`, `name`, `startTime`, `endTime`, `type`, `currency`.

### `get_notifications(offset=0, limit=20)`

Returns `notificationList` with `id`, `type`, `createdAt`.

### `get_public_chats()`

Returns `chats` with `id`, `__typename` only.

### `get_banned_countries()`

Returns `info.bannedCountries` with `name` and `value` (CSV of country codes).

### `get_player_count()`

Returns `playerCountByScope { __typename }` — no count fields accessible.

### `get_feature_flags()`

Returns `featureFlagList` with `name` only.

---

## Mutation Methods

### `claim_bonus_code(code, currency, turnstile_token)`

Claims a condition bonus code. Requires a Cloudflare Turnstile token.

```python
result = await client.claim_bonus_code(
    code="MYCODE",
    currency="btc",
    turnstile_token="0.abc...",  # generated in browser
)
```

### `claim_faucet(currency, turnstile_token)`

Claims the reload bonus. Requires a Turnstile token.

### `claim_rakeback()`

Claims rakeback. No parameters.

### `create_vault_deposit(currency, amount)`

Moves `amount` of `currency` from available to vault.

### `rotate_seed_pair(seed)`

Rotates the provably fair client/server seed pair. `seed` is your new client seed string.

### `blackjack_bet(amount, currency, identifier)`

Places a blackjack bet. `identifier` is a unique string you choose.

### `blackjack_next(action, identifier)`

Takes the next action on an active blackjack hand.

```python
# Hit
result = await client.blackjack_next(
    action={"action": "hit"},
    identifier="your_bet_identifier",
)

# Stand
result = await client.blackjack_next(
    action={"action": "stand"},
    identifier="your_bet_identifier",
)
```

---

## Internal Methods

### `_graphql_request(query, variables=None, operation_name=None)`

Execute any raw GraphQL query:

```python
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
```

Raises `StakeAPIError` on GraphQL errors.

### `close()`

```python
await client.close()
```
