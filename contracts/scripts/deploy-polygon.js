/**
 * Deploy to Polygon Mainnet or Testnet
 * Usage: 
 *   npx hardhat run scripts/deploy-polygon.js --network amoy
 */

const { ethers } = require("hardhat");

async function main() {
  const network = hre.network.name;
  const [deployer] = await ethers.getSigners();
  
  console.log(`\n========================================`);
  console.log(`Deploying to ${network}...`);
  console.log(`Account: ${deployer.address}`);
  console.log(`Balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} MATIC`);
  console.log(`========================================\n`);

  // USDC addresses (checksummed)
  const usdcAddresses = {
    polygon: "0xaf88d065e77c8cC22393274205EaFE5a739160Bee",
    amoy: "0x52D800ca262522580CeBAD275395ca6e2998Dd76"
  };
  
  const usdcAddress = usdcAddresses[network];
  if (!usdcAddress) {
    console.error(`No USDC address for ${network}`);
    process.exit(1);
  }
  
  // Deploy MoltableStaking
  console.log(`USDC: ${usdcAddress}`);
  console.log(`Deploying MoltableStaking...`);
  
  const MoltableStaking = await ethers.getContractFactory("MoltableStaking");
  const staking = await MoltableStaking.deploy(usdcAddress, deployer.address);
  await staking.waitForDeployment();
  const stakingAddress = await staking.getAddress();
  
  console.log(`\n========================================`);
  console.log(`✅ Deployment Complete!`);
  console.log(`========================================`);
  console.log(`Network: ${network}`);
  console.log(`USDC: ${usdcAddress}`);
  console.log(`MoltableStaking: ${stakingAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(`Error:`, error.message);
    process.exit(1);
  });
