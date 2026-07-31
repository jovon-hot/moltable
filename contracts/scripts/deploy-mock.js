/**
 * Deploy Mock USDC first
 */
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  
  console.log(`Deploying Mock USDC...`);
  console.log(`Account: ${deployer.address}`);
  
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  
  console.log(`Mock USDC: ${usdcAddress}`);
  
  // Deploy Staking with Mock USDC
  console.log(`Deploying MoltableStaking...`);
  const Staking = await ethers.getContractFactory("MoltableStaking");
  const staking = await Staking.deploy(usdcAddress, deployer.address);
  await staking.waitForDeployment();
  const stakingAddress = await staking.getAddress();
  
  console.log(`\n✅ Deployed!`);
  console.log(`USDC: ${usdcAddress}`);
  console.log(`Staking: ${stakingAddress}`);
}

main().catch(console.error);
