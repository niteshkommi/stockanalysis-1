import pandas as pd
import numpy as np
import time, os
from nsepython import *
from datetime import date
from dateutil.relativedelta import relativedelta
from bfxhfindicators import Stochastic

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
    print(rangeMax, rangeMin)
    return (rangeMax, rangeMin)


def fibonacciDown(price_max, price_min):
    tempList = []

    diff = price_max - price_min
    level1 = price_max - 0.236 * diff
    level2 = price_max - 0.382 * diff
    level3 = price_max - 0.50 * diff
    level4 = price_max - 0.618 * diff
    level5 = price_max - 0.786 * diff

    tempList = [level1, level2, level3, level4, level5]
    entryTargets.append(tempList)

    return entryTargets


def fibonacciUp(price_max, price_min):
    tempList = []

    diff = price_max - price_min
    level1 = price_max - 0.786 * diff
    level2 = price_max - 0.618 * diff
    level3 = price_max - 0.50 * diff
    level4 = price_max - 0.366 * diff
    level5 = price_max - 0.236 * diff

    tempList = [level1, level2, level3, level4, level5]
    entryTargets.append(tempList)

    return entryTargets

def main():
    # start = time.time()
    while(True):
        n = 48
        j = 0
        hikenCandle = []
        doji = []
        swing = []
        dateTime = []
        today_date = date.today().strftime("%d-%m-%Y")
        six_months = date.today() - relativedelta(months=+6)
        six_months = six_months.strftime("%d-%m-%Y")

        print("----- STOCK MARKET ANALYSIS -----")
        print("Press key q to exit")
        print()
        symbol = input("Enter a stock name:\n").upper()

        if symbol == "Q":
            os.system(['clear', 'cls'][os.name == 'nt'])
            exit()
        
        else:
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
                    if doji[i]:
                        if i!= 0:
                            swingIndex = swing.index(i)
                            if swingIndex != 0:
                                temp = maxMin(
                                    hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                testList = fibonacciDown(temp[0], temp[1])
                                temp = (doji[i][1] * 0.3) / 100
                                stopLoss = (doji[i][1] + temp)
                                callTime = dateTime[i]
                    elif doji[i-1]:
                        swingIndex = swing.index(i)
                        if swingIndex != 0:
                            temp = maxMin(
                                hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                            testList = fibonacciDown(temp[0], temp[1])
                            temp = (doji[i-1][1] * 0.3) / 100
                            stopLoss = (doji[i-1][1] + temp)
                            callTime = dateTime[i]
                elif (stochasticHiken[i]['k'] > stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    if doji[i]:
                        if i!= 0:
                            swingIndex = swing.index(i)
                            if swingIndex > 0:
                                temp = maxMin(
                                    hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                testList = fibonacciUp(temp[0], temp[1])
                                temp = (doji[i][2] * 0.3) / 100
                                stopLoss = (doji[i][2] - temp)
                                callTime = dateTime[i]
                    elif doji[i-1]:
                        if i != 0:
                            swingIndex = swing.index(i)
                            if swingIndex > 0:
                                temp = maxMin(
                                    hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                testList = fibonacciUp(temp[0], temp[1])
                                temp = (doji[i-1][2] * 0.3) / 100
                                stopLoss = (doji[i-1][2] - temp)
                                callTime = dateTime[i]

            os.system(['clear', 'cls'][os.name == 'nt'])  
            print("-----------------------------------------")
            print("|\t",historical_data['CH_SYMBOL'][1],"- DATE:", callTime, "\t|")
            print("-----------------------------------------")
            
            if (testList[-1][0] > stopLoss):
                print("| Buy Above\t|\t", round(testList[-1][0], 2), "\t|")
            else:
                print("| Sell Below\t|\t", round(testList[-1][0], 2), "\t|")

            print("| Stop Loss\t|\t", round(stopLoss, 2), "\t|")
            print("| Target-1 \t|\t", round(testList[-1][1],2), "\t|")
            print("| Target-2 \t|\t", round(testList[-1][2],2), "\t|")
            print("| Target-3 \t|\t", round(testList[-1][3],2), "\t|")
            print("| Target-4 \t|\t", round(testList[-1][4],2), "\t|")
            print("-----------------------------------------")

            if (testList[-1][0] > stopLoss):
                if (lowPrice[0] <= stopLoss):
                    print("Stop Loss has occured")
                elif (highPrice[0] >= testList[-1][1] and highPrice[0] < testList[-1][2]):
                    print("Target 1 Reached")
                elif (highPrice[0] >= testList[-1][2] and highPrice[0] < testList[-1][3]):
                    print("Target 2 Reached")
                elif (highPrice[0] >= testList[-1][3]) and highPrice[0] < testList[-1][4]:
                    print("Target 3 Reached")
                elif (highPrice[0] >= testList[-1][4]):
                    print("Final Target Reached")
                else:
                    print("Awaiting Targets")
            else:
                if (highPrice[0] >= stopLoss):
                    print("Stop Loss has occured")
                elif (lowPrice[0] <= testList[-1][1] and lowPrice[0] > testList[-1][2]):
                    print("Target 1 Reached")
                elif (lowPrice[0] <= testList[-1][2] and lowPrice[0] > testList[-1][3]):
                    print("Target 2 Reached")
                elif (lowPrice[0] <= testList[-1][3]) and lowPrice[0] > testList[-1][4]:
                    print("Target 3 Reached")
                elif (lowPrice[0] <= testList[-1][4]):
                    print("Final Target Reached")
                else:
                    print("Awaiting Targets")
            print()
        
        # end = time.time()
        # print(f"Runtime of the program is {end - start}")

main()
