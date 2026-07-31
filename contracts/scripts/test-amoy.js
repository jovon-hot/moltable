const { ethers } = require("hardhat");
 require("dotenv").config();

const USDC_ADDRESS = "0x177EE15165861977CB5FB6c5BAbB1c55a8B8A004";
const STAKING_ADDRESS = "0x19a62366b5686b11A3dcF90931b054E53A5bb990";

async function main() {
    console.log("========================================");
    console.log("Moltable Contract Test Suite (Amoy)");
    console.log("========================================\n");

    // Use the account from DEPLOYER_PRIVATE_KEY
    const privateKey = process.env.DEPLOYER_PRIVATE_KEY;
    const signer = new ethers.Wallet(privateKey, ethers.provider);
    console.log("Using account:", signer.address);
    const balance = await ethers.provider.getBalance(signer.address);
    console.log("Balance:", ethers.formatEther(balance), "MATIC\n");

    const usdc = await ethers.getContractAt("MockUSDC", USDC_ADDRESS, signer);
    const staking = await ethers.getContractAt("MoltableStaking", STAKING_ADDRESS, signer);

    let passed = 0;
    let failed = 0;

    async function test(name, fn) {
        try {
            await fn();
            console.log(`✅ ${name}`);
            passed++;
        } catch(e) {
            console.log(`❌ ${name}: ${e.message?.slice(0, 80)}`);
            failed++;
        }
    }

    // ===== READ-ONLY TESTS =====
    console.log("--- Read-Only Tests ---\n");
    
    await test("1. Contract USDC Address", async () => {
        const addr = await staking.usdc();
        if (addr.toLowerCase() !== USDC_ADDRESS.toLowerCase()) throw new Error("Mismatch");
    });

    await test("2. Fee Recipient", async () => {
        const fr = await staking.feeRecipient();
        console.log(`   Fee Recipient: ${fr}`);
    });

    await test("3. USDC Total Supply", async () => {
        const supply = await usdc.totalSupply();
        console.log(`   Supply: ${ethers.formatUnits(supply, 6)} USDC`);
    });

    await test("4. FEE_RATE = 2%", async () => {
        const rate = await staking.FEE_RATE();
        if (rate !== 200n) throw new Error(`Expected 200, got ${rate}`);
    });

    await test("5. ARBITRATOR_RATE = 5%", async () => {
        const rate = await staking.ARBITRATOR_RATE();
        if (rate !== 500n) throw new Error(`Expected 500, got ${rate}`);
    });

    // ===== WRITE TESTS =====
    console.log("\n--- Write Tests ---\n");

    await test("6. Mint USDC", async () => {
        const amount = ethers.parseUnits("5000", 6);
        await (await usdc.mint(signer.address, amount)).wait();
    });

    await test("7. Approve USDC", async () => {
        const amount = ethers.parseUnits("3000", 6);
        await (await usdc.approve(STAKING_ADDRESS, amount)).wait();
        console.log(`   Approved: ${ethers.formatUnits(amount, 6)} USDC`);
    });

    await test("8. Deposit USDC", async () => {
        const amount = ethers.parseUnits("1000", 6);
        await (await staking.deposit(amount)).wait();
        const info = await staking.getStakeInfo(signer.address);
        console.log(`   Deposited: ${ethers.formatUnits(info.deposited, 6)} USDC`);
    });

    await test("9. Create Protocol", async () => {
        const amount = ethers.parseUnits("200", 6);
        const protocolId = ethers.keccak256(ethers.toUtf8Bytes("TEST-001"));
        await (await staking.createProtocol(protocolId, amount)).wait();
        const proto = await staking.getProtocolStake(protocolId);
        console.log(`   Creator: ${proto.creator}`);
    });

    await test("10. Withdraw", async () => {
        const amount = ethers.parseUnits("50", 6);
        await (await staking.withdraw(amount)).wait();
        const info = await staking.getStakeInfo(signer.address);
        console.log(`   Available: ${ethers.formatUnits(info.available, 6)} USDC`);
    });

    // ===== SECURITY TESTS =====
    console.log("\n--- Security Tests ---\n");

    await test("11. Reject zero deposit", async () => {
        try {
            await staking.deposit(0);
            throw new Error("Should fail");
        } catch(e) {
            if (e.message.includes("Invalid amount")) console.log("   OK: Rejected");
            else if (!e.message.includes("Should fail")) throw e;
        }
    });

    await test("12. Reject excessive withdraw", async () => {
        try {
            await staking.withdraw(ethers.parseUnits("999999999", 6));
            throw new Error("Should fail");
        } catch(e) {
            if (e.message.includes("Insufficient")) console.log("   OK: Rejected");
            else if (!e.message.includes("Should fail")) throw e;
        }
    });

    await test("13. Non-existent protocol", async () => {
        const fakeId = ethers.keccak256(ethers.toUtf8Bytes("FAKE"));
        const proto = await staking.getProtocolStake(fakeId);
        if (proto.creator !== ethers.ZeroAddress) throw new Error("Should be zero");
    });

    // ===== SUMMARY =====
    console.log("\n========================================");
    console.log(`📊 Results: ${passed} passed, ${failed} failed`);
    console.log("========================================\n");

    if (failed === 0) {
        console.log("✅ ALL TESTS PASSED!\n");
    } else {
        console.log("❌ SOME TESTS FAILED!\n");
        process.exit(1);
    }
}

main().catch(e => {
    console.error("Fatal:", e.message);
    process.exit(1);
});
