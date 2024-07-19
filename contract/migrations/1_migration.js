var MyContract = artifacts.require("ADS");

module.exports = function(deployer) {
  // 部署步骤
  deployer.deploy(MyContract);
};