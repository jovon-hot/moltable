const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  
  console.log("Deploying Mock USDC with account:", deployer.address);
  
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  
  console.log("Mock USDC deployed to:", usdcAddress);

  console.log("Deploying MoltableStaking...");
  
  const MoltableStaking = await ethers.getContractFactory("MoltableStaking");
  const staking = await MoltableStaking.deploy(usdcAddress, deployer.address);
  await staking.waitForDeployment();
  const stakingAddress = await staking.getAddress();
  
  console.log("MoltableStaking deployed to:", stakingAddress);
  
  const [, user1, user2] = await ethers.getSigners();
  const mintAmount = ethers.parseUnits("10000", 6);
  
  await usdc.mint(deployer.address, mintAmount);
  await usdc.mint(user1.address, mintAmount);
  await usdc.mint(user2.address, mintAmount);
  
  console.log("Minted 10000 USDC to deployer, user1, user2");
  
  await usdc.approve(stakingAddress, mintAmount);
  console.log("Approved staking contract");
  
  console.log("\n=== Deployment Summary ===");
  console.log("USDC:", usdcAddress);
  console.log("MoltableStaking:", stakingAddress);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
