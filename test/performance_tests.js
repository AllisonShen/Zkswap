const { performance } = require('perf_hooks');
const config = require('config');
const fs = require('fs');

var receipts = new Map();
var elapsed_time_map = new Map();
var gas_used_map = new Map();
var instances = {};
var owner_accounts = {};
var function_name;
var elapsed_time;
var current_receipt;
var shares;

const amount = 100000 * 10 ** 8;
const tokenSent = 1000 * 10 ** 8;

const contracts_to_deploy = ['sBNB', 'sTSLA', 'Swap']
const network_name = process.env.network;

var map_to_file = function (file_name, map) {
    let json_obj = {};
    json_obj.map = {};
    for (let [key, value] of map)
        json_obj.map[key] = value;
    let json_str = JSON.stringify(json_obj);
    fs.writeFileSync(file_name, json_str);
}

var save_data = function (data_map, key, value) {
    if (key) {
        var data_list = [];
        if (data_map.has(key)) {
            data_list = data_map.get(key);
        }
        data_list.push(value);
        data_map.set(key, data_list);
    }
}

var setup = async function (accounts) {
    console.log('network_name = ', network_name);
    if (network_name == 'development') {
        var contracts = {}
        owner_accounts = accounts;
        for (contract_name of contracts_to_deploy) {
            contracts[contract_name] = artifacts.require(contract_name)
            instances[contract_name] = await contracts[contract_name].deployed();
        }
    } else {
        network = config.get(network_name);
        console.log('network = ', network);
        owner = config.get('owner');
        owner_accounts = owner.accounts.split(', ');
        for (contract_name of contracts_to_deploy) {
            let contract = artifacts.require(contract_name);
            let contract_address = network[contract_name];
            contract.setProvider(web3.currentProvider);
            instances[contract_name] = await contract.at(contract_address);
        }
    }
    console.log('owner_accounts = ', owner_accounts);
}

afterEach(() => {
    if (function_name != 'setup') {
        save_data(elapsed_time_map, function_name, elapsed_time);
        if (current_receipt) {
            save_data(gas_used_map, function_name, current_receipt.gasUsed);
            receipts.set(current_receipt.transactionHash, current_receipt);
            current_receipt = null;
        }
    }
});

after(() => {
    var timestamp = Date.now();
    const dir = 'data_' + network_name;
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir);
    }
    map_to_file(dir + '/receipts-' + timestamp + '.json', receipts);
    map_to_file(dir + '/elapsed-times-' + timestamp + '.json', elapsed_time_map);
    map_to_file(dir + '/gas-used-' + timestamp + '.json', gas_used_map);
});

contract("Performance Tests", async accounts => {

    it("Test 00: setup", async () => {
        function_name = 'setup';
        var start = performance.now();
        await setup(accounts);
        elapsed_time = performance.now() - start;
    });

    it("Test 01: getTokens", async () => {
        function_name = 'getTokens';
        var start = performance.now();
        await instances['Swap'].getTokens.call()
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 02: approve sBNB", async () => {
        function_name = 'approve';
        var start = performance.now();
        await instances['sBNB'].approve(instances['Swap'].address, amount * 2)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 03: approve sTSLA", async () => {
        function_name = 'approve';
        var start = performance.now();
        await instances['sTSLA'].approve(instances['Swap'].address, amount * 2)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 04: init", async () => {
        function_name = 'init';
        var start = performance.now();
        await instances['Swap'].init(amount, amount)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 05: getReserves", async () => {
        function_name = 'getReserves';
        var start = performance.now();
        await instances['Swap'].getReserves.call()
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 06: addLiquidity", async () => {
        function_name = 'addLiquidity';
        var start = performance.now();
        await instances['Swap'].addLiquidity(amount)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 07: transfer sBNB", async () => {
        function_name = 'transfer';
        var start = performance.now();
        await instances['sBNB'].transfer(owner_accounts[1], tokenSent)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 08: approve sBNB", async () => {
        function_name = 'approve';
        var start = performance.now();
        await instances['sBNB'].approve(instances['Swap'].address, tokenSent, { from: owner_accounts[1] })
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 09: token0To1", async () => {
        function_name = 'token0To1';
        var start = performance.now();
        await instances['Swap'].token0To1(tokenSent, { from: owner_accounts[1] })
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 10: balanceOf", async () => {
        function_name = 'balanceOf';
        var start = performance.now();
        await instances['sTSLA'].balanceOf.call(owner_accounts[1])
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 11: transfer sTSLA", async () => {
        function_name = 'transfer';
        var start = performance.now();
        await instances['sTSLA'].transfer(owner_accounts[2], tokenSent)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 12: approve sTSLA", async () => {
        function_name = 'approve';
        var start = performance.now();
        await instances['sTSLA'].approve(instances['Swap'].address, tokenSent, { from: owner_accounts[2] })
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 13: token1To0", async () => {
        function_name = 'token1To0';
        var start = performance.now();
        await instances['Swap'].token1To0(tokenSent, { from: owner_accounts[2] })
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 14: getShares", async () => {
        function_name = 'getShares';
        var start = performance.now();
        shares = await instances['Swap'].getShares.call(owner_accounts[0])
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });

    it("Test 15: removeLiquidity", async () => {
        function_name = 'removeLiquidity';
        var start = performance.now();
        await instances['Swap'].removeLiquidity(shares)
            .on("receipt", function (receipt) {
                current_receipt = receipt;
            })
            .on("error", function (error) {
                console.error('error: ', error);
            });
        elapsed_time = performance.now() - start;
    });
});