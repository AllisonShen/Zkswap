require('dotenv').config();
const HDWalletProvider = require('@truffle/hdwallet-provider');
const config = require('config');

const private_keys = process.env.owner_pks.split(', ');

module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*"
    },
    zkevm_testnet: {
      provider: () => new HDWalletProvider(private_keys, config.get('zkevm_testnet').rpc),
      network_id: 1442,
    },
    goerli: {
      provider: () => new HDWalletProvider(private_keys, config.get('goerli').rpc+process.env.infura_api_key),
      network_id: 5,
    },
    dashboard: {
    }
  },
  compilers: {
    solc: {
      version: "0.8.13",
    }
  },
  db: {
    enabled: false,
    host: "127.0.0.1",
  }
};