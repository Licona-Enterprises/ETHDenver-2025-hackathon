from typing import Dict, List, Any

from langchain_core.documents import Document
import requests

from rag.document_loader import RagDocumentLoader
from rag.embedding_model import EmbeddingModel
from rag.rag_chroma_client import ChromaVectorStoreManager
from rag.mongodb_handler import MongoDBHandler
from backtesting.token_prices import TokenPrices


class RagPipeline:
    """
    A class to handle the complete workflow for RAG (Retrieval-Augmented Generation) pipelines, 
    including document loading, embedding generation, and managing a Chroma vector store.

    Attributes
    ----------
    collection_name : str
        The name of the Chroma database collection.
    document_loader : RagDocumentLoader
        The document loader for handling PDF files.
    embed_model : EmbeddingModel
        The model used for generating embeddings.
    manager : ChromaVectorStoreManager
        The Chroma vector store manager for handling document storage and retrieval.

    Methods
    -------
    process_pdfs() -> None
        Loads, splits, and generates embeddings for PDF documents.
    process_json(json_data: Dict) -> List[Any]
        Splits a single JSON document and generates embeddings for the resulting text chunks.
    process_multiple_json(json_data_list: List[Dict]) -> List[Any]
        Splits multiple JSON documents and generates embeddings for the resulting text chunks.
    add_documents_to_db(documents: List[Document]) -> List[str]
        Adds documents to the Chroma vector store and returns their IDs.
    """

    def __init__(self, collection_name: str):
        """
        Initializes the RagPipeline with a Chroma collection name.

        Parameters
        ----------
        collection_name : str
            The name of the Chroma collection.
        """
        self.collection_name = collection_name
        self.document_loader = RagDocumentLoader()
        self.embed_model = EmbeddingModel()
        self.mfa_mongodb = MongoDBHandler(collection_name="opportunities")
        self.manager = ChromaVectorStoreManager(collection_name)
        self.token_prices = TokenPrices()

    def process_pdfs(self) -> None:
        """
        Loads, splits, and generates embeddings for PDF documents. Documents are processed
        through the `RagDocumentLoader`.
        """
        self.document_loader.load_pdfs()
        self.document_loader.split_documents()
        self.document_loader.generate_embeddings_chroma()

    def process_json(self, json_data: Dict) -> List[Any]:
        """
        Splits a single JSON document into text chunks and generates embeddings.

        Parameters
        ----------
        json_data : Dict
            A JSON object containing the document data.

        Returns
        -------
        List[Any]
            A list of processed text chunks from the JSON document.
        """
        document_list = self.embed_model.split_json(json_data)
        self.embed_model.generate_embeddings_chroma(text_chunks=document_list)
        return document_list

    def process_multiple_json(self, json_data_list: List[Dict], metadata_source:str) -> List[Any]:
        """
        Splits multiple JSON documents into text chunks and generates embeddings.

        Parameters
        ----------
        json_data_list : List[Dict]
            A list of JSON objects containing the document data.

        Returns
        -------
        List[Any]
            A list of processed text chunks from the JSON documents.
        """
        document_list = self.embed_model.split_multiple_json(json_data_list=json_data_list, metadata_source=metadata_source)
        self.embed_model.generate_embeddings_chroma(text_chunks=document_list)
        return document_list

    def add_documents_to_db(self, documents: List[Document]) -> List[str]:
        """
        Adds a list of documents to the Chroma vector store.

        Parameters
        ----------
        documents : List[Document]
            A list of documents to be added to the Chroma vector store.

        Returns
        -------
        List[str]
            A list of document IDs added to the Chroma vector store.
        """
        return self.manager.add_documents(documents)
    
    def delete_later_coinmetrics_token_updates(self) -> List[str]:
        # TODO step 1 replace btc asset with asset from user query
        ASSET = [
            "btc",
            "LINK",
            "HYPE",
            "UNI",
            "AAVE",
            "ARB",
            "JUP",
            "OP",
            "INJ",
            "LDO",
            "ENA",
            "GRT",
            "RAY",

        ]

        ASSET_LIST = "LINK,HYPE,UNI,AAVE,ARB,JUP,OP,INJ,LDO,ENA,GRT,RAY"

        try:
            for i in range(len(ASSET)):

                API_KEY = "8yjPvRMxhzR7nJSUwsXb"
                URL = "https://api.coinmetrics.io/v4/timeseries/asset-metrics"
                PARAMS = {
                    "assets": ASSET[i],
                    "metrics": "PriceUSD,volume_reported_spot_usd_1d,volatility_realized_usd_rolling_7d,volatility_realized_usd_rolling_24h,volatility_realized_usd_rolling_30d,",
                    "frequency": "1d",
                    "start_time": "2025-01-01",
                    "pretty": "true",
                    "paging_from": "start",
                    "page_size": "900",
                    "api_key": API_KEY,
                }

                all_data = []
                asset_stats = {}
                asset_stats_list = []
                next_page_url = URL
                first_page = True
                while next_page_url:
                    response = requests.get(next_page_url, params=PARAMS if first_page else {}).json()
                    data = response.get("data", [])
                    if data:
                        all_data.extend(data)
                    next_page_url = response.get("next_page_url")  # Get next page URL
                    first_page = False

                if all_data:
                    asset_stats[i] = all_data
                    asset_stats_list.extend(data)
                    portfolio_document_list = self.process_multiple_json(json_data_list=asset_stats_list, metadata_source="nfa_opportunities")            
                    latest_portfolio_documents_ids = self.add_documents_to_db(portfolio_document_list)
                    print(f"Added {(len(latest_portfolio_documents_ids))} coinmetrics documents to the Chroma database. \n")
                    return latest_portfolio_documents_ids
                else:
                    print("No data received from Coimetrics API.")
        except Exception as e:
            print(f"Error while updating ChromaDB Coinmetrics API): {e}")
            raise

    def process_and_update_portfolio(self) -> List[str]:
        # when NFA database is down and we need to test i added these coinmarket cap ids of random tokens
        MOCK_LIST_3 = [
            "1",
            "29870", # BOME
            "10804", # FLOKI
            "28752", # WIF
            "52", # XPR 
            "32684", # SONIC
            "74", # DOGE
            "5994", # SHIB
            "1975", # LINK,
            "32196", # HYPE,
            "7083", # UNI,
            "7278", # AAVE,
            "11841", # ARB,
            "29210", # JUP,
            "11840", # OP,
            "7226", # INJ,
            "8000", # LDO,
            "30171", # ENA,
            "6719", # GRT,
            "8526", # RAY,
        ]
        try:

            latest_portfolio_token_data = self.token_prices.get_coinmarketcap_latest_token_stats(ids_list=MOCK_LIST_3)
            portfolio_document_list = self.process_multiple_json(json_data_list=latest_portfolio_token_data, metadata_source="nfa_opportunities")            
            latest_portfolio_documents_ids = self.add_documents_to_db(portfolio_document_list)
            print(f"Added {(len(latest_portfolio_documents_ids))} cmc documents to the Chroma database. \n")
            return latest_portfolio_documents_ids
        except Exception as e:
            print(f"Error while updating ChromaDB in RagPipeline.process_and_update_portfolio(): {e}")
            raise

    def process_and_update_knowledge_base(self) -> List[str]:
        """
        Processes the latest data from Mongodb and updates the Chroma database.

        This method takes the latest tweets (in JSON format), latest opportunities (in JSON format), splits them into smaller
        chunks for embedding, generates embeddings, and adds the data to the Chroma database.

        Returns
        -------
        List[str]
            A list of the IDs of the processed text chunks added to the Chroma database.

        """

        latest_portfolio_documents_ids = self.process_and_update_portfolio()
        return latest_portfolio_documents_ids


    def save_ids_to_file(self, knowledge_base_ids: List[str], file_path: str) -> None:
        """
        Find out which database Coti plans to use
        Temp save file ids here, remove for production

        Parameters
        ----------
        knowledge_base_ids : List[str]
            The list of knowledge base IDs to save.
        file_path : str
            The path to the text file where the IDs will be saved.

        Returns
        -------
        None
        """
        with open(file_path, 'a') as file:
            for knowledge_base_id in knowledge_base_ids:
                file.write(knowledge_base_id + '\n')

    def clear_short_term_memory(self, document_ids: List[str]) -> None:
        """
        Delete documents from Chroma DB that will no longer be needed 

        Parameters
        ----------
        document_ids : List[str]
            List of Chroma db Document ids to delete
        """
        self.manager.delete_documents(document_ids=document_ids)


