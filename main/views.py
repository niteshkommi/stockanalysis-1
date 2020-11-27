from django.shortcuts import render,redirect
import pandas as pd
import numpy as np
import time
import os
from nsepython import *
from datetime import date
from dateutil.relativedelta import relativedelta
from bfxhfindicators import Stochastic
from django.contrib.auth.decorators import login_required

entryTargets = []


def isDoji(out):
    wicks = abs(out[1] - out[2])
    body = abs(out[0] - out[3])
    percentage = 100 / (wicks/body)
    if (percentage <= 33):
        return out


def stochastic(candles):
    stochValues = []
    iStoch = Stochastic(5, 3, 3)
    for candle in candles:
        iStoch.add(candle)
        stochValues.append(iStoch.v())
    return (stochValues)


def HEIKIN(O, H, L, C, oldO, oldC):
    HA_Open = (oldO + oldC)/2
    HA_Close = (O + H + L + C)/4
    elements = np.array([H, L, HA_Open, HA_Close])
    HA_High = elements.max(0)
    HA_Low = elements.min(0)
    out = [HA_Open, HA_High, HA_Low, HA_Close]
    return out


def maxMin(fiboRange):
    rangeMax = max(max(x) if isinstance(x, list) else x for x in fiboRange)
    rangeMin = min(min(x) if isinstance(x, list) else x for x in fiboRange)
    return (rangeMax, rangeMin)


def fibonacciDown(price_max, price_min):
    tempList = []

    diff = price_max - price_min
    level0 = price_max
    level1 = price_max - 0.236 * diff
    level2 = price_max - 0.382 * diff
    level3 = price_max - 0.50 * diff
    level4 = price_max - 0.618 * diff
    level5 = price_max - 0.786 * diff

    tempList = [level1, level2, level3, level4, level5, level0]
    entryTargets.append(tempList)

    return entryTargets


def fibonacciUp(price_max, price_min):
    tempList = []

    diff = price_max - price_min
    level0 = price_max - 1.0 * diff
    level1 = price_max - 0.786 * diff
    level2 = price_max - 0.618 * diff
    level3 = price_max - 0.50 * diff
    level4 = price_max - 0.366 * diff
    level5 = price_max - 0.236 * diff

    tempList = [level1, level2, level3, level4, level5, level0]
    entryTargets.append(tempList)

    return entryTargets


@login_required(login_url='/')
def dashboard(request):

    symbols = ['SBIN','HDFCBANK']
    list_test_buy = []
    list_test_sell = []

    for symbol in symbols:
        n = 48
        j = 0
        hikenCandle = []
        doji = []
        swing = []
        dateTime = []
        today_date = date.today().strftime("%d-%m-%Y")
        six_months = date.today() - relativedelta(months=+6)
        six_months = six_months.strftime("%d-%m-%Y")

        try:
            fetch_url = "https://www.nseindia.com/api/historical/cm/equity?symbol=" + \
                str(symbol)+"&series=[%22EQ%22]&from=" + \
                str(six_months)+"&to="+str(today_date)+""
            historical_data = nsefetch(fetch_url)
            historical_data = pd.DataFrame(historical_data['data'])
            openPrice = historical_data['CH_OPENING_PRICE']
            highPrice = historical_data['CH_TRADE_HIGH_PRICE']
            lowPrice = historical_data['CH_TRADE_LOW_PRICE']
            closePrice = historical_data['CH_CLOSING_PRICE']
            curr_date = historical_data['mTIMESTAMP'][0]

            candle = HEIKIN(openPrice[n], highPrice[n],
                            lowPrice[n], closePrice[n], openPrice[n+1],
                            closePrice[n+1])

            hikenCandle.append(candle)

            for i in range(n-1, -1, -1):
                candle = HEIKIN(openPrice[i], highPrice[i], lowPrice[i],
                                closePrice[i], hikenCandle[j][0], hikenCandle[j][3])

                hikenCandle.append(candle)
                dateTime.append(historical_data['mTIMESTAMP'][i])
                j += 1

            stochasticHiken = stochastic(hikenCandle)
            del stochasticHiken[:4]

            for i in hikenCandle:
                doji.append(isDoji(i))

            del doji[:4]
            del dateTime[:3]

            for i in range(1, len(stochasticHiken)):
                if ((stochasticHiken[i]['k'] < stochasticHiken[i]['d']) and stochasticHiken[i-1]['k'] > stochasticHiken[i-1]['d']) or ((stochasticHiken[i]['k'] > stochasticHiken[i]['d']) and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    swing.append(i)

            for i in range(len(stochasticHiken)):
                if (stochasticHiken[i]['k'] < stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] > stochasticHiken[i-1]['d']):
                    try:
                        if doji[i]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex != 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciDown(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                        elif doji[i-1] or doji[i+1] or doji[i+2]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex != 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciDown(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                    except (IndexError):
                        pass
                elif (stochasticHiken[i]['k'] > stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    try:
                        if doji[i]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex > 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciUp(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                        elif doji[i-1] or doji[i+1] or doji[i+2]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex > 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciUp(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                    except (IndexError):
                        pass

        except (KeyError):
            keyerror = "Please provide a correct ticker"
            context = {"keyerror": keyerror}

        for i in range(len(testList[-1])):
            testList[-1][i] = round(testList[-1][i],2)

        testList[-1].append(historical_data['CH_CLOSING_PRICE'][0])
        testList[-1].append(symbol)


        if testList[-1][0] > testList[-1][5] and callTime == curr_date:
            list_test_buy.append(testList[-1])
        elif testList[-1][0] < testList[-1][5] and callTime == curr_date:
            list_test_sell.append(testList[-1])


    context = {
        "list_buy": list_test_buy,
        "list_sell": list_test_sell
    }
    return render(request, 'main/dashboard.html', context)


@login_required(login_url='/')
def search(request):
    if request.method == 'POST':

        symbol = request.POST.get('ticker')

        n = 48
        j = 0
        hikenCandle = []
        doji = []
        swing = []
        dateTime = []
        today_date = date.today().strftime("%d-%m-%Y")
        six_months = date.today() - relativedelta(months=+6)
        six_months = six_months.strftime("%d-%m-%Y")

        try:
            fetch_url = "https://www.nseindia.com/api/historical/cm/equity?symbol=" + \
                str(symbol)+"&series=[%22EQ%22]&from=" + \
                str(six_months)+"&to="+str(today_date)+""
            historical_data = nsefetch(fetch_url)
            historical_data = pd.DataFrame(historical_data['data'])
            openPrice = historical_data['CH_OPENING_PRICE']
            highPrice = historical_data['CH_TRADE_HIGH_PRICE']
            lowPrice = historical_data['CH_TRADE_LOW_PRICE']
            closePrice = historical_data['CH_CLOSING_PRICE']

            candle = HEIKIN(openPrice[n], highPrice[n],
                            lowPrice[n], closePrice[n], openPrice[n+1],
                            closePrice[n+1])

            hikenCandle.append(candle)

            for i in range(n-1, -1, -1):
                candle = HEIKIN(openPrice[i], highPrice[i], lowPrice[i],
                                closePrice[i], hikenCandle[j][0], hikenCandle[j][3])

                hikenCandle.append(candle)
                dateTime.append(historical_data['mTIMESTAMP'][i])
                j += 1

            stochasticHiken = stochastic(hikenCandle)
            del stochasticHiken[:4]

            for i in hikenCandle:
                doji.append(isDoji(i))

            del doji[:4]
            del dateTime[:3]

            for i in range(1, len(stochasticHiken)):
                if ((stochasticHiken[i]['k'] < stochasticHiken[i]['d']) and stochasticHiken[i-1]['k'] > stochasticHiken[i-1]['d']) or ((stochasticHiken[i]['k'] > stochasticHiken[i]['d']) and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    swing.append(i)

            for i in range(len(stochasticHiken)):
                if (stochasticHiken[i]['k'] < stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] > stochasticHiken[i-1]['d']):
                    try:
                        if doji[i]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex != 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciDown(
                                        temp[0], temp[1])
                                    # temp = (doji[i][1] * 0.3) / 100
                                    # stopLoss = (doji[i][1] + temp)
                                    lastCandle = i
                                    callTime = dateTime[i]
                        elif doji[i-1] or doji[i+1] or doji[i+2]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex != 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciDown(
                                        temp[0], temp[1])
                                    # temp = (doji[i-1][1] * 0.3) / 100
                                    # stopLoss = (doji[i-1][1] + temp)
                                    lastCandle = i
                                    callTime = dateTime[i]
                    except (IndexError):
                        pass
                elif (stochasticHiken[i]['k'] > stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    try:
                        if doji[i]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex > 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciUp(
                                        temp[0], temp[1])
                                    # temp = (doji[i][2] * 0.3) / 100
                                    # stopLoss = (doji[i][2] - temp)
                                    lastCandle = i
                                    callTime = dateTime[i]
                        elif doji[i-1] or doji[i+1] or doji[i+2]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex > 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciUp(
                                        temp[0], temp[1])
                                    # temp = (doji[i-1][2] * 0.3) / 100
                                    # stopLoss = (doji[i-1][2] - temp)
                                    lastCandle = i
                                    callTime = dateTime[i]
                    except (IndexError):
                        pass

            try:
                h_l = maxMin(hikenCandle[lastCandle + 5:])
                if (testList[-1][0] > testList[-1][5]):
                    if (h_l[0] >= testList[-1][1] and h_l[0] < testList[-1][2]):
                        status = "Target 1 Reached"
                    elif (h_l[0] >= testList[-1][2] and h_l[0] < testList[-1][3]):
                        status = "Target 2 Reached"
                    elif (h_l[0] >= testList[-1][3]) and h_l[0] < testList[-1][4]:
                        status = "Target 3 Reached"
                    elif (h_l[0] >= testList[-1][4]):
                        status = "Final Target Reached"
                    elif (h_l[1] <= testList[-1][5]):
                        status = "Stop Loss has occured"
                    else:
                        status = "Awaiting Targets"
                else:
                    if (h_l[1] <= testList[-1][1] and h_l[1] > testList[-1][2]):
                        status = "Target 1 Reached"
                    elif (h_l[1] <= testList[-1][2] and h_l[1] > testList[-1][3]):
                        status = "Target 2 Reached"
                    elif (h_l[1] <= testList[-1][3]) and h_l[1] > testList[-1][4]:
                        status = "Target 3 Reached"
                    elif (h_l[1] <= testList[-1][4]):
                        status = "Final Target Reached"
                    elif (h_l[0] >= testList[-1][5]):
                        status = "Stop Loss has occured"
                    else:
                        status = "Awaiting Targets"

                context = {
                    "symbol": historical_data['CH_SYMBOL'][1],
                    "date": callTime,
                    "call": round(testList[-1][0], 2),
                    "stop_loss": round(testList[-1][5], 2),
                    "target_1": round(testList[-1][1], 2),
                    "target_2": round(testList[-1][2], 2),
                    "target_3": round(testList[-1][3], 2),
                    "target_4": round(testList[-1][4], 2),
                    "status": status,
                }
            except(ValueError):
                status = "Awaiting Targets"
                context = {
                    "symbol": historical_data['CH_SYMBOL'][1],
                    "date": callTime,
                    "call": round(testList[-1][0], 2),
                    "stop_loss": round(testList[-1][5], 2),
                    "target_1": round(testList[-1][1], 2),
                    "target_2": round(testList[-1][2], 2),
                    "target_3": round(testList[-1][3], 2),
                    "target_4": round(testList[-1][4], 2),
                    "status": status,
                    }


        except (KeyError):
            keyerror = "Please provide a correct ticker"
            context = { "keyerror": keyerror }
    else:
        context = { "none": None }


    return render(request, 'main/search.html',context)
