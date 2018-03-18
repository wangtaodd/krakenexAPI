#!/usr/bin/env python
# coding=utf-8

# This file is part of krakenex.
# Licensed under the Simplified BSD license. See `examples/LICENSE.txt`.

# Get balance available for trading/withdrawal (not on orders).
#
# NOTE: Assumes regular orders. Margin positions are not taken into account!
#
# FIXME: Also shows how current krakenex usage has too much sugar.
import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))
import krakenex
import time, sched

# 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数
# 第二个参数以某种人为的方式衡量时间
schedule = sched.scheduler(time.time, time.sleep)


def perform_command(cmd,inc):
    # 安排inc秒后再次运行自己，即周期运行
    schedule.enter(inc, 0, perform_command, (cmd,inc))
    autoSale()


def timming_exe(cmd,inc):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(10, 0, perform_command, (cmd,inc))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()


def autoSale():
    k = krakenex.API()
    k.load_key('kraken.key')

    balance = k.query_private('Balance')
    print ('持有ZEC数量：'+balance['result']['XZEC'])
    amount_Total = float(balance['result']['XZEC'])
    openOrders = k.query_private('OpenOrders')['result']['open']

    amount_onSale = 0
    for i in openOrders:
        if openOrders[i]['descr']['type'] == 'sell':
            amount_onSale = amount_onSale+float(openOrders[i]['vol'])
    print("销售中ZEC数量："+str(amount_onSale))
    amount_forSale = amount_Total-amount_onSale
    print("可销售ZEC数量："+str(amount_forSale))

    """
    pair = asset pair
    type = type of order (buy/sell)
    ordertype = order type:
        market
        limit (price = limit price)
        stop-loss (price = stop loss price)
        take-profit (price = take profit price)
        stop-loss-profit (price = stop loss price, price2 = take profit price)
        stop-loss-profit-limit (price = stop loss price, price2 = take profit price)
        stop-loss-limit (price = stop loss trigger price, price2 = triggered limit price)
        take-profit-limit (price = take profit trigger price, price2 = triggered limit price)
        trailing-stop (price = trailing stop offset)
        trailing-stop-limit (price = trailing stop offset, price2 = triggered limit offset)
        stop-loss-and-limit (price = stop loss price, price2 = limit price)
        settle-position
    price = price (optional.  dependent upon ordertype)
    price2 = secondary price (optional.  dependent upon ordertype)
    volume = order volume in lots
    leverage = amount of leverage desired (optional.  default = none)
    oflags = comma delimited list of order flags (optional):
        viqc = volume in quote currency (not available for leveraged orders)
        fcib = prefer fee in base currency
        fciq = prefer fee in quote currency
        nompp = no market price protection
        post = post only order (available when ordertype = limit)
    starttm = scheduled start time (optional):
        0 = now (default)
        +<n> = schedule start time <n> seconds from now
        <n> = unix timestamp of start time
    expiretm = expiration time (optional):
        0 = no expiration (default)
        +<n> = expire <n> seconds from now
        <n> = unix timestamp of expiration time
    userref = user reference id.  32-bit signed number.  (optional)
    validate = validate inputs only.  do not submit order (optional)
    
    optional closing order to add to system when order gets filled:
        close[ordertype] = order type
        close[price] = price
        close[price2] = secondary price
    """
    priceRes = k.query_public('Ticker',{'pair':'ZECEUR'})
    print('最新成交价格：'+priceRes['result']['XZECZEUR']['c'][0])
    lastPrice=float(priceRes['result']['XZECZEUR']['c'][0])
    price =max(195, lastPrice)
    if (amount_forSale>0.03):
        amount_forSale = int(amount_forSale*100)/100
        res = k.query_private('AddOrder', {'pair': 'ZECEUR',
                                           'type': 'sell',
                                           'ordertype': 'limit',
                                           'price': str(price),
                                           'volume': str(amount_forSale)})
        print("下达出售订单，价格为"+str(price)+'数量为：'+str(amount_forSale))
    # print (openOrders['result']['open'])
    # print(openOrders['result']['open']['descr'])
    #res=k.query_private('CancelOrder',{'txid':'OTFSS2-BYM3K-FTZQXK'})
    #print(res)

if __name__ == "__main__":
    timming_exe('No command',900)
