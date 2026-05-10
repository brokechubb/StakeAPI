---
layout: default
title: Data Models
parent: API Reference
nav_order: 3
---

# Data Models
{: .fs-9 }

Pydantic v2 models matching the real Stake.com GraphQL response shapes.
{: .fs-6 .fw-300 }

---

## Overview

All models extend `StakeModel`, a `BaseModel` subclass that uses `alias_generator=_to_camel` so camelCase API responses (`sessionName`, `createdAt`) map automatically to snake_case Python fields (`session_name`, `created_at`).

```python
from stakeapi.models import (
    User, BalanceEntry, SessionInfo, ApiKeyInfo,
    StatisticEntry, FaucetInfo, TransactionEntry,
    BlackjackBet, BlackjackCard, BlackjackHand,
    BonusCodeInfo, KuratorCollection, KuratorGame,
    CurrencyInfo, SportItem, RaceInfo, NotificationEntry,
)
```

All models have a `from_dict(data)` classmethod.

---

## User

```python
class User(StakeModel):
    id: str = ""
    name: str = ""
    email: Optional[str] = None
    has_email_verified: bool = False   # API: hasEmailVerified
    is_muted: bool = False             # API: isMuted
    is_rainproof: bool = False         # API: isRainproof
    is_banned: bool = False            # API: isBanned
    created_at: Optional[str] = None   # API: createdAt
```

---

## BalanceEntry

Single currency balance (available or vault).

```python
class BalanceEntry(StakeModel):
    amount: Decimal = Decimal("0")
    currency: str = ""
```

---

## SessionInfo

Entry from `user.sessionList`.

```python
class SessionInfo(StakeModel):
    id: str = ""
    session_name: Optional[str] = None  # API: sessionName
    ip: Optional[str] = None
    active: bool = False
    country: Optional[str] = None
    city: Optional[str] = None
    created_at: Optional[str] = None    # API: createdAt
    updated_at: Optional[str] = None    # API: updatedAt
```

---

## ApiKeyInfo

Entry from `user.apiKeys`.

```python
class ApiKeyInfo(StakeModel):
    id: str = ""
    ip: Optional[str] = None
    active: bool = False
    session_name: Optional[str] = None  # API: sessionName
    type: Optional[str] = None
    created_at: Optional[str] = None    # API: createdAt
    updated_at: Optional[str] = None    # API: updatedAt
```

---

## StatisticEntry

Per-currency wagering stat from `user.statistic`.

```python
class StatisticEntry(StakeModel):
    id: str = ""
    bet_amount: Decimal = Decimal("0")  # API: betAmount
    profit: Decimal = Decimal("0")
    amount: Decimal = Decimal("0")
    currency: str = ""
```

---

## FaucetInfo

Reload/faucet status.

```python
class FaucetInfo(StakeModel):
    id: str = ""
    active: bool = False
    value: Decimal = Decimal("0")
    claim_interval: Optional[int] = None  # API: claimInterval
    last_claim: Optional[str] = None      # API: lastClaim
    expire_at: Optional[str] = None       # API: expireAt
```

---

## TransactionEntry

Single transaction from `user.transaction`.

```python
class TransactionEntry(StakeModel):
    id: str = ""
    amount: Decimal = Decimal("0")
    currency: str = ""
    type: str = ""
    created_at: Optional[str] = None  # API: createdAt
```

---

## BlackjackCard / BlackjackHand / BlackjackBet

Blackjack game state.

```python
class BlackjackCard(StakeModel):
    rank: str = ""
    suit: str = ""

class BlackjackHand(StakeModel):
    value: int = 0
    actions: List[str] = []
    cards: List[BlackjackCard] = []

class BlackjackBet(StakeModel):
    id: str = ""
    active: bool = False
    nonce: int = 0
    payout_multiplier: Decimal = Decimal("0")   # API: payoutMultiplier
    amount_multiplier: Decimal = Decimal("0")   # API: amountMultiplier
    amount: Decimal = Decimal("0")
    payout: Decimal = Decimal("0")
    updated_at: Optional[str] = None            # API: updatedAt
    currency: str = ""
    game: str = ""
    player: Optional[BlackjackHand] = None
    dealer: Optional[BlackjackHand] = None
```

---

## BonusCodeInfo

```python
class BonusCodeInfo(StakeModel):
    availability_status: str = ""           # API: availabilityStatus
    bonus_value: Optional[Decimal] = None   # API: bonusValue
    crypto_multiplier: Optional[Decimal] = None  # API: cryptoMultiplier
```

---

## KuratorGame / KuratorCollection

```python
class KuratorGame(StakeModel):
    id: str = ""
    name: str = ""
    slug: str = ""
    provider: Optional[str] = None

class KuratorCollection(StakeModel):
    id: str = ""
    name: str = ""
    slug: str = ""
    games: List[KuratorGame] = []
```

---

## SportItem

```python
class SportItem(StakeModel):
    id: str = ""
    name: str = ""
    slug: str = ""
    icon: Optional[str] = None
    active: bool = False
```

---

## RaceInfo

```python
class RaceInfo(StakeModel):
    id: str = ""
    name: str = ""
    start_date: Optional[str] = None   # API: startDate
    end_date: Optional[str] = None     # API: endDate
    prize: Optional[Decimal] = None
    currency: str = ""
```

---

## NotificationEntry

```python
class NotificationEntry(StakeModel):
    id: str = ""
    type: Optional[str] = None
    message: Optional[str] = None
    read: bool = False
    created_at: Optional[str] = None  # API: createdAt
```

---

## Serialization

```python
# From API response dict (camelCase keys work)
session = SessionInfo.from_dict({
    "id": "abc",
    "sessionName": "Chrome Desktop",
    "ip": "1.2.3.4",
    "active": True,
})
print(session.session_name)  # "Chrome Desktop"

# To dict (snake_case keys)
d = session.model_dump()

# To dict with camelCase keys (for API round-trips)
d = session.model_dump(by_alias=True)

# To JSON
j = session.model_dump_json()
```
