import json
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import dotenv_values

NETWORK_NAME_GOERLI = 'goerli'
NETWORK_NAME_ZKEVM = 'zkevm_testnet'
COMMON_DATA_PREFIX = './data_'
PREFIX_ELAPSED_TIMES = 'elapsed-times-'
PREFIX_GAS_USED = 'gas-used-'
RECEIPT_PREFIX = 'receipts-'

XLABEL = 'Contract method name'
YLABEL_ELAPSED_TIME = 'Elapsed Time (ms)'
YLABEL_GAS_USED = 'Gas units used'
YLABEL_TX_FEE = 'Transaction Fee (ETH)'

ZKEVM_TESTNET_API_URL = 'https://api-testnet-zkevm.polygonscan.com'
GOERLI_API_URL = 'https://api-goerli.etherscan.io'
GET_TRANSACTION_BY_HASH_ACTION = 'eth_getTransactionByHash'
GET_TRANSACTION_RECEIPT_ACTION = 'eth_getTransactionReceipt'

DIR_PLOTS = './plots/'
PLOT_NAME_ELAPSED_TIMES = 'elapsed-times.png'
PLOT_NAME_GAS_USED = 'gas-used.png'
PLOT_NAME_TX_FEE = 'tx-fee.png'


class Transaction:

    def __init__(self, json_tx_str: str, json_tx_receipt_str: str):
        json_obj = json.loads(json_tx_str)['result']
        self._tx_hash = json_obj['hash']
        self._gas_price = float(int(json_obj['gasPrice'], 16)) / float(pow(10, 18))
        self._method_name = decode_method_id(json_obj['input'])
        json_obj = json.loads(json_tx_receipt_str)['result']
        self._gas_used = int(json_obj['gasUsed'], 16)
        self._tx_fee = self._gas_price * float(self._gas_used)


    @property
    def tx_hash(self):
        return self._tx_hash


    @tx_hash.setter
    def tx_hash(self, tx_hash):
        self._tx_hash = hash


    @property
    def gas_used(self):
        return self._gas


    @gas_used.setter
    def gas_used(self, gas_used):
        self._gas_used = gas_used


    @property
    def gas_price(self):
        return self._gas_price


    @gas_price.setter
    def gas_price(self, gas_price):
        self._gas_price = gas_price


    @property
    def gas_price(self):
        return self._gas_price


    @gas_price.setter
    def gas_price(self, gas_price):
        self._gas_price = gas_price


    @property
    def method_name(self):
        return self._method_name


    @method_name.setter
    def method_name(self, method_name):
        self._method_name = method_name


    def to_string(self) -> str:
        return json.dumps(self.__dict__)


def decode_method_id(input):
    method_id = input[:10]
    match method_id:
        case '0x51c6590a':
            method_name = 'addLiquidity'
        case '0xa5843f08':
            method_name = 'init'
        case '0x9c8f9f23':
            method_name = 'removeLiquidity'
        case '0x26ef80c9':
            method_name = 'token0To1'
        case '0xad3bd45c':
            method_name = 'token1To0'
        case '0x095ea7b3':
            method_name = 'approve'
        case '0xa9059cbb':
            method_name = 'transfer'
        case _:
            method_name = 'unknown'
    return method_name


def collect_data_from_path(path, prefix):
    result = {}
    data = {}
    files = [
        os.path.join(dirpath, f)
        for (dirpath, dirnames, filenames) in os.walk(path)
        for f in filenames]
    for filename in files:
        if (prefix in filename):
            with open(filename, newline='') as jsonfile:
                data_map = json.load(jsonfile)
                curr_data = data_map['map']
                for k, v in curr_data.items():
                    arr = data.get(k)
                    if arr == None:
                        arr = []
                    arr.extend(v)
                    data.update({k: arr})
    for k, v in data.items():
        num_of_elems = len(v)
        sum = 0;
        for item in v:
            sum = sum + item
        av = sum / float(num_of_elems)
        result.update({k: av})
    sorted_result = sorted(result.items())
    return sorted_result


def plot(zkevm_data, goerli_data, ylabel, ylim, plot_name):
    test_name_list = []
    for item in zkevm_data:
        test_name_list.append(item[0])
    test_name = tuple(test_name_list)
    data = {}
    data_list_zkevm = []
    for i in range(len(test_name)):
        item = zkevm_data[i][1]
        data_list_zkevm.append(item)
    data.update({NETWORK_NAME_ZKEVM: tuple(data_list_zkevm)})

    data_list_goerli = []
    for i in range(len(test_name)):
        item = goerli_data[i][1]
        data_list_goerli.append(item)
    data.update({NETWORK_NAME_GOERLI: tuple(data_list_goerli)})

    x = np.arange(len(test_name))
    width = 0.3
    multiplier = 0
    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in data.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3, rotation=90)
        multiplier += 1

    ax.set_ylabel(ylabel)
    ax.set_xlabel(XLABEL)
    ax.set_xticks(x + width / 2, test_name)
    plt.xticks(rotation=90)
    ax.legend(loc='upper left', ncols=1)
    ax.set_ylim(0, ylim)

    # plt.show()
    filename = f'{DIR_PLOTS}{plot_name}'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)


def collect_tx_fee_data():
    api_key = dotenv_values(".env")['etherscan_api_key']
    tx_list_goerli = generate_tx_data(NETWORK_NAME_GOERLI, api_key)
    save_tx_data(NETWORK_NAME_GOERLI, tx_list_goerli)
    tx_list_zkevm = generate_tx_data(NETWORK_NAME_ZKEVM, api_key)
    save_tx_data(NETWORK_NAME_ZKEVM, tx_list_zkevm)


def read_tx_data(network_name):
    data = {}
    result = {}
    with open(f'./data_{network_name}/tx_data.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        json_obj = json.loads(line)
        method_name = json_obj['_method_name']
        arr = data.get(method_name)
        if arr == None:
            arr = []
        arr.append(json_obj['_tx_fee'])
        data.update({method_name: arr})
    for k, v in data.items():
        num_of_elems = len(v)
        sum = 0
        for item in v:
            sum = sum + item
        av = sum / float(num_of_elems)
        result.update({k: av})
    sorted_result = sorted(result.items())
    return sorted_result


def get_tx_data(network_name, api_key, tx_hash):
    if network_name == NETWORK_NAME_GOERLI:
        url = GOERLI_API_URL
    else:
        url = ZKEVM_TESTNET_API_URL
    get_transaction_url = f'{url}/api?module=proxy&action={GET_TRANSACTION_BY_HASH_ACTION}&txhash={tx_hash}&apikey={api_key}'
    # maximum rate limit of up to 5 calls per sec/IP
    time.sleep(1.0 / 5.0)
    get_transaction_receipt_url = f'{url}/api?module=proxy&action={GET_TRANSACTION_RECEIPT_ACTION}&txhash={tx_hash}&apikey={api_key}'
    get_transaction_response = requests.get(get_transaction_url + tx_hash)
    get_transaction_receipt_response = requests.get(get_transaction_receipt_url + tx_hash)
    return Transaction(get_transaction_response.content, get_transaction_receipt_response.content)


def get_tx_data_from_path(path, prefix):
    txs = []
    files = [
        os.path.join(dirpath, f)
        for (dirpath, dirnames, filenames) in os.walk(path)
        for f in filenames]
    for filename in files:
        if (prefix in filename):
            with open(filename, newline='') as jsonfile:
                data_map = json.load(jsonfile)
                txs.extend(list(data_map['map'].keys()))
    return txs


def generate_tx_data(network_name, api_key):
    tx_list = []
    tx_hash_list = get_tx_data_from_path(f'{COMMON_DATA_PREFIX}{network_name}', RECEIPT_PREFIX)
    for tx_hash in tx_hash_list:
        tx = get_tx_data(network_name, api_key, tx_hash)
        tx_list.append(tx)
    return tx_list


def save_tx_data(network_name, data):
    with open(f'./data_{network_name}/tx_data.txt', 'a') as f:
        for tx in data:
            f.write(tx.to_string() + '\n')


def generate_plots():
    zkevm_data = collect_data_from_path(f'{COMMON_DATA_PREFIX}{NETWORK_NAME_ZKEVM}', PREFIX_ELAPSED_TIMES)
    goerli_data = collect_data_from_path(f'{COMMON_DATA_PREFIX}{NETWORK_NAME_GOERLI}', PREFIX_ELAPSED_TIMES)
    plot(zkevm_data, goerli_data, YLABEL_ELAPSED_TIME, 30000, PLOT_NAME_ELAPSED_TIMES)
    zkevm_data = collect_data_from_path(f'{COMMON_DATA_PREFIX}{NETWORK_NAME_ZKEVM}', PREFIX_GAS_USED)
    goerli_data = collect_data_from_path(f'{COMMON_DATA_PREFIX}{NETWORK_NAME_GOERLI}', PREFIX_GAS_USED)
    plot(zkevm_data, goerli_data, YLABEL_GAS_USED, 310000, PLOT_NAME_GAS_USED)
    collect_tx_fee_data()
    zkevm_data = read_tx_data(NETWORK_NAME_ZKEVM)
    goerli_data = read_tx_data(NETWORK_NAME_GOERLI)
    plot(zkevm_data, goerli_data, YLABEL_TX_FEE, 0.025, PLOT_NAME_TX_FEE)


generate_plots()
