from typing import List, Dict

class ComplianceManager:
    """
    ComplianceManager class evaluates token risk based on metrics from TokenPrices.
    
    Parameters
    ----------
    volatility_threshold : float
        Maximum acceptable percent change (volatility) for 24 hours to consider a token as safe.
    marketcap_min : float
        Minimum market cap required to consider a token as a viable investment.
    volume_threshold : float
        Minimum trading volume within the last 24 hours for liquidity assessment.

    Methods
    -------
    evaluate_risk(token_stats: List[Dict[str, float]]) -> Dict[str, List[str]]
        Evaluates the risk level of each token and categorizes them as 'risky' or 'safe'.
    """

    def __init__(self, volatility_threshold: float = 20, marketcap_min: float = 1000000, volume_threshold: float = 500000):
        self.volatility_threshold = volatility_threshold
        self.marketcap_min = marketcap_min
        self.volume_threshold = volume_threshold

    def evaluate_risk(self, token_stats: List[Dict[str, float]]) -> Dict[str, List[str]]:
        """
        Evaluates token metrics and categorizes tokens as 'safe' or 'risky'.

        Parameters
        ----------
        token_stats : List[Dict[str, float]]
            A list of dictionaries containing token metrics.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary with 'safe' and 'risky' tokens categorized by their symbols.
        """
        safe_tokens = []
        risky_tokens = []

        for token in token_stats:
            
            symbol = token["symbol"]
            coinmarketcap_id = token["coinmarketcap_id"]
            price_usd = token["price_usd"]
            percent_change_24h = token["percent_change_24h"]
            market_cap = token.get("marketcap") or 0 
            volume_24h = token["volume_24h"]
            # token_address = token["token_address"]
            token_address = "0x0"

            token_id_dict = {
                "symbol": symbol,
                "coinmarketcap_id": coinmarketcap_id,
                "price_usd": price_usd,
                "market_cap": market_cap, 
                "token_address": token_address
            }

            if (abs(percent_change_24h) > self.volatility_threshold or
                market_cap < self.marketcap_min or
                volume_24h < self.volume_threshold):
                risky_tokens.append(token_id_dict)
            else:
                safe_tokens.append(token_id_dict)

        evaluated_tokens_dict = {
            "safe": safe_tokens,
            "risky": risky_tokens
        }

        # best_fit_token = self.get_highest_market_cap_safe_token(token_data=evaluated_tokens_dict)
        best_fit_token = self.get_lowest_market_cap_safe_token(token_data=evaluated_tokens_dict)

        return best_fit_token
    
    def get_highest_market_cap_safe_token(self, token_data: dict) -> dict:
        """
        Finds the safe token with the highest market cap.

        Parameters
        ----------
        token_data : dict
            A dictionary containing 'safe' and 'risky' token lists.

        Returns
        -------
        dict
            The safe token with the highest market cap, or an empty dictionary if none are found.
        """

        if not token_data.get('safe'):
            return {}

        # Find the token with the maximum market cap in 'safe' tokens
        highest_market_cap_token = max(token_data['safe'], key=lambda x: x['market_cap'])
        return highest_market_cap_token

    def get_lowest_market_cap_safe_token(self, token_data: dict) -> dict:
        """
        Finds the safe token with the lowest market cap.

        Parameters
        ----------
        token_data : dict
            A dictionary containing 'safe' and 'risky' token lists.

        Returns
        -------
        dict
            The safe token with the highest market cap, or an empty dictionary if none are found.
        """

        if not token_data.get('safe'):
            return {}

        # Find the token with the maximum market cap in 'safe' tokens
        highest_market_cap_token = min(token_data['safe'], key=lambda x: x['market_cap'])
        return highest_market_cap_token