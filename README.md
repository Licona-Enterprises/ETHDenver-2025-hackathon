# ETHDenver-2025-hackathon

Agent 47 is an AI agent platform that allows users to create agents that can create actively managed portfolios, swap tokens on Uniswap v4, and interact with other on X

# **Agent47Lp - Web3.py & Alloy.rs Integration Guide**  

## **📌 Overview**  
The `Agent47Lp` smart contract allows AI agents to **provide liquidity on Uniswap v4**. It interacts with **Uniswap's `IPositionManager`** and supports **dynamic pool configurations**.  

This guide explains how to interact with the contract using **Web3.py (Python)** and **Alloy.rs (Rust)**.  

---

## **🛠 Prerequisites**  
Before interacting with the contract, ensure you have:  

✅ **Python 3.8+** installed  
✅ **Rust and Cargo** installed for Alloy.rs  
✅ **Web3.py and dependencies** installed (`pip install web3 eth-account`)  
✅ **Alloy.rs setup** (`cargo add alloy`)  

---

# **🔹 Using Web3.py (Python)**
### **1️⃣ Install Dependencies**  
First, install **Web3.py** and dependencies:  

```sh
pip install web3 eth-account
```

### **2️⃣ Initialize Web3 Connection**  
Connect to the **Unichain Sepolia** testnet via Alchemy:  

```python
from web3 import Web3
import json

RPC_URL = "https://unichain-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
PRIVATE_KEY = "0xYourPrivateKey"
CONTRACT_ADDRESS = "0xYourContractAddress"

# Load ABI
with open("path/to/Agent47Lp_abi.json") as f:
    contract_abi = json.load(f)

# Connect to Web3 provider
web3 = Web3(Web3.HTTPProvider(RPC_URL))
assert web3.is_connected(), "Failed to connect to blockchain"

# Load contract
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
wallet_address = web3.eth.account.from_key(PRIVATE_KEY).address
```

---

### **3️⃣ Mint Liquidity Using `agentMintLp`**  
This function deposits tokens into the **Uniswap v4** pool with a **1% fee deduction**.

```python
TOKEN0 = "0xToken0Address"
TOKEN1 = "0xToken1Address"
FEE_TIER = 3000
TICK_SPACING = 60
HOOK_ADDRESS = "0xHookContract"
AMOUNT0 = Web3.to_wei(1, "ether")
AMOUNT1 = Web3.to_wei(1, "ether")

tx_data = contract.functions.agentMintLp(
    TOKEN0, TOKEN1, FEE_TIER, TICK_SPACING, HOOK_ADDRESS, AMOUNT0, AMOUNT1
).build_transaction({
    "from": wallet_address,
    "nonce": web3.eth.get_transaction_count(wallet_address),
    "gas": 3000000,
    "gasPrice": web3.eth.gas_price,
})

# Sign and send transaction
signed_tx = web3.eth.account.sign_transaction(tx_data, PRIVATE_KEY)
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Transaction sent: {tx_hash.hex()}")

# Wait for confirmation
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Confirmed in block: {receipt.blockNumber}")
```

---

### **4️⃣ Read Contract Events**
To listen for **`LPOrderRouted`** events:  

```python
event_filter = contract.events.LPOrderRouted.create_filter(fromBlock="latest")

while True:
    for event in event_filter.get_new_entries():
        print(f"LP Order Routed: {event['args']}")
```

---

# **🔹 Using Alloy.rs (Rust)**  
Alloy.rs is a high-performance Rust library for **Ethereum interactions**.  

### **1️⃣ Install Dependencies**
Add `alloy` to your Rust project:  

```sh
cargo add alloy
```

---

### **2️⃣ Define the ABI Interface**
Save your contract ABI as `agent47lp_abi.json`, then use **Alloy Bindgen** to generate Rust bindings:

```sh
alloy bindgen -f path/to/Agent47Lp_abi.json -o src/agent47lp.rs
```

This will generate a Rust module for your contract.

---

### **3️⃣ Connect to the Blockchain**
Use **Alloy.rs** to initialize a connection:

```rust
use alloy_provider::ProviderBuilder;
use alloy_signer::wallet::LocalWallet;
use alloy_sol_types::sol;
use std::sync::Arc;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let provider = ProviderBuilder::new()
        .with_http("https://unichain-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY")
        .build()?;

    let wallet = "0xYourPrivateKey".parse::<LocalWallet>()?;
    let provider = Arc::new(provider.with_signer(wallet));

    println!("Connected to blockchain!");
    Ok(())
}
```

---

### **4️⃣ Call `agentMintLp`**
Mint liquidity by encoding the function call:

```rust
use alloy_rpc_types::TransactionRequest;
use alloy_primitives::U256;
use alloy_transport::Http;

async fn mint_lp() -> anyhow::Result<()> {
    let provider = ProviderBuilder::<Http>::new()
        .with_http("https://unichain-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY")
        .build()?;

    let wallet = "0xYourPrivateKey".parse::<LocalWallet>()?;
    let provider = Arc::new(provider.with_signer(wallet));

    let contract_address = "0xYourContractAddress".parse::<Address>()?;

    let tx = TransactionRequest::new()
        .to(contract_address)
        .gas(3_000_000)
        .value(U256::from(0))
        .input(encode_function_call(
            "agentMintLp",
            (
                "0xToken0Address".parse::<Address>()?,
                "0xToken1Address".parse::<Address>()?,
                U256::from(3000),
                U256::from(60),
                "0xHookContract".parse::<Address>()?,
                U256::from(1e18 as u128),
                U256::from(1e18 as u128),
            ),
        )?);

    let pending_tx = provider.send_transaction(tx).await?;
    let receipt = pending_tx.confirmations(1).await?;
    
    println!("Transaction confirmed: {:?}", receipt);
    Ok(())
}
```

---

## **📜 Contract Events in Rust**
To listen for **`LPOrderRouted`**:

```rust
let event_filter = agent47lp::events::LPOrderRouted::new()
    .from_block("latest");

loop {
    if let Some(events) = provider.get_logs(&event_filter).await? {
        for event in events {
            println!("LP Order Routed: {:?}", event);
        }
    }
}
```

This guide ensures users can interact with **Agent47Lp** using **Python (Web3.py)** and **Rust (Alloy.rs)**. 