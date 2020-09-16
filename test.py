import pandas as pd
import numpy, time

def isDoji(out):
    wicks = abs(out[1] - out[2])
    body = abs(out[0] - out[3])
    percentage = 100 / (wicks/body)
    if (percentage <= 33):
    # if(abs(out[0]- out[3]) <= (out[1]-out[2])*0.1):
        print("")
        print("***** DOJI *****")
        print("High:", out[1])
        print("Low:", out[2])
        print("***************")
        print("")
        return 0
    else:
        print("Not a DOJI:",end="")
        if(abs(out[3]-out[1]) > abs(out[2]-out[0])):
            print("BLUE CANDLE")
        else:
            print("RED CANDLE")


def HEIKIN(O, H, L, C, oldO, oldC):
    HA_Open = (oldO + oldC)/2
    HA_Close = (O + H + L + C)/4
    elements = numpy.array([H, L, O, C])
    HA_High = elements.max(0)
    HA_Low = elements.min(0)
    out = [HA_Open, HA_High, HA_Low, HA_Close]
    return out


def main():
    start = time.time()
    df = pd.read_csv('maruti.csv')
    df = df.sort_values('Date' , ascending= False)
    df.reset_index(drop = True, inplace = True)
    n = 9
    j = 0
    temp = []
    
    candle = HEIKIN(df['Open'][n], df['High'][n], df['Low'][n],
                    df['Close'][n], df['Open'][n+1], df['Close'][n+1])
    temp.append(candle)

    for i in range(n-1,-1,-1):
        candle = HEIKIN(df['Open'][i], df['High'][i], df['Low'][i],
               df['Close'][i], temp[j][0], temp[j][3])
        temp.append(candle)
        j += 1

    temp.reverse()
    for j in temp:
        isDoji(j)
    end = time.time()
    print(f"Runtime of the program is {end - start}")

main()
