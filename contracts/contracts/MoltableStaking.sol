// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title MoltableStaking
 * @dev USDC 质押合约 (参考 Polymarket 模式)
 */
contract MoltableStaking is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    IERC20 public usdc;
    address public feeRecipient;
    
    uint256 public constant FEE_RATE = 200;
    uint256 public constant FEE_DENOMINATOR = 10000;
    uint256 public constant ARBITRATOR_RATE = 500;
    
    struct StakeInfo {
        uint256 deposited;
        uint256 locked;
        uint256 available;
    }
    
    mapping(address => StakeInfo) public stakes;
    
    struct ProtocolStake {
        address creator;
        address acceptor;
        uint256 creatorStake;
        uint256 acceptorStake;
        uint256 totalStake;
        bool creatorSettled;
        bool acceptorSettled;
        bool disputed;
    }
    
    mapping(bytes32 => ProtocolStake) public protocolStakes;
    
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event ProtocolCreated(bytes32 indexed protocolId, address indexed creator, uint256 stake);
    event ProtocolAccepted(bytes32 indexed protocolId, address indexed acceptor, uint256 stake);
    event ProtocolSettled(bytes32 indexed protocolId, address indexed user, uint256 amount);
    event ProtocolDisputed(bytes32 indexed protocolId);
    event DisputeSettled(bytes32 indexed protocolId, bool creatorWinner);
    
    constructor(address _usdc, address _feeRecipient) Ownable() {
        require(_usdc != address(0), "Invalid USDC address");
        require(_feeRecipient != address(0), "Invalid fee recipient");
        usdc = IERC20(_usdc);
        feeRecipient = _feeRecipient;
    }
    
    function deposit(uint256 amount) external nonReentrant {
        require(amount > 0, "Invalid amount");
        usdc.safeTransferFrom(msg.sender, address(this), amount);
        stakes[msg.sender].deposited += amount;
        stakes[msg.sender].available += amount;
        emit Deposited(msg.sender, amount);
    }
    
    function withdraw(uint256 amount) external nonReentrant {
        require(amount > 0, "Invalid amount");
        require(stakes[msg.sender].available >= amount, "Insufficient available balance");
        stakes[msg.sender].available -= amount;
        usdc.safeTransfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }
    
    function createProtocol(bytes32 protocolId, uint256 stakeAmount) external nonReentrant {
        require(protocolId != bytes32(0), "Invalid protocol ID");
        require(stakeAmount > 0, "Invalid stake amount");
        require(stakes[msg.sender].available >= stakeAmount, "Insufficient available balance");
        
        stakes[msg.sender].available -= stakeAmount;
        stakes[msg.sender].locked += stakeAmount;
        
        protocolStakes[protocolId] = ProtocolStake({
            creator: msg.sender,
            acceptor: address(0),
            creatorStake: stakeAmount,
            acceptorStake: 0,
            totalStake: stakeAmount,
            creatorSettled: false,
            acceptorSettled: false,
            disputed: false
        });
        
        emit ProtocolCreated(protocolId, msg.sender, stakeAmount);
    }
    
    function acceptProtocol(bytes32 protocolId) external nonReentrant {
        ProtocolStake storage proto = protocolStakes[protocolId];
        require(proto.creator != address(0), "Protocol not found");
        require(proto.acceptor == address(0), "Already accepted");
        require(stakes[msg.sender].available >= proto.creatorStake, "Insufficient balance");
        
        uint256 stakeAmount = proto.creatorStake;
        stakes[msg.sender].available -= stakeAmount;
        stakes[msg.sender].locked += stakeAmount;
        
        proto.acceptor = msg.sender;
        proto.acceptorStake = stakeAmount;
        proto.totalStake = stakeAmount * 2;
        
        emit ProtocolAccepted(protocolId, msg.sender, stakeAmount);
    }
    
    function settleProtocol(bytes32 protocolId, bool creatorWins) external nonReentrant {
        ProtocolStake storage proto = protocolStakes[protocolId];
        require(msg.sender == proto.creator || msg.sender == owner(), "Not authorized");
        require(!proto.disputed, "Protocol is disputed");
        
        address winner = creatorWins ? proto.creator : proto.acceptor;
        uint256 totalStake = proto.totalStake;
        uint256 platformFee = totalStake * FEE_RATE / FEE_DENOMINATOR;
        uint256 arbitratorFee = totalStake * ARBITRATOR_RATE / FEE_DENOMINATOR;
        uint256 winnerAmount = totalStake - platformFee - arbitratorFee;
        
        _settleUser(winner, creatorWins ? proto.creatorStake : proto.acceptorStake, winnerAmount);
        
        address loser = creatorWins ? proto.acceptor : proto.creator;
        if (loser != address(0)) {
            _releaseLock(loser, creatorWins ? proto.acceptorStake : proto.creatorStake);
        }
        
        if (platformFee > 0) {
            usdc.safeTransfer(feeRecipient, platformFee);
        }
        
        emit ProtocolSettled(protocolId, winner, winnerAmount);
        delete protocolStakes[protocolId];
    }
    
    function _settleUser(address user, uint256 lockedAmount, uint256 reward) internal {
        StakeInfo storage stake = stakes[user];
        stake.locked -= lockedAmount;
        stake.available += reward;
    }
    
    function _releaseLock(address user, uint256 amount) internal {
        StakeInfo storage stake = stakes[user];
        if (stake.locked >= amount) {
            stake.locked -= amount;
        }
        stake.available += amount;
    }
    
    function raiseDispute(bytes32 protocolId) external {
        ProtocolStake storage proto = protocolStakes[protocolId];
        require(msg.sender == proto.creator || msg.sender == proto.acceptor, "Not authorized");
        require(!proto.disputed, "Already disputed");
        proto.disputed = true;
        emit ProtocolDisputed(protocolId);
    }
    
    function settleDispute(bytes32 protocolId, bool creatorWinner, uint256 arbitratorReward) external onlyOwner nonReentrant {
        ProtocolStake storage proto = protocolStakes[protocolId];
        require(proto.disputed, "Not disputed");
        
        uint256 totalStake = proto.totalStake;
        uint256 platformFee = totalStake * FEE_RATE / FEE_DENOMINATOR;
        uint256 arbitratorFee = totalStake * ARBITRATOR_RATE / FEE_DENOMINATOR;
        
        if (arbitratorReward > arbitratorFee) {
            arbitratorReward = arbitratorFee;
        }
        
        uint256 winnerAmount = totalStake - platformFee - arbitratorReward;
        
        address winner = creatorWinner ? proto.creator : proto.acceptor;
        address loser = creatorWinner ? proto.acceptor : proto.creator;
        
        _settleUser(winner, creatorWinner ? proto.creatorStake : proto.acceptorStake, winnerAmount);
        _releaseLock(loser, creatorWinner ? proto.acceptorStake : proto.creatorStake);
        
        if (platformFee > 0) {
            usdc.safeTransfer(feeRecipient, platformFee);
        }
        if (arbitratorReward > 0) {
            usdc.safeTransfer(feeRecipient, arbitratorReward);
        }
        
        emit DisputeSettled(protocolId, creatorWinner);
        delete protocolStakes[protocolId];
    }
    
    function getStakeInfo(address user) external view returns (uint256 deposited, uint256 locked, uint256 available) {
        StakeInfo memory stake = stakes[user];
        return (stake.deposited, stake.locked, stake.available);
    }
    
    function getProtocolStake(bytes32 protocolId) external view returns (
        address creator, address acceptor, uint256 creatorStake, uint256 acceptorStake,
        uint256 totalStake, bool creatorSettled, bool acceptorSettled, bool disputed
    ) {
        ProtocolStake memory proto = protocolStakes[protocolId];
        return (proto.creator, proto.acceptor, proto.creatorStake, proto.acceptorStake,
            proto.totalStake, proto.creatorSettled, proto.acceptorSettled, proto.disputed);
    }
    
    function setFeeRecipient(address newRecipient) external onlyOwner {
        require(newRecipient != address(0), "Invalid recipient");
        feeRecipient = newRecipient;
    }
    
    receive() external payable {}
}
