import time
from typing import List
from datetime import datetime
from dataclasses import replace
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from config.config import HubPull, TwitterApiConsts, Backtester
from rag.mongodb_handler import MongoDBHandler
from rag.rag_chroma_client import ChromaVectorStoreManager
from ica.logger_config import LoggerConfig
from ica.agent_47 import TheAgent
from rag.rag_pipeline import RagPipeline
from backtesting.portfolio_manager import PortfolioManager

class Diana:
    
    def __init__(self):
        try:
            self.logger = LoggerConfig.setup_logger(self.__class__.__name__)
            self.all_agents_list = []
        except Exception as e:
            print(f"failed to initialize Diana()")

    def start(self):
        
        mongo_db_handler = MongoDBHandler("DIANA")

        try:
            # self.all_agents_list = mongo_db_handler.get_all_agents()

            # use these 2 lines when testing single agent interactions get_agent_settings 
            self.agent_1 = mongo_db_handler.get_agent_settings(agent_id="67bda73d43d6464a9cad4241")
            self.all_agents_list = [self.agent_1]

            self.logger.info(f"loaded {len(self.all_agents_list)} agents from privex agent db")
        except Exception as e:
            print(f"failed to get all agents: {e}")
            self.logger.error(f"failed to get all agents: {e}")

        active_agents = []

        agents_created = []

        for agent in self.all_agents_list:

            agent_info = HubPull()
            twitter_api_consts = TwitterApiConsts()
            agent_trading_info = Backtester()

            agent_id = str(agent.get("_id", ""))
            agent_collection_name = str(agent.get("_id", ""))
            persona_info=agent.get("persona", "")
            agent_strategy=agent.get("strategyType")

            # TODO add embeddings field from mongo db

            updated_agent = replace(
                agent_info, 
                KNOWLEDGE_BASE_COLLECTION_NAME = agent_id,
                AGENT_OBJECT_ID = agent_id,
                PERSONA_INFO = persona_info,
                PROMPT = persona_info + """
                Question: {question} 
                Context: {context} 
                Answer:
                """,
                PORTFOLIO_THREAD_PROMPT = persona_info + """
                Question: {question}
                Context: {context}
                Answer:
                """,
                THREAD_PROMPT = persona_info + """
                Use short, impactful sentences that state ideas as truth.
                Use the following pieces of retrieved context to answer. Break responses into a tweet thread, each sentence its own tweet.
                Question: {question} 
                Context: {context} 
                Answer:
                """,
                COMMENT_ON_TWITTER_POST_PROMPT = persona_info + """
                Use the following pieces of retrieved context to generate a comment to start a conversation with that twitter user on that twitter post. Use 150 characters maximum and keep the answer concise - use the examples from above to get your tone right. Use 150 characters or less
                Question: {question} 
                Context: {context} 
                Answer:
                """,
            )

            agent_twitter_consts = replace(
                twitter_api_consts, 
                TWITTER_API_KEY = agent.get("TWITTER_API_KEY",""),
                TWITTER_API_KEY_SECRET = agent.get("TWITTER_API_KEY_SECRET",""),
                TWITTER_BEARER_TOKEN = agent.get("TWITTER_BEARER_TOKEN",""),
                TWITTER_ACCESS_TOKEN = agent.get("TWITTER_ACCESS_TOKEN",""),
                TWITTER_ACCESS_TOKEN_SECRET = agent.get("TWITTER_ACCESS_TOKEN_SECRET",""),
                TWITTER_CLIENT_ID = agent.get("TWITTER_CLIENT_ID",""),
            )

            updated_agent_trading_settings = replace(
                agent_trading_info,

                BACKTEST_PROMPT = f"""
                consider these trade strategies and make the best possible trade: [
                    {agent_strategy}
                ]
                """ +
                """
                Question: {question} 
                Context: {context} 
                Answer:

                """,
                OPPORTUNITY_SEARCH_PROMPT = f"""
                find the relevant tokens mentioned here: [
                    {agent_strategy}
                ]
                """
            )

            print(f"working on {agent.get("agentName","")} \n")
            self.start_agent(agent_collection_name=agent_collection_name, hub_pull = updated_agent, twitter_api_consts = agent_twitter_consts, strategy_generator=updated_agent_trading_settings)
            print(f"done with invoking {agent.get("agentName","")} \n")

    def start_agent(self, agent_collection_name:str, hub_pull: HubPull, twitter_api_consts:TwitterApiConsts, strategy_generator:Backtester): 

        agent47 = TheAgent(collection_name=agent_collection_name, hub_pull=hub_pull, twitter_api_consts=twitter_api_consts, strategy_generator=strategy_generator)

        # maybe store this so we dont have to make a new agent everytime
        active_agent = agent47.create_agent()

        try:

            with ThreadPoolExecutor(max_workers=1) as executor:            
                executor.submit(agent47.invoke_agent47)

            agent47.api_cool_down()

        except Exception as e:
            self.logger.error(f"failed to start agent {agent_collection_name}: {e}")

    @staticmethod
    def start_listener(retries: int = 3) -> multiprocessing.Process | None:
        """
        Starts a background process to listen for new agents with error handling.

        :param retries: Number of times to retry if the process fails to start.
        :return: The started Process object or None if it failed.
        """
        for attempt in range(1, retries + 1):
            try:
                logger = LoggerConfig.setup_logger("Diana - staticmethod")
                mongo_db_handler = MongoDBHandler("DIANA")
                process = multiprocessing.Process(target=mongo_db_handler.listen_for_changes, daemon=True)
                process.start()
                if process.is_alive():
                    logger.info(f"Listener process started successfully (PID: {process.pid}).")
                    return process
                else:
                    raise RuntimeError("Process started but is not running.")
            
            except Exception as e:
                logger.error(f"Attempt {attempt}: Failed to start listener process - {e}")
                time.sleep(2)  # Small delay before retrying

        logger.error("Listener process failed to start after multiple attempts.")
        return None  # Gracefully return None if it fails

    @staticmethod
    def update_knowledge_base() -> List[str]:
        logger = LoggerConfig.setup_logger(__class__.__name__)
        try:
            rag_pipeline = RagPipeline(collection_name="DIANA")
            agent_diana = HubPull()
            portfolio_manager = PortfolioManager(hub_pull=agent_diana)
            short_term_memory_to_delete = rag_pipeline.process_and_update_knowledge_base()
            portfolio_manager.update_portfolio_metrics()
            logger.info(f"updated knowledgebase with {len(short_term_memory_to_delete)} documents")
            return short_term_memory_to_delete
        except Exception as e:
            logger.error(f"failed to update knowledge base: {e}")

    @staticmethod
    def clean_agent_workspace(content: List[str]) -> None:
        """
        Process the models ToolCall and uses a predefined tool.

        Parameters
        ----------
        content : List[str]
            List of the new knowledgebase document IDs.

        Returns
        -------
            None 
        """
        logger = LoggerConfig.setup_logger(__class__.__name__)
        try:
            chroma_client = ChromaVectorStoreManager("DIANA")
            chroma_client.delete_documents(document_ids=content)
            print(f"removed {len(content)} documents from chroma db \n")
        except Exception as e:
            logger.error(f"failed to update knowledge base: {e}")

    @staticmethod
    def api_cool_down() -> None:
        seconds_to_cool_down:float = 19
        for remaining in range(seconds_to_cool_down, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02}:{secs:02}"  # Format as MM:SS
            print(f"Updating knowledge base in : {timer}", end="\r", flush=True)
            time.sleep(1)
        print(" " * 50, end="\r")

