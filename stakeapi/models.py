"""Data models for StakeAPI.

Models reflect the actual GraphQL API response shapes as verified
against stake.com and stake.us on 2025-05-09/10.

Pydantic v2 model_config handles camelCase (from API) <-> snake_case (Python)
conversion via alias_generator.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field


def _to_camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(r.capitalize() for r in rest)


class StakeModel(_BaseModel):
    """Base model with camelCase alias support."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StakeModel":
        return cls(**data)


class BalanceEntry(StakeModel):
    """Available or vault balance for a single currency."""

    amount: Decimal = Decimal("0")
    currency: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalanceEntry":
        return cls(**data)


class User(StakeModel):
    """User model matching the real GraphQL user shape."""

    id: str = ""
    name: str = ""
    email: Optional[str] = None
    has_email_verified: bool = False
    is_muted: bool = False
    is_rainproof: bool = False
    is_banned: bool = False
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(**data)


class SessionInfo(StakeModel):
    """Session entry from user.sessionList."""

    id: str = ""
    session_name: Optional[str] = None
    ip: Optional[str] = None
    active: bool = False
    country: Optional[str] = None
    city: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionInfo":
        return cls(**data)


class ApiKeyInfo(StakeModel):
    """API key entry from user.apiKeys."""

    id: str = ""
    ip: Optional[str] = None
    active: bool = False
    session_name: Optional[str] = None
    type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiKeyInfo":
        return cls(**data)


class StatisticEntry(StakeModel):
    """Per-currency wagering statistic from user.statistic."""

    id: str = ""
    bet_amount: Decimal = Decimal("0")
    profit: Decimal = Decimal("0")
    amount: Decimal = Decimal("0")
    currency: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatisticEntry":
        return cls(**data)


class SeedPair(StakeModel):
    """Active client/server seed pair."""

    client_seed: str = ""
    server_seed_hash: str = ""
    nonce: int = 0
    next_seed_hash: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeedPair":
        return cls(**data)


class FaucetInfo(StakeModel):
    """Reload/faucet status."""

    id: str = ""
    active: bool = False
    value: Decimal = Decimal("0")
    claim_interval: Optional[int] = None
    last_claim: Optional[str] = None
    expire_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FaucetInfo":
        return cls(**data)


class TransactionEntry(StakeModel):
    """Single transaction from user.transaction."""

    id: str = ""
    amount: Decimal = Decimal("0")
    currency: str = ""
    type: str = ""
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionEntry":
        return cls(**data)


class BlackjackCard(StakeModel):
    """Card in a blackjack hand."""

    rank: str = ""
    suit: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlackjackCard":
        return cls(**data)


class BlackjackHand(StakeModel):
    """Blackjack hand (player or dealer)."""

    value: int = 0
    actions: List[str] = Field(default_factory=list)
    cards: List[BlackjackCard] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlackjackHand":
        return cls(**data)


class BlackjackBet(StakeModel):
    """Active blackjack bet."""

    id: str = ""
    active: bool = False
    nonce: int = 0
    payout_multiplier: Decimal = Decimal("0")
    amount_multiplier: Decimal = Decimal("0")
    amount: Decimal = Decimal("0")
    payout: Decimal = Decimal("0")
    updated_at: Optional[str] = None
    currency: str = ""
    game: str = ""
    player: Optional[BlackjackHand] = None
    dealer: Optional[BlackjackHand] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlackjackBet":
        return cls(**data)


class BonusCodeInfo(StakeModel):
    """Bonus code availability info."""

    availability_status: str = ""
    bonus_value: Optional[Decimal] = None
    crypto_multiplier: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BonusCodeInfo":
        return cls(**data)


class KuratorGame(StakeModel):
    """Game entry in a kurator collection/group."""

    id: str = ""
    name: str = ""
    slug: str = ""
    provider: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KuratorGame":
        return cls(**data)


class KuratorCollection(StakeModel):
    """Kurator game collection."""

    id: str = ""
    name: str = ""
    slug: str = ""
    games: List[KuratorGame] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KuratorCollection":
        return cls(**data)


class CurrencyInfo(StakeModel):
    """Currency configuration entry."""

    name: str = ""
    rates: List[Dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurrencyInfo":
        return cls(**data)


class SportItem(StakeModel):
    """Sport menu entry."""

    id: str = ""
    name: str = ""
    slug: str = ""
    icon: Optional[str] = None
    active: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SportItem":
        return cls(**data)


class RaceInfo(StakeModel):
    """Active race entry."""

    id: str = ""
    name: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prize: Optional[Decimal] = None
    currency: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RaceInfo":
        return cls(**data)


class NotificationEntry(StakeModel):
    """Notification entry."""

    id: str = ""
    type: Optional[str] = None
    message: Optional[str] = None
    read: bool = False
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationEntry":
        return cls(**data)
