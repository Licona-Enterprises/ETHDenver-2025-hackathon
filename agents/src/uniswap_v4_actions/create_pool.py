from web3 import Web3
from eth_account import Account
import json
from typing import Dict, Any


class PoolManagerClient:
    """
    A client for interacting with the Uniswap v4 Pool Manager.

    This class allows users to dynamically configure and initialize new liquidity pools.

    Parameters
    ----------
    rpc_url : str
        Ethereum JSON-RPC URL (e.g., from Alchemy or Infura).
    private_key : str
        Wallet private key for signing transactions.
    pool_manager_address : str
        Address of the deployed Pool Manager contract.
    pool_manager_abi_path : str
        Path to the ABI file for the Pool Manager contract.

    Attributes
    ----------
    web3 : Web3
        Web3 instance for interacting with the blockchain.
    pool_manager : Any
        Web3 contract instance loaded from the provided ABI.
    account : Account
        Ethereum account derived from the private key.
    """

    def __init__(self, rpc_url: str, private_key: str, pool_manager_address: str, pool_manager_abi_path: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.web3.is_connected(), "Failed to connect to blockchain"

        self.private_key = private_key
        self.account = Account.from_key(private_key)

        # Load contract ABI
        with open(pool_manager_abi_path, "r") as f:
            pool_manager_abi = json.load(f)

        # Initialize contract
        self.pool_manager = self.web3.eth.contract(address=pool_manager_address, abi=pool_manager_abi)

    def initialize_pool(
        self,
        currency0: str,
        currency1: str,
        fee: int,
        tick_spacing: int,
        hooks: str,
        sqrt_price_x96: int
    ) -> Dict[str, Any]:
        """
        Calls the `initialize` function to create a new liquidity pool.

        Parameters
        ----------
        currency0 : str
            Address of the first token in the pool.
        currency1 : str
            Address of the second token in the pool.
        fee : int
            The Uniswap fee tier (e.g., 3000 for 0.3%).
        tick_spacing : int
            Tick spacing for the liquidity pool.
        hooks : str
            Address of the hook contract.
        sqrt_price_x96 : int
            Square root price (X96 format) for the initial price of the pool.

        Returns
        -------
        Dict[str, Any]
            The transaction receipt.
        """
        pool_key = {
            "currency0": currency0,
            "currency1": currency1,
            "fee": fee,
            "tickSpacing": tick_spacing,
            "hooks": hooks,
        }

        nonce = self.web3.eth.get_transaction_count(self.account.address, "pending")
        gas_price = self.web3.eth.gas_price

        txn = self.pool_manager.functions.initialize(pool_key, sqrt_price_x96).build_transaction({
            "from": self.account.address,
            "nonce": nonce,
            "gas": 3000000,
            "maxPriorityFeePerGas": self.web3.to_wei("2", "gwei"),  # EIP-1559 field
            "maxFeePerGas": self.web3.to_wei("20", "gwei"),         # EIP-1559 field
            "chainId": self.web3.eth.chain_id,
        })

        # Sign transaction
        signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)

        # Send transaction
        txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Pool initialization transaction sent: {txn_hash.hex()}")

        # Wait for receipt
        print("Waiting for transaction receipt...")
        receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash, timeout=300)
        print("Transaction confirmed!")

        # Parse Initialize event if exists
        try:
            initialize_event = self.pool_manager.events.Initialize().processReceipt(receipt)
            if initialize_event:
                tick = initialize_event[0]["args"]["tick"]
                print(f"Pool initialized with tick: {tick}")
                receipt["tick"] = tick  # Append tick to receipt for reference
        except Exception as e:
            print("No Initialize event found or failed to parse:", str(e))

        return receipt
