"""Tests for data models."""

from decimal import Decimal

from stakeapi.models import (
    ApiKeyInfo,
    BalanceEntry,
    BlackjackBet,
    BlackjackCard,
    BlackjackHand,
    BonusCodeInfo,
    FaucetInfo,
    KuratorCollection,
    KuratorGame,
    RaceInfo,
    SessionInfo,
    StatisticEntry,
    TransactionEntry,
    User,
)


class TestUserModel:
    def test_user_creation(self):
        data = {
            "id": "user123",
            "name": "testuser",
            "email": "test@example.com",
            "has_email_verified": True,
            "is_muted": False,
            "is_rainproof": False,
            "is_banned": False,
            "created_at": "2025-01-01T00:00:00Z",
        }
        user = User.from_dict(data)
        assert user.id == "user123"
        assert user.name == "testuser"
        assert user.has_email_verified is True

    def test_user_defaults(self):
        user = User()
        assert user.id == ""
        assert user.name == ""
        assert user.email is None
        assert user.has_email_verified is False


class TestSessionInfoModel:
    def test_session_info_creation(self):
        data = {
            "id": "sess-123",
            "sessionName": "Chrome Desktop",
            "ip": "1.2.3.4",
            "active": True,
            "country": "US",
            "city": "New York",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-05T00:00:00Z",
        }
        session = SessionInfo.from_dict(data)
        assert session.id == "sess-123"
        assert session.session_name == "Chrome Desktop"
        assert session.ip == "1.2.3.4"
        assert session.active is True


class TestBalanceEntryModel:
    def test_balance_entry(self):
        data = {"amount": "0.001", "currency": "btc"}
        entry = BalanceEntry.from_dict(data)
        assert entry.amount == Decimal("0.001")
        assert entry.currency == "btc"

    def test_balance_entry_defaults(self):
        entry = BalanceEntry()
        assert entry.amount == Decimal("0")
        assert entry.currency == ""


class TestStatisticEntryModel:
    def test_statistic_entry(self):
        data = {
            "id": "stat-1",
            "betAmount": "100.5",
            "profit": "10.2",
            "amount": "50.0",
            "currency": "usd",
        }
        stat = StatisticEntry.from_dict(data)
        assert stat.bet_amount == Decimal("100.5")
        assert stat.profit == Decimal("10.2")


class TestFaucetInfoModel:
    def test_faucet_info(self):
        data = {
            "id": "faucet-1",
            "active": True,
            "value": "0.03",
            "claimInterval": 600000,
            "lastClaim": "2025-01-01T00:00:00Z",
            "expireAt": "2025-01-10T00:00:00Z",
        }
        faucet = FaucetInfo.from_dict(data)
        assert faucet.active is True
        assert faucet.value == Decimal("0.03")


class TestTransactionEntryModel:
    def test_transaction_entry(self):
        data = {
            "id": "tx-1",
            "amount": "10.5",
            "currency": "usd",
            "type": "bonusDrop",
            "createdAt": "2025-01-01T00:00:00Z",
        }
        tx = TransactionEntry.from_dict(data)
        assert tx.id == "tx-1"
        assert tx.amount == Decimal("10.5")
        assert tx.type == "bonusDrop"


class TestBlackjackModels:
    def test_blackjack_card(self):
        data = {"rank": "A", "suit": "spades"}
        card = BlackjackCard.from_dict(data)
        assert card.rank == "A"
        assert card.suit == "spades"

    def test_blackjack_hand(self):
        data = {
            "value": 21,
            "actions": ["hit", "stand"],
            "cards": [{"rank": "A", "suit": "spades"}],
        }
        hand = BlackjackHand.from_dict(data)
        assert hand.value == 21
        assert len(hand.cards) == 1

    def test_blackjack_bet(self):
        data = {
            "id": "bet-1",
            "active": True,
            "nonce": 42,
            "payoutMultiplier": "2.0",
            "amountMultiplier": "1.0",
            "amount": "0.001",
            "payout": "0.002",
            "currency": "btc",
            "game": "blackjack",
        }
        bet = BlackjackBet.from_dict(data)
        assert bet.id == "bet-1"
        assert bet.active is True
        assert bet.currency == "btc"


class TestApiKeyInfoModel:
    def test_api_key_info(self):
        data = {
            "id": "key-1",
            "ip": "1.2.3.4",
            "active": True,
            "sessionName": "API Key 1",
            "type": "api",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }
        key = ApiKeyInfo.from_dict(data)
        assert key.id == "key-1"
        assert key.active is True
        assert key.session_name == "API Key 1"


class TestBonusCodeInfoModel:
    def test_bonus_code_info(self):
        data = {
            "availabilityStatus": "available",
            "bonusValue": "10.0",
            "cryptoMultiplier": "1.5",
        }
        info = BonusCodeInfo.from_dict(data)
        assert info.availability_status == "available"
        assert info.bonus_value == Decimal("10.0")


class TestKuratorModels:
    def test_kurator_game(self):
        data = {"id": "g1", "name": "Slots", "slug": "slots", "provider": "Pragmatic"}
        game = KuratorGame.from_dict(data)
        assert game.name == "Slots"
        assert game.provider == "Pragmatic"

    def test_kurator_collection(self):
        data = {
            "id": "c1",
            "name": "Popular",
            "slug": "popular",
            "games": [
                {"id": "g1", "name": "Slots", "slug": "slots", "provider": "Pragmatic"}
            ],
        }
        coll = KuratorCollection.from_dict(data)
        assert coll.slug == "popular"
        assert len(coll.games) == 1


class TestRaceInfoModel:
    def test_race_info(self):
        data = {
            "id": "race-1",
            "name": "Daily Race",
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2025-01-02T00:00:00Z",
            "prize": "100.0",
            "currency": "usd",
        }
        race = RaceInfo.from_dict(data)
        assert race.name == "Daily Race"
        assert race.prize == Decimal("100.0")
