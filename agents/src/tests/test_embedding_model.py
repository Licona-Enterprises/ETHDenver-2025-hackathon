import os
import pytest
import tempfile
from unittest.mock import patch
from config.config import GeneratedTradesFilePaths, KnowledgeBaseFilePaths, OpenAiConsts
from rag.embedding_model import EmbeddingModel

@pytest.fixture
def setup_environment():
    """Set up temporary environment variables and file paths."""
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as trade_file, \
         tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as response_file:
        
        # Write mock JSON content to files
        trade_file.write('{"trading_strategy": [{"name": "strategy1"}, {"name": "strategy2"}]}')
        response_file.write('[{"response": "This is a mock response."}]')
        trade_file.close()
        response_file.close()

        # Mock environment variable for OpenAI API key
        os.environ["OPENAI_API_KEY"] = "test_api_key_12345"

        # Mock config paths
        with patch.object(GeneratedTradesFilePaths, "get_generated_trades_file_paths", return_value=[trade_file.name]), \
             patch.object(KnowledgeBaseFilePaths, "get_knowledge_base_json_file_paths", return_value=[response_file.name]):
            
            yield trade_file.name, response_file.name
        
        # Clean up temp files
        os.remove(trade_file.name)
        os.remove(response_file.name)
        del os.environ["OPENAI_API_KEY"]

def test_embedding_model_integration(setup_environment):
    """Integration test for EmbeddingModel class."""
    trade_file, response_file = setup_environment

    # Initialize the EmbeddingModel
    model = EmbeddingModel()
    
    # Verify API key is loaded
    assert model.api_key == "test_api_key_12345"
    
    # Mock trade data generation
    trade_data = model.mock_trade_generator()
    assert trade_data == {"trading_strategy": [{"name": "strategy1"}, {"name": "strategy2"}]}

    # Mock response data generation
    response_data = model.mock_response_generator()
    assert response_data == [{"response": "This is a mock response."}]

    # Load trade details from JSON
    trade_details = model.load_trade_details_json()
    assert len(trade_details) == 2  # Two strategies in the mock JSON
    
    # Split JSON data
    docs = model.split_json(trade_data)
    assert len(docs) > 0  # Verify documents were created

    # Split multiple JSONs
    all_docs = model.split_multiple_json(response_data, metadata_source="test_source")
    assert len(all_docs) > 0  # Verify documents were created

    # Generate embeddings with Chroma (mocked)
    with patch("langchain_chroma.Chroma.add_documents", return_value=["doc1", "doc2"]), \
         patch("langchain_openai.OpenAIEmbeddings.embed_query", return_value=[0.1, 0.2, 0.3, 0.4, 0.5]):
        
        model.generate_embeddings_chroma(all_docs)
        assert len(model.splits) == len(all_docs)  # Verify splits match input
