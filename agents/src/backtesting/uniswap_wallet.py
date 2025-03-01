from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.signers.local import LocalAccount
import json
from typing import Optional

from config.config import UniswapWallet

class WalletManager:
    """
    A class to handle wallet management, token approvals, and swapping tokens on Uniswap V4.

    Attributes
    ----------
    web3 : Web3
        A Web3 instance connected to an Ethereum-compatible network.
    account : LocalAccount
        The wallet account used for transactions.
    uniswap_router : str
        The Uniswap V4 router contract address.
    """

    def __init__(self, uniswap_router: str, uniswap_wallet: UniswapWallet) -> None:
        """
        Initializes the WalletManager with a private key and Web3 connection.

        Parameters
        ----------
        rpc_url : str
            The RPC URL of the Ethereum-compatible network.
        private_key : str
            The private key of the wallet to sign transactions.
        uniswap_router : str
            The Uniswap V4 router contract address.
        """
        agent_wallet = uniswap_wallet
        rpc_url = agent_wallet.UNICHAIN_SEPOLIA_RPC
        private_key = agent_wallet.DEV_PRIVATE_KEY

        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError("Web3 connection failed. Check RPC URL.")
        
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Required for some chains (Polygon, BSC, etc.)
        
        self.account: LocalAccount = self.web3.eth.account.from_key(private_key)
        self.uniswap_router: str = Web3.to_checksum_address(uniswap_router)

    def approve_token(self, token_address: str, amount: int) -> str:
        """
        Approves the Uniswap router to spend a specified amount of a given ERC-20 token.

        Parameters
        ----------
        token_address : str
            The ERC-20 token contract address.
        amount : int
            The amount of tokens to approve (in smallest unit, e.g., wei for ETH).

        Returns
        -------
        str
            The transaction hash of the approval transaction.
        """
        token_address = Web3.to_checksum_address(token_address)
        with open("erc20_abi.json") as f:
            erc20_abi = json.load(f)
        
        token_contract = self.web3.eth.contract(address=token_address, abi=erc20_abi)
        
        tx = token_contract.functions.approve(self.uniswap_router, amount).build_transaction({
            "from": self.account.address,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
            "gas": 100000,
            "gasPrice": self.web3.eth.gas_price,
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.web3.to_hex(tx_hash)

    def swap_tokens(
        self, 
        token_in: str, 
        token_out: str, 
        amount_in: int, 
        recipient: Optional[str] = None
    ) -> str:
        """
        Executes a token swap on Uniswap V4.

        Parameters
        ----------
        token_in : str
            The address of the input token.
        token_out : str
            The address of the output token.
        amount_in : int
            The amount of input tokens to swap (in smallest unit).
        recipient : Optional[str], default=None
            The recipient address for the swapped tokens (defaults to the sender).

        Returns
        -------
        str
            The transaction hash of the swap transaction.
        """
        token_in = Web3.to_checksum_address(token_in)
        token_out = Web3.to_checksum_address(token_out)
        recipient = recipient if recipient else self.account.address

        with open("uniswap_v4_router_abi.json") as f:
            router_abi = json.load(f)

        uniswap_router = self.web3.eth.contract(address=self.uniswap_router, abi=router_abi)
        
        # Swap logic - Using Uniswap V4's exactInputSingle
        swap_params = {
            "tokenIn": token_in,
            "tokenOut": token_out,
            "fee": 3000,  # Fee tier (adjustable)
            "recipient": recipient,
            "amountIn": amount_in,
            "amountOutMinimum": 1,  # Can be set dynamically
            "sqrtPriceLimitX96": 0
        }

        tx = uniswap_router.functions.exactInputSingle(swap_params).build_transaction({
            "from": self.account.address,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
            "gas": 250000,
            "gasPrice": self.web3.eth.gas_price,
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.web3.to_hex(tx_hash)

# Example Usage
if __name__ == "__main__":
    
    UNISWAP_V4_ROUTER = "0xAF32fda2e4c44A1b3c431f9dfba3c3b7D3A5a921"  # Example Uniswap V4 Router

    active_agent_wallet = UniswapWallet()

    wallet = WalletManager(uniswap_router=UNISWAP_V4_ROUTER, uniswap_wallet=active_agent_wallet)

    # Approve USDC to Uniswap V4
    USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    AMOUNT_TO_APPROVE = 100 * (10 ** 6)  # 100 USDC (assuming 6 decimals)
    approval_tx = wallet.approve_token(USDC_ADDRESS, AMOUNT_TO_APPROVE)
    print(f"Approval Transaction: {approval_tx}")

    # Swap 100 USDC for WETH
    WETH_ADDRESS = "0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    AMOUNT_TO_SWAP = 100 * (10 ** 6)  # 100 USDC
    swap_tx = wallet.swap_tokens(USDC_ADDRESS, WETH_ADDRESS, AMOUNT_TO_SWAP)
    print(f"Swap Transaction: {swap_tx}")
