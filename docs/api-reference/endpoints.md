---
layout: default
title: Endpoints & Queries
parent: API Reference
nav_order: 4
---

# Endpoints & GraphQL Queries
{: .fs-9 }

Reference for `Endpoints` and `GraphQLQueries` constants.
{: .fs-6 .fw-300 }

---

## Endpoints Class

```python
from stakeapi.endpoints import Endpoints, GraphQLQueries
```

The only real API surface is `/_api/graphql`. All `/api/v1/*` REST paths return 404.

| Constant | Value | Description |
|:---------|:------|:------------|
| `Endpoints.GRAPHQL` | `/_api/graphql` | GraphQL endpoint (POST) |

---

## GraphQLQueries Class

All queries verified against live stake.com and stake.us APIs (2025-05-10).

### User Queries

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `USER_BALANCES` | `UserBalances` | — |
| `USER_PROFILE` | `UserProfile` | — |
| `USER_META` | `UserMeta` | `name: String` |
| `USER_META_EXTENDED` | `UserMetaExtended` | `name: String, signupCode: Boolean` |
| `USER_ACCOUNT_INFO` | `UserAccountInfo` | — |
| `USER_KYC_STATUS` | `UserKycStatus` | — |
| `USER_SESSIONS` | `UserSessions` | — |
| `USER_API_KEYS` | `UserApiKeys` | — |
| `USER_STATISTIC` | `UserStatistic` | — |
| `USER_SEED_PAIR` | `UserSeedPair` | — |
| `IS_USER_TFA_ENABLED` | `IsUserTfaEnabled` | — |
| `USER_PREFERENCES` | `UserPreferences` | — |
| `USER_RECENT_GAME_LIST` | `UserRecentGameList` | `limit: Int` |

### VIP / Reload

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `VIP_META` | `VipMeta` | — |
| `FAUCET` | `Faucet` | — |
| `ACTIVE_RAKEBACK` | `ActiveRakeback` | — |
| `TIP_LIMIT` | `TipList` | `limit: Int` |

### Currency / Config

| Constant | Operation | Variables | Notes |
|:---------|:----------|:----------|:------|
| `CURRENCY_CONFIGURATION` | `CurrencyConfiguration` | `isAcp: Boolean!` | `true` for stake.us |
| `CURRENCY_NEW_CONVERSION_RATE` | `CurrencyNewConversionRate` | `displayCurrencies: [FiatCurrencyEnum!]!` | Values are lowercase: `["usd"]` |

### Bonus / Promo

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `BONUS_CODE_INFORMATION` | `BonusCodeInformation` | `code: String!, couponType: CouponType!` |
| `CAMPAIGN_LIST` | `CampaignList` | — |
| `CAMPAIGN_BALANCES` | `CampaignBalances` | — |

### Transaction / History

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `TRANSACTION` | `Transaction` | `types: [TransactionTypeEnum!], offset: Int, limit: Int` |
| `DEPOSIT_LIST` | `DepositList` | `offset: Int, limit: Int` |
| `WITHDRAWAL_LIST` | `WithdrawalList` | `offset: Int, limit: Int` |
| `MY_BET_LIST` | `MyBetList` | `limit: Int` |

### Casino / Games

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `BLACKJACK_ACTIVE_BET` | `BlackjackActiveBet` | — |
| `KURATOR_COLLECTION` | `KuratorCollection` | `type: GameKuratorCollectionEnum!` |
| `SLUG_KURATOR_GROUP` | `SlugKuratorGroup` | `slug: String!` |

### Sports

| Constant | Operation | Variables | Notes |
|:---------|:----------|:----------|:------|
| `SPORT_LIST_MENU` | `SportListMenu` | — | stake.com only |

### Social / Misc

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `ACTIVE_RACES` | `ActiveRaces` | — |
| `NOTIFICATION_LIST` | `NotificationList` | `offset: Int, limit: Int` |
| `PUBLIC_CHATS` | `PublicChats` | — |
| `BANNED_COUNTRIES` | `BannedCountries` | — |
| `PLAYER_COUNT_BY_SCOPE` | `PlayerCountByScope` | — |
| `FEATURE_FLAG_DETAILS` | `FeatureFlagDetails` | — |

### Mutations

| Constant | Operation | Variables |
|:---------|:----------|:----------|
| `CLAIM_CONDITION_BONUS_CODE` | `ClaimConditionBonusCode` | `code!, currency!, turnstileToken!` |
| `CLAIM_FAUCET` | `ClaimFaucet` | `currency!, turnstileToken!` |
| `CLAIM_RAKEBACK` | `ClaimRakeback` | — |
| `CREATE_VAULT_DEPOSIT` | `CreateVaultDeposit` | `currency!, amount!` |
| `ROTATE_SEED_PAIR` | `RotateSeedPair` | `seed!` |
| `BLACKJACK_BET` | `BlackjackBet` | `amount!, currency!, identifier!` |
| `BLACKJACK_NEXT` | `BlackjackNext` | `action!, identifier!` |

---

## Usage

```python
from stakeapi import StakeAPI
from stakeapi.endpoints import GraphQLQueries

async with StakeAPI(access_token="token", base_url="https://stake.us") as client:
    # Use a built-in query
    data = await client._graphql_request(
        GraphQLQueries.USER_BALANCES,
        operation_name="UserBalances",
    )

    # Use a query with variables
    data = await client._graphql_request(
        GraphQLQueries.CURRENCY_CONFIGURATION,
        variables={"isAcp": True},
        operation_name="CurrencyConfiguration",
    )

    # Use a query with type filter
    data = await client._graphql_request(
        GraphQLQueries.TRANSACTION,
        variables={"limit": 20, "types": ["rakeback", "bonusDrop"]},
        operation_name="Transaction",
    )
```

---

## Known Schema Quirks

- **`USER_PREFERENCES`**: `preference` field exists but has no queryable subfields beyond `__typename`.
- **`PLAYER_COUNT_BY_SCOPE`**: Takes no arguments; returns no count fields — only `__typename`.
- **`FEATURE_FLAG_DETAILS`**: `featureFlagList` returns `name` only — no `enabled` or `description` fields.
- **`CAMPAIGN_LIST`**: Maps to `raceList`, not `campaignList` (which doesn't exist).
- **`MY_BET_LIST`**: Maps to `chatList` — the API has no direct bet list field on `User`.
- **`ACTIVE_RAKEBACK`**: Schema is valid but server returns "You are not allowed to do that" on most accounts.
- **`KURATOR_COLLECTION`**: Requires a `GameKuratorCollectionEnum` value; valid values are not publicly documented.
- **`FiatCurrencyEnum`**: Values are lowercase (`"usd"`, `"eur"`) — not uppercase.
