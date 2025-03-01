import random
import math
import json
from typing import Dict
from typing_extensions import List

import polars as pl
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from config.config import DataProviders

class TokenPrices:
    def __init__(self):
        self.data_providers = DataProviders()
        self.coinmarketcap_api_key = self.data_providers.COINMARKET_CAP_API_KEY
    
    # def get_token_address(self) -> str:
    #     return "0x"
    
    def get_weekly_returns(self, current_price: float, percent_change_7d: float) -> pl.Series:
        """
        Calculate and return a polars Series of 7 daily prices from the current price 
        and the 7-day percent change.
        
        Parameters
        ----------
        current_price : float
            The latest price of the token.
        percent_change_7d : float
            The 7-day percentage change in price.
            
        Returns
        -------
        pl.Series
            A polars Series of daily prices from 7 days ago to the current day.
        """
        
        daily_percent_change = (math.pow(1 + percent_change_7d / 100, 1/7) - 1) * 100
        
        daily_prices = [current_price]
        for _ in range(7):
            prev_price = daily_prices[-1]
            new_price = prev_price / (1 + daily_percent_change / 100)
            daily_prices.append(new_price)
        
        return pl.Series("daily_prices", list(reversed(daily_prices)))
    
    def get_coinmarketcap_latest_token_stats(self, ids_list:List[str]) -> List[Dict]:
        
        # url = 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

        token_id_list_to_str = ",".join(ids_list)
        # token_id_list_to_str = ",".join(f"{int(token_id)}" for token_id in ids_list)

        parameters = {
            "id": token_id_list_to_str
        }

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key,
        }

        session = Session()

        session.headers.update(headers)

        token_stats_list = []

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            if data["status"]["error_code"] == 0:
                for token_id in range(len(ids_list)):
                    token_stats_dict = {
                        "coinmarketcap_id": data["data"][ids_list[token_id]]["id"],
                        "symbol": data["data"][ids_list[token_id]]["symbol"],
                        "price_usd": data["data"][ids_list[token_id]]["quote"]["USD"]["price"],
                        "volume_24h": data["data"][ids_list[token_id]]["quote"]["USD"]["volume_24h"],
                        "volume_change_24h": data["data"][ids_list[token_id]]["quote"]["USD"]["volume_change_24h"],
                        "percent_change_1h": data["data"][ids_list[token_id]]["quote"]["USD"]["percent_change_1h"],
                        "percent_change_24h": data["data"][ids_list[token_id]]["quote"]["USD"]["percent_change_24h"],
                        "percent_change_7d": data["data"][ids_list[token_id]]["quote"]["USD"]["percent_change_7d"],
                        "percent_change_30d": data["data"][ids_list[token_id]]["quote"]["USD"]["percent_change_30d"],
                        "marketcap": data["data"][ids_list[token_id]]["quote"]["USD"]["market_cap"],
                        # TODO add token address to token_stats_dict
                        "token_address": "0x333"
                    }
                    token_stats_list.append(token_stats_dict)
            else:
                print(f"get_coinmarketcap_latest_token_stats() Coinmetrics API encountered error: {data["status"]["error_message"]}")
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"Failed to load prices from Coinmarketcap endpoint v2/cryptocurrency/quotes/latest: {e} \n")

    
        return token_stats_list
    
    def get_coinmarketcap_latest_token_stats_by_slug(self, slugs_list:List[str]) -> List[Dict]:
        
        # url = 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

        token_slug_list_to_str = ",".join(slugs_list)

        parameters = {
            "symbol": token_slug_list_to_str
        }

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key,
        }

        session = Session()

        session.headers.update(headers)

        token_stats_list = []

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            if data["status"]["error_code"] == 0:
                for token_id in range(len(slugs_list)):
                    token_stats_dict = {
                        "coinmarketcap_id": data["data"][slugs_list[token_id]]["id"],
                        "symbol": data["data"][slugs_list[token_id]]["symbol"],
                        "price_usd": data["data"][slugs_list[token_id]]["quote"]["USD"]["price"],
                        "volume_24h": data["data"][slugs_list[token_id]]["quote"]["USD"]["volume_24h"],
                        "volume_change_24h": data["data"][slugs_list[token_id]]["quote"]["USD"]["volume_change_24h"],
                        "percent_change_1h": data["data"][slugs_list[token_id]]["quote"]["USD"]["percent_change_1h"],
                        "percent_change_24h": data["data"][slugs_list[token_id]]["quote"]["USD"]["percent_change_24h"],
                        "percent_change_7d": data["data"][slugs_list[token_id]]["quote"]["USD"]["percent_change_7d"],
                        "percent_change_30d": data["data"][slugs_list[token_id]]["quote"]["USD"]["percent_change_30d"],
                        "marketcap": data["data"][slugs_list[token_id]]["quote"]["USD"]["market_cap"],
                        # TODO add token address to token_stats_dict
                        "token_address": "0x"
                    }
                    token_stats_list.append(token_stats_dict)
            else:
                print(f"get_coinmarketcap_latest_token_stats_by_slug() Coinmetrics API encountered error: {data["status"]["error_message"]}")
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"Failed to load prices from Coinmarketcap endpoint v2/cryptocurrency/quotes/latest: {e} \n")

    
        return token_stats_list
    
    def get_coinmarketcap_ids_by_symbol(self, slugs_list:List[str]) -> List[str]:
        
        # url = 'https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

        token_slug_list_to_str = ",".join(slugs_list)

        parameters = {
            "symbol": token_slug_list_to_str
        }

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key,
        }

        session = Session()

        session.headers.update(headers)

        coinmarket_cap_id_list = []

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            if data["status"]["error_code"] == 0:
                for symbol, tokens in data["data"].items():
                    for token in tokens:
                        coinmarket_cap_id_list.append(str(token["id"]))
            else:
                print(f"get_coinmarketcap_latest_token_stats_by_symbol() Coinmetrics API encountered error: {data["status"]["error_message"]}")
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"Failed to load prices from Coinmarketcap endpoint v2/cryptocurrency/quotes/latest: {e} \n")

    
        return coinmarket_cap_id_list
    