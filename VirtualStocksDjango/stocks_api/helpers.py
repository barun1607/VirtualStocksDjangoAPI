from .models import *
from .stocksapi import *
from decimal import Decimal


def getPriceCurrent(PortfolioID):
    portfolioItems = PortfolioStocks.objects.filter(
        PortfolioID=PortfolioID)

    stockList = [{
        'code': item.StockID.ApiRef,
        'number': item.NumberOfStocks
    } for item in portfolioItems]

    compressedList = {}
    for item in stockList:
        if item['code'] in compressedList.keys():
            compressedList[item['code']] += item['number']
        else:
            compressedList[item['code']] = item['number']

    keys = list(compressedList.keys())
    values = list(compressedList.values())

    stockList = []
    for i in range(compressedList.__len__()):
        data = {
            'stock': get_stock_by_name(keys[i]),
            'number': values[i]
        }
        stockList.append(data)

    unrealizedValueCurr = 0

    for stock in stockList:
        unrealizedValueCurr += Decimal(stock['stock']['averagePrice']) * \
            stock['number']

    portfolioObj = Portfolios.objects.get(PortfolioID=PortfolioID)
    portfolioObj.UnrealizedValueCurrent = unrealizedValueCurr
    portfolioObj.save()

    return [stockList, unrealizedValueCurr]


def setPrice(idInp):
    portfolio = Portfolios.objects.get(
        PortfolioID=idInp)

    unrealizedValue = 0
    transactAggregate = PortfolioStocks.objects.filter(
        PortfolioID=idInp)

    for entry in transactAggregate:
        p = Decimal(entry.TransactionID.Price)
        q = Decimal(entry.NumberOfStocks)
        unrealizedValue += (p * q)
    portfolio.UnrealizedValue = unrealizedValue
    portfolio.save()


def saveTransaction(user, portfolioID, price, quantity, stock, typeBool):
    transaction = Transactions()
    transaction.UserID = user
    transaction.PortfolioID = portfolioID
    transaction.Price = price
    transaction.Quantity = quantity
    transaction.StockID = stock
    transaction.isSold = typeBool
    transaction.save()
    return transaction


def getUser(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    token_val = token.split(' ')[1]
    user_ptr = Token.objects.get(
        key=token_val).user
    user = User.objects.get(user_ptr=user_ptr)
    return user
