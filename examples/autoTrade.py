#!/usr/bin/env python
# coding=utf-8

# This file is part of krakenex.
# Licensed under the Simplified BSD license. See `examples/LICENSE.txt`.

# Get balance available for trading/withdrawal (not on orders).
#
# NOTE: Assumes regular orders. Margin positions are not taken into account!

import sys
import os

if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(1, os.path.join(here, os.path.pardir))

import krakenex
import time
import sched




def perform_command(cmd, inc):
    # 安排inc秒后再次运行自己，即周期运行
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    autoSale()


def timing_exe(cmd, inc):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(1, 0, perform_command, (cmd, inc))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()


def autoSale():
    k = krakenex.API()
    if __name__ == "__main__":
        k.load_key('kraken.key')
    # if __name__ == "__main__":
    #     k.load_key('krakenex\kraken.key')

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    balance = {}
    count = 0
    while not ("result" in balance) and count < 5:
        balance = k.query_private('Balance')
        count += 1
    if not ("result" in balance):
        return print("request Balance failed")

    print('持有ZEC数量：' + balance['result']['XZEC'])
    print('持有EUR数量：' + balance['result']['ZEUR'])
    amount_Total = float(balance['result']['XZEC'])

    openOrdersDict = {}
    count = 0
    while not ("result" in openOrdersDict) and count < 5:
        openOrdersDict = k.query_private('OpenOrders')
        count += 1
    if not ("result" in openOrdersDict):
        return print("request OpenOrders failed")

    openOrders = openOrdersDict['result']['open']
    amount_onSale = 0
    for i in openOrders:
        if openOrders[i]['descr']['type'] == 'sell':
            amount_onSale += float(openOrders[i]['vol'])
    print("销售中ZEC数量：" + str(amount_onSale))
    amount_forSale = amount_Total - amount_onSale
    print("可销售ZEC数量：" + str(amount_forSale))

    priceRes = {}
    count = 0
    while not ("result" in priceRes) and count < 5:
        priceRes = k.query_public('Ticker', {'pair': 'ZECEUR'})
        count += 1
    if not ("result" in priceRes):
        return print("request Current Price failed")

    print('最新成交价格：' + priceRes['result']['XZECZEUR']['c'][0])
    lastPrice = round(float(priceRes['result']['XZECZEUR']['c'][0]), 2)
    price = max(300, lastPrice)
    if amount_forSale > 0.03:
        amount_forSale = int(amount_forSale * 100) / 100
        res = {}
        count = 0
        while not ("result" in res) and count < 5:
            res = k.query_private('AddOrder', {'pair': 'ZECEUR',
                                               'type': 'sell',
                                               'ordertype': 'market',
                                               'trading_agreement': 'agree',
                                               'price': str(price),
                                               'volume': str(amount_forSale)})
            count += 1
        if not ("result" in res):
            return print("request AddOrder failed")
        print(res)
        if not res['error']:
            print("下达出售订单，价格为" + str(price) + '数量为：' + str(amount_forSale))
            return "下达出售订单，价格为" + str(price) + '数量为：' + str(amount_forSale)


if __name__ == "__main__":
    # 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数
    # 第二个参数以某种人为的方式衡量时间
    schedule = sched.scheduler(time.time, time.sleep)
    timing_exe('No command', 900)
