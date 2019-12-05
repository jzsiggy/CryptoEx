from assets import get_binance_close, get_daily_data
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression

from sklearn.preprocessing import scale, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, median_absolute_error

from matplotlib import pyplot as plt

import sys

model = RandomForestRegressor()
# model = DecisionTreeRegressor()
# model = ExtraTreesRegressor()
# model = GradientBoostingRegressor()


def hit_the_trend(pred, actual):
  if len(pred) != len(actual):
    print("Arrays are not the same length")
    return
  true  = 0
  false = 0
  for i in range(len(pred) - 1):
    if pred[i+1] > pred[i] and actual[i+1] > actual[i]:
      true += 1
    elif pred[i+1] < pred[i] and actual[i+1] < actual[i]:
      true += 1
    else:
      false += 1

  return (true / (len(pred) - 1))


def create_x_y_subsets(arr, step):
  X = []
  y = []
  for i in range(len(arr) - step):
    subset = []
    for n in range(step):
      subset.append(arr[i+n])
    X.append(subset)
    y.append(arr[i+step])
  X, y = np.array(X), np.array(y)
  return(X, y)

def train_model(data, step, model):
  price = data[ : int(len(data) * 0.75) ]

  X_train, y_train = create_x_y_subsets(price, step)

  model.fit(X_train, y_train)

  return(model)

def get_regression(data, step, model, plot=False):
  data = scale(data)
  
  model = train_model(data, step, model)
  
  price = data[ int(len(data) * 0.75) : ]

  X, y = create_x_y_subsets(price, step)

  y_pred = model.predict(X)

  percentage_of_hits= hit_the_trend(y_pred, y)
  print("Percent of times right about the trend: ", percentage_of_hits)

  if plot:
    plt.plot(y_pred, color='b', label='pred')
    plt.plot(y, color='orange', label='actual price')
    plt.legend()
    plt.show()

  data = np.append(data, [y_pred[-1]])
  print(len(y_pred), y_pred[-1])

  return y, y_pred

# get_regression(list(get_daily_data("BTC", 500)["close"]), 3, model, plot=True)
