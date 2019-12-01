from assets import get_binance_close
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression

from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, median_absolute_error

from matplotlib import pyplot as plt

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

def train_model(df, step, model):
  data = df.head(int(len(df) * 0.75))
  price = data.close

  X_train, y_train = create_x_y_subsets(price, step)
  X_train, y_train = scale(X_train), scale(y_train)
  model.fit(X_train, y_train)

  return(model)

def get_regression(df, step, model):
  model = train_model(df, step, model)
  data = df.tail(int(len(df) * 0.25))
  price = list(data.close)

  X, y = create_x_y_subsets(price, step)
  X, y = scale(X), scale(y)

  y_pred = model.predict(X)

  percentage_of_hits= hit_the_trend(y_pred, y)
  print("Percent of times right about the trend: ", percentage_of_hits)

  plt.plot(y_pred, color='b', label='pred')
  plt.plot(y, color='orange', label='actual price')
  plt.legend()
  plt.show()

  return percentage_of_hits, y_pred[-2:]


# get_regression(get_binance_close("LTCBTC"), 3, model)
