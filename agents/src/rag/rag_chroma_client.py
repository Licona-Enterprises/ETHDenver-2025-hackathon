import os
import chromadb
from uuid import uuid4
from typing import Any, List, Dict, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

from config.config import OpenAiConsts


class ChromaVectorStoreManager:
    """
    A manager for interacting with a Chroma vector store, including adding, updating,
    deleting, and querying documents.

    Parameters
    ----------
    collection_name : str
        The name of the collection in the Chroma vector store.

    Attributes
    ----------
    client : PersistentClient
        A persistent Chroma client used for interacting with the vector store.
    vector_store : Chroma
        The Chroma vector store initialized with the specified collection.
    collection : PersistentClient.Collection
        The collection used for managing document storage and retrieval.
    """
    def __init__(self, collection_name: str) -> None:
        self.open_ai_consts = OpenAiConsts()
        self._load_api_key()
        self.collection_name = collection_name
        self.open_ai_embedding_function = OpenAIEmbeddings(model=self.open_ai_consts.DEFAULT_EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient()
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.open_ai_embedding_function,
            persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
        )
        self.collection = self.client.get_or_create_collection(collection_name)

    def _load_api_key(self) -> None:
        """
        Loads the OpenAI API key from environment variables using dotenv.
        """
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set it in your environment.")

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.

        Parameters
        ----------
        documents : List[Document]
            A list of documents to be added to the vector store.

        Returns
        -------
        List[str]
            A list of unique IDs assigned to the added documents.
        """
        uuids = [str(uuid4()) for _ in documents]
        self.vector_store.add_documents(documents=documents, ids=uuids)
        return uuids

    def update_document(self, document_id: str, document: Document) -> None:
        """
        Update a single document in the vector store.

        Parameters
        ----------
        document_id : str
            The ID of the document to update.
        document : Document
            The updated document content.
        """
        self.vector_store.update_document(document_id=document_id, document=document)

    def update_documents(self, ids: List[str], documents: List[Document]) -> None:
        """
        Update multiple documents in the vector store.

        Parameters
        ----------
        ids : List[str]
            A list of IDs corresponding to the documents to be updated.
        documents : List[Document]
            A list of updated documents.
        """
        self.vector_store.update_documents(ids=ids, documents=documents)

    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Delete a List of documents from the vector store.

        Parameters
        ----------
        document_id : str
            The ID of the document to delete.
        """
        self.vector_store.delete(ids=document_ids)

    def similarity_search(
        self, query: str, k: int = 6, filters: Optional[Dict[str, str]] = None
    ) -> List[Document]:
        """
        Perform a similarity search on the vector store.

        Parameters
        ----------
        query : str
            The query string to search against.
        k : int, optional
            The number of top results to return, by default 2.
        filters : Optional[Dict[str, str]], optional
            Filters to apply to the query, by default None.

        Returns
        -------
        List[Document]
            A list of documents matching the query.
        """
        return self.vector_store.similarity_search(query, k=k, filter=filters)

    def similarity_search_with_score(
        self, query: str, k: int = 1
    ) -> List[Dict[str, float]]:
        """
        Perform a similarity search and return results with scores.

        Parameters
        ----------
        query : str
            The query string to search against.
        k : int, optional
            The number of top results to return, by default 1.

        Returns
        -------
        List[Dict[str, float]]
            A list of dictionaries containing documents and their similarity scores.
        """
        results_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        return [{"document": res, "score": score} for res, score in results_with_scores]

    def get_documents_by_id(self, ids: List[str]) -> List[Document]:
        """
        Fetch documents from the vector store by their unique IDs.

        Parameters
        ----------
        ids : List[str]
        A list of unique IDs to retrieve documents.

        Returns
        -------
        List[Document]
        A list of documents corresponding to the given IDs.
        """
        return self.vector_store.get(ids)

