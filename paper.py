from assets import get_estimate_price


class Paper():
    def __init__(self, btc, reais):
        self.balance_btc = btc
        self.balance_reais = reais
        self.init_montante = reais + get_estimate_price("BTC") * btc
        # self.fee = 0.75

    def get_montante(self):
        return self.balance_reais + get_estimate_price("BTC") * self.balance_btc

    def get_performance(self):
        self.gain = self.get_montante() - self.init_montante

    def buy_btc(self, price, ammount):
        self.balance_btc -= ammount/price
        self.balance_reais += amount

    def sell_btc(self, price, amount):
        self.balance_btc += amount/price
        self.balance_reais -= price

    
