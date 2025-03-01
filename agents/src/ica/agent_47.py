import os
import time
import json
import threading
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph
from langchain.tools import Tool

from config.config import OpenAiConsts, HubPull, TwitterApiConsts, Backtester
from rag.rag_pipeline import RagPipeline
from rag.rag_chroma_client import ChromaVectorStoreManager
from twitter.tweet_generator import TweetGenerator, State
from backtesting.strategy_generator import StrategyGenerator
from backtesting.portfolio_manager import PortfolioManager
from ica.logger_config import LoggerConfig

class TheAgent:
    """
    A class that encapsulates the process of generating and posting tweets
    using OpenAI's GPT model, a Chroma vector store, and a custom RAG pipeline.
    
    Attributes
    ----------
    collection_name : str
        Name of the Chroma collection to manage vectors and tweets.
    open_ai_consts : OpenAiConsts
        OpenAI configuration constants for the model.
    chroma_client : ChromaVectorStoreManager
        Manager for handling Chroma vector store operations.
    tweet_generator : TweetGenerator
        Tool for generating tweets based on the knowledge base.
    pipeline : RagPipeline
        Custom pipeline for processing and updating the knowledge base.
    model : ChatOpenAI
        OpenAI chat model used for generating responses and tweets.
    tools : List[Tool]
        A list of LangChain tools for interacting with the model.
    model_with_tools : ChatOpenAI
        The OpenAI model bound with LangChain tools.
    """

    def __init__(self, collection_name: str, hub_pull: HubPull, twitter_api_consts: TwitterApiConsts, strategy_generator:Backtester):
        """
        Initializes the TheAgent with required components.

        Parameters
        ----------
        collection_name : str
            Name of the Chroma collection to use for managing vectors and tweets.
        """
        self.collection_name = collection_name
        self._load_api_key()
        self.stop_flag = False

        # Initialize components
        self.open_ai_consts = OpenAiConsts()
        agent_info = hub_pull
        self.agent_persona = agent_info.PERSONA_INFO
        self.invoke_agent = agent_info.TOOL_PROMPTS
        self.tool_function_call_limit = agent_info.TOOL_FUNCTION_CALL_LIMIT
        self.tool_function_calls = 0

        self.generate_trades_function_call_counter = 0
        self.generate_trades_flag = False
        self.generate_trades_function_call_limit = agent_info.GENERATE_TRADES_CALL_LIMIT

        self.chroma_client = ChromaVectorStoreManager(collection_name=self.collection_name)
        self.tweet_generator = TweetGenerator(collection_name=self.collection_name, hub_pull=hub_pull, twitter_api_consts=twitter_api_consts)
        self.backtesting_strategy_generator = StrategyGenerator(collection_name=self.collection_name, hub_pull=hub_pull, strategy_generator=strategy_generator)
        self.portfolio_manager = PortfolioManager(hub_pull=hub_pull)
        self.pipeline = RagPipeline(collection_name=self.collection_name)
        self.model = ChatOpenAI(model=self.open_ai_consts.DEFAULT_MODEL_NAME)

        # Define and bind tools
        self.tools = self._define_tools()
        self.model_with_tools = self.model.bind_tools(self.tools)

        self.logger = LoggerConfig.setup_logger(self.__class__.__name__)

        # Initialize the thread lock
        self.lock = threading.Lock()

    def create_agent(self) -> CompiledGraph:
        self.agent_executor = create_react_agent(self.model, self.tools)
        return self.agent_executor

    def _load_api_key(self) -> None:
        """
        Loads the OpenAI API key from environment variables using dotenv.
        
        Raises
        ------
        ValueError
            If the OpenAI API key is not found in the environment variables.
        """
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set it in your environment.")
        print(f"Loaded env successfully: {api_key[:5]}*** \n")

    def _define_tools(self) -> List[Tool]:
        """
        Defines the LangChain tools for interacting with the model.

        Returns
        -------
        List[Tool]
            A list of tools to be bound to the OpenAI model.
        """
        def tweet_text_tool(content: List[str]) -> str:
            """
            A tool that generates and posts a tweet based on the input text.

            Parameters
            ----------
            input_text : str
                Text input to generate a tweet.

            Returns
            -------
            str
                The generated tweet text.
            """
            if self.stop_flag:
                print("Stop flag is set. Halting tweet tool execution.")
                return "Execution stopped due to stop flag."
            
            print(f"Tweet Tool is processing {len(content)} tweets")
            self.tool_function_calls = self.tool_function_calls + 1
            if self.tool_function_calls >= self.tool_function_call_limit:
                self.stop_flag = True
            tweet_response = self.tweet_generator.create_tweet()
            print(f"Tweet Tool response: {tweet_response}")  

            # TODO for dev test - remove later
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"{current_time} - Tweet Tool response: {tweet_response}\n"
            with open("dev_test_output.txt", "a") as file:
                file.write(content)

            return tweet_response
        
        def tweet_thread_text_tool(content: List[str]) -> str:
            """
            A tool that generates and posts a tweet thread based on the input text.

            Parameters
            ----------
            input_text : str
                Text input to generate a tweet.

            Returns
            -------
            str
                The generated tweet text.
            """

            try: 
                
                if self.stop_flag:
                    print("Stop flag is set. Halting tweet tool execution.")
                    return "Execution stopped due to stop flag."
                
                print(f"Tweet Thread Tool is processing {len(content)} tweets")
                self.tool_function_calls = self.tool_function_calls + 1
                if self.tool_function_calls >= self.tool_function_call_limit:
                    self.stop_flag = True
                tweet_response = self.tweet_generator.create_tweet_thread()
                print(f"Tweet Thread Tool response: {tweet_response}") 
                self.logger.info(f"agent {self.collection_name} tweeted thread with tweet_thread_text_tool")  
                
                # TODO for dev test to save to json
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                content = {"timestamp": current_time, "response": tweet_response}
                current_date = datetime.now()
                date_string = current_date.strftime('%Y-%m-%d')
                if os.path.exists(f"thread_generated_for_testing-{date_string}.json"):
                    with open(f"thread_generated_for_testing-{date_string}.json", "r",encoding="utf-8") as file:
                        try:
                            data = json.load(file)  # Load existing data
                        except json.JSONDecodeError:
                            data = []  # If the file is empty or corrupted, start with an empty list
                else:
                    data = []  # If the file doesn't exist, start with an empty list

                # Append the new content
                data.append(content)

                # Write the updated data back to the JSON file
                with open(f"thread_generated_for_testing-{date_string}.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

                return tweet_response
            
            except Exception as e:
                print(f"Failed to use Tool tweet_thread_text_tool(): {e}")
                self.logger.error(f"agent {self.collection_name} failed to tweet thread with tweet_thread_text_tool: {e}")
        
        def tweet_comment_text_tool(content: List[str]) -> str:
            """
            A tool that generates and posts a tweet thread based on the input text.

            Parameters
            ----------
            input_text : str
                Text input to generate a tweet.

            Returns
            -------
            str
                The generated tweet text.
            """
            if self.stop_flag:
                print("Stop flag is set. Halting tweet tool execution.")
                return "Execution stopped due to stop flag."
            
            print(f"Tweet Comment Tool is processing {len(content)} tweets")
            self.tool_function_calls = self.tool_function_calls + 1
            if self.tool_function_calls >= self.tool_function_call_limit:
                self.stop_flag = True
            
            try:
                tweet_response = self.tweet_generator.create_comment()
                print(f"Tweet Comment Tool response: {tweet_response}")   
                self.logger.info(f"agent {self.collection_name} commented with tweet_comment_text_tool")     
            except Exception as e:
                print(f"agent {self.collection_name} failed to comment with tweet_comment_text_tool: {e}")


            # TODO for dev  test to save to json
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = {"timestamp": current_time, "response": tweet_response}
            if os.path.exists("comments_generated_for_testing-2025-01-15.json"):
                with open("comments_generated_for_testing-2025-01-15.json", "r",encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
            else:
                data = []
            data.append(content)
            with open("comments_generated_for_testing-2025-01-15.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)



            return tweet_response

        def generate_trade_tool(content: List[str]) -> str:
            """
            Tool that generates a trade using the agents knowledge base, generated trade is being backtest for mvp1 of this project

            Returns
            -------
            str
                _description_
            """
            if self.generate_trades_flag:
                print("generate_trades_flag is set. Halting trade generation execution. \n")
                self.portfolio_manager.update_portfolio_metrics()
                print("     -> backtester is update_portfolio_metrics() \n")
                return "Execution stopped due to generate_trades_flag."
            
            print(f"Generate Trade Tool is processing {len(content)} data points")
            
            self.generate_trades_function_call_counter = self.generate_trades_function_call_counter + 1
            
            if self.generate_trades_function_call_counter >= self.generate_trades_function_call_limit:
                self.generate_trades_flag = True

            try: 
                generate_trade_response = self.portfolio_manager.create_opportunity()
                self.portfolio_manager.update_portfolio_metrics()
                self.logger.info(f"agent {self.collection_name} traded with generate_trade_tool")
            except Exception as e:
                print(f"unable to generate trade using the generate_trade_tool() {e}")
                self.logger.error(f"agent {self.collection_name} failed to trade with generate_trade_tool: {e}")

            # return generate_trade_response
            return [""]

        tweet_tool = Tool(
            name="TweetTextTool",
            func=tweet_text_tool,
            description="Generates a tweet text and posts that text to Twitter."
        )

        tweet_thread_tool = Tool(
            name="TweetThreadTextTool",
            func=tweet_thread_text_tool,
            description="Generates a tweet thread and posts that list of text to Twitter."
        )

        tweet_comment_tool = Tool(
            name="TweetThreadTextTool",
            func=tweet_comment_text_tool,
            description="Generates a tweet comment and posts that as a comment to Twitter."
        )

        backtesting_tool = Tool(
            name="GenerateTradeTool",
            func=generate_trade_tool,
            description="Generates a trade based on opportunities found in the knowledge base."
        )
        return [tweet_thread_tool, tweet_comment_tool, backtesting_tool]

    def invoke_agent47(self) -> str:
        """
        Invokes the active agent model with a given persona and optional messages.

        Parameters
        ----------
        human_messages : Optional[List[str]]
            A list of human messages to interact with the persona.

        Returns
        -------
        str
            The content of the model's response.
        """
        system_message = SystemMessage(content=self.agent_persona)
        human_message = HumanMessage(content=self.invoke_agent)

        if self.stop_flag:
            print("Stop flag is set. Halting tweet tool execution.")
            return "Execution stopped due to stop flag."

        with self.lock:
            response = self.agent_executor.invoke({"messages": [system_message,human_message]})
        
        self.tool_function_calls = self.tool_function_calls + 1

        if self.tool_function_calls >= self.tool_function_call_limit:
                self.stop_flag = True

        return response["messages"]

    def invoke_persona(self, persona_prompt: str, messages: Optional[List[HumanMessage]] = None) -> str:
        """
        Invokes the OpenAI model with a given persona and optional messages.

        Parameters
        ----------
        persona_prompt : str
            A prompt to set the persona for the model.
        messages : Optional[List[HumanMessage]]
            A list of human messages to interact with the persona.

        Returns
        -------
        str
            The content of the model's response.
        """
        system_message = SystemMessage(content=persona_prompt)
        all_messages = [system_message]
        if messages:
            all_messages.extend(messages)
        response = self.model_with_tools.invoke(all_messages)
        print(f"ToolCalls: {response.tool_calls}")
        return response.content

    def update_knowledge_base(self) -> List[str]:
        """
        Updates the knowledge base by processing new tweets.

        Returns
        -------
        List[str]
            A list of new tweet IDs added to the knowledge base.
        """
        new_document_ids = self.pipeline.process_and_update_knowledge_base()
        print(f"Updated knowledge base with {len(new_document_ids)} new Documents \n")
        self.portfolio_manager.update_portfolio_metrics()
        return new_document_ids

    def clean_agent_workspace(self, content: List[str]) -> None:
        """
        Process the models ToolCall and uses a predefined tool.

        Parameters
        ----------
        content : List[str]
            List of the new knowledgebase document IDs.

        Returns
        -------
        str
            The response after posting the tweet.
        """
        self.stop_flag = False
        self.tool_function_calls = 0

        # TODO add flags to limit agent to 3 posts a day, 20 comments a day
        # self.generate_trades_flag = False
        # self.generate_trades_function_call_counter = 0

        self.chroma_client.delete_documents(document_ids=content)

    @staticmethod
    def api_cool_down() -> None:
        seconds_to_cool_down:float = 60
        for remaining in range(seconds_to_cool_down, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02}:{secs:02}"  # Format as MM:SS
            print(f"Allocating compute for next agent in : {timer}", end="\r", flush=True)
            time.sleep(1)
        print(" " * 50, end="\r")


