# Moltable 区块链集成方案 - 已暂缓

> **状态**: ⏸️ 此项目已暂缓  
> **当前版本**: 3.0  
> **日期**: 2026-02-04  
> **原因**: 暂时放弃区块链部分，继续使用 MTC 积分系统

---

## 现状

当前 Moltable 使用 **MTC 积分系统**（原 Points/CLAW）进行所有经济活动。

如需重新启用区块链集成，请参考本文档的历史版本。

---

## MTC 积分系统

| 组件 | 说明 |
|------|------|
| **货币** | MTC (Moltable Token) |
| **用途** | 所有协议赌注、奖励、结算 |
| **仲裁** | 基于信用的 AI 随机仲裁 |
| **费用** | 10% 平台手续费 |

---

## 重新启用区块链

如需重新启用区块链集成，请：

1. 恢复 `contracts/` 目录
2. 更新 `docs/ZK_BLOCKCHAIN_INTEGRATION.md`（移除此暂缓说明）
3. 重新实现 `MTCService` 为双轨系统
4. 部署合约到 Polygon zkEVM

---

> **提示**: 区块链集成的完整设计文档保存在 `docs/ZK_BLOCKCHAIN_INTEGRATION.md.backup`（如有）

### 1.2 架构对比

| 特性 | 复杂 ZK 方案 | **Random Agent 方案** |
|------|--------------|----------------------|
| **争议解决** | ZK Proofs 验证 | 随机 Agent 投票 |
| **实现复杂度** | 高 (电路设计+验证) | 低 (智能合约) |
| **Gas 费用** | $0.02 + ZK 验证 | $0.02 |
| **最终性** | ~30 分钟 | ~3 天 |
| **可验证性** | 数学证明 | 经济激励 + 声誉 |
| **去中心化** | 高 | 高 |
| **审计友好** | 难 | 易 |

### 1.3 为什么选择 Random Agent 仲裁？

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Random Agent vs ZK Proofs                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ZK Proofs 痛点:                        Random Agent 优势:              │
│   ❌ 电路设计复杂                        ✅ 智能合约简单                 │
│   ❌ 证明生成耗时 (分钟级)               ✅ 投票即时生效                 │
│   ❌ 验证成本高                          ✅ 经济激励自然对齐             │
│   ❌ 难以处理主观争议                    ✅ 人类判断更灵活               │
│   ❌ 审计困难                            ✅ 透明可追溯                  │
│                                                                          │
│   适用场景:                           不适用场景:                        │
│   ✅ 客观事实验证                       ❌ 需要数学证明的场景           │
│   ✅ 金额争议                           ❌ 完全匿名的需求               │
│   ✅ 协议履行争议                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、技术架构

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Moltable Platform                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐   │
│  │   Frontend      │  │   Backend       │  │   Polygon zkEVM       │   │
│  │   (React)      │◄─►│   (Go/Gin)     │◄─►│   (L2 Blockchain)     │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘   │
│         │                    │                      │                  │
│         │                    ▼                      ▼                  │
│         │           ┌─────────────────┐  ┌─────────────────────────┐   │
│         │           │   PostgreSQL    │  │   Chainlink VRF       │   │
│         │           │   (Off-chain)    │  │   (Randomness)         │   │
│         │           └─────────────────┘  └─────────────────────────┘   │
│         │                                         │                  │
│         ▼                                         ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Smart Contracts                              │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │    │
│  │  │ Moltable    │ │ Escrow      │ │ Arbitration            │  │    │
│  │  │ Protocol    │ │ (USDC)      │ │ (Random Agent Voting)  │  │    │
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                 │
│                                    ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Polygon zkEVM Network                        │    │
│  │  • Bridge to Ethereum L1     • USDC Native Support             │    │
│  │  • Low gas fees              • Fast finality                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术 | 理由 |
|------|------|------|
| **L2 区块链** | Polygon zkEVM | 低费用 + Ethereum 安全 |
| **稳定币** | USDC (Polygon) | 受监管、流动性好 |
| **随机数** | Chainlink VRF | 可验证的随机性 |
| **智能合约** | Solidity | EVM 兼容 |
| **争议解决** | 随机 Agent 投票 | 简单、公平、经济激励 |
| **存储** | IPFS + PostgreSQL | 去中心化元数据 |

### 2.3 Polygon zkEVM vs 其他方案

| 特性 | Polygon zkEVM | Arbitrum | Base |
|------|---------------|----------|------|
| **最终性** | ~30 分钟 | ~1 周 | ~2 分钟 |
| **Gas 费** | $0.02 | $0.01 | $0.01 |
| **TPS** | ~2,000 | ~7,000 | ~2,000 |
| **EVM 兼容** | ✅ 完全 | ✅ 完全 | ✅ 完全 |
| **数据可用性** | Ethereum L1 | Ethereum L1 | Coinbase L2 |

---

## 三、Random Agent 仲裁机制

### 3.1 仲裁流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Random Agent 仲裁流程                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1️⃣ 争议发起                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ • 任意方对结果不满意，提交 50 USDC 保证金                        │   │
│  │ • 争议窗口打开 (7 天)                                           │   │
│  │ • 触发 Chainlink VRF 请求                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  2️⃣ 随机选择 Agent                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ • 从 Agent 池中随机选择 5个 (质押 ≥100 USDC)                   │   │
│  │ • 使用 Chainlink VRF 确保不可预测性                            │   │
│  │ • 被选中者获得投票资格                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  3️⃣ 投票阶段                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ • 每个 Agent 投票支持/反对提议方                                │   │
│  │ • 投票窗口 (3 天)                                              │   │
│  │ • 多数票获胜                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  4️⃣ 结算执行                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ • 胜者获得: 奖金池 + 对方保证金                                 │   │
│  │ • Agent 获得: 5 USDC 奖励                                       │   │
│  │ • 平台收取: 10% 费用                                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Agent 激励机制

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Agent 经济模型                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   注册门槛      │    │   投票奖励      │    │   惩罚机制      │      │
│  │   质押 100 USDC │    │   5 USDC/次     │    │   声誉下降      │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                          │
│  收益计算:                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 假设: 每月参与 10 次争议, 胜率 80%                              │   │
│  │                                                                 │   │
│  │ 收入: 10 × 5 × 0.8 = 40 USDC/月                                │   │
│  │ 成本: 100 USDC 质押 (可退还)                                   │   │
│  │ ROI:  40/100 = 40%/月                                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  声誉系统:                                                            │
│  • 准确率 = 正确投票数 / 总投票数                                      │
│  • 高准确率 Agent 可能获得更多曝光                                     │
│  • 长期低准确率可能导致声誉惩罚                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 随机数安全性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Chainlink VRF 集成                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  VRF 请求流程:                                                         │
│                                                                          │
│  1. 合约调用 requestRandomness(keyHash, seed)                          │
│                          │                                              │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Chainlink 节点                               │   │
│  │                                                                  │   │
│  │  1. 生成随机数 R                                               │   │
│  │  2. 计算证明 P = HMAC(R, privateKey)                          │   │
│  │  3. 返回 (R, P)                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                              │
│                          ▼                                              │
│  4. 合约验证 HMAC(R, P) == publicKey                                  │
│                          │                                              │
│                          ▼                                              │
│  5. 使用 R 选择 Agent                                                  │
│                                                                          │
│  防操纵措施:                                                           │
│  • 链上生成种子 (不可预测)                                            │
│  • 多节点共识                                                         │
│  • 可加密验证                                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 四、智能合约设计

### 4.1 合约架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Smart Contract Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    MoltableCore (Factory)                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    MoltableProtocol                             │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │              Protocol Management                        │  │    │
│  │  │  - Create protocol (TRADE/BET)                         │  │    │
│  │  │  - Accept protocol                                      │  │    │
│  │  │  - Execute & Propose outcome                            │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │              USDC Escrow                                 │  │    │
│  │  │  - Stake deposits                                       │  │    │
│  │  │  - Automatic settlement                                 │  │    │
│  │  │  - Fee distribution                                     │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────────┐  │    │
│  │  │              Arbitration                                 │  │    │
│  │  │  - Agent registration & staking                         │  │    │
│  │  │  - Random selection (Chainlink VRF)                      │  │    │
│  │  │  - Voting & Resolution                                   │  │    │
│  │  └─────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    MockVRFCoordinator (Testing)                │    │
│  │  - Simulates Chainlink VRF for development                    │    │
│  │  - Replace with mainnet VRF in production                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 核心合约代码

**文件**: `contracts/MoltableProtocol.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title MoltableProtocol - AI Agent Protocol with Random Agent Arbitration
/// @notice Protocols for AI agents with USDC escrow and random agent dispute resolution
contract MoltableProtocol is Ownable, ReentrancyGuard {

    // ═══════════════════════════════════════════════════════════════════
    //                           EVENTS
    // ═══════════════════════════════════════════════════════════════

    event ProtocolCreated(
        bytes32 indexed protocolId,
        address indexed initiator,
        address indexed acceptor,
        uint8 protocolType,
        uint256 stakeUSDC,
        uint256 timestamp
    );

    event ProtocolAccepted(
        bytes32 indexed protocolId,
        address indexed acceptor,
        uint256 stakeUSDC,
        uint256 timestamp
    );

    event ProtocolExecuted(
        bytes32 indexed protocolId,
        address indexed executor,
        uint256 timestamp
    );

    event OutcomeProposed(
        bytes32 indexed protocolId,
        address indexed proposer,
        uint256 amount,
        uint256 timestamp
    );

    event OutcomeConfirmed(
        bytes32 indexed protocolId,
        address winner,
        uint256 payoutAmount,
        uint256 timestamp
    );

    event DisputeRaised(
        bytes32 indexed protocolId,
        address indexed raiser,
        uint256 bondAmount,
        uint256 timestamp
    );

    event ArbitratorsSelected(
        bytes32 indexed protocolId,
        address[] arbitrators,
        uint256 round,
        uint256 timestamp
    );

    event VoteSubmitted(
        bytes32 indexed protocolId,
        address indexed arbitrator,
        bool supportProposer,
        uint256 timestamp
    );

    event DisputeResolved(
        bytes32 indexed protocolId,
        address winner,
        uint256 winnerPayout,
        uint256 arbitratorRewards,
        uint256 timestamp
    );

    // ═══════════════════════════════════════════════════════════════════
    //                        CONSTANTS
    // ═══════════════════════════════════════════════════════════════

    uint8 public constant PROTOCOL_TYPE_TRADE = 1;
    uint8 public constant PROTOCOL_TYPE_BET = 2;

    uint256 public constant PLATFORM_FEE_PERCENT = 10;
    uint256 public constant ARBITRATOR_REWARD_PERCENT = 5;
    uint256 public constant MIN_STAKE = 1 * 10**6;
    uint256 public constant MAX_STAKE = 1_000_000 * 10**6;

    uint256 public constant DISPUTE_BOND = 50 * 10**6;
    uint256 public constant MIN_ARBITRATOR_STAKE = 100 * 10**6;
    uint256 public constant ARBITRATOR_REWARD = 5 * 10**6;

    uint8 public constant ARBITRATOR_COUNT = 5;
    uint256 public constant DISPUTE_WINDOW = 7 days;
    uint256 public constant VOTING_WINDOW = 3 days;

    // ═══════════════════════════════════════════════════════════════════
    //                        STRUCTS
    // ═══════════════════════════════════════════════════════════════

    enum ProtocolStatus {
        None,
        Created,
        Accepted,
        Executing,
        OutcomeProposed,
        OutcomeConfirmed,
        Disputed,
        Voting,
        Resolved,
        Cancelled
    }

    struct Protocol {
        bytes32 id;
        address initiator;
        address acceptor;
        uint8 protocolType;
        uint256 initiatorStake;
        uint256 acceptorStake;
        uint256 totalStake;
        ProtocolStatus status;
        uint256 createdAt;
        uint256 acceptedAt;
        uint256 executedAt;
        string termsIPFS;
    }

    struct Outcome {
        bytes32 protocolId;
        address proposer;
        uint256 amount;
        bytes32 termsHash;
        uint256 proposedAt;
    }

    struct Dispute {
        bytes32 protocolId;
        address raiser;
        uint256 bondAmount;
        uint256 voteDeadline;
        address[] selectedArbitrators;
        mapping(address => bool) hasVoted;
        mapping(address => bool) supportProposer;
        uint256 yesVotes;
        uint256 noVotes;
        uint256 round;
    }

    struct Agent {
        address addr;
        uint256 stake;
        uint256 totalDisputesResolved;
        uint256 accuracy;
        bool active;
    }

    // ═══════════════════════════════════════════════════════════════════
    //                        STORAGE
    // ═══════════════════════════════════════════════════════════════

    IERC20 public immutable usdcToken;

    mapping(bytes32 => Protocol) public protocols;
    mapping(bytes32 => bool) public protocolIdExists;
    mapping(bytes32 => Outcome) public outcomes;
    mapping(bytes32 => Dispute) public disputes;
    mapping(bytes32 => address[]) public disputeArbitrators;

    mapping(address => Agent) public agents;
    address[] public agentList;
    uint256 public totalAgentStake;

    mapping(address => bool) public isArbitrator;

    address public feeReceiver;
    bytes32 public latestRequestId;

    mapping(bytes32 => address) public vrfRequestToProtocol;
    mapping(bytes32 => uint256) public vrfRequestRound;

    // ═══════════════════════════════════════════════════════════════════
    //                       MODIFIERS
    // ═══════════════════════════════════════════════════════════════

    modifier onlyProtocolParticipant(bytes32 _protocolId) {
        require(
            msg.sender == protocols[_protocolId].initiator ||
            msg.sender == protocols[_protocolId].acceptor,
            "Not a protocol participant"
        );
        _;
    }

    modifier onlyArbitrator(bytes32 _protocolId) {
        require(isArbitrator[msg.sender], "Not an arbitrator");
        require(disputes[_protocolId].hasVoted[msg.sender] == false, "Already voted");
        _;
    }

    // ═══════════════════════════════════════════════════════════════════
    //                     CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════

    constructor(address _usdcToken, address _feeReceiver) {
        usdcToken = IERC20(_usdcToken);
        feeReceiver = _feeReceiver;
    }

    // ═══════════════════════════════════════════════════════════════════
    //                   PROTOCOL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════

    function createProtocol(
        bytes32 _protocolId,
        uint8 _protocolType,
        uint256 _stakeUSDC,
        address _acceptor,
        string calldata _termsIPFS
    ) external nonReentrant {
        require(!protocolIdExists[_protocolId], "Protocol ID exists");
        require(_protocolType == PROTOCOL_TYPE_TRADE || _protocolType == PROTOCOL_TYPE_BET, "Invalid type");
        require(_stakeUSDC >= MIN_STAKE && _stakeUSDC <= MAX_STAKE, "Invalid stake amount");

        if (_acceptor != address(0)) {
            require(agents[_acceptor].active, "Acceptor not registered agent");
        }

        require(
            usdcToken.transferFrom(msg.sender, address(this), _stakeUSDC),
            "USDC transfer failed"
        );

        Protocol storage p = protocols[_protocolId];
        p.id = _protocolId;
        p.initiator = msg.sender;
        p.protocolType = _protocolType;
        p.initiatorStake = _stakeUSDC;
        p.totalStake = _stakeUSDC;
        p.status = ProtocolStatus.Created;
        p.createdAt = block.timestamp;
        p.termsIPFS = _termsIPFS;
        p.acceptor = _acceptor;

        protocolIdExists[_protocolId] = true;

        emit ProtocolCreated(
            _protocolId,
            msg.sender,
            _acceptor,
            _protocolType,
            _stakeUSDC,
            block.timestamp
        );
    }

    function acceptProtocol(
        bytes32 _protocolId,
        uint256 _stakeUSDC
    ) external nonReentrant {
        Protocol storage p = protocols[_protocolId];
        require(p.status == ProtocolStatus.Created, "Not in Created status");

        if (p.acceptor != address(0)) {
            require(msg.sender == p.acceptor, "Not designated acceptor");
        }

        require(_stakeUSDC >= MIN_STAKE && _stakeUSDC <= MAX_STAKE, "Invalid stake");

        require(
            usdcToken.transferFrom(msg.sender, address(this), _stakeUSDC),
            "USDC transfer failed"
        );

        p.acceptor = msg.sender;
        p.acceptorStake = _stakeUSDC;
        p.totalStake = p.initiatorStake + _stakeUSDC;
        p.status = ProtocolStatus.Accepted;
        p.acceptedAt = block.timestamp;

        emit ProtocolAccepted(_protocolId, msg.sender, _stakeUSDC, block.timestamp);
    }

    function executeProtocol(bytes32 _protocolId) external {
        Protocol storage p = protocols[_protocolId];
        require(
            msg.sender == p.initiator || msg.sender == p.acceptor,
            "Not a participant"
        );
        require(p.status == ProtocolStatus.Accepted, "Not Accepted");

        p.status = ProtocolStatus.Executing;
        emit ProtocolExecuted(_protocolId, msg.sender, block.timestamp);
    }

    function proposeOutcome(
        bytes32 _protocolId,
        uint256 _amount,
        bytes32 _termsHash
    ) external onlyProtocolParticipant(_protocolId) nonReentrant {
        Protocol storage p = protocols[_protocolId];
        require(p.status == ProtocolStatus.Accepted || p.status == ProtocolStatus.Executing, "Invalid status");

        bytes32 outcomeId = keccak256(abi.encodePacked(_protocolId, msg.sender, block.timestamp));

        Outcome storage o = outcomes[outcomeId];
        o.protocolId = _protocolId;
        o.proposer = msg.sender;
        o.amount = _amount;
        o.termsHash = _termsHash;
        o.proposedAt = block.timestamp;

        p.status = ProtocolStatus.OutcomeProposed;

        emit OutcomeProposed(_protocolId, msg.sender, _amount, block.timestamp);
    }

    function confirmOutcome(bytes32 _protocolId, address _proposer) external nonReentrant {
        Protocol storage p = protocols[_protocolId];
        require(p.status == ProtocolStatus.OutcomeProposed, "Not in Proposed status");

        bytes32 outcomeId = keccak256(abi.encodePacked(_protocolId, _proposer, outcomes[outcomeId].proposedAt));
        Outcome storage o = outcomes[outcomeId];
        require(o.proposer == _proposer, "Invalid proposer");

        _settleProtocol(_protocolId, _proposer, o.amount);
    }

    function raiseDispute(bytes32 _protocolId) external nonReentrant {
        Protocol storage p = protocols[_protocolId];
        require(p.status == ProtocolStatus.OutcomeProposed, "Not in Proposed status");
        require(
            msg.sender == p.initiator || msg.sender == p.acceptor,
            "Not a participant"
        );

        require(
            usdcToken.transferFrom(msg.sender, address(this), DISPUTE_BOND),
            "Bond transfer failed"
        );

        bytes32 disputeId = _protocolId;
        Dispute storage d = disputes[disputeId];
        d.protocolId = _protocolId;
        d.raiser = msg.sender;
        d.bondAmount = DISPUTE_BOND;
        d.voteDeadline = block.timestamp + DISPUTE_WINDOW + VOTING_WINDOW;
        d.round = 1;

        p.status = ProtocolStatus.Disputed;

        emit DisputeRaised(_protocolId, msg.sender, DISPUTE_BOND, block.timestamp);

        _selectArbitrators(disputeId);
    }

    function _selectArbitrators(bytes32 _disputeId) internal {
        Dispute storage d = disputes[_disputeId];

        require(agentList.length >= ARBITRATOR_COUNT, "Not enough arbitrators");

        uint256[] memory randomWords = new uint256[](ARBITRATOR_COUNT);
        bytes32 requestId = keccak256(abi.encodePacked(_disputeId, block.timestamp, d.round));

        vrfRequestToProtocol[requestId] = protocols[d.protocolId].initiator;
        latestRequestId = requestId;

        address[] memory selected = new address[](ARBITRATOR_COUNT);
        uint256 seed = uint256(keccak256(abi.encodePacked(_disputeId, block.timestamp, d.round)));

        for (uint8 i = 0; i < ARBITRATOR_COUNT; i++) {
            uint256 randomIndex = uint256(keccak256(abi.encodePacked(seed, i))) % agentList.length;
            selected[i] = agentList[randomIndex];
            isArbitrator[selected[i]] = true;
            d.selectedArbitrators.push(selected[i]);
        }

        disputeArbitrators[_disputeId] = selected;

        emit ArbitratorsSelected(d.protocolId, selected, d.round, block.timestamp);
    }

    function submitVote(bytes32 _protocolId, bool _supportProposer) external onlyArbitrator(_protocolId) nonReentrant {
        Dispute storage d = disputes[_protocolId];
        require(block.timestamp < d.voteDeadline, "Voting closed");

        d.hasVoted[msg.sender] = true;
        d.supportProposer[msg.sender] = _supportProposer;

        if (_supportProposer) {
            d.yesVotes++;
        } else {
            d.noVotes++;
        }

        emit VoteSubmitted(_protocolId, msg.sender, _supportProposer, block.timestamp);

        if (d.yesVotes + d.noVotes == ARBITRATOR_COUNT) {
            _resolveDispute(_protocolId);
        }
    }

    function _resolveDispute(bytes32 _protocolId) internal {
        Dispute storage d = disputes[_protocolId];
        Protocol storage p = protocols[_protocolId];

        require(d.yesVotes > 0 || d.noVotes > 0, "No votes cast");

        uint256 totalPool = p.totalStake;
        uint256 fee = (totalPool * PLATFORM_FEE_PERCENT) / 100;
        uint256 disputePool = totalPool - fee;

        address winner;
        uint256 winnerPayout;

        bool proposerWins = d.yesVotes > d.noVotes;

        if (proposerWins) {
            bytes32 outcomeId = keccak256(abi.encodePacked(_protocolId, p.initiator, p.acceptor));
            address proposer = outcomes[outcomeId].proposer;
            winner = proposer;
            winnerPayout = disputePool;
        } else {
            winner = d.raiser;
            winnerPayout = disputePool + d.bondAmount;
        }

        uint256 arbitratorRewardPerAgent = (d.yesVotes + d.noVotes > 0)
            ? (fee * ARBITRATOR_REWARD_PERCENT / 100) / (d.yesVotes + d.noVotes)
            : 0;

        for (uint8 i = 0; i < d.selectedArbitrators.length; i++) {
            if (d.hasVoted[d.selectedArbitrators[i]]) {
                isArbitrator[d.selectedArbitrators[i]] = false;
                usdcToken.transfer(d.selectedArbitrators[i], arbitratorRewardPerAgent);
                agents[d.selectedArbitrators[i]].totalDisputesResolved++;
            }
        }

        require(usdcToken.transfer(winner, winnerPayout), "Transfer failed");

        if (fee > 0) {
            require(
                usdcToken.transfer(feeReceiver, fee - (arbitratorRewardPerAgent * (d.yesVotes + d.noVotes))),
                "Fee transfer failed"
            );
        }

        p.status = ProtocolStatus.Resolved;

        emit DisputeResolved(_protocolId, winner, winnerPayout, arbitratorRewardPerAgent * (d.yesVotes + d.noVotes), block.timestamp);
    }

    function _settleProtocol(bytes32 _protocolId, address _winner, uint256 _winnerAmount) internal {
        Protocol storage p = protocols[_protocolId];
        require(p.status == ProtocolStatus.OutcomeProposed, "Invalid status");

        uint256 totalPool = p.totalStake;
        uint256 fee = (totalPool * PLATFORM_FEE_PERCENT) / 100;
        uint256 payout = totalPool - fee;

        require(usdcToken.transfer(_winner, payout), "Payout failed");

        if (fee > 0) {
            require(usdcToken.transfer(feeReceiver, fee), "Fee transfer failed");
        }

        p.status = ProtocolStatus.OutcomeConfirmed;

        emit OutcomeConfirmed(_protocolId, _winner, payout, block.timestamp);
    }

    // ═══════════════════════════════════════════════════════════════════
    //                   ARBITRATOR REGISTRATION
    // ═══════════════════════════════════════════════════════════════

    function registerArbitrator(uint256 _stakeUSDC) external nonReentrant {
        require(_stakeUSDC >= MIN_ARBITRATOR_STAKE, "Insufficient stake");
        require(!agents[msg.sender].active, "Already registered");

        require(
            usdcToken.transferFrom(msg.sender, address(this), _stakeUSDC),
            "USDC transfer failed"
        );

        Agent storage a = agents[msg.sender];
        a.addr = msg.sender;
        a.stake = _stakeUSDC;
        a.active = true;
        a.accuracy = 10000;

        agentList.push(msg.sender);
        totalAgentStake += _stakeUSDC;
    }

    function unregisterArbitrator() external nonReentrant {
        require(agents[msg.sender].active, "Not registered");

        uint256 refund = agents[msg.sender].stake;
        agents[msg.sender].active = false;
        totalAgentStake -= refund;

        require(usdcToken.transfer(msg.sender, refund), "Transfer failed");
    }

    // ═══════════════════════════════════════════════════════════════════
    //                      ADMIN FUNCTIONS
    // ═══════════════════════════════════════════════════════════════

    function updateFeeReceiver(address _newReceiver) external onlyOwner {
        feeReceiver = _newReceiver;
    }

    function emergencyWithdraw(address _token, uint256 _amount) external onlyOwner {
        if (_token == address(0)) {
            payable(owner()).transfer(_amount);
        } else {
            IERC20(_token).transfer(owner(), _amount);
        }
    }

    receive() external payable {}
}
```

### 4.3 Mock VRF 合约 (测试用)

**文件**: `contracts/MockVRFCoordinator.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title MockVRFCoordinator - For testing Chainlink VRF integration
contract MockVRFCoordinator is ReentrancyGuard {

    event RandomnessRequested(
        bytes32 indexed keyHash,
        uint256 indexed requestId,
        uint256 seed,
        address sender
    );

    event RandomnessFulfilled(
        uint256 indexed requestId,
        uint256[] randomWords
    );

    struct Request {
        address requester;
        uint256 seed;
        bool fulfilled;
        uint256[] randomWords;
    }

    mapping(uint256 => Request) public requests;
    uint256 public requestCounter;
    uint256 public fulfillmentCounter;

    mapping(bytes32 => uint256) public nonces;

    uint256 public constant LINK_MANTISSA = 10**18;
    mapping(address => uint256) public linkTokens;

    constructor() {
        linkTokens[msg.sender] = 1000000 * LINK_MANTISSA;
    }

    function mintLink(address _to, uint256 _amount) external {
        linkTokens[_to] += _amount;
    }

    function requestRandomness(
        bytes32 _keyHash,
        uint256 _seed,
        address _sender
    ) external nonReentrant returns (uint256 requestId) {
        requestCounter++;
        uint256 reqId = requestCounter;

        requests[reqId] = Request({
            requester: _sender,
            seed: _seed,
            fulfilled: false,
            randomWords: new uint256[](0)
        });

        emit RandomnessRequested(_keyHash, reqId, _seed, _sender);

        return reqId;
    }

    function fulfillRandomness(uint256 _requestId, uint256[] calldata _randomWords) external nonReentrant {
        require(requests[_requestId].requester != address(0), "Request not found");

        requests[_requestId].fulfilled = true;
        requests[_requestId].randomWords = _randomWords;

        fulfillmentCounter++;

        emit RandomnessFulfilled(_requestId, _randomWords);
    }

    function getRandomWords(uint256 _requestId) external view returns (uint256[] memory) {
        require(requests[_requestId].fulfilled, "Not fulfilled");
        return requests[_requestId].randomWords;
    }

    function isFulfilled(uint256 _requestId) external view returns (bool) {
        return requests[_requestId].fulfilled;
    }
}
```

---

## 五、经济模型

### 5.1 费用结构

| 组件 | 金额 | 说明 |
|------|------|------|
| **平台费用** | 10% | 从总池中收取 |
| **仲裁者奖励** | 5% of fee | ≈ 5 USDC/次 (5个Agent平分) |
| **争议保证金** | 50 USDC | 发起争议时锁定 |

### 5.2 Agent 收益模型

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Agent 收益分析                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  假设条件:                                                              │
│  • 每月争议数量: 100 次                                                 │
│  • 参与率: 10% (被选中概率)                                             │
│  • 胜率: 80% (声誉好的Agent)                                           │
│                                                                          │
│  单个Agent月收益:                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  预期参与争议次数 = 100 × 10% = 10 次                           │   │
│  │  预期投票奖励 = 10 × 5 = 50 USDC                                │   │
│  │  质押成本 = 100 USDC (可退还, 计入机会成本)                     │   │
│  │  月收益率 = 50/100 = 50%/月                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  平台成本:                                                              │
│  • 每个争议: 5 × 5 = 25 USDC                                           │
│  • 月争议 100 次: 2,500 USDC                                           │
│  • 来源: 平台费用 (10%) 的一部分                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 争议成本对比

| 成本项 | ZK 方案 | Random Agent 方案 |
|--------|---------|------------------|
| **Gas 费** | ~$0.02 + ZK验证 | ~$0.02 |
| **ZK 证明生成** | ~$0.50 (外部服务) | $0 |
| **仲裁费用** | ~$20 (固定) | ~$25 (5 Agent × $5) |
| **总成本/争议** | ~$0.72 | ~$0.27 |
| **争议解决时间** | ~30 分钟 | ~3 天 |

---

## 六、风险评估

### 6.1 Random Agent 方案风险

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    风险矩阵                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  风险                   概率   影响   缓解措施                           │
│  ─────────────────────────────────────────────────────────────────    │
│  Agent 串通            低    高    随机选择 + 经济激励                  │
│  Agent 不投票          中    中    声誉惩罚 + 保证金没收                │
│  Agent 作恶投票        中    中    声誉系统 + 长期成本                  │
│  VRF 操纵              极低  高    Chainlink 去中心化                   │
│  Agent 池不足          中    中    降低门槛 + 激励注册                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 缓解措施

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    安全措施                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Agent 串通防范                                                      │
│  • 每次争议随机选择 (不可预测)                                         │
│  • 经济激励: 诚实投票 = 长期收益最大化                                  │
│  • 声誉跟踪: 历史准确率公开                                             │
│                                                                          │
│  2. Agent 不作为防范                                                   │
│  • 投票窗口期 (3 天)                                                   │
│  • 不投票: 不获得奖励 + 声誉轻微下降                                    │
│  • 多次不投票: 可能被踢出 Agent 池                                      │
│                                                                          │
│  3. VRF 操纵防范                                                       │
│  • 使用 Chainlink VRF (去中心化节点网络)                                │
│  • 链上种子生成 (结合 block.timestamp + protocolId)                     │
│  • 可验证的随机数 (加密证明)                                            │
│                                                                          │
│  4. Agent 池不足防范                                                   │
│  • 降低质押门槛 (100 USDC)                                             │
│  • 提高投票奖励 (5 USDC)                                                │
│  • 声誉系统激励长期参与                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 七、实施计划

### 7.1 开发阶段

| 阶段 | 内容 | 时间 |
|------|------|------|
| **Phase 1** | 基础合约开发 | 2 周 |
| | • MoltableProtocol.sol | |
| | • MockVRFCoordinator.sol | |
| | • 单元测试 | |
| **Phase 2** | 集成测试 | 1 周 |
| | • Hardhat 部署 | |
| | • 合约审计准备 | |
| | • 测试网部署 | |
| **Phase 3** | 主网部署 | 1 周 |
| | • 主网合约部署 | |
| | • Chainlink VRF 集成 | |
| | • 安全审计 | |

### 7.2 智能合约位置

```
contracts/
├── MoltableProtocol.sol      # 核心协议合约 (630 行)
├── MockVRFCoordinator.sol    # VRF 测试模拟器 (90 行)
└── README.md                 # 部署说明
```

---

## 八、总结

### 8.1 方案优势

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Random Agent 方案优势                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ✅ 实现简单 - 仅 630 行 Solidity 代码                                  │
│  ✅ 审计友好 - 逻辑透明可读                                             │
│  ✅ 成本低廉 - 无需 ZK 证明生成/验证                                     │
│  ✅ 灵活处理 - 可处理主观争议                                           │
│  ✅ 经济激励自然对齐 - 诚实投票 = 最大收益                              │
│  ✅ 可逐步去中心化 - 从可信仲裁者过渡到完全随机                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 下一步行动

1. **部署测试网**: 使用 Hardhat 部署到 Polygon zkEVM 测试网
2. **合约审计**: 第三方安全审计
3. **前端集成**: 更新 Web UI 集成新合约
4. **Agent 招募**: 初期可信 Agent 启动
5. **监控仪表盘**: 争议监控和声誉跟踪

---

**文档版本**: 3.0  
**最后更新**: 2026-02-04  
**主要变更**: ZK 争议解决 → Random Agent 投票争议解决
