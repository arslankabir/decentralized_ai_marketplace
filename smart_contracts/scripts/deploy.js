const hre = require("hardhat");

async function main() {
  const TaskMarketplace = await hre.ethers.getContractFactory("TaskMarketplace");
  const taskMarketplace = await TaskMarketplace.deploy();

  await taskMarketplace.deployed();

  console.log("TaskMarketplace deployed to:", taskMarketplace.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
