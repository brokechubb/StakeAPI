---
layout: default
title: GraphQL Queries
parent: Guides
nav_order: 5
---

# GraphQL Queries
{: .fs-9 }

Using the raw GraphQL API for maximum flexibility.
{: .fs-6 .fw-300 }

---

## Overview

Stake.com's only API surface is `/_api/graphql` (POST). There are no REST endpoints. All client methods are thin wrappers around `_graphql_request()`.

---

## Making Raw Requests

```python
from stakeapi import StakeAPI

async with StakeAPI(access_token="token", base_url="https://stake.us") as client:
    data = await client._graphql_request(
        query="""
        query UserSeedPair {
          user {
            id
            activeClientSeed { id seed __typename }
            activeServerSeed { id nonce seedHash nextSeedHash __typename }
            __typename
          }
        }
        """,
        operation_name="UserSeedPair",
    )
    print(data["user"]["activeServerSeed"]["seedHash"])
```

---

## Using Built-in Queries

```python
from stakeapi.endpoints import GraphQLQueries

# Query with variables
data = await client._graphql_request(
    GraphQLQueries.CURRENCY_CONFIGURATION,
    variables={"isAcp": True},   # True for stake.us
    operation_name="CurrencyConfiguration",
)

# Query with type filter
data = await client._graphql_request(
    GraphQLQueries.TRANSACTION,
    variables={"limit": 20, "types": ["rakeback", "bonusDrop"]},
    operation_name="Transaction",
)
```

---

## Verified Working Queries

### Balance

```graphql
query UserBalances {
  user {
    id
    balances {
      available { amount currency __typename }
      vault { amount currency __typename }
      __typename
    }
    __typename
  }
}
```

### Deposits

```graphql
query DepositList($offset: Int, $limit: Int) {
  user {
    id
    depositList(offset: $offset, limit: $limit) {
      id
      amount
      currency
      status
      createdAt
      __typename
    }
    __typename
  }
}
```

### Faucet / Reload Status

```graphql
query Faucet {
  user {
    id
    faucet {
      id
      active
      value
      claimInterval
      lastClaim
      expireAt
      __typename
    }
    __typename
  }
}
```

### Conversion Rates (FiatCurrencyEnum is lowercase)

```graphql
query CurrencyNewConversionRate($displayCurrencies: [FiatCurrencyEnum!]!) {
  info {
    currencies {
      name
      values(displayCurrencies: $displayCurrencies) {
        currency
        rate
        __typename
      }
      __typename
    }
    __typename
  }
}
```

Variables: `{"displayCurrencies": ["usd", "eur"]}` — **lowercase**.

### Active Races

```graphql
query ActiveRaces {
  activeRaces {
    id
    name
    startTime
    endTime
    type
    currency
    __typename
  }
}
```

### Bonus Code Check

```graphql
query BonusCodeInformation($code: String!, $couponType: CouponType!) {
  bonusCodeInformation(code: $code, couponType: $couponType) {
    availabilityStatus
    bonusValue
    cryptoMultiplier
    __typename
  }
}
```

Variables: `{"code": "MYCODE", "couponType": "drop"}`

### Claim Rakeback (Mutation)

```graphql
mutation ClaimRakeback {
  claimRakeback {
    amount
    currency
    user {
      id
      balances {
        available { amount currency __typename }
        __typename
      }
      __typename
    }
    __typename
  }
}
```

### Blackjack Bet (Mutation)

```graphql
mutation BlackjackBet(
  $amount: Float!,
  $currency: CurrencyEnum!,
  $identifier: String!
) {
  blackjackBet(
    amount: $amount,
    currency: $currency,
    identifier: $identifier
  ) {
    id
    active
    nonce
    amount
    payout
    currency
    state {
      ... on CasinoGameBlackjack {
        player { value actions cards { rank suit __typename } __typename }
        dealer { value actions cards { rank suit __typename } __typename }
      }
    }
    __typename
  }
}
```

---

## Schema Quirks

- **`preferences` is singular**: `preference { __typename }` — no queryable subfields.
- **`hasTfaEnabled`** not `isTfaEnabled`.
- **`sessionList`** not `sessions`; has `sessionName`, `ip`, `country`, `city`, `updatedAt`.
- **`statistic`** (array) not `statistics`.
- **`campaignList`** doesn't exist — use `raceList`.
- **`betList` on User** doesn't exist — use `transaction` with type filters.
- **`chatList` on User** exists but returns chat entries, not bet history.
- **`bannedCountries`** lives under `info { bannedCountries { name value } }` where `value` is a CSV of country codes.
- **`FiatCurrencyEnum`** values are lowercase (`"usd"`, `"eur"`, `"bhd"`, etc.).
- **Sports queries** are region-locked on stake.us — `sportList` returns a connection error.

---

## Tips

1. **Always include `__typename`** — the API expects it on every selection.
2. **Name your operations** — makes debugging easier and is required for batching.
3. **Don't use string interpolation** — always use variables for values.
4. **Filter transactions by type** — use `types: ["rakeback"]` instead of fetching all and filtering client-side.
5. **Concurrent requests with `asyncio.gather`** — the aiohttp session is thread-safe for concurrent use within one event loop.
