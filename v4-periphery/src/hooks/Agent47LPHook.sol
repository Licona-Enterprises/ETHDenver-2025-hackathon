// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Currency} from "@uniswap/v4-core/src/types/Currency.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";
import {IHooks} from "@uniswap/v4-core/src/interfaces/IHooks.sol";
import {Actions} from "../libraries/Actions.sol";
import {IPositionManager} from "../interfaces/IPositionManager.sol";



contract Agent47LPHook {
    /// @notice Address of the PositionManager contract.
    address public positionManager;
    IPositionManager public posm = IPositionManager(0xf969Aee60879C54bAAed9F3eD26147Db216Fd664);

    /// @notice Emitted when an LP order is routed.
    event LPOrderRouted(address indexed sender, bytes unlockData, uint256 deadline);

    constructor() {
        positionManager = address(0xf969Aee60879C54bAAed9F3eD26147Db216Fd664);
        testNowLP();
    }

    function testNowLP() internal {
        bytes memory actions = abi.encodePacked(uint8(Actions.MINT_POSITION), uint8(Actions.SETTLE_PAIR));
        bytes[] memory params = new bytes[](2);
        Currency currency0 = Currency.wrap(0xd1Ea20F1fDeb55aE3F1Fa0aFba67e5fDBbf266a3); // tokenAddress0
        Currency currency1 = Currency.wrap(0xFc805F9e0Bd4Dd73E13aE662cFC4e3B752147255); // tokenAddress1
        
        
        // PoolKey poolKey = PoolKey(currency0, currency1, 3000, 60, IHooks(hook));
        PoolKey memory poolKey = PoolKey(currency0, currency1, 3000, 60, IHooks(0x5566Dd8a550C05a75e9cb980DA61B9dDAF1E8AC0));
        
        
        bytes memory hookData = new bytes(0);

        // params[0] = abi.encode(poolKey, tickLower, tickUpper, liquidity, amount0Max, amount1Max, recipient, hookData);
        params[0] = abi.encode(poolKey, 6, 6, 1, 1000, 1000, 0x418347C00Df30Ae80114c77e06216e8fDd708e06, hookData);

        params[1] = abi.encode(currency0, currency1);

        uint256 deadline = block.timestamp + 60;

        uint256 valueToPass = currency0.isAddressZero() ? 1000 : 0;

        // !!! this fails right here!!!
        posm.modifyLiquidities{value: valueToPass}(
            abi.encode(actions, params),
            deadline
        );
    }

    /// @notice Routes an LP order to the PositionManager.
    /// @param unlockData The encoded LP order data.
    /// @param deadline The deadline by which the order must be executed.
    /// @dev The function is payable so that any ETH attached is forwarded.
    function routeLPOrder(bytes calldata unlockData, uint256 deadline) external payable {
        
        
        // Forward the call to the PositionManager's modifyLiquidities function,
        // forwarding any attached ETH.
        
        IPositionManager(positionManager).modifyLiquidities{value: msg.value}(unlockData, deadline);
        emit LPOrderRouted(msg.sender, unlockData, deadline);
    }
}
