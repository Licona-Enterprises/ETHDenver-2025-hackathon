from typing import List, Dict, Tuple, Any, Optional
import time
import os
import openai
from dotenv import load_dotenv
from config.config import OpenAiConsts
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from datetime import datetime, timedelta
from tqdm import tqdm
from bson.objectid import ObjectId

from config.config import MFAMongodbConsts, PrivexMongodbConsts


class MongoDBHandler:
    """
    A class to manage MongoDB connections and operations.
    """

    def __init__(self, collection_name:str):
        """
        Initializes the MongoDBHandler class.

        """
        mfa_mongodb = MFAMongodbConsts()
        open_ai_consts = OpenAiConsts()
        self.default_embedding_model = open_ai_consts.DEFAULT_EMBEDDING_MODEL
        self.uri = None
        self.db_name = None
        self.collection_name = collection_name
        self.client = None
        self.database = None
        self.collection = None
        self._mfa_database(uri=mfa_mongodb.MFA_MONGDB_URI, db_name=mfa_mongodb.DB_NAME, collection_name=self.collection_name)
        
        self.privex_mongodb = PrivexMongodbConsts()
        self._privex_database(uri=self.privex_mongodb.PRIVEX_MONGDB_URI, db_name=self.privex_mongodb.DB_NAME)

    def _load_api_key(self) -> str:
        """
        Loads the OpenAI API key from environment variables using dotenv.

        Returns
        -------
        str
            The OpenAI API key.

        Raises
        ------
        ValueError
            If the OpenAI API key is not found in the environment variables.
        """
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set it in your environment.")
        
        return api_key

    def _mfa_database(self, uri: str = None, db_name: str = None, collection_name: str = None):
        """
        Initializes the MFA Database Handler.

        Args:
            uri (str): MongoDB connection URI. If None, reads from environment variable `MONGO_URI`.
            db_name (str): Name of the database to connect to.
            collection_name (str): Name of the collection to use.
        """
         
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.database = None
        self.collection = None

    def _privex_database(self, uri: str = None, db_name: str = None):
        """
        Initializes the Privex Database Handler.

        Args:
            uri (str): MongoDB connection URI. If None, reads from environment variable `MONGO_URI`.
            db_name (str): Name of the database to connect to.
        """
        self.privex_mongodb_client = MongoClient(uri)
        self.privex_db = self.privex_mongodb_client[db_name]
        self.agent_settings = self.privex_db["agent_settings"]
        self.agent_portfolio = self.privex_db["agent_portfolio"]
        self.agent_strategy_logs = self.privex_db["agent_strategy_logs"]

        self.tweet_comments_delete_later = self.privex_db["tweet_comments_delete_later"]
        self.tweet_threads_delete_later = self.privex_db["tweet_threads_delete_later"]

    def connect(self):
        """
        Establishes a connection to the MongoDB instance.
        """
        try:
            if not self.uri:
                raise ValueError("MongoDB URI is not provided or missing in environment variables.")

            self.client = MongoClient(self.uri)
            # Test connection
            self.client.admin.command("ping")
            print("Connected to MongoDB successfully!")

            if self.db_name:
                self.database = self.client[self.db_name]
                print(f"Using database: {self.db_name}")

            if self.db_name and self.collection_name:
                self.collection = self.database[self.collection_name]
                print(f"Using collection: {self.collection_name}")

        except ConnectionFailure as e:
            print("Failed to connect to MongoDB:", e)
        except ConfigurationError as e:
            print("Configuration error:", e)
        except Exception as e:
            print("An error occurred while connecting to MongoDB:", e)

    def set_database(self, db_name: str):
        """
        Sets the database to use.

        Args:
            db_name (str): Name of the database.
        """
        if self.client:
            self.database = self.client[db_name]
            self.db_name = db_name
            print(f"Database set to: {db_name}")
        else:
            print("MongoDB client is not connected. Call connect() first.")

    def set_collection(self, collection_name: str):
        """
        Sets the collection to use.

        Args:
            collection_name (str): Name of the collection.
        """
        if self.database:
            self.collection = self.database[collection_name]
            self.collection_name = collection_name
            print(f"Collection set to: {collection_name}")
        else:
            print("Database is not selected. Call set_database() first.")
    
    @staticmethod
    def generate_embedding(text: str) -> Optional[List[float]]:
        """Generate OpenAI embeddings for a given text"""

        if not text or text.strip() == "":  # Avoid sending empty text
            return None
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set it in your environment.")
        
        try:
            response = openai.embeddings.create(
                model=self.default_embedding_model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            return None

    def mongo_db_insert_one_document_for_agent(self, agent_id: str, document: dict, db_collection_name: str) -> None:
        """
        Inserts one document into the Privex mongodb collection 

        This is a custom def specifically tailored to the NFA database, which was used in this project.

        Your Agent will require their own database querying logic, replace this def with your database query logic.

        Parameters
        ----------
        document : dict
            _description_
        db_collection_name : str
            _description_
        """
        agent = self.agent_settings.find_one({"_id": ObjectId(agent_id)})

        if not agent:
            print(f"Agent not found! Could not update {db_collection_name}")
        else:
            client = self.privex_mongodb_client
            mongo_db_collection = self.privex_db[db_collection_name]
            portfolio_document = {
                "agentId": ObjectId(agent_id),
                "portfolioDetails": document
            }
            result = mongo_db_collection.insert_one(portfolio_document)
            print(f"updated agent {db_collection_name} for {agent_id}")
        client.close()

    def update_or_create_portfolio(self, agent_id:str, portfolio_updates:dict) -> None:
        """
        Checks if an agent has an existing portfolio entry.
        If found, updates it. If not, creates a new entry.

        :param agent_id: The _id of the agent (as a string).
        :param portfolio_updates: Dictionary with updated token balances.
        """
        agent_object_id = ObjectId(agent_id)

        existing_portfolio = self.agent_portfolio.find_one({"agentId": agent_object_id})

        if existing_portfolio:
            update_data = {
                "portfolioDetails": portfolio_updates,
            }
            
            result = self.agent_portfolio.update_one(
                {"agentId": agent_object_id},
                {"$set": update_data}
            )

            if result.matched_count > 0:
                print(f"Updated portfolio for agent {agent_id}.")
            else:
                print("Portfolio update failed.")
        else:
            new_portfolio = {
                "agentId": agent_object_id,
                "portfolioDetails": portfolio_updates,
            }
            result = self.agent_portfolio.insert_one(new_portfolio)
            print(f"Created new portfolio entry for agent {agent_id} with _id {result.inserted_id}")

    def update_or_create_portfolio_v2(self, agent_id:str, portfolio_updates:dict, portfolio_metrics: dict) -> None:
        """
        Checks if an agent has an existing portfolio entry.
        If found, updates it. If not, creates a new entry.

        :param agent_id: The _id of the agent (as a string).
        :param portfolio_updates: Dictionary with updated token balances.
        """
        agent_object_id = ObjectId(agent_id)

        existing_portfolio = self.agent_portfolio.find_one({"agentId": agent_object_id})

        if existing_portfolio:
            update_data = {
                "portfolioDetails": portfolio_updates,
                "portfolioMetrics": portfolio_metrics,
            }
            
            result = self.agent_portfolio.update_one(
                {"agentId": agent_object_id},
                {"$set": update_data}
            )

            if result.matched_count > 0:
                print(f"Updated portfolio for agent {agent_id}.")
            else:
                print("Portfolio update failed.")
        else:
            new_portfolio = {
                "agentId": agent_object_id,
                "portfolioDetails": portfolio_updates,
            }
            result = self.agent_portfolio.insert_one(new_portfolio)
            print(f"Created new portfolio entry for agent {agent_id} with _id {result.inserted_id}")

    def save_tweet_comment_delete_later(self, agent_id: str, tweet_comments_updates: str) -> None:
        """
        If an agent has an existing tweet comment entry, appends new comments.
        Otherwise, creates a new entry.

        :param agent_id: The _id of the agent (as a string).
        :param tweet_comments_updates: A string representing the new comment.
        """
        agent_object_id = ObjectId(agent_id)

        existing_tweet_comments = self.tweet_comments_delete_later.find_one({"agentId": agent_object_id})

        if existing_tweet_comments:
            # Ensure tweetCommentDetails is a list before appending
            if not isinstance(existing_tweet_comments.get("tweetCommentDetails"), list):
                self.tweet_comments_delete_later.update_one(
                    {"agentId": agent_object_id},
                    {"$set": {"tweetCommentDetails": [existing_tweet_comments["tweetCommentDetails"]]}}
                )

            result = self.tweet_comments_delete_later.update_one(
                {"agentId": agent_object_id},
                {"$push": {"tweetCommentDetails": tweet_comments_updates}}
            )

            if result.modified_count > 0:
                print(f"Appended to comment collection for agent {agent_id}.")
            else:
                print("Tweet comment update failed.")
        else:
            new_tweet_comments = {
                "agentId": agent_object_id,
                "tweetCommentDetails": [tweet_comments_updates],  # Store as a list for easy appending
            }
            result = self.tweet_comments_delete_later.insert_one(new_tweet_comments)
            print(f"Created new tweet comment entry for agent {agent_id} with _id {result.inserted_id}")

    def save_tweet_thread_delete_later(self, agent_id: str, tweet_comments_updates: List[str]) -> None:
        """
        If an agent has an existing tweet comment entry, appends new comments.
        Otherwise, creates a new entry.

        :param agent_id: The _id of the agent (as a string).
        :param tweet_comments_updates: A string representing the new comment.
        """
        agent_object_id = ObjectId(agent_id)

        existing_tweet_comments = self.tweet_threads_delete_later.find_one({"agentId": agent_object_id})

        if existing_tweet_comments:
            
            if not isinstance(existing_tweet_comments.get("tweetThreadDetails"), list):
                self.tweet_threads_delete_later.update_one(
                    {"agentId": agent_object_id},
                    {"$set": {"tweetThreadDetails": [existing_tweet_comments["tweetThreadDetails"]]}}
                )

            result = self.tweet_threads_delete_later.update_one(
                {"agentId": agent_object_id},
                {"$push": {"tweetThreadDetails": tweet_comments_updates}}
            )

            if result.modified_count > 0:
                print(f"Appended to comment collection for agent {agent_id}.")
            else:
                print("Tweet comment update failed.")
        else:
            new_tweet_comments = {
                "agentId": agent_object_id,
                "tweetThreadDetails": [tweet_comments_updates],  # Store as a list for easy appending
            }
            result = self.tweet_threads_delete_later.insert_one(new_tweet_comments)

    # TODO finish this
    def get_portfolio_details(self, agent_id:str):
        """
        Fetch portfolio details for a given agent ID from MongoDB.
         
        This is a custom def specifically tailored to the NFA database, which was used in this project.

        Your Agent will require their own database querying logic, replace this def with your database query logic.

        Returns
        -------
        List[Dict[str, Any]]
            List of agent details
        
        """
        try:
            client = self.privex_mongodb_client
            collection = self.agent_portfolio
            document = collection.find_one({"agentId": ObjectId(agent_id)})

            if not document:
                print(f"No portfolio found for agentId: {agent_id}")
                return {}

            portfolio_details = document.get("portfolioDetails", {})

            return portfolio_details  
        # TODO close db connection 

        except Exception as e:
            print(f"Error fetching portfolio details: {e}")
            return None

    def get_all_agents(self)-> List[Dict[str, Any]]:
        """
        Gets all agent settings from mongodb 
        
        This is a custom def specifically tailored to the NFA database, which was used in this project.

        Your Agent will require their own database querying logic, replace this def with your database query logic.

        Returns
        -------
        List[Dict[str, Any]]
            List of agent details
        """
        agents = []
        try:
            client = self.privex_mongodb_client
            collection = self.agent_settings
            agents = list(collection.find())
            client.close()
        except Exception as e:
            print(f"Error retrieving agents: {e}")
            agents = None
        return agents
    
    def get_agent_settings(self, agent_id: str)-> List[Dict[str, Any]]:
        """
        Gets one agent settings from mongodb 
        
        This is a custom def specifically tailored to the NFA database, which was used in this project.

        Your Agent will require their own database querying logic, replace this def with your database query logic.

        Returns
        -------
        List[Dict[str, Any]]
            List of agent settings
        """
        agent = []
        try:
            client = self.privex_mongodb_client
            collection = self.agent_settings
            agent = collection.find_one({"_id": ObjectId(agent_id)})
            # client.close()
        except Exception as e:
            print(f"Error retrieving agent: {e}")
            agent = None
        return agent

    # TODO deprecate this def
    def insert_one(self, document: dict):
        """
        Inserts a single document into the collection.

        Args:
            document (dict): Document to insert.

        Returns:
            InsertOneResult: Result of the insertion.
        """
        if self.collection:
            result = self.collection.insert_one(document)
            print(f"Inserted document with ID: {result.inserted_id}")
            return result
        else:
            print("Collection is not set. Call set_collection() first.")

    def find(self, query: dict = None):
        """
        Finds documents in the collection.

        Args:
            query (dict): Query filter to apply. Default is an empty query.

        Returns:
            Cursor: MongoDB cursor for the query results.
        """
        if self.collection:
            query = query or {}
            return self.collection.find(query)
        else:
            print("Collection is not set. Call set_collection() first.")

    # TODO deprecate this def
    def query_tweets_by_created_date(self) -> List[Dict]:
        """
        Queries tweets created within the last hour from the MongoDB database
        and returns the results as a list of dictionaries.

        Returns
        -------
        List[Dict]
            A list of dictionaries representing the queried tweets.
        """
        mfa_mongodb = MFAMongodbConsts()
        client = MongoClient(mfa_mongodb.MFA_MONGDB_URI)
        db = client[mfa_mongodb.DB_NAME]
        collection = db["twitterposts"]
        now = datetime.now()
        date_filter = now - timedelta(minutes=1440)
        query = {"created_at": {"$gt": date_filter}}
        results = collection.find(query)
        total_results = collection.count_documents(query)
        tweets=[]
        for tweet in tqdm(results, total=total_results, desc="Processing tweets", unit="tweet"):
            tweet["_id"] = str(tweet["_id"])
            tweet["oppDocId"] = str(tweet["oppDocId"])
            
            for key, value in tweet.items():
                if isinstance(value, datetime):
                    tweet[key] = value.isoformat()
    
            tweets.append(tweet)

        print(f"Found {len(tweets)} tweets to process in RAG Pipeline \n")

        # Close the connection
        client.close()

        return tweets
    
    def query_nfa_collection_by_most_recent_entries(self, minutes_to_backfill: float) -> Tuple[List[Dict], List[Dict]]:
        """
        Queries collection entries created within the minutes_to_backfill param from the MongoDB database
        and returns the results as a list of dictionaries.

        This is a custom def specifically tailored to the NFA database, which was used in this project.

        Your Agent will require their own database querying logic, replace this def with your database query logic.

        Parameters
        ----------
        minutes_to_backfill : float
            number of minutes to look back to and return collection entries

        Returns
        -------
        List[Dict]
            A list of dictionaries representing the queried tweets.
        """
        mfa_mongodb = MFAMongodbConsts()
        client = MongoClient(mfa_mongodb.MFA_MONGDB_URI)
        db = client[mfa_mongodb.DB_NAME]
        tweet_collection = db["twitterposts"]
        opportunities_collection = db["opportunities"]

        now = datetime.now()
        date_filter = now - timedelta(minutes=minutes_to_backfill)
        twitter_posts_query = {"created_at": {"$gt": date_filter}}
        opportunities_query = {"createdAt": {"$gt": date_filter}}

        tweet_results = tweet_collection.find(twitter_posts_query)
        tweet_total_results = tweet_collection.count_documents(twitter_posts_query)
        opportunities_results = opportunities_collection.find(opportunities_query)
        opportunities_total_results = opportunities_collection.count_documents(opportunities_query)

        twitter_nfa_results=[]
        opportunities_nfa_results = []

        # format tweets from nfa database here
        for tweet in tqdm(tweet_results, total=tweet_total_results, desc="Processing tweets", unit="tweet"):
            tweet["_id"] = str(tweet["_id"])
            tweet["oppDocId"] = str(tweet["oppDocId"])
            for key, value in tweet.items():
                if isinstance(value, datetime):
                    tweet[key] = value.isoformat()
            twitter_nfa_results.append(tweet)

        # format opportunities from nfa database here
        for opportunity in tqdm(opportunities_results, total=opportunities_total_results, desc="Processing opportunities", unit="opportunity"):
            
            for key, value in opportunity.items():
                if isinstance(value, datetime):
                    opportunity[key] = value.isoformat()

            opportunity_at_index_dict = {}
            opportunity_at_index_dict[str(opportunity["_id"])] = {
                "data":str(opportunity["data"])
            }
            opportunities_nfa_results.append(opportunity_at_index_dict)

        print(f"Found {len(twitter_nfa_results) + len(opportunities_nfa_results)} data points to process in RAG Pipeline \n")

        # Close the connection
        client.close()

        return twitter_nfa_results, opportunities_nfa_results

    def get_cmc_ids_by_symbols(self, symbol: str) -> List[str]:
        """
        Query the 'tokens' collection and return all 'id' values from 'cmc_info' for the given symbol.

        This is a custom def specifically tailored to the NFA database, which was used in this project.

        Your Agent will require their own database querying logic, replace this def with your database query logic.

        Parameters
        ----------
        symbol : str
            The token symbol to search for.

        Returns
        -------
        list
            A list of 'id' values found in the 'cmc_info' array of matching documents.
        """

        mfa_mongodb = MFAMongodbConsts()
        client = MongoClient(mfa_mongodb.MFA_MONGDB_URI)
        db = client[mfa_mongodb.DB_NAME]
        collection = db['tokens']
        
        try: 
            result = collection.find_one({"symbol": symbol})            
            if result and "cmc_info" in result:
                # ids = [float(entry["id"]) for entry in result["cmc_info"]]
                ids = [str(entry["id"]) for entry in result["cmc_info"]]
                client.close()
                return ids
            else:
                client.close()
                return [] 
        except Exception as e:
            print(f"unable to get Coinmarketcap token IDs from nfa mongo db")
            return []

    @staticmethod
    def process_new_document(doc) -> None:
        """Process a new document, generate embeddings, and update MongoDB"""

        # because the listener is static we have to load these everytime
        privex_mongodb = PrivexMongodbConsts()
        privex_mongodb_client = MongoClient(privex_mongodb.PRIVEX_MONGDB_URI)
        privex_db = privex_mongodb_client[privex_mongodb.DB_NAME]
        agent_settings = privex_db["agent_settings"]
        
        doc_id = doc["_id"]
        persona_text = doc.get("persona", "")
        knowledge_base_text = doc.get("knowledgeBase", "")

        # Generate embeddings
        persona_embedding = MongoDBHandler.generate_embedding(persona_text)
        knowledge_base_embedding = MongoDBHandler.generate_embedding(knowledge_base_text)

        # Prepare update query
        update_query = {}
        if persona_embedding:
            update_query["embedded_persona"] = persona_embedding
        if knowledge_base_embedding:
            update_query["embedded_knowledgeBase"] = knowledge_base_embedding

        # Update MongoDB document with new embeddings
        if update_query:  # Only update if there's something to insert
            agent_settings.update_one({"_id": doc_id}, {"$set": update_query})
            print(f"Updated document {doc_id} with embeddings.")

    @staticmethod
    def listen_for_changes():
        
        """Listen for new documents and process them in real-time"""

        try:

            # because the listener is static we have to load these everytime
            privex_mongodb = PrivexMongodbConsts()
            privex_mongodb_client = MongoClient(privex_mongodb.PRIVEX_MONGDB_URI)
            privex_db = privex_mongodb_client[privex_mongodb.DB_NAME]
            agent_settings = privex_db["agent_settings"]

            with agent_settings.watch([{"$match": {"operationType": "insert"}}]) as stream:
                for change in stream:
                    new_document = change["fullDocument"]
                    self.process_new_document(new_document)

        except Exception as e:
            print(f"Change Stream error: {e} \n")
            print("Retrying in 5 seconds... \n")
            time.sleep(5)
            MongoDBHandler.listen_for_changes()  # Restart listening


    def close(self):
        """
        Closes the MongoDB connection.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

