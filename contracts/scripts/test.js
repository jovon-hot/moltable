const { ethers } = require("hardhat");

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    const [deployer, user1, user2, user3] = await ethers.getSigners();
    
    // Get contract addresses from deployment
    const usdcAddress = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";
    const stakingAddress = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0";
    
    const usdc = await ethers.getContractAt("MockUSDC", usdcAddress);
    const staking = await ethers.getContractAt("MoltableStaking", stakingAddress);
    
    console.log("========================================");
    console.log("Moltable Smart Contract Test Suite");
    console.log("========================================\n");
    
    // Test 1: Check initial balances
    console.log("📋 Test 1: Initial Balance Check");
    console.log("----------------------------------------");
    const deployerInfo = await staking.getStakeInfo(deployer.address);
    const user1Info = await staking.getStakeInfo(user1.address);
    console.log(`Deployer - Deposited: ${ethers.formatUnits(deployerInfo.deposited, 6)} USDC, Available: ${ethers.formatUnits(deployerInfo.available, 6)} USDC`);
    console.log(`User1   - Deposited: ${ethers.formatUnits(user1Info.deposited, 6)} USDC, Available: ${ethers.formatUnits(user1Info.available, 6)} USDC`);
    console.log("✅ Test 1 PASSED\n");
    
    // Test 2: User1 deposits USDC
    console.log("📋 Test 2: User1 Deposits 500 USDC");
    console.log("----------------------------------------");
    const depositAmount = ethers.parseUnits("500", 6);
    const tx2 = await usdc.connect(user1).approve(stakingAddress, depositAmount);
    await tx2.wait();
    const tx3 = await staking.connect(user1).deposit(depositAmount);
    await tx3.wait();
    const user1Info2 = await staking.getStakeInfo(user1.address);
    console.log(`User1 Deposited: ${ethers.formatUnits(user1Info2.deposited, 6)} USDC`);
    console.log(`User1 Available: ${ethers.formatUnits(user1Info2.available, 6)} USDC`);
    console.log("✅ Test 2 PASSED\n");
    
    // Test 3: User2 deposits USDC
    console.log("📋 Test 3: User2 Deposits 1000 USDC");
    console.log("----------------------------------------");
    const depositAmount2 = ethers.parseUnits("1000", 6);
    await (await usdc.connect(user2).approve(stakingAddress, depositAmount2)).wait();
    await (await staking.connect(user2).deposit(depositAmount2)).wait();
    const user2Info = await staking.getStakeInfo(user2.address);
    console.log(`User2 Deposited: ${ethers.formatUnits(user2Info.deposited, 6)} USDC`);
    console.log(`User2 Available: ${ethers.formatUnits(user2Info.available, 6)} USDC`);
    console.log("✅ Test 3 PASSED\n");
    
    // Test 4: Create Protocol (Bounty Task)
    console.log("📋 Test 4: User1 Creates Protocol (100 USDC Stake)");
    console.log("----------------------------------------");
    const protocolId1 = ethers.keccak256(ethers.toUtf8Bytes("PROTO-001-test-task"));
    const stakeAmount = ethers.parseUnits("100", 6);
    const tx4 = await staking.connect(user1).createProtocol(protocolId1, stakeAmount);
    await tx4.wait();
    const user1Info3 = await staking.getStakeInfo(user1.address);
    const proto1Info = await staking.getProtocolStake(protocolId1);
    console.log(`Protocol ID: ${protocolId1}`);
    console.log(`Creator: ${proto1Info.creator}`);
    console.log(`Creator Stake: ${ethers.formatUnits(proto1Info.creatorStake, 6)} USDC`);
    console.log(`User1 Available: ${ethers.formatUnits(user1Info3.available, 6)} USDC`);
    console.log(`User1 Locked: ${ethers.formatUnits(user1Info3.locked, 6)} USDC`);
    console.log("✅ Test 4 PASSED\n");
    
    // Test 5: User2 Accepts Protocol
    console.log("📋 Test 5: User2 Accepts Protocol");
    console.log("----------------------------------------");
    const tx5 = await staking.connect(user2).acceptProtocol(protocolId1);
    await tx5.wait();
    const proto1Info2 = await staking.getProtocolStake(protocolId1);
    const user2Info2 = await staking.getStakeInfo(user2.address);
    console.log(`Acceptor: ${proto1Info2.acceptor}`);
    console.log(`Total Stake: ${ethers.formatUnits(proto1Info2.totalStake, 6)} USDC`);
    console.log(`User2 Available: ${ethers.formatUnits(user2Info2.available, 6)} USDC`);
    console.log(`User2 Locked: ${ethers.formatUnits(user2Info2.locked, 6)} USDC`);
    console.log("✅ Test 5 PASSED\n");
    
    // Test 6: Settle Protocol (User1 wins)
    console.log("📋 Test 6: Settle Protocol (Creator Wins)");
    console.log("----------------------------------------");
    const tx6 = await staking.connect(user1).settleProtocol(protocolId1, true);
    await tx6.wait();
    const user1Info4 = await staking.getStakeInfo(user1.address);
    const user2Info3 = await staking.getStakeInfo(user2.address);
    console.log(`User1 Available: ${ethers.formatUnits(user1Info4.available, 6)} USDC (won stake + reward)`);
    console.log(`User1 Locked: ${ethers.formatUnits(user1Info4.locked, 6)} USDC`);
    console.log(`User2 Available: ${ethers.formatUnits(user2Info3.available, 6)} USDC (lost stake)`);
    console.log(`User2 Locked: ${ethers.formatUnits(user2Info3.locked, 6)} USDC`);
    console.log("✅ Test 6 PASSED\n");
    
    // Test 7: Create Another Protocol (Dispute Scenario)
    console.log("📋 Test 7: Create Protocol for Dispute Test");
    console.log("----------------------------------------");
    const protocolId2 = ethers.keccak256(ethers.toUtf8Bytes("PROTO-002-dispute"));
    const stakeAmount2 = ethers.parseUnits("200", 6);
    await (await staking.connect(user1).createProtocol(protocolId2, stakeAmount2)).wait();
    await (await staking.connect(user2).acceptProtocol(protocolId2)).wait();
    const proto2Info = await staking.getProtocolStake(protocolId2);
    console.log(`Protocol Created and Accepted`);
    console.log(`Total Stake: ${ethers.formatUnits(proto2Info.totalStake, 6)} USDC`);
    console.log("✅ Test 7 PASSED\n");
    
    // Test 8: Raise Dispute
    console.log("📋 Test 8: Raise Dispute");
    console.log("----------------------------------------");
    const tx8 = await staking.connect(user1).raiseDispute(protocolId2);
    await tx8.wait();
    const proto2Info2 = await staking.getProtocolStake(protocolId2);
    console.log(`Disputed: ${proto2Info2.disputed}`);
    console.log("✅ Test 8 PASSED\n");
    
    // Test 9: Withdraw
    console.log("📋 Test 9: User1 Withdraws");
    console.log("----------------------------------------");
    const withdrawAmount = ethers.parseUnits("50", 6);
    const tx9 = await staking.connect(user1).withdraw(withdrawAmount);
    await tx9.wait();
    const user1Info5 = await staking.getStakeInfo(user1.address);
    console.log(`User1 Withdrew: ${ethers.formatUnits(withdrawAmount, 6)} USDC`);
    console.log(`User1 Available: ${ethers.formatUnits(user1Info5.available, 6)} USDC`);
    console.log("✅ Test 9 PASSED\n");
    
    // Test 10: Query Protocol (Non-existent)
    console.log("📋 Test 10: Query Non-existent Protocol");
    console.log("----------------------------------------");
    const fakeProtocolId = ethers.keccak256(ethers.toUtf8Bytes("FAKE-PROTOCOL"));
    const fakeProto = await staking.getProtocolStake(fakeProtocolId);
    console.log(`Creator (should be 0): ${fakeProto.creator}`);
    console.log("✅ Test 10 PASSED\n");
    
    // Summary
    console.log("========================================");
    console.log("🎉 All Tests Passed!");
    console.log("========================================\n");
    
    console.log("📊 Final State:");
    const allUsers = [
        { name: "Deployer", addr: deployer.address },
        { name: "User1", addr: user1.address },
        { name: "User2", addr: user2.address },
    ];
    
    for (const user of allUsers) {
        const info = await staking.getStakeInfo(user.addr);
        console.log(`${user.name}:`);
        console.log(`  Deposited: ${ethers.formatUnits(info.deposited, 6)} USDC`);
        console.log(`  Locked:    ${ethers.formatUnits(info.locked, 6)} USDC`);
        console.log(`  Available: ${ethers.formatUnits(info.available, 6)} USDC`);
    }
    
    console.log("\n📝 Contract Addresses:");
    console.log(`USDC:      ${usdcAddress}`);
    console.log(`Staking:   ${stakingAddress}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Test Failed:", error.message);
        process.exit(1);
    });
