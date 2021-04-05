from nsetools import Nse as NSE
from .models import Stock as StockModel
from itertools import islice


class Stock():

    def __init__(self, averagePrice, high, low, previous_close, symbol, change, company_name):
        self.averagePrice = averagePrice
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
    averagePrice = data.get('averagePrice')
    previous_close = data.get('previousClose')
    change = data.get('change')
    symbol = data.get('symbol')
    company_name = data.get('companyName')
    stock = Stock(averagePrice, high, low, previous_close,
                  symbol, change, company_name)
    return stock


def get_stocks_list():
    codes = nse.get_stock_codes(cached=True)
    return list(codes.values())


def get_stock_by_name(name):
    data = nse.get_quote(name)
    stock = get_stock_object(data)
    return stock.__dict__


def get_gainers():
    gainers = nse.get_top_gainers()
    stocks = [get_stock_by_name(gainer['symbol']) for gainer in gainers]
    return stocks


def get_losers():
    losers = nse.get_top_losers()
    stocks = [get_stock_by_name(loser['symbol']) for loser in losers]
    return stocks


def populate_stocks():
    stocks = nse.get_stock_codes()
    stock_codes = list(stocks.keys())
    obj_set = (StockModel(ApiRef=f"{code}", StockID=stock_codes.index(
        code)) for code in stock_codes)
    batch_size = 100
    while True:
        batch = list(islice(obj_set, batch_size))
        if not batch:
            break
        StockModel.objects.bulk_create(batch, batch_size)
