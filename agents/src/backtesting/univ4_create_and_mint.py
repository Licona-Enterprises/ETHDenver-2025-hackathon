from web3 import Web3
from eth_account import Account
import json

# Configuration
RPC_URL = "https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ"
PRIVATE_KEY = "0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93"
POSITION_MANAGER_ADDRESS = "0xf969Aee60879C54bAAed9F3eD26147Db216Fd664"
TOKEN_0 = "0xd1Ea20F1fDeb55aE3F1Fa0aFba67e5fDBbf266a3"  # Replace with actual token address
TOKEN_1 = "0xFc805F9e0Bd4Dd73E13aE662cFC4e3B752147255"  # Replace with actual token address
FEE_TIER = 3000  # 0.3% fee tier
AMOUNT_0 = Web3.to_wei(1, 'ether')  # Example amount
AMOUNT_1 = Web3.to_wei(1, 'ether')
POSITION_MANAGER_ABI_FILE_PATH = "/Users/Alejandro_Licona/Downloads/agent-47/twitter-agent/src/backtesting/position_manager_abi.json"
HOOK_ADDRESS = "0x5566Dd8a550C05a75e9cb980DA61B9dDAF1E8AC0"  # Replace with actual hook address if needed
TICK_LOWER = 6
TICK_UPPER = 6
LIQUIDITY = Web3.to_wei(1, 'ether')  # Example liquidity amount
AMOUNT_0_MAX = Web3.to_wei(1000, 'ether')
AMOUNT_1_MAX = Web3.to_wei(1000, 'ether')
DEADLINE = int(Web3(Web3.HTTPProvider(RPC_URL)).eth.get_block('latest')['timestamp']) + 60
HOOK_DATA = b''  # Empty hook data

# Initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)


nonce = w3.eth.get_transaction_count(account.address, 'pending')

print(nonce)

