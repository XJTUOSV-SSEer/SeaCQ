var MyContract = artifacts.require("write");

module.exports = function(deployer) {
  deployer.deploy(MyContract);
};