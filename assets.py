"""

api calls using Poloniex, cryptocompare, coingecko Brasil Bitcoin, and google trends

"""
from config import *
from cryptocompy import coin, price
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from poloniex import Poloniex
from pprint import pprint
from pycoingecko import CoinGeckoAPI
from pymongo import MongoClient
from pytrends.request import TrendReq
from telethon import TelegramClient, events, sync
import numpy as np
import requests
import pandas as pd
import talib as ta


polo = Poloniex(key=polo_key, secret=polo_secret)
cg = CoinGeckoAPI()
pytrends = TrendReq(hl='en-US', tz=360)
client = MongoClient("mongodb://localhost:27017/")
db = client["BTC_db"]
data = db["minute_data"]


##################### {[ BRASIL BITCOIN ]} #####################


def get_bitbrasil_balance(display=False):
    url = "https://brasilbitcoin.com.br/api/get_balance"
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    montante = float(data["brl"]) + (float(data["btc"]) * get_estimate_price("btc"))
    if display:
        for coin, quant in data.items():
            print("[", coin.upper(), "]", quant)
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
                "order_type" : "limited",
                "amount" : real_to_btc(quantity),
                "price" : price_of_one
                }
    r = requests.post(url, data=payload, headers=header)
    print(r.text)
    return r

def sell_BRLBTC(quantity): # in reais
    price_of_one = get_estimate_price("BTC")
    url = "https://brasilbitcoin.com.br/api/create_order"
    header = brasil_bit_header
    payload = {"coin_pair" : "BRLBTC",
                "type" : "sell",
                "order_type" : "limited",
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

def get_transactions(display=False):
    url = "https://brasilbitcoin.com.br/api/my_transactions"
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    if display:
        for transaction in data:
            print(transaction)
    return data

def cancel_order(order_id):
    url = 'https://brasilbitcoin.com.br/api/remove_order/{}'.format(order_id)
    header = brasil_bit_header
    r = requests.get(url, headers=header)
    data = r.json()
    print(data)
    return data


##################### {[ BINANCE ]} #####################


def get_binance_close(pair):
  close_price_list = []
  data = requests.get('https://www.binance.com/api/v3/klines?symbol={}&interval=1d'.format(pair))
  ohlc = data.text
  ohlc = ohlc[2:-2].split("],[") 
  for element in ohlc:
    element = element.split(',')
    close_price_list.append(float(element[4][1:-1]))
  df = pd.DataFrame({ "close" : close_price_list })
  # print(df)
  return df


##################### {[ POLONIEX ]} #####################


def print_polo_balance():
    # print anything that isnt zero
    balance = polo.returnBalances()
    print(balance)
    return balance

def get_polo_price(pair):
    price = polo.returnTicker()
    print(price[pair])
    return price[pair]

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


def get_minute_data(ticker, quantity, plot=False, display=False):
    hist = price.get_historical_data(ticker, 'USD', 'minute', aggregate=1, limit=quantity)
    data = pd.DataFrame.from_dict(hist)
    if display:
        print(data.head())
        print(data.tail())
    if plot:
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
    return price

def get_daily_data(ticker, quantity, plot=False, display=False):
    hist = price.get_historical_data(ticker, 'USD', 'day', aggregate=1, limit=quantity)
    data = pd.DataFrame.from_dict(hist)
    if display:
        print(data.head())
        print(data.tail())
    if plot:
        plt.plot(data.time, data.close, label="Close")
        plt.plot(data.time, data.high, label="High")
        plt.plot(data.time, data.open, label="Open")
        plt.legend()
        plt.grid(True)
        plt.show()
    return data

def get_crypto_compy_coin_list():
    coins = coin.get_coin_list(coins='all')
    symbols = list(coins.keys())
    return(symbols)


##################### {[ GOOGLE TRENDS ]} #####################


def get_pytrend_interest(display=False):
    kw_list = ["BTC USD", "buy bitcoin"]
    pytrends.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='', gprop='')
    data = pytrends.interest_over_time()
    if display:
        print(data.to_string())
    return data


##################### {[ FEAR & GREED ]} #####################


def get_greed_fear_index(limit=100, display=False, backtest=False):
    url = "https://api.alternative.me/fng/?limit={}&format=json&date_format=cn".format(limit)
    r = requests.get(url)
    j = r.json()
    data = pd.DataFrame(j["data"])
    data = data.astype({'value': 'int32'})
    data = data.reindex(index=data.index[::-1])
    data = data.reset_index()
    data["indicator_change"] = (data.value - data.value.shift(1))
    data.drop(["index"], axis=1, inplace=True)
    if display:
        print(data)
        data.plot()
        plt.show()
        print(data.value[len(data)-1], data.indicator_change[len(data)-1])
    if backtest:
        return data
    return(data.value[len(data)-1], data.indicator_change[len(data)-1])


##################### {[ STARTEGIES & ALGORITHMS ]} #####################


#                                                                                       #
#  THE PARAMETERS FOR THESE FUNCTIONS MUST BE A DATAFRAME WITH AT LEAST "close" COLUMN  #
#                                                                                       #

def find_change(df, display=False):
    df["change"] = df.close - df.close.shift(1)
    df["percentChange"] = (df.close / df.close.shift(1) - 1) * 100
    if display:
        print(df.head())
        print(df.tail())
    return df

def find_dip(df):
    data = find_change(df)
    data["buy"] = 0
    data.loc[(data.percentChange.shift(1) < -6.5) & (data.percentChange > -2) & (data.percentChange < 2), "buy"] = 1
    print(data.to_string())
    return data

def get_rsi(df, display=False):
    data = find_change(df)
    data["rsi"] = ta.RSI(data["close"].values)
    if display:
        print(data.to_string())
    return data

def get_bbp(df, plot=False):
    data = find_change(df)
    up, mid, low = ta.BBANDS(df.close, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0)
    data["upper_band"] = up
    data["lower_band"] = low
    data["mid_band"] = mid
    # bbp = (df['close'] - low) / (up - low)
    if plot:
        plt.plot(data.time, data.upper_band, label="upper-band")
        plt.plot(data.time, data.lower_band, label="lower-band")
        plt.plot(data.time, data.mid_band, label="middle-band")
        plt.plot(data.time, data.close, label="price")
        plt.show()
    return data

def get_sma(df, first, second, plot=False):
    df["short_sma"] = df["close"].rolling(window=first).mean()
    df["long_sma"] = df["close"].rolling(window=second).mean()
    if plot:
        df.close.plot()
        df.long_sma.plot(label="{}-period sma".format(second))
        df.short_sma.plot(label="{}-period sma".format(first))
        plt.legend()
        plt.show()
    return df



def trend_algo(df):
    prices = find_change(df)
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
    daily_data = get_daily_data("BTC", 200, plot=False)
    gf_index = get_greed_fear_index(200, backtest=True)
    price = find_change(daily_data)
    gf_index = gf_index.shift(1)
    data = price.join(gf_index)
    data["buy"] = 0
    data["sell"] = 0
    data.loc[(data.indicator_change < -12) | (data.value < 30), "buy"] = data.close
    # data.loc[(data.value > 60) & (data.percentChange.shift(0) > 6), "sell"] = data.close
    data.loc[(data.indicator_change > 15) | (data.value > 90), "sell"] = data.close
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
        ax1.xaxis.grid(True)
        fig.tight_layout()
        plt.show()


def day_trade_BB_rsi_backtest(plot=False):
    minute = get_daily_data("XRP", 365, plot=False)
    rsi = get_rsi(minute, display=False)
    bbp = get_bbp(minute, plot=False)
    data = rsi.merge(bbp)
    data["rsi_rolling"] = data["rsi"].rolling(window=15).mean()
    data["buy"] = np.nan
    data["sell"] = np.nan
    margem = 3
    rsi_buy_limit = 40 #35 #20
    rsi_sell_limit = 60 #65 #80
    # data.loc[(data.rsi < rsi_buy_limit) | (data.close <= data.lower_band + margem), "buy"] = data.close
    # data.loc[(data.rsi > rsi_sell_limit) | (data.close >= data.upper_band - margem), "sell"] = data.close
    data.loc[(data.rsi_rolling < rsi_buy_limit), "buy"] = data.close
    data.loc[(data.rsi_rolling > rsi_sell_limit), "sell"] = data.close

    data["distance"] = np.nan
    data.loc[(data.sell.notnull() | data.buy.notnull()), "distance"] = data.mid_band-data.close

    if plot:
        print(data.to_string())

        fig, ax1 = plt.subplots()

        ax1.set_xlabel("Time (min)")
        ax1.set_ylabel('XRP', color="black")

        ax1.plot(data.time, data.upper_band, color="red", label="Superior Bollinger Band")
        ax1.plot(data.time, data.lower_band, color="blue", label="Inferior Bollinger Band")
        ax1.plot(data.time, data.mid_band, color="orange", label="15-day moving avg")

        ax1.scatter(data.time, data.sell, color="red", s=abs(data.distance * 3))
        ax1.scatter(data.time, data.buy, color="blue", s=abs(data.distance * 3))

        ax1.plot(data.time, data.close, color="black", label="Close")
        ax1.tick_params(axis='y', labelcolor="black")

        ax2 = ax1.twinx()

        ax2.set_ylabel('RSI', color="purple")
        ax2.plot(data.time, data.rsi, label="rsi", color="purple")
        # ax2.plot(data.time, data.rsi_rolling, label="rsi_sma", color="brown")
        ax2.tick_params(axis='y', labelcolor="purple")

        ax2.xaxis.set_major_locator(MaxNLocator(nbins=7))

        fig.tight_layout()
        fig.legend()
        plt.show()


##################### {[ PERFORMANCE ]} #####################


def get_performance():
    first = get_transactions()[-1]["price"]
    last = get_estimate_price("BTC")
    btc_change = (last / float(first)) - 1
    balance_change = (get_bitbrasil_balance() / 250) - 1
    print("[ Balance Change ] {}".format(balance_change)) 
    print("[ BTC Price Change ] {}".format(btc_change))



##################### {[ MONGODB ]} #####################


def add_column(collection, data):
    collection.insert_one(data)
    pass

def get_last_column(collection):
    collection.find_onde()
    pass


##################### {[ TELEGRAM ]} #####################


def send_msg(msg):
    with TelegramClient('Simba', telegram_id, telegram_hash) as client:
        client.send_message('jzsig', '{}'.format(msg))


##################### {[ FUNCTION CALLS ]} #####################

# get_daily_data("BTC", 7, True)
# get_polo_coins()
# get_polo_price("BTC_ETH")
# find_dip("BTC", 7)
# get_bitbrasil_balance(True)
# get_estimate_price("BTC", True)
# buy_all_()
# real_to_btc(100)
# buy_BRLBTC(50)
# sell_BRLBTC(100)
# get_transactions()
# cancel_order(get_open_orders()[0]["id"])
# get_open_orders()
# check_orders(get_open_orders()[-1]["id"])
# get_pytrend_interest()
# send_msg(get_bitbrasil_balance())
# trend_algo("BTC", 7)
# get_greed_fear_index(True)
# greed_fear_backtest(plot=True)
# day_trade_BB_rsi_backtest(plot=True)
# get_rsi(get_daily_data("XRP", 360), display=True)
# get_bbp(get_minute_data("KMD", 360), plot=True)
# get_sma(get_daily_data("XMR", 300), 5, 20, plot=True)
# get_performance()
# get_daily_data("XMR", 50, plot=True)
# get_crypto_compy_coin_list()


##################### {[ TO-DO ]} #####################