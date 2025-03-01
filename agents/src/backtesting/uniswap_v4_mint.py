from web3 import Web3
from eth_account import Account
import json

# Configuration
RPC_URL = "https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ"
PRIVATE_KEY = "0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93"
POSITION_MANAGER_ADDRESS = "0xf969Aee60879C54bAAed9F3eD26147Db216Fd664"
TOKEN_0 = "0xd1Ea20F1fDeb55aE3F1Fa0aFba67e5fDBbf266a3"
TOKEN_1 = "0xFc805F9e0Bd4Dd73E13aE662cFC4e3B752147255"
FEE_TIER = 3000
AMOUNT_0 = Web3.to_wei(1, 'ether')
AMOUNT_1 = Web3.to_wei(1, 'ether')
POSITION_MANAGER_ABI_FILE_PATH = "/Users/Alejandro_Licona/Downloads/agent-47/twitter-agent/src/backtesting/position_manager_abi.json"
ERC20_ABI = '[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

HOOK_ADDRESS = "0x5566Dd8a550C05a75e9cb980DA61B9dDAF1E8AC0"
TICK_LOWER = 6
TICK_UPPER = 6
LIQUIDITY = Web3.to_wei(1, 'ether')
AMOUNT_0_MAX = Web3.to_wei(1000, 'ether')
AMOUNT_1_MAX = Web3.to_wei(1000, 'ether')
DEADLINE = int(Web3(Web3.HTTPProvider(RPC_URL)).eth.get_block('latest')['timestamp']) + 60
HOOK_DATA = b''

# Initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)

# Load ABI for Position Manager
with open(POSITION_MANAGER_ABI_FILE_PATH, "r") as f:
    POSITION_MANAGER_ABI = json.load(f)

position_manager = w3.eth.contract(address=POSITION_MANAGER_ADDRESS, abi=POSITION_MANAGER_ABI)
erc20_token_0 = w3.eth.contract(address=TOKEN_0, abi=json.loads(ERC20_ABI))
erc20_token_1 = w3.eth.contract(address=TOKEN_1, abi=json.loads(ERC20_ABI))

# Approve PositionManager to spend tokens
def approve_token(token_contract, amount, token_symbol):
    approve_txn = token_contract.functions.approve(POSITION_MANAGER_ADDRESS, amount).build_transaction({
        'from': account.address,
        'gas': 100000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })
    
    signed_txn = w3.eth.account.sign_transaction(approve_txn, private_key=PRIVATE_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Approval Transaction for {token_symbol} sent: {txn_hash.hex()}")

# Approve both tokens
approve_token(erc20_token_0, AMOUNT_0_MAX, "TOKEN_0")
approve_token(erc20_token_1, AMOUNT_1_MAX, "TOKEN_1")

# Encode PoolKey
pool_key = [TOKEN_0, TOKEN_1, FEE_TIER, 60, HOOK_ADDRESS]
encoded_pool_key = Web3.to_hex(w3.codec.encode(['address', 'address', 'uint24', 'uint8', 'address'], pool_key))
print(f"Encoded PoolKey: {encoded_pool_key}")

# Encode actions
MINT_POSITION = 0x02
SETTLE_PAIR = 0x0d
actions = Web3.to_hex(w3.codec.encode(['uint8', 'uint8'], [MINT_POSITION, SETTLE_PAIR]))
print(f"Encoded Actions: {actions}")

# Encode parameters
encoded_params_0 = Web3.to_hex(w3.codec.encode(
    ['bytes', 'int24', 'int24', 'uint256', 'uint128', 'uint128', 'address', 'bytes'],
    [encoded_pool_key, TICK_LOWER, TICK_UPPER, LIQUIDITY, AMOUNT_0_MAX, AMOUNT_1_MAX, account.address, HOOK_DATA]
))
print(f"Encoded Params[0]: {encoded_params_0}")

encoded_params_1 = Web3.to_hex(w3.codec.encode(
    ['address', 'address'],
    [TOKEN_0, TOKEN_1]
))
print(f"Encoded Params[1]: {encoded_params_1}")

params = [encoded_params_0, encoded_params_1]

# Define modifyLiquidities transaction
modify_txn = position_manager.functions.modifyLiquidities(
    Web3.to_hex(w3.codec.encode(['bytes', 'bytes[]'], [actions, params])),
    DEADLINE
).build_transaction({
    'from': account.address,
    'gas': 300000,
    'gasPrice': w3.to_wei('10', 'gwei'),
    # 'nonce': w3.eth.get_transaction_count(account.address) + 2  # Incrementing for pending approvals
    'nonce': nonce

})

print(f"Encoded Transaction Data: {Web3.to_hex(w3.codec.encode(['bytes', 'bytes[]'], [actions, params]))}")
print(f"DEADLINE: {DEADLINE}")

# Sign and send transaction
signed_txn = w3.eth.account.sign_transaction(modify_txn, private_key=PRIVATE_KEY)
txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction sent: {txn_hash.hex()}")
