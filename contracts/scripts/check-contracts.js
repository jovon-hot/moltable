const { ethers } = require("hardhat");

async function main() {
    console.log("Checking contracts on Amoy...\n");
    
    const STAKING_ADDR = "0x19a62366b5686b11A3dcF90931b054E53A5bb990";
    const USDC_ADDR = "0x177EE15165861977CB5FB6c5BAbB1c55a8B8A004";
    
    // Check USDC
    try {
        const usdc = await ethers.getContractAt("MockUSDC", USDC_ADDR);
        const totalSupply = await usdc.totalSupply();
        console.log(`✅ USDC at ${USDC_ADDR}`);
        console.log(`   Total Supply: ${ethers.formatUnits(totalSupply, 6)} USDC\n`);
    } catch(e) {
        console.log(`❌ USDC at ${USDC_ADDR}: ${e.message.slice(0, 50)}\n`);
    }
    
    // Check Staking
    try {
        const staking = await ethers.getContractAt("MoltableStaking", STAKING_ADDR);
        const usdcAddr = await staking.usdc();
        const feeRecipient = await staking.feeRecipient();
        console.log(`✅ Staking at ${STAKING_ADDR}`);
        console.log(`   USDC: ${usdcAddr}`);
        console.log(`   Fee Recipient: ${feeRecipient}\n`);
    } catch(e) {
        console.log(`❌ Staking at ${STAKING_ADDR}: ${e.message.slice(0, 80)}\n`);
    }
}

main();
