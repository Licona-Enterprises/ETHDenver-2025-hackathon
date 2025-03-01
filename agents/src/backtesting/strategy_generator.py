import os
import re
import numpy as np
import ast
import time
import json
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Any, Dict, Optional
from typing_extensions import List, TypedDict, Tuple

import textwrap
import polars as pl
import pandas as pd
import quantstats as qs
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

from rag.embedding_model import EmbeddingModel
from twitter.twitter_api import TwitterAPI
from rag.rag_chroma_client import ChromaVectorStoreManager
from config.config import OpenAiConsts, Backtester, HubPull
from backtesting.structured_output_formatters import ResponseFormatter
from backtesting.token_prices import TokenPrices
from rag.mongodb_handler import MongoDBHandler
from backtesting.compliance_manager import ComplianceManager

class StrategyGenerator:
    """
    A class to manage the logic for an application that integrates Chroma, 
    OpenAI's Chat model, and document-based stateful processing.

    Parameters
    ----------
    collection_name : str
        The name of the Chroma vector store collection.

    Attributes
    ----------
    api_key : str
        The OpenAI API key loaded from environment variables.
    llm : ChatOpenAI
        The language model used for chat-based interactions.
    manager : Chroma
        The Chroma vector store manager for document similarity search.
    prompt : PromptTemplate
        The prompt template used to interact with the model.
    """

    def __init__(self, collection_name: str, hub_pull: HubPull, strategy_generator: Backtester) -> None:
        """
        Initializes the TweetGenerator with the required components.

        Parameters
        ----------
        collection_name : str
            The name of the Chroma vector store collection.
        """

        self.api_key = ""
        self._load_api_key()
        open_ai_consts = OpenAiConsts()
        self.open_ai_embedding_function = OpenAIEmbeddings(model=open_ai_consts.DEFAULT_EMBEDDING_MODEL)
        llm = ChatOpenAI(model=open_ai_consts.DEFAULT_MODEL_NAME)
        self.model_with_structure = llm.with_structured_output(schema=ResponseFormatter)
        self.llm = ChatOpenAI(model=open_ai_consts.DEFAULT_MODEL_NAME)
        self.mongo_db_handler = MongoDBHandler(collection_name=collection_name)
        self.compliance_manager = ComplianceManager()

        # since chroma is only going to be used for short term data which diana class gets from nfa database and market data ChromaVectorStoreManager collection name is DIANA
        self.manager = ChromaVectorStoreManager("DIANA")

        # backtester_settings = Backtester()
        backtester_settings = strategy_generator
        self.opportunities_similarity_search_prompt = backtester_settings.OPPORTUNITY_SEARCH_PROMPT
        self.backtest_prompt = PromptTemplate.from_template(backtester_settings.BACKTEST_PROMPT)

        # for dev test: check startegy loaded correctly
        print(backtester_settings.BACKTEST_PROMPT)

        self.backtest_clmm_prompt = PromptTemplate.from_template(backtester_settings.BACKTEST_CLMM_PROMPT)

        # hub_pull = HubPull()
        hub_pull = hub_pull
        self.joey_agent_object_id = hub_pull.AGENT_OBJECT_ID

        self.double_down_flag = hub_pull.DOUBLE_DOWN

        self.token_prices = TokenPrices()
        self.portfolio: Dict[str, TokenHolding] = {}

    def _load_api_key(self) -> None:
        """
        Loads the OpenAI API key from environment variables using dotenv.

        Raises
        ------
        ValueError
            If the OpenAI API key is not found in the environment.
        """
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set it in your environment.")
        
    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieves documents from the Chroma vector store based on a similarity search.

        Parameters
        ----------
        query : str
            The query string used for similarity search.

        Returns
        -------
        List[Document]
            A list of retrieved documents that match the query.
        """
        return self.manager.similarity_search(query)

    def sample_chroma_documents(self, query: str, similarity_search_filter: str, num_docs: int = 50) -> List[Document]:
        """
        Fetch a sample of the knowledge base from the vector store.

        Parameters
        ----------
        num_docs : int, optional
            The number of random documents to retrieve, by default 5.

        Returns
        -------
        List[Document]
            A list of randomly selected documents.
        """
        search_results = self.manager.similarity_search(query, k=200, filters={"source": similarity_search_filter})
        # sampled_results = random.sample(search_results, min(num_docs, len(search_results)))
    
        return search_results

    def add_to_token_holding(self, symbol: str, token_address:str, amount: float, price: float, signal_timestamp:str, token_id: float) -> None:
        """
        Add to or update the token holdings in the portfolio.

        Parameters
        ----------
        symbol : str
            The symbol of the token (e.g., 'BTC', 'ETH').
        token_address : str
            The on chain address of the token
        amount : float
            The amount of the token to add.
        price : float
            The price of the token when added.
        signal_timestamp : str
            Timestamp of when signal was generated in def generate_opportunities()
        """
        portfolio = self.load_portfolio()
        print(f"dev set double down flag to {self.double_down_flag} - buying of the same asset not allowed\n")
        if symbol in portfolio:

            print(f"Accumulating {symbol} \n")
            current_holding = portfolio[symbol]
            amount = amount
            new_total_amount = current_holding['amount'] + amount

            if new_total_amount > 0:
                average_price = ((current_holding['amount'] * current_holding['last_price']) + (amount * price)) / new_total_amount
            else:
                average_price = price

            portfolio[symbol]['token_address'] = token_address
            portfolio[symbol]['amount'] = new_total_amount
            portfolio[symbol]['last_price'] = average_price
        else:
            print(f"1.  adding new token {symbol}\n")
            amount = amount # for dev test
            portfolio[symbol] = TokenHolding(symbol=symbol, token_address=token_address, amount=amount, signal_price=price, signal_timestamp=signal_timestamp,last_price=price, token_id=token_id)

        self.save_portfolio(portfolio=portfolio)

    def remove_from_token_holding(self, symbol: str, token_address:str, amount: float, price: float, signal_timestamp:str, token_id: float) -> None:
        """
        Close the position or remove the token holdings in the portfolio.

        Parameters
        ----------
        symbol : str
            The symbol of the token (e.g., 'BTC', 'ETH').
        token_address : str
            The on chain address of the token
        amount : float
            The amount of the token to add.
        price : float
            The price of the token when added.
        signal_timestamp : str
            Timestamp of when signal was generated in def generate_opportunities()
        """
        
        try: 
            portfolio = self.load_portfolio()
            portfolio[symbol] = TokenHolding(symbol=symbol, token_address=token_address, amount=0.0, signal_price=price, signal_timestamp=signal_timestamp,last_price=price, token_id=token_id)
            self.save_portfolio(portfolio=portfolio)
        except Exception as e: 
            print(f"failed to close positon and remove: {symbol}")
        pass 

    def generate_opportunities(self, question: str, context: List[Document]) -> Dict:
        """
        Generates a signal based on the given question and document context.

        Parameters
        ----------
        question : str
            The user's question or prompt to generate the thread.
        context : List[Document]
            The list of documents providing the context for the thread.

        Returns
        -------
        List[str]
            A list of tweet texts that form a thread.
        """
        docs_content = "\n\n".join(doc.page_content for doc in context)

        
        messages = self.backtest_prompt.invoke({"question": question, "context": docs_content})

        generate_opportunities_model_output = {}
        signal_list = []
        for doc in context:
            try:
                content_dict = json.loads(doc.page_content)
            except json.JSONDecodeError:
                content_dict = doc.page_content 

            for key, value in content_dict.items():
                string_data = content_dict[key]['data']
                data_dict = ast.literal_eval(string_data)  
                
                signals_considered = {
                    "sentiment": data_dict['sentiment'],
                    "crypto_tokens_identified": data_dict['cryptoTokensIdentified'],
                    "confidence_level": data_dict['marketSignals']['confidenceLevel'],
                    "token_performance_context": data_dict['onlineAnalysisEnhancements']['tokenPerformanceContext'],
                    "expected_duration": data_dict['positioning']['expectedDuration'],
                    "market_signals": data_dict['marketSignals']['type']
                }

                signal_list.append(signals_considered)
                
        response = self.model_with_structure.invoke(messages)
        response_dict = response.dict()

        # save model output
        generate_opportunities_model_output[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = {
            f"agent_trade_{self.joey_agent_object_id}":[response_dict],
            "agent_signals_considered": signal_list
        }
        self.save_model_trade_generation_process(generate_opportunities_model_output)

        signal_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = response_dict["token_symbol"]
        response_direction = response_dict["direction"]

        print(f"Agent is searching NFA database for metadata on: {symbol} \n")

        try:
            symbol_id_list = self.mongo_db_handler.get_cmc_ids_by_symbols(symbol=symbol)

            if len(symbol_id_list) < 1:
                print(f"NFA database does not have symbol id for {symbol}\n")
                symbol_id_list = self.token_prices.get_coinmarketcap_ids_by_symbol(slugs_list=[symbol])
                print(f"{symbol} has an id:{symbol_id_list} souce: cmc api\n")
                
            token_data_list = self.token_prices.get_coinmarketcap_latest_token_stats(ids_list=symbol_id_list)
            allowlist_tokens = self.compliance_manager.evaluate_risk(token_stats=token_data_list)

            token_address = allowlist_tokens["token_address"]
            token_id = allowlist_tokens["coinmarketcap_id"]
            if response_direction.lower() == "sell":
                amount = -0.1 # test amount    
            else: 
                amount = 0.1 # test amount
            signal_price = allowlist_tokens["price_usd"]

            self.add_to_token_holding(symbol=symbol, token_address=token_address, amount=amount, price=signal_price, signal_timestamp=signal_timestamp, token_id=token_id)
        
        except Exception as e:
            print(f"Unable to add token to portfolio. Lack of token details: {e}")

        # generated_opportunities = Document(
        #     page_content=str(response),
        #     metadata={"source": "generated_opportunities"},
        # )
        # self.manager.add_documents([generated_opportunities])

        return response_dict

    def create_opportunity(self):
        """
        Creates a signal based on documents loaded from the nfa_opportunities database

        This is a custom def specifically tailored to the NFA database, which was used in this project.

        For your use, use your own database and search those documents using self.sample_chroma_documents()

        Returns
        -------
        str
            the generated twitter thread
        """
        state: State = {"question": self.opportunities_similarity_search_prompt, "context": [], "answer": ""}
        # TODO maybe add functionality to sample users knowledge base here
        retrieved_docs = self.sample_chroma_documents(query=state["question"], similarity_search_filter="nfa_opportunities")
        state["context"] = retrieved_docs
        generated_trade_answer = self.generate_opportunities(question=state["question"], context=state["context"])
        state["answer"] = generated_trade_answer

        return generated_trade_answer
    
    def generate_clmm_opportunities(self, question: str, context: List[Document]) -> Dict:
        """
        Generates a signal based on the given question and document context.

        Parameters
        ----------
        question : str
            The user's question or prompt to generate the thread.
        context : List[Document]
            The list of documents providing the context for the thread.

        Returns
        -------
        List[str]
            A list of tweet texts that form a thread.
        """
        messages = self.backtest_clmm_prompt.invoke({"question": question, "context": context})
        response = self.llm.invoke(messages).content
        generate_opportunities_model_output = {}
        signal_list = []

    def create_clmm_opportunity(self):
        """
        Creates a signal based on documents loaded from the nfa_opportunities database

        This is a custom def specifically tailored to the NFA database, which was used in this project.

        For your use, use your own database and search those documents using self.sample_chroma_documents()

        Returns
        -------
        str
            the generated twitter thread
        """
        state: State = {"question": "hJLP aims to mitigate the inherent price risks faced by liquidity providers while maintaining attractive returns - based on these asset prices how can i implement hJLP on base", "context": [], "answer": ""}
        
        # TODO find out why sample_chroma_documents() is not returning anything 
        retrieved_docs = self.sample_chroma_documents(query=state["question"], similarity_search_filter="PDF")
        
        # TODO remove hard coded base asssets 
        token_data_list = self.token_prices.get_coinmarketcap_latest_token_stats(ids_list=["3408", "5994", "6536", "29420", "28081"])
        
        dict_list: List[Dict] = [{}]
        dict_list.extend([{"page_content": doc.page_content, "metadata": doc.metadata} for doc in retrieved_docs])
        print(retrieved_docs)

        for doc_dict, token_data in zip(dict_list, token_data_list):
            doc_dict["token_data"] = token_data

        state["context"] = dict_list
        generated_trade_answer = self.generate_clmm_opportunities(question=state["question"], context=state["context"])
        state["answer"] = generated_trade_answer

        return generated_trade_answer
    
    def update_portfolio_metrics(self) -> None:
        """
        Update all token holdings in the portfolio with a mock price of 100.
        
        """
        portfolio = self.load_portfolio()

        portfolio_metrics = []
        
        for symbol, holding in portfolio.items():
            current_holding = portfolio[symbol]

            token_id = holding["token_id"]
            token_data_list = self.token_prices.get_coinmarketcap_latest_token_stats(ids_list=[str(token_id)])
            last_price = token_data_list[0]["price_usd"]

            current_holding.update({
                "symbol": symbol,
                "token_address": holding.get('token_address', ''),
                "token_id": holding.get('token_id', ''),
                "amount": holding.get('amount', ''),
                "signal_price": holding.get('signal_price', ''),
                "signal_timestamp": holding.get('signal_timestamp', ''),
                "last_price": last_price
            })


        portfolio_metrics = self.calculate_portfolio_metrics()

        # TODO find a way to use update_or_create_portfolio_v2() for the other updates 
        self.mongo_db_handler.update_or_create_portfolio_v2(agent_id=self.joey_agent_object_id, portfolio_updates=portfolio, portfolio_metrics=portfolio_metrics)
       
    def save_portfolio(self, portfolio: Dict, portfolio_metrics: Optional[dict] = None):
        existing_data = self.load_portfolio()
        new_data = []

        for symbol, holding in portfolio.items():
            if symbol in existing_data:

                current_holding = existing_data[symbol]
                current_amount = current_holding['amount']
                updated_amount = current_holding['amount']
                if updated_amount > 0:

                    # TODO check if average price is really needed here, this should be done in add_to_token_holding
                    average_price = (
                        (current_holding['amount'] * current_holding['last_price'] +
                        holding['amount'] * holding['last_price']) / updated_amount
                    )
                    current_holding.update({
                        "amount": updated_amount,
                        # "last_price": average_price,
                        "last_price": holding['last_price'],
                        "signal_price": holding.get('signal_price', current_holding['signal_price']),
                        "signal_timestamp": holding.get('signal_timestamp', current_holding['signal_timestamp']),
                    })
                    
                else:
                    # del existing_data[symbol]
                    # new logic for selling 
                    current_holding.update({
                        "amount": updated_amount,
                        # "last_price": average_price,
                        "last_price": holding['last_price'],
                        "signal_price": holding.get('signal_price', current_holding['signal_price']),
                        "signal_timestamp": holding.get('signal_timestamp', current_holding['signal_timestamp']),
                    })

            # elif holding['amount'] > 0:
            #     # Add new token if it doesn't already exist
            #     existing_data[symbol] = {
            #         "symbol": symbol,
            #         "token_address": holding['token_address'],
            #         "token_id": holding['token_id'],
            #         "amount": holding['amount'],
            #         "signal_price": holding['signal_price'],
            #         "signal_timestamp": holding['signal_timestamp'],
            #         "last_price": holding['last_price'],
            #     }
        
            else:
                # Add new token if it doesn't already exist
                existing_data[symbol] = {
                    "symbol": symbol,
                    "token_address": holding['token_address'],
                    "token_id": holding['token_id'],
                    "amount": holding['amount'],
                    "signal_price": holding['signal_price'],
                    "signal_timestamp": holding['signal_timestamp'],
                    "last_price": holding['last_price'],
                }

        self.mongo_db_handler.update_or_create_portfolio(agent_id=self.joey_agent_object_id, portfolio_updates=existing_data)

    def load_portfolio(self) -> Dict:
        portfolio_holdings = self.mongo_db_handler.get_portfolio_details(agent_id=str(self.joey_agent_object_id))
        return portfolio_holdings

    def calculate_portfolio_metrics(self) -> List[Any]:
        """
        Calculate and return portfolio performance metrics.
        
        Returns
        -------
        metrics_df : pl.DataFrame
            A DataFrame containing performance metrics for each token.
        """
        metrics_list = []

        current_time = datetime.now()

        portfolio = self.load_portfolio()

        for symbol, holding in portfolio.items():
            amount = holding['amount']
            signal_price = holding['signal_price']
            last_price = holding['last_price']
            signal_timestamp = datetime.strptime(holding['signal_timestamp'], "%Y-%m-%d %H:%M:%S")

            # cumulative_return = (last_price - signal_price) / signal_price
            cumulative_return = ((last_price - signal_price) / signal_price) * np.sign(amount)

            holding_days = max((current_time - signal_timestamp).days, 1)  # Avoid division by zero
            daily_return = cumulative_return / holding_days

            token_id = holding["token_id"]
            token_data_list = self.token_prices.get_coinmarketcap_latest_token_stats(ids_list=[str(token_id)])
            latest_price = float(token_data_list[0]["price_usd"])

            percent_change_7d = float(token_data_list[0]["percent_change_7d"])
            token_returns = self.token_prices.get_weekly_returns(current_price=latest_price, percent_change_7d=percent_change_7d)
            returns = token_returns.pct_change().drop_nulls()
            returns_mean = returns.mean() if not returns.is_empty() else 0.0
            volatility = returns.std() if not returns.is_empty() else 0.0

            returns_mean = returns_mean if returns_mean is not None else 0.0
            volatility = volatility if volatility is not None else 0.0

            sharpe_ratio = returns_mean / volatility if volatility != 0 else 0.0

            max_price = max(signal_price, last_price)
            min_price = min(signal_price, last_price)
            max_drawdown = (max_price - min_price) / max_price

            pnl = (last_price - signal_price) * amount

            metrics_list.append({
                "symbol": symbol,
                "signal_price": signal_price,
                "last_price": last_price,
                "token_amount": amount,
                "PnL": pnl,
                "cumulative_return": cumulative_return,
                "daily_return": daily_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "holding_duration_days": holding_days
            })

        metrics_df = pl.DataFrame(metrics_list)
        print(metrics_df)
        metrics_df.write_csv("portfolio_metrics.csv")

        return metrics_list

    def save_model_trade_generation_process(self, content: Dict) -> None:
        current_date = datetime.now()
        date_string = current_date.strftime('%Y-%m-%d')
        if os.path.exists(F"generated_trades_for_testing-{date_string}.json"):
            with open(f"generated_trades_for_testing-{date_string}.json", "r",encoding="utf-8") as file:
                try:
                    data = json.load(file) 
                except json.JSONDecodeError:
                    data = []
        else:
            data = []  

        data.append(content)

        with open(f"generated_trades_for_testing-{date_string}.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

class TokenHolding(TypedDict):
    """
    Represents the details of a token in the portfolio.

    Attributes
    ----------
    symbol : str
        The symbol of the token (e.g., 'BTC', 'ETH').
    amount : float
        The amount of the token held.
    last_price : float
        The last recorded price of the token.
    """

    symbol: str
    token_address: str
    amount: float
    signal_price: float
    signal_timestamp: str
    last_price: float
    token_id: float

class State(TypedDict):
    """
    A typed dictionary to represent the application's state, including portfolio details.

    Attributes
    ----------
    question : str
        The user's question.
    context : List[Document]
        The context documents retrieved for the question.
    answer : str | List[str]
        The generated answer from the language model.
    portfolio : Dict[str, TokenHolding]
        A dictionary mapping token symbols to token holdings.
    transaction_history : List[Dict[str, str | float]]
        A list of transactions performed, tracking action, token, amount, and price.
    """

    question: str
    context: List['Document']
    answer: str | List[str]
    portfolio: Dict[str, TokenHolding]
    transaction_history: List[Dict[str, str | float]]

