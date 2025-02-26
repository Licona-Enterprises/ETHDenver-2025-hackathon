// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

import {IPoolManager} from "@uniswap/v4-core/src/interfaces/IPoolManager.sol";
import {BaseHook} from '../utils/BaseHook.sol';

abstract contract CoolHook is BaseHook {

    /// @param _manager The Uniswap V4 pool manager
    constructor(IPoolManager _manager) BaseHook(_manager) {}

}
