# Uniswap v4 Periphery

source ~/.bashrc

forge build

Test USDC deploy at 0xC7f2Cf4845C6db0e1a1e91ED41Bcd0FcC1b0E141

forge create src/hooks/Agent47Lp.sol:Agent47Lp \
  --rpc-url https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ \
  --private-key 0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93 \
  --broadcast

forge create src/hooks/DebugLPContract.sol:DebugLPContract \
  --rpc-url https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ \
  --private-key 0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93 \
  --broadcast

forge create src/hooks/TestnetTokenERC20.sol:TestnetTokenERC20 \
  --rpc-url https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ \
  --private-key 0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93 \
  --broadcast


forge create src/hooks/LiquidityManager.sol:LiquidityManager \
  --rpc-url https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ \
  --private-key 0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93 \
  --broadcast

forge script /Users/Alejandro_Licona/Downloads/v4-periphery/script/DeployHook.s.sol:DeployHookScript \
    --rpc-url https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ \
    --private-key 0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93 \
    --broadcast


forge create src/hooks/AgHook1.sol:AgHook1 \
  --rpc-url https://unichain-sepolia.g.alchemy.com/v2/DaboUGjPdJKw2UY-R1TUCrZhV-q30azQ \
  --private-key 0xa014ad6259d79063b5f34b73835751dbb8122986d9a4d7573e6d91731ba8ae93 \
  --constructor-args $(cast abi-encode "constructor(address)" 0x00B036B58a818B1BC34d502D3fE730Db729e62AC) \
  --broadcast




Uniswap v4 is a new automated market maker protocol that provides extensibility and customizability to pools. `v4-periphery` hosts the logic that builds on top of the core pool logic like hook contracts, position managers, and even possibly libraries needed for integrations. The `v4-periphery` contracts in this repository are still in development and further periphery contracts have not yet been built.

## Contributing

If you’re interested in contributing please see the [contribution guidelines](https://github.com/Uniswap/v4-periphery/blob/main/CONTRIBUTING.md)!

## Local Deployment and Usage

To utilize the contracts and deploy to a local testnet, you can install the code in your repo with forge:

```solidity
forge install https://github.com/Uniswap/v4-periphery
```

If you are building hooks, it may be useful to inherit from the `BaseHook` contract:

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

## License

The license for Uniswap V4 Periphery is the GNU General Public License (GPL 2.0), see [LICENSE](https://github.com/Uniswap/v4-periphery/blob/main/LICENSE).
