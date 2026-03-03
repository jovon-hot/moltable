/**
 * Simple Test - Check if account is connected properly
 */
const { ethers } = require("hardhat");

async function main() {
  console.log("Testing account connection...");
  
  // Get the signer directly
  const [signer] = await ethers.getSigners();
  console.log("Signer:", signer.address);
  
  // Check balance
  const balance = await ethers.provider.getBalance(signer.address);
  console.log("Balance:", ethers.formatEther(balance), "MATIC");
  
  // Try to call a view function (should work)
  const usdc = await ethers.getContractAt(
    "MockUSDC", 
    "0x177EE15165861977CB5FB6c5BAbB1c55a8B8A004"
  );
  
  console.log("\nUSDC Contract loaded");
  
  // Try a read-only call
  try {
    const totalSupply = await usdc.totalSupply();
    console.log("USDC Total Supply:", ethers.formatUnits(totalSupply, 6));
  } catch(e) {
    console.log("Error reading USDC:", e.message);
  }
}

main();
