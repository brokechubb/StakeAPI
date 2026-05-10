"""Test configuration and fixtures."""

from unittest.mock import AsyncMock, Mock

import pytest

from stakeapi import StakeAPI


@pytest.fixture
def access_token():
    """Test access token."""
    return "test_access_token_12345"


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    session = Mock()
    session.request = AsyncMock()
    return session


@pytest.fixture
async def stake_client(access_token):
    """StakeAPI client for testing."""
    client = StakeAPI(access_token=access_token)
    yield client
    await client.close()
