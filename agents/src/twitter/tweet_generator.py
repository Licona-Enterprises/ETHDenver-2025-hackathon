import os
import re
import time
import json
import random
from dotenv import load_dotenv
from typing_extensions import List, TypedDict, Tuple

import textwrap
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

from rag.embedding_model import EmbeddingModel
from twitter.twitter_api import TwitterAPI
from rag.rag_chroma_client import ChromaVectorStoreManager
from config.config import HubPull, OpenAiConsts, TwitterApiConsts
from rag.mongodb_handler import MongoDBHandler


class TweetGenerator:
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

    def __init__(self, collection_name: str, hub_pull: HubPull, twitter_api_consts:TwitterApiConsts) -> None:
        """
        Initializes the TweetGenerator with the required components.

        Parameters
        ----------
        collection_name : str
            The name of the Chroma vector store collection.
        """
        self.api_key = ""
        # twitter_consts = TwitterApiConsts()
        twitter_consts = twitter_api_consts
        self.max_response_length = twitter_consts.MAX_RESPONSE_LENGTH
        self.max_retries = twitter_consts.MAX_RETRY_RESPONSE_GENERATE
        self.tweet_similarity_threshold = twitter_consts.MAX_SIMILARITY_THRESHOLD
        self._load_api_key()
        open_ai_consts = OpenAiConsts()
        self.open_ai_embedding_function = OpenAIEmbeddings(model=open_ai_consts.DEFAULT_EMBEDDING_MODEL)
        self.llm = ChatOpenAI(model=open_ai_consts.DEFAULT_MODEL_NAME)

        # since chroma is only going to be used for short term data which diana class gets from nfa database and market data ChromaVectorStoreManager collection name is DIANA
        self.manager = ChromaVectorStoreManager("DIANA")

        # hub_pull = HubPull()
        self.similarity_search_prompt = hub_pull.SIMILARITY_SEARCH_PROMPT
        self.similarity_opportunities_search_prompt = hub_pull.SIMILARITY_OPPORTUNITY_SEARCH_PROMPT
        self.similarity_trade_search_prompt = hub_pull.SIMILARITY_TRADE_SEARCH_PROMPT
        self.comment_on_similarity_search_prompt = hub_pull.COMMENT_ON_POST_SIMILARITY_SEARCH_PROMPT
        self.agent_tasks = hub_pull.get_agent_tasks()
        self.prompt = PromptTemplate.from_template(hub_pull.PROMPT)
        self.thread_prompt = PromptTemplate.from_template(hub_pull.THREAD_PROMPT)
        self.comment_prompt = PromptTemplate.from_template(hub_pull.COMMENT_ON_TWITTER_POST_PROMPT)
        self.portfolio_thread_prompt = PromptTemplate.from_template(hub_pull.PORTFOLIO_THREAD_PROMPT)
        self.twitter_api = TwitterAPI(twitter_api_consts=twitter_api_consts)      

        self.mongo_db_handler = MongoDBHandler(collection_name=collection_name) 
        self.active_agent_id = collection_name

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

    def generate(self, question: str, context: List[Document]) -> str:
        """
        Generates a response to the given question using retrieved document context.

        Parameters
        ----------
        question : str
            The user's question to be answered.
        context : List[Document]
            The list of documents providing the context for the answer.

        Returns
        -------
        str
            The generated response from the language model.
        """
        docs_content = "\n\n".join(doc.page_content for doc in context)
        messages = self.prompt.invoke({"question": question, "context": docs_content})
        retry_count = 0

        while retry_count < self.max_retries:
            response = self.llm.invoke(messages).content
            if len(response) > self.max_response_length:
                print(f"Response too long (length={len(response)}). Regenerating...")
                messages = self.prompt.invoke(
                    {
                        "question": question,
                        "context": docs_content,
                        "retry_hint": f"Response must be {self.max_response_length} characters or fewer.",
                    }
                )
                retry_count += 1
                continue

            similar_responses = self.manager.similarity_search(
                response, k=6, filters={"source": "generated_tweet"}
            )
            
            if similar_responses:
                similarity_score = self._calculate_similarity(response, similar_responses[0].page_content)
                if similarity_score >= self.tweet_similarity_threshold:
                    print(f"Response too similar to an existing response (SIM={similarity_score:.2f}). Regenerating...\n")
                    messages = self.prompt.invoke(
                        {
                            "question": question,
                            "context": docs_content,
                            "retry_hint": f"Response too similar to an existing response (SIM={similarity_score:.2f}). Try using another document to talk about something new",
                        }
                    )
                    retry_count += 1
                    continue

            print(f"Response accepted (length={len(response)}): {response}")
            generated_tweet = Document(
                page_content=str(response),
                metadata={"source": "generated_tweet"},
            )
            self.manager.add_documents([generated_tweet])
            return response

        raise RuntimeError("Failed to generate a valid, unique response within the maximum number of retries.")

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates the cosine similarity between two text strings using embeddings.

        Parameters
        ----------
        text1 : str
            The first text string.
        text2 : str
            The second text string.

        Returns
        -------
        float
            The cosine similarity between the two text embeddings.
        """
        embeddings = self.open_ai_embedding_function
        
        vector1 = embeddings.embed_query(text1)
        vector2 = embeddings.embed_query(text2)
        similarity = cosine_similarity([vector1], [vector2])[0][0]
        return similarity

    def generate_thread(self, question: str, context: List[Document]) -> List[str]:
        """
        Generates a Twitter thread (a list of tweets) based on the given question and document context.

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
        # Combine all the context into one string
        docs_content = "\n\n".join(doc.page_content for doc in context)

        messages = self.portfolio_thread_prompt.invoke({"question": question, "context": docs_content})
        response = self.llm.invoke(messages).content

        similar_responses = self.manager.similarity_search(
            response, k=6, filters={"source": "generated_tweet"}
        )
        retry_count = 0

        while retry_count < self.max_retries:
            if similar_responses:
                similarity_score = self._calculate_similarity(response, similar_responses[0].page_content)
                if similarity_score >= self.tweet_similarity_threshold:
                    print(f"Response too similar to an existing response (SIM={similarity_score:.2f}). Regenerating...\n")
                    messages = self.prompt.invoke(
                        {
                            "question": question,
                            "context": docs_content,
                            "retry_hint": f"Response too similar to an existing response (SIM={similarity_score:.2f}). Try using another document to talk about something new",
                        }
                    )
                    retry_count += 1
                    continue

            print(f"Response accepted (length={len(response)}): {response}")
            
            # generated_tweet = Document(
            #     page_content=str(response),
            #     metadata={"source": "generated_tweet"},
            # )
            # self.manager.add_documents([generated_tweet])

            break
            # return response

        # Split the response into tweets, ensuring each is under the character limit
        tweets = self._split_into_tweets(response)
        print(f"Generated thread with {len(tweets)} tweets.")
        self.mongo_db_handler.save_tweet_thread_delete_later(agent_id=self.active_agent_id, tweet_comments_updates=tweets)
        return tweets

    def generate_comment(self, question: str, context: List[Document]) -> str:
        """
        Generates a response to the given question using retrieved document context.

        Parameters
        ----------
        question : str
            The user's question to be answered.
        context : List[Document]
            The list of documents providing the context for the answer.

        Returns
        -------
        str
            The generated response from the language model.
        """
        messages = self.comment_prompt.invoke({"question": question, "context": context})
        retry_count = 0

        while retry_count < self.max_retries:
            response = self.llm.invoke(messages).content
            if len(response) > self.max_response_length:
                print(f"Response too long (length={len(response)}). Regenerating...")
                messages = self.prompt.invoke(
                    {
                        "question": question,
                        "context": context,
                        "retry_hint": f"Response must be {self.max_response_length} characters or fewer.",
                    }
                )
                retry_count += 1
                continue

            print(f"Response accepted (length={len(response)}): {response} \n")

            # TODO remove this since we no longer need chroma db for long term memeory
            # generated_tweet = Document(
            #     # page_content=str(response),
            #     page_content=response,
            #     metadata={"source": "generated_tweet"},
            # )
            # self.manager.add_documents([generated_tweet])

            self.mongo_db_handler.save_tweet_comment_delete_later(agent_id=self.active_agent_id, tweet_comments_updates=response)

            return response

        raise RuntimeError("Failed to generate a valid, unique response within the maximum number of retries.")

    def _split_into_tweets(self, text: str, max_length: int = 150) -> List[str]:
        """
        Splits a long text into smaller chunks that fit within the Twitter character limit.

        Parameters
        ----------
        text : str
            The long text to be split into tweets.
        max_length : int
            The maximum allowed length for each tweet (default is 280).

        Returns
        -------
        List[str]
            A list of tweet texts.
        """

        combined_text = "".join(text)
        formatted_text = re.sub(r'(\d+/)', r'\n\1', combined_text)        
        numbered_tweets = [line.strip() for line in formatted_text.split('\n') if line.strip()]

        return numbered_tweets

    def sample_chroma_documents(self, query: str, similarity_search_filter: str, num_docs: int = 10) -> List[Document]:
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
        sampled_results = random.sample(search_results, min(num_docs, len(search_results)))
    
        return sampled_results

    def normalize_tweets_to_comment(self, recent_tweets: List[Document]) -> List[str]:
        """
        used to get the tweet id to respond to and to normalize other tweet metadata

        Parameters
        ----------
        recent_tweets : List[Document]
            List of documents from the ChromaDB tweets

        Returns
        -------
        str
            ID of tweet to reply to
        """
        all_ids = []
        normalized_tweets = {}
        for doc in recent_tweets:
            try:
                content_dict = json.loads(doc.page_content)
                if "id" in content_dict and "description" in content_dict:
                    normalized_tweets[content_dict["id"]] = {
                        "user_id": content_dict.get("user_id", ""),
                        "content": content_dict.get("description", "")  # Use .get() to handle missing keys
                    }
                    all_ids.append(content_dict["id"])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for document: {doc.page_content}. Error: {e}")
        return all_ids

    # This a tool will be deprecated later
    def create_tweet(self) -> str:
        state: State = {"question": self.similarity_search_prompt, "context": [], "answer": ""}
        retrieved_docs = self.sample_chroma_documents(query=state["question"])
        state["context"] = retrieved_docs
        generated_answer = self.generate(question=state["question"], context=state["context"])
        state["answer"] = generated_answer
        # self.twitter_api.post_tweet(str(generated_answer))
        return generated_answer
    
    # This a tool the agent can use
    def create_tweet_thread(self) -> Tuple[str, str]:
        """
        creates a twitter thread and posts the twitter thread using the twitter api class

        Returns
        -------
        str
            the generated twitter thread
        """
        
        state: State = {"question": self.similarity_trade_search_prompt, "context": [], "answer": ""}
        
        # TODO maybe add functionality to sample users knowledge base here  
        retrieved_docs = self.twitter_api.get_recent_tweets()
        if len(retrieved_docs) <=0: 
            print(f"users twitter account returned no posts \n")
            retrieved_docs = self.sample_chroma_documents(query=state["question"], similarity_search_filter="nfa_opportunities")
            print(f"sampled NFA database for {len(retrieved_docs)} docs \n")
            state["context"] = retrieved_docs    

        clean_responses = []

        if len(retrieved_docs) > 0:
            generated_thread_answer = self.generate_thread(question=state["question"], context=state["context"])
            state["answer"] = generated_thread_answer

            for entry in generated_thread_answer:
                
                if entry.startswith('"') and entry.endswith('"'):
                    entry = entry[1:-1]
                
                clean_responses.append(entry)

            self.twitter_api.post_thread(clean_responses)

        return clean_responses

    # This a tool the agent can use
    def create_comment(self) -> str: 
        """
        creates a twitter comment and posts the comment using the twitter api class

        Returns
        -------
        str
            the generated comment
        """
        state: State = {"question": self.comment_on_similarity_search_prompt, "context": [], "answer": ""}
        # TODO maybe add functionality to sample users knowledge base here
        retrieved_docs = self.sample_chroma_documents(query=state["question"], similarity_search_filter="twitter_posts", num_docs=1)
        state["context"] = retrieved_docs
        print(retrieved_docs)
        tweets_dict = self.normalize_tweets_to_comment(recent_tweets=retrieved_docs)
        generated_answer = self.generate_comment(question=state["question"], context=retrieved_docs[0])
        state["answer"] = generated_answer    

         # Check if response has extra quotes
        if generated_answer.startswith('"') and generated_answer.endswith('"'):
            generated_answer = generated_answer[1:-1]  # Remove leading and trailing quotes

        self.twitter_api.comment_on_tweet(content=generated_answer, tweet_id=tweets_dict[0])
        return generated_answer

class State(TypedDict):
    """
    A typed dictionary to represent the application's state.

    Attributes
    ----------
    question : str
        The user's question.
    context : List[Document]
        The context documents retrieved for the question.
    answer : str
        The generated answer from the language model.
    """
    question: str
    context: List[Document]
    answer: str | List[str]
