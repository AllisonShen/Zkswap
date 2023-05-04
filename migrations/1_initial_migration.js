const Migrations = artifacts.require("Migrations");

module.exports = function (deployer) {
  process.env.network = deployer.network;
  if(process.env.network == 'development')
    deployer.deploy(Migrations);
};
