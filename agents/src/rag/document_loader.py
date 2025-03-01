import os
from typing import List, Any, Optional
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from config.config import HubPull
from config.config import KnowledgeBaseFilePaths
from config.config import OpenAiConsts


class RagDocumentLoader:
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
        Initializes the RagDocumentLoader class with paths to multiple PDF files.
        """
        knowledge_base = KnowledgeBaseFilePaths()
        self.file_paths: List[str] = knowledge_base.get_knowledge_base_pdf_file_paths()
        self.open_ai_consts = OpenAiConsts()
        self.agent_info = HubPull()
        self.embedding_model = self.open_ai_consts.DEFAULT_EMBEDDING_MODEL
        self.docs: List[Any] = []
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

    # TODO support more file types(JSON, txt, csv)
    def load_pdfs(self) -> None:
        """
        Loads multiple PDF documents using PyPDFLoader.

        Raises
        ------
        FileNotFoundError
            If any of the PDF files do not exist at the specified paths.
        """
        for file_path in self.file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found at path: {file_path}")
            loader = PyPDFLoader(file_path)
            self.docs.extend(loader.load())
        print(f"Loaded {len(self.docs)} document(s) from {len(self.file_paths)} file(s). \n")

    def split_documents(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """
        Splits the loaded documents into smaller chunks.

        Parameters
        ----------
        chunk_size : int, optional
            The maximum size of each text chunk (default is 1000).
        chunk_overlap : int, optional
            The overlap size between chunks (default is 200).
        """
        if not self.docs:
            raise ValueError("No documents loaded. Please load PDFs first.")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )
        self.splits = text_splitter.split_documents(self.docs)
        print(f"Split documents into {len(self.splits)} chunks. \n")

    def generate_embeddings_in_memory(self) -> None:
        """
        Generates embeddings for the text chunks using OpenAI embeddings.
        """
        if not self.splits:
            raise ValueError("No text splits found. Please split the documents first.")
        embeddings = OpenAIEmbeddings(model=self.embedding_model)
        self.vector_store = InMemoryVectorStore(embeddings)
        ids = self.vector_store.add_documents(documents=self.splits)
        print(f"Generated and stored embeddings for {len(ids)} documents. \n")

        # for dev sanity - print vector previews
        first_document_content = self.splits[0].page_content
        first_vector = embeddings.embed_query(first_document_content)
        
        print("Vector Preview (First 5 dimensions):")
        print(f"Document: {first_document_content[:100]}...")
        print(f"Vector (First 5 elements): {first_vector[:5]}\n \n")

    def generate_embeddings_chroma(self) -> None:
        """
        Generates embeddings for the text chunks using OpenAI embeddings.
        The OpenAI model to use for embeddings (default is found at DEFAULT_EMBEDDING_MODEL).
        """
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

    def search(self, query: str, top_k: int = 1) -> List[Any]:
        """
        Searches the vector store for the most similar documents to the query.

        Parameters
        ----------
        query : str
            The query to search for.
        top_k : int, optional
            The number of top results to return (default is 1).

        Returns
        -------
        List[Any]
            A list of the top matching documents.
        """
        if not self.vector_store:
            raise ValueError("Vector store is not initialized. Please generate embeddings first.")
        results = self.vector_store.similarity_search(query, k=top_k)
        return results
