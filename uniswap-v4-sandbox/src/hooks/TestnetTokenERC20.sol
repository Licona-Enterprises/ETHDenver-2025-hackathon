// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC20} from "../../lib/permit2/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "../../lib/permit2/lib/openzeppelin-contracts/contracts/access/Ownable.sol";

contract TestnetTokenERC20 is ERC20, Ownable {
    
    string private _logoUrl;

    // weird ownable implemention here 
    constructor(string memory name, string memory symbol, string memory logoUrl) ERC20(name, symbol) Ownable() {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
        setLogoUrl(logoUrl);
    }

    function setLogoUrl(string memory logoUrl) internal onlyOwner {
        _logoUrl = logoUrl;
    }

    function getLogoUrl() external view returns (string memory) {
        return _logoUrl;
    }
}
