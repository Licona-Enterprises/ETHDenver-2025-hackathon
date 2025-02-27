// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "../../lib/permit2/lib/forge-std/src/interfaces/IERC20.sol";
import {Currency} from "@uniswap/v4-core/src/types/Currency.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";
import {IHooks} from "@uniswap/v4-core/src/interfaces/IHooks.sol";
import {Actions} from "../libraries/Actions.sol";
import {IPositionManager} from "../interfaces/IPositionManager.sol";


contract DebugLPContract {
    /// @notice Address of the PositionManager contract.
    address public positionManager;
    IPositionManager public posm = IPositionManager(0xf969Aee60879C54bAAed9F3eD26147Db216Fd664);
    IERC20 token0Contract = IERC20(0xd1Ea20F1fDeb55aE3F1Fa0aFba67e5fDBbf266a3);
    IERC20 token1Contract = IERC20(0xFc805F9e0Bd4Dd73E13aE662cFC4e3B752147255);

    /// @notice Emitted when an LP order is routed.
    event LPOrderRouted(address indexed sender, bytes unlockData, uint256 deadline);

    constructor() {
        positionManager = address(0xf969Aee60879C54bAAed9F3eD26147Db216Fd664);
        // testNowLP();
    }

    function testNowLP() internal {

        bytes memory actions = abi.encodePacked(uint8(Actions.MINT_POSITION), uint8(Actions.SETTLE_PAIR));
        bytes[] memory params = new bytes[](2);
        Currency currency0 = Currency.wrap(0xd1Ea20F1fDeb55aE3F1Fa0aFba67e5fDBbf266a3); // tokenAddress0
        Currency currency1 = Currency.wrap(0xFc805F9e0Bd4Dd73E13aE662cFC4e3B752147255); // tokenAddress1
        
        // Approve PositionManager to spend the tokens
        require(token0Contract.approve(address(posm), 2), "Token0 approval failed");
        require(token1Contract.approve(address(posm), 2), "Token1 approval failed");

        // Approve this contract to spend the tokens
        require(token0Contract.approve(address(this), 2), "Token0 approval failed");
        require(token1Contract.approve(address(this), 2), "Token1 approval failed");

                
        // PoolKey poolKey = PoolKey(currency0, currency1, 3000, 60, IHooks(hook));
        PoolKey memory poolKey = PoolKey(currency0, currency1, 3000, 60, IHooks(0x5566Dd8a550C05a75e9cb980DA61B9dDAF1E8AC0));
        
        
        bytes memory hookData = new bytes(0);

        // params[0] = abi.encode(poolKey, tickLower, tickUpper, liquidity, amount0Max, amount1Max, recipient, hookData);
        params[0] = abi.encode(poolKey, 0, 60, 1, 2, 2, 0x418347C00Df30Ae80114c77e06216e8fDd708e06, hookData);

        params[1] = abi.encode(currency0, currency1);

        uint256 deadline = block.timestamp + 60;

        uint256 valueToPass = currency0.isAddressZero() ? 2 : 0;

        // !!! this fails right here!!!
        posm.modifyLiquidities{value: valueToPass}(
            abi.encode(actions, params),
            deadline
        );
    }

}
