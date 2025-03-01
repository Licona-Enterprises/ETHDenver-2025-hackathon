# local set up instructions:
### 1. pip install -r requirements.txt
### 2. export OPENAI_API_KEY = <you-api-key>


# Docker build instructions
### 1. While in the agent47/twitter-agent folder, run in terminal:
  #### docker system prune -f
  #### docker build --progress=plain --no-cache -t twitter-agent .
  #### docker run -e OPENAI_API_KEY="your-openai-api-key" -p 8000:8000 twitter-agent


# Uniswap agent tools

## **PoolManagerClient - Uniswap v4 Pool Initialization**
The `PoolManagerClient` is a Python-based Web3 client designed for interacting with a Uniswap v4 Pool Manager contract. It allows users to **dynamically initialize new liquidity pools** by specifying token pairs, fee tiers, tick spacing, and other parameters.


## **📌 Features**
✅ **Connect to Ethereum via Web3**  
✅ **Initialize new Uniswap v4 liquidity pools**  
✅ **Handles transaction signing and broadcasting**  
✅ **Supports EIP-1559 gas pricing**  
✅ **Parses `Initialize` event to extract the initial tick value**  


### **1️⃣ Import the PoolManagerClient Class**
```python
from pool_manager_client import PoolManagerClient
```

### **2️⃣ Initialize the Client**
```python
client = PoolManagerClient(
    rpc_url="https://your_rpc_provider_url",
    private_key="0xYourPrivateKey",
    pool_manager_address="0xYourPoolManagerAddress",
    pool_manager_abi_path="path/to/your_pool_manager_abi.json",
)
```

### **3️⃣ Initialize a New Pool**
Call the `initialize_pool` function with dynamic parameters:

```python
receipt = client.initialize_pool(
    currency0="0xToken0Address",
    currency1="0xToken1Address",
    fee=3000,  # Uniswap fee tier (0.3%)
    tick_spacing=60,  # Tick spacing for liquidity range
    hooks="0xHookAddress",  # Custom hook contract
    sqrt_price_x96=79228162514264337593543950336,  # Initial price ratio (1:1)
)
```

### **4️⃣ Check Transaction Status**
```python
print(f"Transaction Hash: {receipt['transactionHash'].hex()}")
print(f"Block Number: {receipt['blockNumber']}")
if 'tick' in receipt:
    print(f"Pool initialized at tick: {receipt['tick']}")
```


## **🔍 Understanding Pool Initialization**
### **Pool Parameters**
| Parameter         | Description                                         |
|------------------|-----------------------------------------------------|
| `currency0`      | Address of the first token in the pool. Must be lower than `currency1`. |
| `currency1`      | Address of the second token in the pool. Must be higher than `currency0`. |
| `fee`           | Fee tier (e.g., `3000` for 0.3%). |
| `tick_spacing`  | Tick spacing for the liquidity pool (e.g., `60`). |
| `hooks`         | Address of the hook contract for custom logic. |
| `sqrt_price_x96` | Initial price (in **square root X96 format**). |



## **🛠 Additional Features**
### **✅ ERC-20 Approval (Before Pool Initialization)**
Before initializing a pool, you may need to **approve the Pool Manager contract** to manage your tokens.  

```python
erc20_token = client.web3.eth.contract(address="0xToken0Address", abi=ERC20_ABI)

approve_txn = erc20_token.functions.approve(
    "0xYourPoolManagerAddress",  # Pool Manager contract
    Web3.to_wei(10, "ether")  # Approval amount
).build_transaction({
    "from": client.account.address,
    "nonce": client.web3.eth.get_transaction_count(client.account.address),
    "gas": 100000,
    "gasPrice": client.web3.eth.gas_price
})

signed_approve_txn = client.web3.eth.account.sign_transaction(approve_txn, client.private_key)
tx_hash = client.web3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)
print(f"Approval transaction sent: {tx_hash.hex()}")
```


## **📝 Notes**
- Make sure **currency0 < currency1** (token addresses should be ordered correctly).
- The `sqrt_price_x96` value represents the **initial price of token0 relative to token1**.
- Transactions use **EIP-1559 gas pricing** for optimal fee estimation.
- Always confirm the **gas limits** before broadcasting a transaction.
---


## **AgentLPClient - Uniswap v4 Liquidity Minting**
The `AgentLPClient` is a Python Web3-based client that interacts with a **custom Uniswap v4 liquidity minting contract**. It enables AI-driven liquidity provisioning by dynamically minting LP positions using Uniswap v4's `IPositionManager`.  

## **📌 Features**
✅ **Mint Uniswap v4 LP positions programmatically**  
✅ **Specify token pairs, fee tiers, and tick spacing**  
✅ **Handles transaction signing and submission**  
✅ **Supports dynamic configuration for multiple pools**  
✅ **Seamless interaction with on-chain liquidity**  



### **1️⃣ Import the `AgentLPClient` Class**
```python
from agent_lp_client import AgentLPClient
```

### **2️⃣ Initialize the Client**
```python
client = AgentLPClient(
    rpc_url="https://unichain-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY",
    private_key="0xYourPrivateKey",
    contract_address="0xYourDebugLPContract",
    abi_path="path/to/agent_47_lp_abi.json",
)
```

### **3️⃣ Mint a New LP Position**
Call the `mint_lp` function with dynamic parameters:

```python
receipt = client.mint_lp(
    token0="0xToken0Address",
    token1="0xToken1Address",
    fee=3000,  # Uniswap fee tier (0.3%)
    tick_spacing=60,  # Tick spacing for liquidity range
    hook_address="0xHookAddress",  # Custom hook contract
    amount0_max=Web3.to_wei(1, "ether"),  # Max token0 liquidity
    amount1_max=Web3.to_wei(1, "ether"),  # Max token1 liquidity
)
```

### **4️⃣ Check Transaction Status**
```python
print(f"Transaction Hash: {receipt['transactionHash'].hex()}")
print(f"Block Number: {receipt['blockNumber']}")
```


## **🔍 Understanding LP Minting**
### **LP Minting Parameters**
| Parameter       | Description |
|----------------|-------------|
| `token0`      | Address of the first token in the LP position. |
| `token1`      | Address of the second token in the LP position. |
| `fee`         | Fee tier for the Uniswap pool (e.g., `3000` for 0.3%). |
| `tick_spacing`| Tick spacing that defines the liquidity range. |
| `hook_address` | Address of the hook contract for custom logic. |
| `amount0_max` | Maximum amount of `token0` to deposit as liquidity. |
| `amount1_max` | Maximum amount of `token1` to deposit as liquidity. |


## **🛠 Additional Features**
### **✅ Approving Token Transfers**
Before calling `mint_lp`, ensure you approve the contract to transfer tokens on your behalf.

```python
erc20_token = client.web3.eth.contract(address="0xToken0Address", abi=ERC20_ABI)

approve_txn = erc20_token.functions.approve(
    client.contract_address,  # LP Contract
    Web3.to_wei(10, "ether")  # Approval amount
).build_transaction({
    "from": client.wallet_address,
    "nonce": client.web3.eth.get_transaction_count(client.wallet_address),
    "gas": 100000,
    "gasPrice": client.web3.eth.gas_price
})

signed_approve_txn = client.web3.eth.account.sign_transaction(approve_txn, client.private_key)
tx_hash = client.web3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)
print(f"Approval transaction sent: {tx_hash.hex()}")
```


## **📝 Notes**
- Ensure that **`token0 < token1`** (addresses must be in the correct order).  
- Adjust `amount0_max` and `amount1_max` based on available balances.  
- Transactions use **EIP-1559 gas pricing** for optimized fees.  
- Verify the Uniswap pool exists before minting LP positions.  

---


# **RAG Pipeline Class**

## **Overview**
The RAG (Retrieval-Augmented Generation) pipeline class is designed to process and retrieve information from structured data (e.g., JSON files), split it into manageable chunks, generate embeddings, and store them for efficient retrieval in AI-driven applications. This pipeline leverages OpenAI embeddings, LangChain tools, and Chroma as a vector database to enable advanced document search and question-answering workflows.

---

## **Features**
1. **Document Loading**:
   - Loads JSON-formatted data files containing trade strategies and knowledge base information.
   - Parses and extracts relevant data using a schema (`jq_schema`).

2. **Text Splitting**:
   - Splits JSON documents into smaller, manageable text chunks using the `RecursiveJsonSplitter` from LangChain.
   - Supports splitting both single and multiple JSON documents for modular processing.

3. **Embedding Generation**:
   - Creates dense vector embeddings for the text chunks using OpenAI's embedding model.
   - Stores the embeddings in a persistent Chroma database for fast and efficient similarity searches.

4. **Retry Mechanism and Validation**:
   - Ensures that embeddings and splits are valid.
   - Provides mechanisms to validate processed data and regenerate embeddings if needed.

5. **Integration**:
   - Integrates with OpenAI's API for embedding generation.
   - Uses `dotenv` for secure API key management.
   - Offers modularity to extend the pipeline for other retrieval-based AI use cases.

---

## **Usage**

### **1. Initialization**
To initialize the RAG pipeline class:
```python
from pipeline import EmbeddingModel

rag_pipeline = EmbeddingModel()
```

### **2. Loading JSON Data**
The pipeline supports loading trade and response data from JSON files:
- **Load Trades**:
   ```python
   trades = rag_pipeline.load_trade_details_json()
   print(trades)
   ```

- **Load Responses**:
   ```python
   responses = rag_pipeline.response_generator()
   print(responses)
   ```

### **3. Splitting JSON Data**
- **Single JSON File**:
   ```python
   docs = rag_pipeline.split_json(json_data)
   ```

- **Multiple JSON Files**:
   ```python
   docs = rag_pipeline.split_multiple_json(json_data_list)
   ```

### **4. Generating Embeddings**
Embeddings can be generated and stored in Chroma:
```python
rag_pipeline.generate_embeddings_chroma(docs)
```

---

## **Pipeline Components**

### **1. Document Loading**
The `load_trade_details_json` and `response_generator` methods handle loading JSON files. These methods:
- Extract data based on a predefined schema (`jq_schema`).
- Validate file paths and ensure proper JSON formatting.

### **2. Text Splitting**
The `split_json` and `split_multiple_json` methods:
- Break down large JSON files into smaller chunks to enhance embedding accuracy.
- Use the `RecursiveJsonSplitter` to maintain semantic coherence in splits.
- Return smaller document objects ready for embedding.

### **3. Embedding Generation**
The `generate_embeddings_chroma` method:
- Utilizes OpenAI embeddings to create dense vector representations of text chunks.
- Stores embeddings in a persistent Chroma vector store for future retrieval.
- Offers diagnostic information, such as embedding previews.

Example Output:
```plaintext
Vector Preview (First 5 dimensions):
Document: "Example text content..."
Vector (First 5 elements): [0.123, 0.456, 0.789, ...]
```

---

## **Error Handling**
1. **API Key Validation**:
   - Ensures the OpenAI API key is correctly loaded from environment variables.
   - Throws an error if the key is missing or invalid.

2. **File Path Validation**:
   - Confirms all JSON files exist before attempting to load them.
   - Provides detailed error messages for missing files or invalid JSON.

3. **Data Validation**:
   - Checks that documents have been split before generating embeddings.
   - Validates input data for all major operations.

---

## **Technical Stack**
- **Embedding Generation**: OpenAI embeddings (via `langchain_openai.OpenAIEmbeddings`).
- **Vector Storage**: Chroma (persistent vector database).
- **Text Splitting**: LangChain `RecursiveJsonSplitter`.
- **Document Loading**: LangChain `JSONLoader`.
- **Environment Management**: `dotenv` for OpenAI API key handling.

---

## **Example Workflow**
### **1. Load Data**
```python
json_data = rag_pipeline.response_generator()
```

### **2. Split Data**
```python
split_docs = rag_pipeline.split_multiple_json(json_data)
```

### **3. Generate and Store Embeddings**
```python
rag_pipeline.generate_embeddings_chroma(split_docs)
```


# TweetGenerator

## Overview  
The `TweetGenerator` class manages the integration of Chroma's vector store, OpenAI's Chat model, and document-based stateful processing. It is designed to retrieve relevant documents, generate meaningful responses, and interact with Twitter to post tweets and comments. This functionality makes it ideal for applications that require AI-driven content generation with contextual relevance.  

---

## Features  
- **OpenAI Integration**: Uses OpenAI's Chat model for generating tweets and responses.  
- **Chroma Vector Store**: Leverages document embeddings for similarity search and context-based generation.  
- **Twitter Automation**: Posts tweets and comments directly to Twitter via the Twitter API.  
- **Document Retrieval**: Retrieves and samples documents from a vector store for context-based processing.  
- **Content Similarity Checking**: Ensures generated content is unique and avoids redundancy by checking cosine similarity with existing tweets.  

---

## Usage  

### Initialization  
Create an instance of the `TweetGenerator` by providing the Chroma vector store collection name:  
```python
from tweet_generator import TweetGenerator

generator = TweetGenerator(collection_name="my_collection")
```  

---

### Methods  

#### `_load_api_key()`  
Loads the OpenAI API key from environment variables.  

#### `retrieve(query: str) -> List[Document]`  
Retrieves documents from the Chroma vector store based on a similarity search.  

- **Parameters**:  
  - `query`: A string query for similarity search.  
- **Returns**:  
  A list of documents matching the query.  

#### `generate(question: str, context: List[Document]) -> str`  
Generates a response to a given question using the provided context.  

- **Parameters**:  
  - `question`: The user's question to answer.  
  - `context`: A list of documents for context.  
- **Returns**:  
  A string containing the generated response.  

#### `sample_documents(query: str, num_docs: int = 10) -> List[Document]`  
Fetches a sample of documents from the knowledge base.  

- **Parameters**:  
  - `query`: Query to search the vector store.  
  - `num_docs`: The number of documents to sample (default is 10).  
- **Returns**:  
  A randomly selected list of documents.  

#### `create_tweet() -> str`  
Generates and posts a tweet based on retrieved context.  

- **Returns**:  
  The generated tweet content as a string.  

#### `create_comment(content: str, tweet_id: str) -> str`  
Generates and posts a comment on a specific tweet.  

- **Parameters**:  
  - `content`: The content of the comment.  
  - `tweet_id`: The ID of the tweet to comment on.  
- **Returns**:  
  The generated comment content as a string.  

#### `_calculate_similarity(text1: str, text2: str) -> float`  
Calculates the cosine similarity between two text strings using embeddings.  

- **Parameters**:  
  - `text1`: The first text string.  
  - `text2`: The second text string.  
- **Returns**:  
  A float representing the cosine similarity score.  

---

### Example Usage  

#### Posting a Tweet  
```python
tweet_content = generator.create_tweet()
print(f"Generated tweet: {tweet_content}")
```  

#### Commenting on a Tweet  
```python
tweet_id = "1234567890"
comment_content = "What do you think about AI in trading?"
response = generator.create_comment(content=comment_content, tweet_id=tweet_id)
print(f"Comment posted: {response}")
```  

---

## Error Handling  

- Raises a `ValueError` if the OpenAI API key is not found in the environment.  
- Raises a `RuntimeError` if a valid, unique response cannot be generated within the allowed number of retries.  

---
