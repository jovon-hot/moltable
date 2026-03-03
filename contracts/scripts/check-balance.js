const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Balance: ${ethers.formatEther(balance)} MATIC`);
  
  const blockNumber = await ethers.provider.getBlockNumber();
  console.log(`Block: ${blockNumber}`);
}

main();
