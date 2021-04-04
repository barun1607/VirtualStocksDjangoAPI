from nsetools import Nse as NSE
import json

# self.image=image


class Stock():

    def __init__(self, high, low, previous_close, symbol, change, company_name):
        self.high = high
        self.low = low
        self.previous_close = previous_close
        self.symbol = symbol
        self.change = change
        self.company_name = company_name


nse = NSE()


def get_stock_object(data):
    if data == None:
        return (None)
    high = data.get('dayHigh')
    low = data.get('dayLow')
    if high == None:
        high = data.get('highPrice')
    if low == None:
        low = data.get('lowPrice')
    previous_close = data.get('previousClose')
    change = data.get('change')
    symbol = data.get('symbol')
    company_name = data.get('companyName')
    stock = Stock(high, low, previous_close, symbol, change, company_name)
    return stock


def get_stocks_list():
    codes = nse.get_stock_codes(cached=True)
    return list(codes.values())


def get_stock_by_name(name):
    data = nse.get_quote(name)
    stock = get_stock_object(data)
    return (stock.__dict__)


def get_gainers():
    gainers = nse.get_top_gainers()
    stocks = []
    for data in gainers:
        stocks.append(get_stock_object(data).__dict__)
    return stocks


def get_losers():
    losers = nse.get_top_losers()
    stocks = []
    for data in losers:
        stocks.append(get_stock_object(data).__dict__)
    return stocks
