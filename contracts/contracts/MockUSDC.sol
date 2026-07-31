// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockUSDC is ERC20 {
    uint8 private _decimals = 6; // USDC has 6 decimals

    constructor() ERC20("USD Coin", "USDC") {
        _mint(msg.sender, 1000000000 * 10**6); // 1 billion initial supply
    }

    function decimals() public view override returns (uint8) {
        return _decimals;
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}
