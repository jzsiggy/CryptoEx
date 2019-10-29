from assets import get_daily_data
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation, performance_metrics
from fbprophet.plot import plot_cross_validation_metric

pd.plotting.register_matplotlib_converters()

m = Prophet()


def prophetize(ticker):
  df = get_daily_data(ticker, 90)
  df.rename(columns={'time': 'ds', 'close': 'y'}, inplace=True)

  m.fit(df)
  future = m.make_future_dataframe(periods=10)
  forecast = m.predict(future)

  m.plot(forecast)
  plt.show()

  return forecast


def test_prophecy(ticker):
  df = get_daily_data(ticker, 90)
  df.rename(columns={'time': 'ds', 'close': 'y'}, inplace=True)

  m.fit(df)

  df_cv = cross_validation(m, horizon = '10 days')
  df_p = performance_metrics(df_cv)
  df_p.head(5)

  plot_cross_validation_metric(df_cv, metric='mape')
  plt.show()


# test_prophecy("ETH")
prophetize("ETH")

