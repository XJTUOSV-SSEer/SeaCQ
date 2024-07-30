var MyContract = artifacts.require("Merkle");

module.exports = function(deployer) {
  // 部署步骤
  deployer.deploy(MyContract);
};