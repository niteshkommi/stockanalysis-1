import numpy

def HEIKIN(O, H, L, C, oldO, oldC):
    HA_Open = (oldO + oldC)/2
    HA_Close = (O + H + L + C)/4
    elements = numpy.array([H, L, O, C])
    HA_High = elements.max(0)
    HA_Low = elements.min(0)
    out = numpy.array([HA_Open, HA_High, HA_Low, HA_Close])
    return out

def isDoji(out):
    wicks = abs(out[1] - out[2])
    body = abs(out[0] - out[3])
    percentage = 100 / (wicks/body)
    if (percentage <= 33):
        print("DOJI")
        print("High:",out[1])
        print("Low:",out[2])
    else:
        print("Not a doji")

def main():
    CANDLE = HEIKIN(7164, 7175, 7005, 7052.8, 7231.04, 7168.11)
    print(CANDLE)
    isDoji(CANDLE)

main()
