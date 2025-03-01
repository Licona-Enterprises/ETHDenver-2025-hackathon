from web3 import Web3
import json
from typing import Any


class AgentLPClient:
    """
    A client for interacting with the DebugLPContract on Uniswap v4.

    This class allows users to dynamically configure parameters for minting LP positions
    using Uniswap v4 via the `agentMintLp` function.

    Parameters
    ----------
    rpc_url : str
        Ethereum JSON-RPC URL (e.g., from Alchemy or Infura).
    private_key : str
        Wallet private key for signing transactions.
    contract_address : str
        Address of the deployed DebugLPContract.
    path_to_abi : str
        Path to the ABI file for the DebugLPContract.

    Attributes
    ----------
    web3 : Web3
        Web3 instance for interacting with the blockchain.
    contract : Any
        Web3 contract instance loaded from the provided ABI.
    wallet_address : str
        The Ethereum address derived from the provided private key.
    """

    def __init__(self, rpc_url: str, private_key: str, contract_address: str, path_to_abi: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.web3.is_connected(), "Failed to connect to blockchain"

        self.private_key = private_key
        self.wallet_address = self.web3.eth.account.from_key(private_key).address

        # Load contract ABI
        with open(path_to_abi, "r") as f:
            contract_abi = json.load(f)

        # Initialize contract
        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)

    def mint_lp(
        self,
        token0_address: str,
        token1_address: str,
        fee_tier: int,
        tick_spacing: int,
        hook_address: str,
        amount0_max: int,
        amount1_max: int
    ) -> str:
        """
        Calls the `agentMintLp` function to mint a new LP position.

        Parameters
        ----------
        token0_address : str
            Address of token0.
        token1_address : str
            Address of token1.
        fee_tier : int
            The Uniswap fee tier (e.g., 3000 for 0.3%).
        tick_spacing : int
            Tick spacing for the liquidity pool.
        hook_address : str
            Address of the hook contract.
        amount0_max : int
            Maximum amount of token0 to deposit (in wei).
        amount1_max : int
            Maximum amount of token1 to deposit (in wei).

        Returns
        -------
        str
            Transaction hash of the submitted transaction.
        """
        nonce = self.web3.eth.get_transaction_count(self.wallet_address)
        gas_price = self.web3.eth.gas_price

        tx_data = self.contract.functions.agentMintLp(
            token0_address, token1_address, fee_tier, tick_spacing, hook_address, amount0_max, amount1_max
        ).build_transaction({
            "from": self.wallet_address,
            "nonce": nonce,
            "gas": 3000000,  # Adjust as necessary
            "gasPrice": gas_price,
        })

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(tx_data, self.private_key)

        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent! Hash: {tx_hash.hex()}")

        # Wait for confirmation
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed! Block: {receipt.blockNumber}")

        return tx_hash.hex()
