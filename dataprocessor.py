# to generate plots, run commands:
# virtualenv env
# source env/bin/activate
# pip install --upgrade pip
# pip install matplotlib
# ./env/bin/python dataprocessor.py

import json
import os

import matplotlib.pyplot as plt
import numpy as np

NETWORK_NAME_GOERLI = 'goerli'
NETWORK_NAME_ZKEVM = 'zkevm_testnet'
PREFIX_ELAPSED_TIMES = 'elapsed-times-'
PREFIX_GAS_USED = 'gas-used-'
COMMON_DATA_PREFIX = './data_'

XLABEL = 'Contract method name'
YLABEL_ELAPSED_TIME = 'Elapsed Time (ms)'
YLABEL_GAS_USED = 'Gas units used'

DIR_PLOTS = './plots/'
PLOT_NAME_ELAPSED_TIMES = 'elapsed-times.png'
PLOT_NAME_GAS_USED = 'gas-used.png'


def getFromPath(path, prefix):
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


def plot(prefix, ylabel, ylim, plot_name):
    zkevm_data = getFromPath(f'{COMMON_DATA_PREFIX}{NETWORK_NAME_ZKEVM}', prefix)
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

    goerli_data = getFromPath(f'{COMMON_DATA_PREFIX}{NETWORK_NAME_GOERLI}', prefix)
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


def generate_plots():
    plot(PREFIX_ELAPSED_TIMES, YLABEL_ELAPSED_TIME, 30000, PLOT_NAME_ELAPSED_TIMES)
    plot(PREFIX_GAS_USED, YLABEL_GAS_USED, 310000, PLOT_NAME_GAS_USED)


generate_plots()
