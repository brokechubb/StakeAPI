"""API endpoints and GraphQL queries for StakeAPI."""


class Endpoints:
    """API endpoint constants.

    NOTE: All /api/v1/* REST endpoints are fictional and return 404.
    The only real API surface is /_api/graphql (see GraphQLQueries).
    These constants are kept for backward compatibility but should not be used.
    """

    GRAPHQL = "/_api/graphql"


class GraphQLQueries:
    """GraphQL query constants for stake.com/stake.us API.

    Verified against both domains on 2025-05-09/10.  Queries that
    differ between stake.com and stake.us are noted in docstrings.

    Domain-specific notes:
      - stake.us: uses ``isAcp: true`` in CurrencyConfiguration
      - stake.com: uses ``isAcp: false``, has ``kycStatus`` field
      - Sports queries are restricted on stake.us (region-locked)

    Tags:
      [verified] — tested against live API on stake.com and/or stake.us
      [constructed] — built from Playwright-captured operation names & schema
          patterns; NOT yet tested against live API
    """

    # ═══════════════════════════════════════════════════════════════════
    #  USER QUERIES  [verified]
    # ═══════════════════════════════════════════════════════════════════

    USER_BALANCES = """
    query UserBalances {
      user {
        id
        balances {
          available {
            amount
            currency
            __typename
          }
          vault {
            amount
            currency
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    USER_PROFILE = """
    query UserProfile {
      user {
        id
        name
        email
        hasEmailVerified
        isMuted
        isRainproof
        isBanned
        createdAt
        __typename
      }
    }
    """

    USER_META = """
    query UserMeta($name: String) {
      user(name: $name) {
        id
        name
        balances {
          available {
            amount
            currency
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    USER_META_EXTENDED = """
    query UserMetaExtended($name: String, $signupCode: Boolean = false) {
      user(name: $name) {
        id
        name
        isMuted
        isRainproof
        isBanned
        createdAt
        campaignSet
        selfExclude {
          id
          status
          active
          createdAt
          expireAt
          __typename
        }
        signupCode @include(if: $signupCode) {
          id
          code {
            id
            code
          }
          __typename
        }
        __typename
      }
    }
    """

    USER_ACCOUNT_INFO = """
    query UserAccountInfo {
      user {
        id
        name
        email
        createdAt
        __typename
      }
    }
    """

    USER_KYC_STATUS = """
    query UserKycStatus {
      user {
        id
        kycStatus
        __typename
      }
    }
    """

    USER_SESSIONS = """
    query UserSessions {
      user {
        id
        sessionList {
          id
          sessionName
          ip
          active
          country
          city
          createdAt
          updatedAt
          __typename
        }
        __typename
      }
    }
    """

    USER_API_KEYS = """
    query UserApiKeys {
      user {
        id
        apiKeys {
          id
          ip
          active
          sessionName
          type
          createdAt
          updatedAt
          __typename
        }
        __typename
      }
    }
    """

    USER_STATISTIC = """
    query UserStatistic {
      user {
        id
        statistic {
          id
          betAmount
          profit
          amount
          currency
          __typename
        }
        __typename
      }
    }
    """

    USER_SEED_PAIR = """
    query UserSeedPair {
      user {
        id
        activeClientSeed {
          id
          seed
          __typename
        }
        activeServerSeed {
          id
          nonce
          seedHash
          nextSeedHash
          __typename
        }
        __typename
      }
    }
    """

    IS_USER_TFA_ENABLED = """
    query IsUserTfaEnabled {
      user {
        id
        hasTfaEnabled
        __typename
      }
    }
    """

    USER_PREFERENCES = """
    query UserPreferences {
      user {
        id
        preference {
          __typename
        }
        __typename
      }
    }
    """

    USER_RECENT_GAME_LIST = """
    query UserRecentGameList($limit: Int = 10) {
      user {
        id
        recentGameList(limit: $limit) {
          id
          name
          slug
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  VIP / RELOAD / FAUCET QUERIES  [verified]
    # ═══════════════════════════════════════════════════════════════════

    VIP_META = """
    query VipMeta {
      user {
        id
        balances {
          available {
            amount
            currency
            __typename
          }
          __typename
        }
        reload: faucet {
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
    """

    FAUCET = """
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
    """

    ACTIVE_RAKEBACK = """
    query ActiveRakeback {
      user {
        id
        rakeback {
          id
          __typename
        }
        __typename
      }
    }
    """

    TIP_LIMIT = """
    query TipList($limit: Int = 20) {
      user {
        id
        tipList(limit: $limit) {
          id
          amount
          currency
          user {
            id
            name
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  CURRENCY / CONFIG QUERIES  [verified]
    # ═══════════════════════════════════════════════════════════════════

    CURRENCY_CONFIGURATION = """
    query CurrencyConfiguration($isAcp: Boolean!) {
      currencyConfiguration(isAcp: $isAcp) {
        currencies {
          name
          rates {
            currency
            rate
            __typename
          }
          __typename
        }
        launchedFiatCurrencies
        displayFiatCurrencies
        __typename
      }
    }
    """

    CURRENCY_NEW_CONVERSION_RATE = """
    query CurrencyNewConversionRate(
      $displayCurrencies: [FiatCurrencyEnum!]!
    ) {
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
    """

    # ═══════════════════════════════════════════════════════════════════
    #  BONUS / PROMO QUERIES  [verified]
    # ═══════════════════════════════════════════════════════════════════

    BONUS_CODE_INFORMATION = """
    query BonusCodeInformation($code: String!, $couponType: CouponType!) {
      bonusCodeInformation(code: $code, couponType: $couponType) {
        availabilityStatus
        bonusValue
        cryptoMultiplier
        __typename
      }
    }
    """

    CAMPAIGN_LIST = """
    query CampaignList {
      raceList {
        id
        name
        __typename
      }
    }
    """

    CAMPAIGN_BALANCES = """
    query CampaignBalances {
      user {
        id
        campaignBalances {
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  TRANSACTION / HISTORY QUERIES  [verified]
    # ═══════════════════════════════════════════════════════════════════

    TRANSACTION = """
    query Transaction($types: [TransactionTypeEnum!], $offset: Int, $limit: Int) {
      user {
        id
        transaction(types: $types, offset: $offset, limit: $limit) {
          id
          amount
          currency
          type
          createdAt
          __typename
        }
        __typename
      }
    }
    """

    DEPOSIT_LIST = """
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
    """

    WITHDRAWAL_LIST = """
    query WithdrawalList($offset: Int, $limit: Int) {
      user {
        id
        withdrawalList(offset: $offset, limit: $limit) {
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
    """

    MY_BET_LIST = """
    query MyBetList($limit: Int = 20) {
      user {
        id
        chatList(limit: $limit) {
          id
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  CASINO / GAME QUERIES  [verified for Blackjack]
    # ═══════════════════════════════════════════════════════════════════

    BLACKJACK_ACTIVE_BET = """
    query BlackjackActiveBet {
      user {
        id
        activeCasinoBet(game: blackjack) {
          id
          active
          nonce
          payoutMultiplier
          amountMultiplier
          amount
          payout
          updatedAt
          currency
          game
          clientSeed {
            seed
            __typename
          }
          serverSeed {
            seedHash
            __typename
          }
          user {
            id
            name
            __typename
          }
          state {
            ... on CasinoGameBlackjack {
              player {
                value
                actions
                cards {
                  rank
                  suit
                  __typename
                }
                __typename
              }
              dealer {
                value
                actions
                cards {
                  rank
                  suit
                  __typename
                }
                __typename
              }
            }
          }
          __typename
        }
        __typename
      }
    }
    """

    KURATOR_COLLECTION = """
    query KuratorCollection($type: GameKuratorCollectionEnum!) {
      kuratorCollection(type: $type) {
        id
        __typename
      }
    }
    """

    SLUG_KURATOR_GROUP = """
    query SlugKuratorGroup($slug: String!) {
      slugKuratorGroup(slug: $slug) {
        id
        name
        slug
        gameCount
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  SPORTS QUERIES  [constructed — verified only for stake.com]
    # ═══════════════════════════════════════════════════════════════════

    SPORT_LIST_MENU = """
    query SportListMenu {
      sportList {
        id
        name
        slug
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  RACE / SOCIAL / MISC QUERIES  [constructed]
    # ═══════════════════════════════════════════════════════════════════

    ACTIVE_RACES = """
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
    """

    NOTIFICATION_LIST = """
    query NotificationList($offset: Int, $limit: Int = 20) {
      user {
        id
        notificationList(offset: $offset, limit: $limit) {
          id
          type
          createdAt
          __typename
        }
        __typename
      }
    }
    """

    PUBLIC_CHATS = """
    query PublicChats {
      chats {
        id
        __typename
      }
    }
    """

    BANNED_COUNTRIES = """
    query BannedCountries {
      info {
        bannedCountries {
          name
          value
          __typename
        }
        __typename
      }
    }
    """

    PLAYER_COUNT_BY_SCOPE = """
    query PlayerCountByScope {
      playerCountByScope {
        __typename
      }
    }
    """

    FEATURE_FLAG_DETAILS = """
    query FeatureFlagDetails {
      featureFlagList {
        name
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — BONUS / FAUCET / RAKEBACK  [verified]
    # ═══════════════════════════════════════════════════════════════════

    CLAIM_CONDITION_BONUS_CODE = """
    mutation ClaimConditionBonusCode(
      $code: String!,
      $currency: CurrencyEnum!,
      $turnstileToken: String!
    ) {
      claimConditionBonusCode(
        code: $code,
        currency: $currency,
        turnstileToken: $turnstileToken
      ) {
        bonusCode {
          id
          code
          __typename
        }
        amount
        currency
        user {
          id
          balances {
            available {
              amount
              currency
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    CLAIM_FAUCET = """
    mutation ClaimFaucet($currency: CurrencyEnum!, $turnstileToken: String!) {
      claimFaucet(currency: $currency, turnstileToken: $turnstileToken) {
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
    """

    CLAIM_RAKEBACK = """
    mutation ClaimRakeback {
      claimRakeback {
        amount
        currency
        user {
          id
          balances {
            available {
              amount
              currency
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — VAULT  [verified]
    # ═══════════════════════════════════════════════════════════════════

    CREATE_VAULT_DEPOSIT = """
    mutation CreateVaultDeposit($currency: CurrencyEnum!, $amount: Float!) {
      createVaultDeposit(currency: $currency, amount: $amount) {
        id
        amount
        currency
        user {
          id
          balances {
            available {
              amount
              currency
            }
            vault {
              amount
              currency
            }
          }
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — SEED  [verified]
    # ═══════════════════════════════════════════════════════════════════

    ROTATE_SEED_PAIR = """
    mutation RotateSeedPair($seed: String!) {
      rotateSeedPair(seed: $seed) {
        clientSeed {
          user {
            id
            activeClientSeed {
              id
              seed
              __typename
            }
            activeServerSeed {
              id
              nonce
              seedHash
              nextSeedHash
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    # ═══════════════════════════════════════════════════════════════════
    #  MUTATIONS — BLACKJACK  [verified — from wen-bj-bot]
    # ═══════════════════════════════════════════════════════════════════

    BLACKJACK_BET = """
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
        payoutMultiplier
        amountMultiplier
        amount
        payout
        updatedAt
        currency
        game
        clientSeed {
          seed
          __typename
        }
        serverSeed {
          seedHash
          __typename
        }
        user {
          id
          name
          __typename
        }
        state {
          ... on CasinoGameBlackjack {
            player {
              value
              actions
              cards {
                rank
                suit
                __typename
              }
              __typename
            }
            dealer {
              value
              actions
              cards {
                rank
                suit
                __typename
              }
              __typename
            }
          }
        }
        __typename
      }
    }
    """

    BLACKJACK_NEXT = """
    mutation BlackjackNext($action: BlackjackNextActionInput!, $identifier: String!) {
      blackjackNext(action: $action, identifier: $identifier) {
        id
        active
        nonce
        payoutMultiplier
        amountMultiplier
        amount
        payout
        updatedAt
        currency
        game
        clientSeed {
          seed
          __typename
        }
        serverSeed {
          seedHash
          __typename
        }
        user {
          id
          name
          __typename
        }
        state {
          ... on CasinoGameBlackjack {
            player {
              value
              actions
              cards {
                rank
                suit
                __typename
              }
              __typename
            }
            dealer {
              value
              actions
              cards {
                rank
                suit
                __typename
              }
              __typename
            }
          }
        }
        __typename
      }
    }
    """
