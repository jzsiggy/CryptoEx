from assets import *

def greed_fear_trade():
    btc_price = get_estimate_price("BTC")
    yesterday = find_change("BTC", 2)
    change = yesterday.at[1, "percentChange"]
    btc_balance_in_real = float(get_bitbrasil_balance()["btc"]) * btc_price
    real_balance = float(get_bitbrasil_balance()["brl"])
    gfi, gfi_change = get_greed_fear_index()

    if (gfi < 30 or gfi_change < -12) and real_balance > 30:
        r = buy_BRLBTC(real_balance / 2)
        send_msg(r.text)
        send_msg("BUYING BTC")
        send_msg("AMOUNT: {}".format(real_balance / 2))
    elif (gfi > 90 or gfi_change > 15) and btc_balance_in_real > 30:
        r = sell_BRLBTC(btc_balance_in_real / 2)
        send_msg(r.text)
        send_msg("SELLING BTC")
        send_msg("AMOUNT: {}".format(btc_balance_in_real / 2))
    else:
        send_msg("HOLDING POSITION")
    time.sleep(60)
    send_msg("CURRENT BALANCE: {}".format(get_bitbrasil_balance()))