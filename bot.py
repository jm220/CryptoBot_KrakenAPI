#Proof of Concept Crypto Bot
#This bot stores transactions as JSON objects

import krakenex
import json 
import time
import datetime
import calendar

def get_crypto_data(pair, since):
    return api.query_public('OHLC', data = {'pair' : pair, 'since' : since})['result'][pair]

def analyze(pair, since):
    data = get_crypto_data(pair[0]+pair[1], since)  #concatanate those two to get string 

    lowest = 0
    highest = 0
    
    for prices in data:
        balance = get_fake_balance()
        last_trade = get_last_trade(pair[0]+pair[1])
        last_trade_price = float(last_trade['price'])

        open_ = float(prices[1])
        high_ = float(prices[2])
        low_ =  float(prices[3])
        close_ = float(prices[4])

        did_sell = False

        try: 
            balance[pair[0]]
            #IF we own any of the pair currency that we are looking at then check sell
            selling_point_win = last_trade_price * 1.005
            selling_point_loss = last_trade_price * 0.995
            
            #selling at a win
            if open_ >= selling_point_win or close_ >= selling_point_win:
                #Sell at a win
                did_sell = True
                fake_sell(pair, close_, last_trade)
            elif open_ <= selling_point_loss or close_ <= selling_point_loss:
                did_sell = True
                fake_sell(pair, close_, last_trade)
        except:
            pass

        # logic for if we should buy
        if not did_sell and (balance['USD.HOLD']) > 0:
            if low_ <= lowest or lowest == 0:
                lowest = low_
            if high_ > highest:
                highest = high_
            
            price_to_buy = 1.0005

            if highest/lowest >= price_to_buy and low_ <= lowest:
                available_money = balance['USD.HOLD']
                fake_buy(pair, available_money, close_, last_trade)

def fake_update_balance(pair, dollar_amount, close_, was_sold):
    balance = get_fake_balance()
    prev_balance = float(balance['USD.HOLD'])
    new_balance = 0
    if was_sold:
        new_balance = prev_balance + float(dollar_amount)
        del balance[pair[0]]
    else:
        new_balance = prev_balance - dollar_amount
        balance[pair[0]] = str(float(dollar_amount)/close_)
    balance['USD.HOLD'] = str(new_balance)

    with open('balance.json', 'w') as f:
        json.dump(balance, f, indent=4)


def fake_buy(pair, dollar_amount, close_, last_trade):
    trades_history = get_fake_trades_history()
    last_trade['price'] = str(close_)
    last_trade['type'] = 'buy'
    last_trade['cost'] = dollar_amount
    last_trade['time'] = datetime.datetime.now().timestamp()
    last_trade['vol'] = str(float(dollar_amount)/close_)

    trades_history['result']['trades'][str(datetime.datetime.now().timestamp)] = last_trade
    with open('tradeshistory.json', 'w') as f:
        json.dump(trades_history, f, indent=4)
        fake_update_balance(pair, dollar_amount, close_, False)

    #api.query_private() do this for real buy and sell

def fake_sell(pair, close_, last_trade):
    trades_history = get_fake_trades_history()
    last_trade['price'] = str(close_)
    last_trade['type'] = 'sell'
    last_trade['cost'] = str(float(last_trade['vol'])*close_)
    last_trade['time'] = datetime.datetime.now().timestamp()

    trades_history['result']['trades'][str(datetime.datetime.now().timestamp())] = last_trade
    
    with open('tradeshistory.json', 'w') as f:
        json.dump(trades_history, f, indent=4)
        fake_update_balance(pair, dollar_amount, close_, True)
    
def get_balance():
    return api.query_private('Balance')

def get_fake_balance():
    with open('balance.json', 'r') as f:
        return json.load(f)

def get_last_trade(pair):
    trades_history = get_fake_trades_history()['result']['trades']
    
    last_trade = {}

    for trade in trades_history:
        trade = trades_history[trade]
        if trade['pair'] == pair and trade['type'] == 'buy':
            last_trade = trade
    return last_trade

def get_fake_trades_history():
    with open('tradeshistory.json', 'r') as f:
        return json.load(f)

def get_trades_history():
    start_date = datetime.datetime(2021, 7, 4)
    end_date = datetime.datetime.today()
    return api.query_private('TradesHistory', req(start_date, end_date, 1))['result']

def date_nix(str_date):
    return calendar.timegm(str_date.timetuple())

def req(start, end, ofs):
    req_date = {
        'type' : 'all',
        'trades' : 'true',
        'start': str(date_nix(start)),
        'end': str(date_nix(end)),
        'ofs': str(ofs)
    }


if __name__ == '__main__':
    api = krakenex.API()
    api.load_key('kraken.key')
    pair = ("XETH", "ZUSD")                       #Get price of Etherum of US dollars
    since = str(int(time.time() - 3600))          #timestamp from one hour ago

    analyze(pair, since)                          #Include a while true, to constanly analyze a pair







