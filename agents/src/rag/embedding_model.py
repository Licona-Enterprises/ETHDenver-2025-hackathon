import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import json

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_chroma import Chroma

from config.config import GeneratedTradesFilePaths
from config.config import OpenAiConsts
from config.config import KnowledgeBaseFilePaths
from config.config import HubPull

class EmbeddingModel:
    """
    A class to process multiple PDF documents into a knowledge base using OpenAI embeddings
    and vector storage.

    This class provides methods for loading, splitting, embedding, and storing
    documents for retrieval-based AI applications.

    Attributes
    ----------
    api_key : str
        OpenAI API key for embedding generation.
    file_paths : List[str]
        Paths to the PDF files to be processed.
    docs : List[Any]
        Loaded PDF documents.
    splits : List[Any]
        Text chunks generated from splitting the documents.
    vector_store : InMemoryVectorStore
        Vector store for storing and retrieving embeddings.
    """

    def __init__(self):
        """
        Initializes the EmbeddingModel class with consts from the config file.
        """
        self.generated_trades = GeneratedTradesFilePaths()
        self.knowledge_base = KnowledgeBaseFilePaths()
        self.open_ai_consts = OpenAiConsts()
        self.agent_info = HubPull()
        self.embedding_model = self.open_ai_consts.DEFAULT_EMBEDDING_MODEL
        self.generated_trades_file_paths: List[str] = self.generated_trades.get_generated_trades_file_paths()
        self.generated_responses_file_paths: List[str] = self.knowledge_base.get_knowledge_base_json_file_paths()
        self.open_trades: List[Any] = []
        self.splits: List[Any] = []
        self.vector_store: InMemoryVectorStore = None
        self.api_key: Optional[str] = None
        self._load_api_key()

    def _load_api_key(self) -> None:
        """
        Loads the OpenAI API key from environment variables using dotenv.
        """
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set it in your environment.")

    def mock_trade_generator(self) -> dict:
        """
        Reads a JSON file and converts it into a Python dictionary.

        Returns
        -------
        dict
            The JSON content as a Python dictionary.
        """
        with open(self.generated_trades_file_paths[0], "r") as json_file:
            data = json.load(json_file)
        return data

    def mock_response_generator(self) -> list[dict]:
        """
        Reads all JSON files in self.file_paths and returns a list of dictionaries.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the data from each JSON file.
        """
        if not self.generated_responses_file_paths:
            raise ValueError("No file paths provided in self.generated_responses_file_paths.")

        all_data = []
        for file_path in self.generated_responses_file_paths:
            try:
                with open(file_path, "r") as json_file:
                    data = json.load(json_file)
                    all_data.append(data)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except json.JSONDecodeError:
                print(f"Invalid JSON format in file: {file_path}")

        return all_data

    def load_trade_details_json(self) -> List[Any]:
        """
        Loads data that has been formatted in json.

        Raises
        ------
        FileNotFoundError
            If any of the json files do not exist at the specified paths.
        """
        trading_strategy_details: List[Any] = []
        for file_path in self.generated_trades_file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found at path: {file_path}")
            loader = JSONLoader(
                file_path=file_path,
                jq_schema='.trading_strategy',
                text_content=False)
            trading_strategy_details.extend(loader.load())
        return trading_strategy_details

    def split_json(self, json_data:Dict) -> List[Any]:
        """
        Splits the loaded documents into smaller chunks.

        Parameters
        ----------
        json_data:Dict
            json data to split and turn to documents.

        Returns
        -------
        List of Documents
        """        
        splitter = RecursiveJsonSplitter(max_chunk_size=300)
        json_chunks = splitter.split_json(json_data=json_data)
        for chunk in json_chunks[:3]:
            print(chunk)
        docs = splitter.create_documents(texts=[json_data])
        return docs

    def split_multiple_json(self, json_data_list: List[Dict], metadata_source: str) -> List[Any]:
        """
        Splits a list of loaded JSON documents into smaller chunks.

        Parameters
        ----------
        json_data_list : List[Dict]
            A list of JSON data (dictionaries) to split and turn into documents.

        Returns
        -------
        List[Any]
            A list of smaller document chunks generated from all JSON data.
        """
        if not json_data_list:
            raise ValueError("The input list of JSON data is empty.")
        
        splitter = RecursiveJsonSplitter(max_chunk_size=300)
        all_docs = []

        for json_data in json_data_list:
            # json_chunks = splitter.split_json(json_data=json_data)
            # for chunk in json_chunks[:3]:
            #     print(chunk)
            docs = splitter.create_documents(texts=[json_data], metadatas=[{"source": metadata_source}])
            all_docs.extend(docs)

        return all_docs

    def generate_embeddings_chroma(self, text_chunks:List[Any]) -> None:
        """
        Generates embeddings for the text chunks using OpenAI embeddings.

        Parameters
        ----------
        model : str, optional
            The OpenAI model to use for embeddings (default is found at DEFAULT_EMBEDDING_MODEL).
        """
        self.splits = text_chunks
        if not self.splits:
            raise ValueError("No text splits found. Please split the documents first.")
        embeddings = OpenAIEmbeddings(model=self.embedding_model)
        vector_store = Chroma(
            collection_name=self.agent_info.KNOWLEDGE_BASE_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db", 
        )
        ids = vector_store.add_documents(documents=self.splits)
        print(f"Generated and stored embeddings for {len(ids)} documents. \n")

        # for dev sanity - print vector previews
        first_document_content = self.splits[0].page_content
        first_vector = embeddings.embed_query(first_document_content)
        
        print("Vector Preview (First 5 dimensions):")
        print(f"Document: {first_document_content[:100]}...")
        print(f"Vector (First 5 elements): {first_vector[:5]}\n \n")