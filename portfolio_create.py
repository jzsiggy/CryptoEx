import requests
import json
import pandas as pd
from matplotlib import pyplot as plt

from assets import get_binance_close
from model_prediction import get_regression

from sklearn.ensemble import RandomForestRegressor

import sys

def get_coin_list():
  data = requests.get('https://www.binance.com/api/v1/ticker/allPrices')
  all_pairs_prices = json.loads(data.text)
  coin_pair_list = [ pair['symbol'] for pair in all_pairs_prices ]
  return coin_pair_list

def plot_all_pairs():
  pairs = get_coin_list()
  model = RandomForestRegressor()
  high_acc_pairs = []

  for pair in pairs:
    try:
      print(pair)
      acc, pred = get_regression(get_binance_close(pair), 3, model)
      print("The regressor got {0} percent of hits and these are the values of today and tommorrow {1}".format(acc, pred))
      if acc > 0.65:
        high_acc_pairs.append(pair)
    except KeyboardInterrupt:
      print("The high accuracy pairs until now are:")
      print(high_acc_pairs)
      sys.exit(1)
    except:
      print("There was an error with pair {}".format(pair))
      print("The high accuracy pairs until now are:")
      print(high_acc_pairs)
  print("The Binance High Accuracy pairs are:")
  print(high_acc_pairs)


def get_values():
  model = RandomForestRegressor()

  # high_aac_pairs = ['WTCETH', 'STRATBTC', 'SNGLSETH', 'IOTABTC', 'SUBETH', 'SNTBTC', 'XRPETH', 'MODETH', 'RCNBTC', 'BCCETH', 'BATETH', 'XLMBTC', 'RLCETH', 'CHATBTC', 'RPXBTC', 'RPXETH', 'RPXBNB', 'CLOAKETH', 'BCNETH', 'BCNBNB', 'REPBNB', 'TUSDBTC', 'TUSDBNB', 'ZENBTC', 'QKCBTC', 'NPXSETH', 'HOTETH', 'HCETH', 'GOBNB', 'RVNBNB', 'XRPPAX', 'XLMPAX', 'RENBNB', 'XRPUSDC', 'TRXXRP', 'LINKTUSD', 'LINKPAX', 'LINKUSDC', 'BCHABCPAX', 'BCHABCUSDC', 'TRXPAX', 'BNBUSDS', 'BTTTUSD', 'ONGBNB', 'HOTBNB', 'ZILUSDT', 'FETBNB', 'FETBTC', 'XMRBNB', 'DASHBNB', 'DASHUSDT', 'ENJUSDT', 'MITHUSDT', 'ETCUSDC', 'ETCTUSD', 'TFUELTUSD', 'ONEBNB', 'ALGOBNB', 'ALGOBTC', 'GTOUSDT', 'DOGEBNB', 'DOGEBTC', 'DUSKBNB', 'DUSKUSDC', 'ANKRBNB', 'ANKRBTC', 'ANKRUSDT', 'ONTPAX']
  for pair in high_aac_pairs:
    print(pair)
    acc, pred = get_regression(get_binance_close(pair), 3, model)
    print("The regressor got {0} percent of hits and these are the values of today and tommorrow {1}".format(acc, pred))


get_coin_list()