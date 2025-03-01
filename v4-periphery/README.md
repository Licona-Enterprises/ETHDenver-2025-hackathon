# Uniswap v4 Periphery

Uniswap v4 is a new automated market maker protocol that provides extensibility and customizability to pools. `v4-periphery` hosts the logic that builds on top of the core pool logic like hook contracts, position managers, and even possibly libraries needed for integrations. The `v4-periphery` contracts in this repository are still in development and further periphery contracts have not yet been built.

## Local Deployment and Usage

install forge:

```solidity
forge install https://github.com/Uniswap/v4-periphery
```

Creating hooks example:

```solidity

import {BaseHook} from 'v4-periphery/src/utils/BaseHook.sol';

contract CoolHook is BaseHook {
    // Override the hook callbacks you want on your hook
    function beforeAddLiquidity(
        address,
        IPoolManager.PoolKey calldata key,
        IPoolManager.ModifyLiquidityParams calldata params
    ) external override onlyByManager returns (bytes4) {
        // hook logic
        return BaseHook.beforeAddLiquidity.selector;
    }
}

```

## Deploy contract and run scripts in this repo

source ~/.bashrc

```sh
forge build
```

devs can deploy new tokens for testing using the TestnetTokenERC20.sol contract 

Test USDC deploy at 0xC7f2Cf4845C6db0e1a1e91ED41Bcd0FcC1b0E141

example commands to deploy contracts and run forge scripts
```sh
forge create src/hooks/Agent47Lp.sol:Agent47Lp \
  --rpc-url https://unichain-sepolia.g.alchemy.com/v2/<alchemy-api-key>> \
  --private-key <private_key> \
  --broadcast
```

```sh
forge script /script/DeployHook.s.sol:DeployHookScript \
    --rpc-url https://unichain-sepolia.g.alchemy.com/v2/<alchemy-api-key> \
    --private-key <private_key> \
    --broadcast
```