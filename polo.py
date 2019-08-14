"""

api calls using Poloniex, cryptocompare, coingecko Brasil Bitcoin, and google trends

"""
from config import *
from cryptocompy import coin, price
from matplotlib import pyplot as plt
from poloniex import Poloniex
from pprint import pprint
from pycoingecko import CoinGeckoAPI
from pytrends.request import TrendReq
from telethon import TelegramClient, events, sync
import requests
import pandas as pd
import pymongo
import talib as ta


polo = Poloniex(key=polo_key, secret=polo_secret)
cg = CoinGeckoAPI()
pytrends = TrendReq(hl='en-US', tz=360)


##################### {[ BRASIL BITCOIN ]} #####################


def get_bitbrasil_balance():
    url = "https://brasilbitcoin.com.br/api/get_balance"
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    montante = 0
    for coin, quant in data.items():
        print("[", coin.upper(), "]", quant)
    montante = float(data["brl"]) + (float(data["btc"]) * get_estimate_price("btc"))
    # print(r.text)
    print("[ TOTAL ]", montante)
    return montante

def get_estimate_price(coin, display=False):
    url = "https://brasilbitcoin.com.br/api/estimate/sell/{}/1".format(coin.upper())
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    price = float(data["message"])
    if display:
        print(r.text)
    return price

def real_to_btc(r):
    btc_price = get_estimate_price("BTC")
    print(r / btc_price)
    return (r / btc_price)

def buy_BRLBTC(quantity): # in reais
    price_of_one = get_estimate_price("BTC")
    url = "https://brasilbitcoin.com.br/api/create_order"
    header = brasil_bit_header
    payload = {"coin_pair" : "BRLBTC",
                "type" : "buy",
                "order_type" : "market",
                "amount" : real_to_btc(quantity),
                "price" : price_of_one
                }
    r = requests.post(url, data=payload, headers=header)
    print(r.text)
    return r

def buy_all():
    montante = get_bitbrasil_balance()
    price_of_one = get_estimate_price()
    print(montante)
    r = buy_BRLBTC(montante - 10)
    return r

def get_open_orders():
    url = "https://brasilbitcoin.com.br/api/my_orders"
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    print(r.text)
    return data

def check_orders(order_id):
    url = "https://brasilbitcoin.com.br/api/check_order/{}".format(order_id)
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    print(r.text)
    return data

def get_transactions():
    url = "https://brasilbitcoin.com.br/api/my_transactions"
    header = BrasilBit_header
    r = requests.get(url, headers=header)
    data = r.json()
    print(r.text)
    return(data)


##################### {[ POLONIEX ]} #####################


def print_polo_balance():
    # print anything that isnt zero
    balance = polo.returnBalances()
    print(balance)
    return balance

def get_polo_price(pair):
    price = polo.returnTicker()
    print(price[pair])

def get_polo_coins():
    coins = []
    PoloniexCoins = polo.returnTicker()
    for pair in PoloniexCoins:
        tick = pair.split("_")
        for coin in tick:
            if coin not in coins:
                coins.append(coin)
    return coins


##################### {[ CRIPTOCOMPARE ]} {[ COINGECKO ]} #####################


def get_day_history(ticker):
    hist = price.get_historical_data(ticker, 'USD', 'minute', aggregate=1, limit=900)
    data = pd.DataFrame.from_dict(hist)
    print(data.head())
    print(data.tail())
    plt.plot(data.time, data.close, label="Close")
    plt.plot(data.time, data.high, label="High")
    plt.plot(data.time, data.open, label="Open")
    plt.legend()
    plt.grid(True)
    plt.show()
    return data

def get_coin_price_by_date(ticker, date):   # dd-mm-yyyy
    price = cg.get_coin_history_by_id(ticker, date, localization="false")
    print(price)

def get_weekly_data(ticker, plot=False):
    hist = price.get_historical_data(ticker, 'USD', 'day', aggregate=1, limit=7)
    data = pd.DataFrame.from_dict(hist)
    if plot:
        print(data.head())
        print(data.tail())
        plt.plot(data.time, data.close, label="Close")
        plt.plot(data.time, data.high, label="High")
        plt.plot(data.time, data.open, label="Open")
        plt.legend()
        plt.grid(True)
        plt.show()
    return data

def get_hundred_day_data(ticker, plot=False):
    hist = price.get_historical_data(ticker, 'USD', 'day', aggregate=1, limit=99)
    data = pd.DataFrame.from_dict(hist)
    if plot:
        print(data.head())
        print(data.tail())
        plt.plot(data.time, data.close, label="Close")
        plt.plot(data.time, data.high, label="High")
        plt.plot(data.time, data.open, label="Open")
        plt.legend()
        plt.grid(True)
        plt.show()
    return data


##################### {[ GOOGLE TRENDS ]} #####################


def get_pytrend_interest(display=False):
    kw_list = ["BTC USD", "buy bitcoin"]
    pytrends.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='', gprop='')
    data = pytrends.interest_over_time()
    if display:
        print(data.to_string())
    return data


##################### {[ FEAR & GREED ]} #####################


def get_greed_fear_index(display=False, backtest=False):
    url = "https://api.alternative.me/fng/?limit=100&format=json&date_format=cn"
    r = requests.get(url)
    j = r.json()
    data = pd.DataFrame(j["data"])
    data = data.astype({'value': 'int32'})
    data = data.reindex(index=data.index[::-1])
    data = data.reset_index()
    data.drop(["index"], axis=1, inplace=True)
    if display:
        print(data)
        data.plot()
        plt.show()
        print(data.value[len(data)-1])
    if backtest:
        return data
    return(data.value[len(data)-1])


##################### {[ STARTEGIES & ALGORITHMS ]} #####################


def find_change(ticker, display=False):
    data = get_weekly_data(ticker)
    data["change"] = data.close - data.close.shift(1)
    data["percentChange"] = (data.close / data.close.shift(1) - 1) * 100
    if display:
        print(data.head())
        print(data.tail())
    return data

def find_dip(ticker):
    data = find_change(ticker)
    data["buy"] = 0
    data.loc[(data.percentChange.shift(1) < -6.5) & (data.percentChange > -2) & (data.percentChange < 2), "buy"] = 1
    print(data.to_string())
    return data

def get_rsi(ticker, display=False):
    data = find_change(ticker)
    data["BuySell"] = 0
    data["rsi"] = ta.RSI(data["close"].values)
    data.loc[(data.rsi >= 70), "BuySell"] = -1
    data.loc[(data.rsi <= 30), "BuySell"] = 1
    if display:
        print(data.to_string())
    return(data)

def trend_algo(ticker):
    prices = find_change(ticker)
    # prices["time"] = prices["time"].str[:10]
    prices.rename(columns = {'time':'date'}, inplace = True)
    prices.index = prices.date
    prices.drop(["date", "volumefrom", "volumeto"], axis = 1, inplace = True)
    trends = get_pytrend_interest()
    trends["ratio"] = 0
    trends.ratio = trends["buy bitcoin"] / trends["BTC USD"]
    ratio = trends.ratio.mean()
    last_change = prices.change[-1]
    # print(ratio)
    # print(prices)
    if ratio * 100 > 34 and last_change > 80:
        return True
    else:
        return False

    # data = prices.join(trends)
    # data.drop(["close", "high", "low", "open", "volumefrom", "volumeto", "BTC USD", "buy bitcoin", "isPartial"], axis = 1, inplace = True)
    # data['ratio MA'] = data.rolling(window=24)["ratio"].mean()


##################### {[ BACKTESTING ]} #####################


def greed_fear_backtest(plot=False):
    gf_index = get_greed_fear_index(backtest=True)
    price = get_hundred_day_data("BTC")
    gf_index = gf_index.shift(1)
    data = price.join(gf_index)
    data["buy"] = 0
    data["sell"] = 0
    data.loc[(data.value < 30), "buy"] = data.close
    data.loc[(data.value > 60) & (data.close - data.open > 600), "sell"] = data.close
    print(data.to_string())

    if plot:
        fig, ax1 = plt.subplots()

        color = 'tab:red'
        ax1.set_xlabel("Time (D)")
        ax1.set_ylabel('BTC', color=color)
        ax1.scatter(data.time, data.buy, color="blue")
        ax1.scatter(data.time, data.sell, color="red")
        ax1.plot(data.time, price.close, color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()

        color = 'tab:blue'
        ax2.set_ylabel('Index', color=color)
        ax2.plot(data.value, label="index", color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()
        plt.grid(True)
        plt.show()


##################### {[ IMPLEMENTATION ]} #####################


def trend_trade():
    while True:
        if trend_algo("BTC"):
            print("BUY")
        else:
            print("HOLD/SELL")

def greed_fear_trade():
    # Buy below thirty
    # Sell Above ninety or 
    # Sell over 60, when last btc change was over 5% up...
    # Spikes up more than 40% in last 10 days
    pass


##################### {[ TELEGRAM ]} #####################


def send_msg(msg):
    with TelegramClient('Simba', telegram_id, telegram_hash) as client:
        client.send_message('jzsig', '{}'.format(msg))


##################### {[ FUNCTION CALLS ]} #####################

        
# get_weekly_data("BTC", True)
# get_polo_coins()
# get_day_history("BTC")
# get_polo_price("BTC_ETH")
# find_dip("BTC")
# bitbrasil_balance()
# get_rsi("BTC", True)
# get_montante("BTC")
# get_bitbrasil_balance()
# get_transactions()
# get_estimate_price("BTC")
# buy_all_()
# real_to_btc(100)
# buy_BRLBTC(100)
# get_open_orders()
# check_orders(get_open_orders()[-1]["id"])
# get_pytrend_interest()
# send_msg(get_bitbrasil_balance())
# trend_algo("BTC")
# get_greed_fear_index(True)
greed_fear_backtest(plot=True)
