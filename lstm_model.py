import numpy as np

from sklearn.model_selection import train_test_split

from keras import Sequential
from keras.layers import LSTM, Dropout, Dense
from keras import optimizers

from model_prediction import create_x_y_subsets as split_sequence
from model_prediction import hit_the_trend
from assets import get_binance_close

from matplotlib import pyplot as plt

model = Sequential()
model.add(LSTM(50, return_sequences = True, input_shape=(3, 1)))
model.add(Dropout(0.2))

model.add(LSTM(50))
model.add(Dropout(0.2))

model.add(Dense(units = 1))

model.compile(optimizer='adam', loss='mse')


price = list(get_binance_close("ETHBTC")["close"])
n_steps = 3
X, y = split_sequence(price, n_steps)

# reshape from [samples, timesteps] into [samples, timesteps, features]
n_features = 1
X = X.reshape((X.shape[0], X.shape[1], n_features))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=False)


# fit model
model.fit(X_train, y_train, epochs=100, verbose=0)
# demonstrate prediction

x_input = np.array(X_test)
x_input = x_input.reshape(len(y_test), n_steps, n_features)
yhat = model.predict(x_input, verbose=0)

print(hit_the_trend(yhat, y_test))

plt.plot(yhat)
plt.plot(y_test)

plt.show()
