"""Tests for StakeAPI client."""

from unittest.mock import AsyncMock, patch

import pytest

from stakeapi import StakeAPI
from stakeapi.exceptions import AuthenticationError, RateLimitError, StakeAPIError


class TestStakeAPI:
    """Test cases for StakeAPI client."""

    def test_init(self, access_token):
        """Test client initialization."""
        client = StakeAPI(access_token=access_token)
        assert client.access_token == access_token
        assert client.base_url == "https://stake.com"
        assert client.timeout == 30
        assert client.rate_limit == 10

    def test_init_with_custom_params(self):
        """Test client initialization with custom parameters."""
        client = StakeAPI(
            access_token="test",
            base_url="https://stake.us",
            timeout=60,
            rate_limit=5,
        )
        assert client.base_url == "https://stake.us"
        assert client.timeout == 60
        assert client.rate_limit == 5

    @pytest.mark.asyncio
    async def test_context_manager(self, access_token):
        """Test client as async context manager."""
        async with StakeAPI(access_token=access_token) as client:
            assert client._session is not None

    @pytest.mark.asyncio
    async def test_authentication_error(self, stake_client):
        """Test authentication error handling."""
        with patch.object(stake_client, "_request") as mock_request:
            mock_request.side_effect = AuthenticationError("Invalid access token")

            with pytest.raises(AuthenticationError):
                await stake_client.get_user_profile()

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, stake_client):
        """Test rate limit error handling."""
        with patch.object(stake_client, "_request") as mock_request:
            mock_request.side_effect = RateLimitError("Rate limit exceeded")

            with pytest.raises(RateLimitError):
                await stake_client.get_user_profile()

    @pytest.mark.asyncio
    async def test_graphql_error_handling(self, stake_client):
        """Test GraphQL error response handling."""
        mock_response = {
            "errors": [{"message": "Cannot query field"}],
        }
        with patch.object(stake_client, "_request", return_value=mock_response):
            with pytest.raises(StakeAPIError, match="GraphQL errors"):
                await stake_client._graphql_request("query { test }")

    @pytest.mark.asyncio
    async def test_get_user_balance(self, stake_client):
        """Test getting user balance via GraphQL."""
        mock_data = {
            "user": {
                "id": "test-id",
                "balances": [
                    {
                        "available": {
                            "amount": 100.50,
                            "currency": "usd",
                            "__typename": "CasinoBalance",
                        },
                        "vault": {
                            "amount": 0.0,
                            "currency": "usd",
                            "__typename": "CasinoBalance",
                        },
                        "__typename": "UserBalance",
                    },
                    {
                        "available": {
                            "amount": 0.001,
                            "currency": "btc",
                            "__typename": "CasinoBalance",
                        },
                        "vault": {
                            "amount": 0.5,
                            "currency": "btc",
                            "__typename": "CasinoBalance",
                        },
                        "__typename": "UserBalance",
                    },
                ],
                "__typename": "User",
            }
        }

        with patch.object(stake_client, "_graphql_request", return_value=mock_data):
            balance = await stake_client.get_user_balance()

            assert "available" in balance
            assert "vault" in balance
            assert balance["available"]["usd"] == 100.50
            assert balance["available"]["btc"] == 0.001
            assert balance["vault"]["btc"] == 0.5

    @pytest.mark.asyncio
    async def test_get_user_profile(self, stake_client):
        """Test getting user profile via GraphQL."""
        mock_data = {
            "user": {
                "id": "test-id",
                "name": "testuser",
                "email": "test@example.com",
                "hasEmailVerified": True,
                "isMuted": False,
                "isRainproof": False,
                "isBanned": False,
                "createdAt": "2025-01-01T00:00:00Z",
                "__typename": "User",
            }
        }

        with patch.object(stake_client, "_graphql_request", return_value=mock_data):
            result = await stake_client.get_user_profile()
            assert result["user"]["name"] == "testuser"
            assert result["user"]["hasEmailVerified"] is True

    @pytest.mark.asyncio
    async def test_check_bonus_code(self, stake_client):
        """Test checking bonus code availability."""
        mock_data = {
            "bonusCodeInformation": {
                "availabilityStatus": "available",
                "bonusValue": 10.0,
                "cryptoMultiplier": None,
                "__typename": "BonusCodeInformationResult",
            }
        }

        with patch.object(stake_client, "_graphql_request", return_value=mock_data):
            result = await stake_client.check_bonus_code("test_code")
            assert result["bonusCodeInformation"]["availabilityStatus"] == "available"

    @pytest.mark.asyncio
    async def test_get_faucet(self, stake_client):
        """Test getting faucet/reload status."""
        mock_data = {
            "user": {
                "id": "test-id",
                "faucet": {
                    "id": "faucet-id",
                    "active": True,
                    "value": 0.03,
                    "claimInterval": 600000,
                    "lastClaim": "2025-01-01T00:00:00Z",
                    "expireAt": "2025-01-10T00:00:00Z",
                    "__typename": "Faucet",
                },
                "__typename": "User",
            }
        }

        with patch.object(stake_client, "_graphql_request", return_value=mock_data):
            result = await stake_client.get_faucet()
            assert result["user"]["faucet"]["active"] is True
            assert result["user"]["faucet"]["value"] == 0.03
