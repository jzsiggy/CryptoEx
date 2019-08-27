from assets import *
from paper import Paper
import time


paper = Paper(0.0200000, 1000.00)

def day_trade():
    rsi = get_rsi(get_minute_data("BTC", 30, plot=False), display=False)
    bbp = get_bbp(get_minute_data("BTC", 30, plot=False), plot=False)
    data = rsi.merge(bbp)
    now = data.loc[len(data)-1]
    # print(now)

    if (now.rsi < 35) and (now.close >= now.lower_band - 12 or now.close <= now.lower_band + 12):
        print("[ SELL ]")
        paper.sell_btc(now.close, paper.balance_btc)
    elif (now.rsi > 60) and (now.close >= now.upper_band - 12 or now.close <= now.upper_band + 12):
        print("[ BUY ]")
        paper.buy_btc(now.close, paper.balance_reais)
    print("BALANCE \n [ BTC ] : {0} \n [ REAIS ] : {1}".format(paper.balance_btc, paper.balance_reais))

while True:
    day_trade()
