import requests
import json
import pandas as pd
from matplotlib import pyplot as plt

from assets import get_binance_close
from model_prediction import get_regression

from sklearn.ensemble import RandomForestRegressor

def get_coin_list():
  data = requests.get('https://www.binance.com/api/v1/ticker/allPrices')
  all_pairs_prices = json.loads(data.text)
  coin_pair_list = [ pair['symbol'] for pair in all_pairs_prices ]
  return coin_pair_list

def plot_all_pairs():
  pairs = get_coin_list()
  model = RandomForestRegressor()
  high_acc_pairs = []

  for pair in pairs[0:100]:
    print(pair)
    acc, pred = get_regression(get_binance_close(pair), 10, model)
    print("The regressor got {0} percent of hits and these are the values of today and tommorrow {1}".format(acc, pred))

plot_all_pairs()