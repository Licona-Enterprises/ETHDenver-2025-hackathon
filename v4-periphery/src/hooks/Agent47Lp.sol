// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Currency} from "@uniswap/v4-core/src/types/Currency.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";
import {IHooks} from "@uniswap/v4-core/src/interfaces/IHooks.sol";
import {Actions} from "../libraries/Actions.sol";
import {IPositionManager} from "../interfaces/IPositionManager.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Agent47Lp {
    /// @notice Address of the contract owner (fee receiver).
    address public owner;

    /// @notice PositionManager contract.
    IPositionManager public posm;

    /// @notice Emitted when an LP order is routed.
    event LPOrderRouted(address indexed sender, bytes unlockData, uint256 deadline);

    /// @notice Emitted when a 1% fee is taken from token0 and token1.
    event AgentFee(address indexed recipient, address token0, uint256 feeToken0, address token1, uint256 feeToken1);


    constructor() {
        owner = msg.sender; // Set contract deployer as owner
        posm = IPositionManager(0xf969Aee60879C54bAAed9F3eD26147Db216Fd664);
    }

    /// @notice Executes a liquidity providing operation while taking a 1% fee.
    /// @param token0 Address of the first token
    /// @param token1 Address of the second token
    /// @param feeTier Fee tier for the pool
    /// @param tickSpacing Tick spacing for the pool
    /// @param hook Address of the hook contract
    /// @param amount0Max Max amount of token0 to deposit
    /// @param amount1Max Max amount of token1 to deposit
    function agentMintLp(
        address token0,
        address token1,
        uint24 feeTier,
        int24 tickSpacing,
        address hook,
        uint256 amount0Max,
        uint256 amount1Max
    ) external payable {
        require(amount0Max > 0 && amount1Max > 0, "Invalid deposit amounts");

        IERC20 token0Contract = IERC20(token0);
        IERC20 token1Contract = IERC20(token1);

        // Calculate 1% fee
        uint256 feeToken0 = (amount0Max * 1) / 100; // 1% of token0
        uint256 feeToken1 = (amount1Max * 1) / 100; // 1% of token1

        // Approve this contract to spend the tokens
        require(token0Contract.approve(address(this), feeToken0), "Token0 approval failed");
        require(token1Contract.approve(address(this), feeToken1), "Token1 approval failed");

        // Transfer fee to owner
        require(token0Contract.transferFrom(msg.sender, owner, feeToken0), "Token0 fee transfer failed");
        require(token1Contract.transferFrom(msg.sender, owner, feeToken1), "Token1 fee transfer failed");

        // Emit AgentFee event
        emit AgentFee(owner, token0, feeToken0, token1, feeToken1);

        // Subtract fees from the amounts
        uint256 depositAmount0 = amount0Max - feeToken0;
        uint256 depositAmount1 = amount1Max - feeToken1;

        // Approve PositionManager to spend the tokens
        require(token0Contract.approve(address(posm), depositAmount0), "Token0 approval failed");
        require(token1Contract.approve(address(posm), depositAmount1), "Token1 approval failed");

        // Declare actions array
        bytes memory actions = abi.encodePacked(uint8(Actions.MINT_POSITION), uint8(Actions.SETTLE_PAIR));

        // Declare params array properly
        bytes[] memory params = new bytes[](2);

        // Wrap the token addresses into Currency type
        Currency currency0 = Currency.wrap(token0);
        Currency currency1 = Currency.wrap(token1);

        // Define the poolKey dynamically
        PoolKey memory poolKey = PoolKey(currency0, currency1, feeTier, tickSpacing, IHooks(hook));

        bytes memory hookData = new bytes(0);

        // Encode mint position parameters dynamically
        params[0] = abi.encode(poolKey, int24(-60), int24(60), uint128(1), depositAmount0, depositAmount1, msg.sender, hookData);
        params[1] = abi.encode(currency0, currency1);

        uint256 deadline = block.timestamp + 60;
        uint256 valueToPass = currency0.isAddressZero() ? depositAmount0 : 0;

        // Call modifyLiquidities dynamically with encoded params
        posm.modifyLiquidities{value: valueToPass}(abi.encode(actions, params), deadline);

        // Emit event for LP order
        emit LPOrderRouted(msg.sender, abi.encode(actions, params), deadline);
    }
}
