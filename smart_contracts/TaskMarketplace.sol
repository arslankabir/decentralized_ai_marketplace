// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract TaskMarketplace is Ownable, ReentrancyGuard {
    enum TaskStatus { Created, Assigned, Submitted, Completed, Cancelled }

    struct Task {
        address creator;
        address assignedFreelancer;
        string title;
        string description;
        uint256 budget;
        TaskStatus status;
        bytes32 submissionHash;
    }

    mapping(uint256 => Task) public tasks;
    uint256 public taskCount;
    uint256 public constant MAX_TASK_BUDGET = 10 ether;

    event TaskCreated(uint256 taskId, address creator, string title, uint256 budget);
    event TaskAssigned(uint256 taskId, address freelancer);
    event WorkSubmitted(uint256 taskId, bytes32 submissionHash);
    event FundsReleased(uint256 taskId, address freelancer, uint256 amount);

    function createTask(string memory _title, string memory _description) external payable {
        require(msg.value > 0 && msg.value <= MAX_TASK_BUDGET, "Invalid task budget");
        
        taskCount++;
        tasks[taskCount] = Task({
            creator: msg.sender,
            assignedFreelancer: address(0),
            title: _title,
            description: _description,
            budget: msg.value,
            status: TaskStatus.Created,
            submissionHash: bytes32(0)
        });

        emit TaskCreated(taskCount, msg.sender, _title, msg.value);
    }

    function assignTask(uint256 _taskId, address _freelancer) external {
        Task storage task = tasks[_taskId];
        require(task.creator == msg.sender, "Only task creator can assign");
        require(task.status == TaskStatus.Created, "Task cannot be assigned");
        
        task.assignedFreelancer = _freelancer;
        task.status = TaskStatus.Assigned;

        emit TaskAssigned(_taskId, _freelancer);
    }

    function submitWork(uint256 _taskId, bytes32 _submissionHash) external nonReentrant {
        Task storage task = tasks[_taskId];
        require(msg.sender == task.assignedFreelancer, "Only assigned freelancer can submit");
        require(task.status == TaskStatus.Assigned, "Task not in assignable state");

        task.submissionHash = _submissionHash;
        task.status = TaskStatus.Submitted;

        emit WorkSubmitted(_taskId, _submissionHash);
    }

    function validateAndReleaseFunds(uint256 _taskId, bool _approved) external nonReentrant {
        Task storage task = tasks[_taskId];
        require(task.creator == msg.sender, "Only task creator can validate");
        require(task.status == TaskStatus.Submitted, "Task not ready for validation");

        if (_approved) {
            task.status = TaskStatus.Completed;
            (bool success, ) = task.assignedFreelancer.call{value: task.budget}("");
            require(success, "Transfer failed");

            emit FundsReleased(_taskId, task.assignedFreelancer, task.budget);
        } else {
            task.status = TaskStatus.Assigned;
            task.submissionHash = bytes32(0);
        }
    }

    function withdrawFunds() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }

    receive() external payable {}
}
