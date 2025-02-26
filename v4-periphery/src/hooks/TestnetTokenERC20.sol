// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC20} from "../../lib/permit2/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";

contract TestnetTokenERC20 is ERC20 {
    
    string private _logoUrl;

    // Hardcoded values for name, symbol, and logoUrl
    constructor() ERC20("Agent 47", "A47 AI") {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
        setLogoUrl("https://a47.ai/wp-content/uploads/2025/01/Logo.svg");  // Example logo URL
    }

    function setLogoUrl(string memory logoUrl) internal {
        _logoUrl = logoUrl;
    }

    function getLogoUrl() external view returns (string memory) {
        return _logoUrl;
    }

}
