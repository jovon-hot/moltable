const { ethers } = require("hardhat");

async function main() {
    console.log("Checking USDC contracts on Amoy...\n");
    
    const addresses = [
        "0x177EE15165861977CB5FB6c5BAbB1c55a8B8A004",
        "0x52D800ca262522580CeBAD275395ca6e2998Dd76"
    ];
    
    for (const addr of addresses) {
        try {
            const usdc = await ethers.getContractAt("IERC20", addr);
            const name = await usdc.name();
            const symbol = await usdc.symbol();
            const supply = await usdc.totalSupply();
            console.log(`✅ ${addr}`);
            console.log(`   Name: ${name}`);
            console.log(`   Symbol: ${symbol}`);
            console.log(`   Supply: ${ethers.formatUnits(supply, 6)}\n`);
        } catch(e) {
            console.log(`❌ ${addr}: NOT DEPLOYED\n`);
        }
    }
}

main();
