"""Main client for StakeAPI."""

from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

from .auth import AuthManager
from .endpoints import Endpoints, GraphQLQueries
from .exceptions import AuthenticationError, RateLimitError, StakeAPIError
from .models import (  # noqa: F401
    ApiKeyInfo,
    BalanceEntry,
    BlackjackBet,
    BlackjackCard,
    BlackjackHand,
    BonusCodeInfo,
    CurrencyInfo,
    FaucetInfo,
    KuratorCollection,
    KuratorGame,
    NotificationEntry,
    RaceInfo,
    SeedPair,
    SessionInfo,
    SportItem,
    StatisticEntry,
    TransactionEntry,
    User,
)


class StakeAPI:
    """Main client for interacting with stake.com API."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        session_cookie: Optional[str] = None,
        cf_clearance: Optional[str] = None,
        user_agent: Optional[str] = None,
        base_url: str = "https://stake.com",
        timeout: int = 30,
        rate_limit: int = 10,
    ):
        """
        Initialize the StakeAPI client.

        Args:
            access_token: Your stake.com access token (x-access-token header)
            session_cookie: Session cookie for authentication
            cf_clearance: Cloudflare clearance cookie (required for stake.com)
            user_agent: Browser UA (must match the one that got cf_clearance)
            base_url: Base URL for the API (use https://stake.us for stake.us)
            timeout: Request timeout in seconds
            rate_limit: Maximum requests per second
        """
        self.access_token = access_token
        self.session_cookie = session_cookie
        self.cf_clearance = cf_clearance
        self.user_agent = user_agent
        self.base_url = base_url
        self.timeout = timeout
        self.rate_limit = rate_limit

        self._session: Optional[aiohttp.ClientSession] = None
        self._auth_manager = AuthManager(access_token)

    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _create_session(self):
        """Create aiohttp session with proper headers."""
        ua = self.user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        )
        headers = {
            "User-Agent": ua,
            "Accept": "application/graphql+json, application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Language": "en",
        }

        if self.access_token:
            headers["X-Access-Token"] = self.access_token

        cookies = {}
        if self.session_cookie:
            cookies["session"] = self.session_cookie
        if self.cf_clearance:
            cookies["cf_clearance"] = self.cf_clearance

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self._session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            cookies=cookies or None,
        )

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[Any, Any]:
        """Make an authenticated HTTP request to the API."""
        if not self._session:
            await self._create_session()

        url = urljoin(self.base_url, endpoint)

        try:
            async with self._session.request(
                method, url, params=params, json=data
            ) as response:
                if response.status == 403:
                    raise StakeAPIError(
                        "403 Forbidden — Cloudflare blocking the request. "
                        "Provide a valid 'cf_clearance' cookie. "
                        "Get it from: stake.com -> DevTools (F12) -> "
                        "Application -> Cookies -> cf_clearance. "
                        "Pass as: StakeAPI(access_token=..., cf_clearance='...')"
                    )
                elif response.status == 401:
                    raise AuthenticationError(
                        "Invalid access token or unauthorized access"
                    )
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")

                response_data = await response.json()

                if response.status >= 400:
                    raise StakeAPIError(
                        f"API error: {response.status} - {response_data}"
                    )

                return response_data

        except (StakeAPIError, AuthenticationError, RateLimitError):
            raise
        except aiohttp.ClientError as e:
            raise StakeAPIError(f"Request failed: {e}")

    async def _graphql_request(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[Any, Any]:
        """Make a GraphQL request to the stake.com API."""
        payload: Dict[str, Any] = {"query": query}

        if variables:
            payload["variables"] = variables

        if operation_name:
            payload["operationName"] = operation_name

        response = await self._request("POST", Endpoints.GRAPHQL, data=payload)

        if "errors" in response:
            error_messages = [
                error.get("message", "Unknown error") for error in response["errors"]
            ]
            raise StakeAPIError(f"GraphQL errors: {', '.join(error_messages)}")

        return response.get("data", {})

    # ═══════════════════════════════════════════════════════════════════
    #  USER METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_user_balance(self) -> Dict[str, Dict[str, float]]:
        """Get user account balance.

        Returns:
            Balance information by currency with available and vault amounts.
        """
        data = await self._graphql_request(
            GraphQLQueries.USER_BALANCES, operation_name="UserBalances"
        )

        result: Dict[str, Dict[str, float]] = {"available": {}, "vault": {}}

        if "user" in data and data["user"] and "balances" in data["user"]:
            for entry in data["user"]["balances"]:
                if "available" in entry:
                    currency = entry["available"].get("currency", "").lower()
                    amount = float(entry["available"].get("amount", 0))
                    result["available"][currency] = amount
                if "vault" in entry:
                    currency = entry["vault"].get("currency", "").lower()
                    amount = float(entry["vault"].get("amount", 0))
                    result["vault"][currency] = amount

        return result

    async def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile (verified fields only)."""
        return await self._graphql_request(
            GraphQLQueries.USER_PROFILE, operation_name="UserProfile"
        )

    async def get_user_meta(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get lightweight user info with balances.

        Args:
            name: Optional username to look up
        """
        variables = {}
        if name:
            variables["name"] = name
        return await self._graphql_request(
            GraphQLQueries.USER_META,
            variables=variables or None,
            operation_name="UserMeta",
        )

    async def get_user_meta_extended(
        self, name: Optional[str] = None, signup_code: bool = False
    ) -> Dict[str, Any]:
        """Get extended user info including self-exclude and campaign status.

        Args:
            name: Optional username to look up
            signup_code: Whether to include signup code info
        """
        return await self._graphql_request(
            GraphQLQueries.USER_META_EXTENDED,
            variables={"name": name, "signupCode": signup_code},
            operation_name="UserMetaExtended",
        )

    async def get_user_account_info(self) -> Dict[str, Any]:
        """Get user account info with email, country details (stake.com)."""
        return await self._graphql_request(
            GraphQLQueries.USER_ACCOUNT_INFO, operation_name="UserAccountInfo"
        )

    async def get_user_kyc_status(self) -> Dict[str, Any]:
        """Get user KYC status (stake.com only; returns null on stake.us)."""
        return await self._graphql_request(
            GraphQLQueries.USER_KYC_STATUS, operation_name="UserKycStatus"
        )

    async def get_user_sessions(self) -> Dict[str, Any]:
        """Get user session list with ip, location details."""
        return await self._graphql_request(
            GraphQLQueries.USER_SESSIONS, operation_name="UserSessions"
        )

    async def get_user_api_keys(self) -> Dict[str, Any]:
        """Get user API keys (stake.com only; may return empty on stake.us)."""
        return await self._graphql_request(
            GraphQLQueries.USER_API_KEYS, operation_name="UserApiKeys"
        )

    async def get_user_statistic(self) -> Dict[str, Any]:
        """Get per-currency wagering statistics."""
        return await self._graphql_request(
            GraphQLQueries.USER_STATISTIC, operation_name="UserStatistic"
        )

    async def get_user_seed_pair(self) -> Dict[str, Any]:
        """Get active client/server seed pair and nonce."""
        return await self._graphql_request(
            GraphQLQueries.USER_SEED_PAIR, operation_name="UserSeedPair"
        )

    async def is_user_tfa_enabled(self) -> Dict[str, Any]:
        """Check if user has two-factor authentication enabled."""
        return await self._graphql_request(
            GraphQLQueries.IS_USER_TFA_ENABLED, operation_name="IsUserTfaEnabled"
        )

    async def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        return await self._graphql_request(
            GraphQLQueries.USER_PREFERENCES, operation_name="UserPreferences"
        )

    async def get_user_recent_games(self, limit: int = 10) -> Dict[str, Any]:
        """Get user's recently played games.

        Args:
            limit: Maximum number of games to return (default: 10)
        """
        return await self._graphql_request(
            GraphQLQueries.USER_RECENT_GAME_LIST,
            variables={"limit": limit},
            operation_name="UserRecentGameList",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  VIP / RELOAD / FAUCET METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_vip_meta(self) -> Dict[str, Any]:
        """Get VIP meta info: balances + reload/faucet status combined."""
        return await self._graphql_request(
            GraphQLQueries.VIP_META, operation_name="VipMeta"
        )

    async def get_faucet(self) -> Dict[str, Any]:
        """Get reload/faucet status."""
        return await self._graphql_request(
            GraphQLQueries.FAUCET, operation_name="Faucet"
        )

    async def get_active_rakeback(self) -> Dict[str, Any]:
        """Get active rakeback amount per currency."""
        return await self._graphql_request(
            GraphQLQueries.ACTIVE_RAKEBACK, operation_name="ActiveRakeback"
        )

    async def get_tip_list(self, limit: int = 20) -> Dict[str, Any]:
        """Get user tip list.

        Args:
            limit: Number of tips to return (default: 20)
        """
        return await self._graphql_request(
            GraphQLQueries.TIP_LIMIT,
            variables={"limit": limit},
            operation_name="TipList",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  CURRENCY / CONFIG METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_currency_configuration(self, is_acp: bool = False) -> Dict[str, Any]:
        """Get currency configuration and rates.

        Args:
            is_acp: True for stake.us, False for stake.com
        """
        return await self._graphql_request(
            GraphQLQueries.CURRENCY_CONFIGURATION,
            variables={"isAcp": is_acp},
            operation_name="CurrencyConfiguration",
        )

    async def get_conversion_rates(
        self, display_currencies: List[str]
    ) -> Dict[str, Any]:
        """Get currency conversion rates for specified fiat display currencies.

        Args:
            display_currencies: List of lowercase fiat currency codes
                                (e.g., ["usd", "eur"]) — enum is lowercase
        """
        return await self._graphql_request(
            GraphQLQueries.CURRENCY_NEW_CONVERSION_RATE,
            variables={"displayCurrencies": display_currencies},
            operation_name="CurrencyNewConversionRate",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  BONUS / PROMO METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def check_bonus_code(
        self, code: str, coupon_type: str = "drop"
    ) -> Dict[str, Any]:
        """Check bonus code availability.

        Args:
            code: Bonus code to check
            coupon_type: Type of coupon (default: "drop")
        """
        return await self._graphql_request(
            GraphQLQueries.BONUS_CODE_INFORMATION,
            variables={"code": code, "couponType": coupon_type},
            operation_name="BonusCodeInformation",
        )

    async def get_racing_list(self) -> Dict[str, Any]:
        """Get racing/campaign list."""
        return await self._graphql_request(
            GraphQLQueries.CAMPAIGN_LIST, operation_name="CampaignList"
        )

    async def get_campaign_balances(self) -> Dict[str, Any]:
        """Get user campaign balances."""
        return await self._graphql_request(
            GraphQLQueries.CAMPAIGN_BALANCES, operation_name="CampaignBalances"
        )

    # ═══════════════════════════════════════════════════════════════════
    #  TRANSACTION / HISTORY METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_transactions(
        self,
        offset: int = 0,
        limit: int = 20,
        types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get transaction history.

        Args:
            offset: Pagination offset
            limit: Number of transactions to return
            types: Optional list of transaction types to filter
                    (e.g., ["bonusDrop", "rakeback", "chatTip"])
        """
        variables: Dict[str, Any] = {"offset": offset, "limit": limit}
        if types:
            variables["types"] = types
        return await self._graphql_request(
            GraphQLQueries.TRANSACTION,
            variables=variables,
            operation_name="Transaction",
        )

    async def get_deposits(self, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Get deposit history.

        Args:
            offset: Pagination offset
            limit: Number of deposits to return
        """
        return await self._graphql_request(
            GraphQLQueries.DEPOSIT_LIST,
            variables={"offset": offset, "limit": limit},
            operation_name="DepositList",
        )

    async def get_withdrawals(self, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Get withdrawal history.

        Args:
            offset: Pagination offset
            limit: Number of withdrawals to return
        """
        return await self._graphql_request(
            GraphQLQueries.WITHDRAWAL_LIST,
            variables={"offset": offset, "limit": limit},
            operation_name="WithdrawalList",
        )

    async def get_my_bets(self, limit: int = 20) -> Dict[str, Any]:
        """Get user chat list (bet history not available via this field).

        Args:
            limit: Number of entries to return (default: 20)
        """
        return await self._graphql_request(
            GraphQLQueries.MY_BET_LIST,
            variables={"limit": limit},
            operation_name="MyBetList",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  CASINO / GAME METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_blackjack_active_bet(self) -> Dict[str, Any]:
        """Get current active blackjack bet (returns null if none)."""
        return await self._graphql_request(
            GraphQLQueries.BLACKJACK_ACTIVE_BET,
            operation_name="BlackjackActiveBet",
        )

    async def get_kurator_collection(self, collection_type: str) -> Dict[str, Any]:
        """Get a kurator collection by type.

        Args:
            collection_type: GameKuratorCollectionEnum value
                             (must match the server enum exactly)
        """
        return await self._graphql_request(
            GraphQLQueries.KURATOR_COLLECTION,
            variables={"type": collection_type},
            operation_name="KuratorCollection",
        )

    async def get_kurator_group(self, slug: str) -> Dict[str, Any]:
        """Get a kurator group (game category) by slug.

        Args:
            slug: Group slug identifier (e.g., "stake-originals")
        """
        return await self._graphql_request(
            GraphQLQueries.SLUG_KURATOR_GROUP,
            variables={"slug": slug},
            operation_name="SlugKuratorGroup",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  SPORTS METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_sport_list_menu(self) -> Dict[str, Any]:
        """Get sports menu list (stake.com only; region-locked on stake.us)."""
        return await self._graphql_request(
            GraphQLQueries.SPORT_LIST_MENU, operation_name="SportListMenu"
        )

    # ═══════════════════════════════════════════════════════════════════
    #  SOCIAL / RACE / MISC METHODS
    # ═══════════════════════════════════════════════════════════════════

    async def get_active_races(self) -> Dict[str, Any]:
        """Get active race list."""
        return await self._graphql_request(
            GraphQLQueries.ACTIVE_RACES,
            operation_name="ActiveRaces",
        )

    async def get_notifications(
        self, offset: int = 0, limit: int = 20
    ) -> Dict[str, Any]:
        """Get user notification list.

        Args:
            offset: Pagination offset
            limit: Number of notifications to return
        """
        return await self._graphql_request(
            GraphQLQueries.NOTIFICATION_LIST,
            variables={"offset": offset, "limit": limit},
            operation_name="NotificationList",
        )

    async def get_public_chats(self) -> Dict[str, Any]:
        """Get public chat entries."""
        return await self._graphql_request(
            GraphQLQueries.PUBLIC_CHATS,
            operation_name="PublicChats",
        )

    async def get_banned_countries(self) -> Dict[str, Any]:
        """Get list of banned countries (returns CSV string in value)."""
        return await self._graphql_request(
            GraphQLQueries.BANNED_COUNTRIES, operation_name="BannedCountries"
        )

    async def get_player_count(self) -> Dict[str, Any]:
        """Get player count by scope (no parameters)."""
        return await self._graphql_request(
            GraphQLQueries.PLAYER_COUNT_BY_SCOPE,
            operation_name="PlayerCountByScope",
        )

    async def get_feature_flags(self) -> Dict[str, Any]:
        """Get feature flag list (all flags with names)."""
        return await self._graphql_request(
            GraphQLQueries.FEATURE_FLAG_DETAILS,
            operation_name="FeatureFlagDetails",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — BONUS / FAUCET / RAKEBACK
    # ═══════════════════════════════════════════════════════════════════

    async def claim_bonus_code(
        self, code: str, currency: str, turnstile_token: str
    ) -> Dict[str, Any]:
        """Claim a condition bonus code.

        Args:
            code: Bonus code to claim
            currency: Currency enum (e.g., "btc", "usd")
            turnstile_token: Cloudflare Turnstile CAPTCHA token
                             (sitekey: 0x4AAAAAAAGD4gMGOTFnvupz)
        """
        return await self._graphql_request(
            GraphQLQueries.CLAIM_CONDITION_BONUS_CODE,
            variables={
                "code": code,
                "currency": currency,
                "turnstileToken": turnstile_token,
            },
            operation_name="ClaimConditionBonusCode",
        )

    async def claim_faucet(self, currency: str, turnstile_token: str) -> Dict[str, Any]:
        """Claim faucet/reload bonus.

        Args:
            currency: Currency enum (e.g., "btc", "usd")
            turnstile_token: Cloudflare Turnstile CAPTCHA token
                             (sitekey: 0x4AAAAAAAGD4gMGOTFnvupz)
        """
        return await self._graphql_request(
            GraphQLQueries.CLAIM_FAUCET,
            variables={"currency": currency, "turnstileToken": turnstile_token},
            operation_name="ClaimFaucet",
        )

    async def claim_rakeback(self) -> Dict[str, Any]:
        """Claim rakeback (no parameters required)."""
        return await self._graphql_request(
            GraphQLQueries.CLAIM_RAKEBACK, operation_name="ClaimRakeback"
        )

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — VAULT
    # ═══════════════════════════════════════════════════════════════════

    async def create_vault_deposit(
        self, currency: str, amount: float
    ) -> Dict[str, Any]:
        """Deposit funds into vault.

        Args:
            currency: Currency enum (e.g., "btc", "usd")
            amount: Amount to deposit
        """
        return await self._graphql_request(
            GraphQLQueries.CREATE_VAULT_DEPOSIT,
            variables={"currency": currency, "amount": amount},
            operation_name="CreateVaultDeposit",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — SEED
    # ═══════════════════════════════════════════════════════════════════

    async def rotate_seed_pair(self, seed: str) -> Dict[str, Any]:
        """Rotate the client/server seed pair.

        Args:
            seed: New client seed string
        """
        return await self._graphql_request(
            GraphQLQueries.ROTATE_SEED_PAIR,
            variables={"seed": seed},
            operation_name="RotateSeedPair",
        )

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — BLACKJACK
    # ═══════════════════════════════════════════════════════════════════

    async def blackjack_bet(
        self, amount: float, currency: str, identifier: str
    ) -> Dict[str, Any]:
        """Place a blackjack bet.

        Args:
            amount: Bet amount
            currency: Currency enum (e.g., "btc", "usd")
            identifier: Unique bet identifier string
        """
        return await self._graphql_request(
            GraphQLQueries.BLACKJACK_BET,
            variables={
                "amount": amount,
                "currency": currency,
                "identifier": identifier,
            },
            operation_name="BlackjackBet",
        )

    async def blackjack_next(
        self, action: Dict[str, Any], identifier: str
    ) -> Dict[str, Any]:
        """Take the next action in a blackjack hand.

        Args:
            action: BlackjackNextActionInput dict, e.g. {"action": "hit"}
                    or {"action": "stand"} or {"action": "double"}
            identifier: The bet identifier from blackjack_bet response
        """
        return await self._graphql_request(
            GraphQLQueries.BLACKJACK_NEXT,
            variables={"action": action, "identifier": identifier},
            operation_name="BlackjackNext",
        )
