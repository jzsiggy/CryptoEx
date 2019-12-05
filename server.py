from model_prediction import get_regression
from assets import get_binance_close, get_daily_data

from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

from flask import Flask, request, jsonify
from flask_cors import CORS

import json

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=["POST"])
def regress():
  data = json.loads(request.data.decode("utf-8"))

  coin_pair = data["coin"]
  regressor = data["regressor"]
  step = int(data["timeStep"])

  price = list(get_daily_data(coin_pair, 500)["close"])

  if regressor == "Linear":
    model = LinearRegression()
  elif regressor == "Random Forest":
    model = RandomForestRegressor()
  elif regressor == "Gradient Boost":
    model = GradientBoostingRegressor()
  elif regressor == "Decision Tree":
    model = DecisionTreeRegressor()

  y, y_pred = get_regression(price, step, model)

  prediction = {
    "pred" : list(y_pred),
    "actual" : list(y),
  }

  return(prediction)