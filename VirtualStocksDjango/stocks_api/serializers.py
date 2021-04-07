from rest_framework import serializers
from .models import *
from .stocksapi import get_stock_by_name
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = [
            'PortfolioID',
            'UserID',
            'WatchlistID'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


class RegistrationSerializer(serializers.ModelSerializer):
    ConfPassword = serializers.CharField(
        style={'input-type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'ConfPassword',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User()
        watchlist = Watchlists()
        portfolio = Portfolios()

        unameInp = self.validated_data['username']
        password = self.validated_data['password']
        password2 = self.validated_data['ConfPassword']

        if User.objects.filter(username=unameInp).exists():
            raise serializers.ValidationError(
                {'detail': 'Username already exists'})

        if password != password2:
            raise serializers.ValidationError(
                {'detail': 'Passwords do not match'})

        user.username = unameInp
        user.set_password(password)

        watchlist.save()
        portfolio.save()

        user.PortfolioID = portfolio
        user.WatchlistID = watchlist

        user.save()


class WatchlistSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = WatchlistStocks
        fields = [
            'WatchlistID',
            'code'
        ]

    def save(self):

        watchlistID = self.validated_data['WatchlistID']
        apiRef = self.validated_data['code']

        if not Stock.objects.filter(ApiRef=apiRef).exists():
            raise serializers.ValidationError({
                "detail": "Stock code does not exist"
            })

        stock = Stock.objects.get(ApiRef=apiRef)

        if WatchlistStocks.objects.filter(StockID=stock.StockID, WatchlistID=watchlistID).exists():
            raise serializers.ValidationError({
                "detail": "Stock is already there in the watchlist"
            })

        watchlistItem = WatchlistStocks()
        watchlistItem.WatchlistID = watchlistID
        watchlistItem.StockID = stock

        watchlistItem.save()

    def delete(self):
        watchlistID = self.validated_data['WatchlistID']
        apiRef = self.validated_data['code']

        if not Stock.objects.filter(ApiRef=apiRef).exists():
            raise serializers.ValidationError({
                "detail": "Stock code does not exist"
            })

        stock = Stock.objects.get(ApiRef=apiRef)

        if WatchlistStocks.objects.filter(StockID=stock.StockID, WatchlistID=watchlistID).exists():
            watchlistItem = WatchlistStocks.objects.get(
                StockID=stock.StockID, WatchlistID=watchlistID)
            watchlistItem.delete()
        else:
            raise serializers.ValidationError({
                "detail": "Stock does not exist in the watchlist"
            })


class TransactStockSerializer(serializers.Serializer):
    UserID = serializers.IntegerField()
    code = serializers.CharField()
    quantity = serializers.IntegerField()

    class Meta:
        fields = [
            'UserID',
            'code',
            'quantity'
        ]

    def buy(self):
        uID = self.validated_data['UserID']
        code = self.validated_data['code']
        quantity = self.validated_data['quantity']

        user = User.objects.get(UserID=uID)

        try:
            stockDetails = get_stock_by_name(code)
        except AttributeError:
            raise serializers.ValidationError({
                "detail": "Stock api returned null response for the given stock code"
            })

        price = Decimal(stockDetails['averagePrice'])
        balance = user.Usermoney

        if not Stock.objects.filter(ApiRef=code).exists():
            raise serializers.ValidationError({
                "detail": "Stock code does not exist"
            })

        stock = Stock.objects.get(ApiRef=code)

        if (balance < (price * quantity)):
            raise serializers.ValidationError({
                "detail": "There aren't sufficient funds in your account to carry out this transaction."
            })

        user.Usermoney = balance - (price * quantity)
        user.save()

        transaction = Transactions()
        transaction.UserID = user
        transaction.PortfolioID = user.PortfolioID
        transaction.Price = price
        transaction.Quantity = quantity
        transaction.StockID = stock
        transaction.save()

        portfolioEntry = PortfolioStocks()
        portfolioEntry.TransactionID = transaction
        portfolioEntry.PortfolioID = user.PortfolioID
        portfolioEntry.StockID = stock
        portfolioEntry.NumberOfStocks = quantity
        portfolioEntry.save()

        portfolio = Portfolios.objects.get(
            PortfolioID=user.PortfolioID.PortfolioID)

        unrealizedValue = 0
        transactAggregate = PortfolioStocks.objects.filter(
            PortfolioID=user.PortfolioID.PortfolioID)

        for entry in transactAggregate:
            p = entry.TransactionID.Price
            q = entry.NumberOfStocks
            unrealizedValue += (p * q)
        portfolio.UnrealizedValue = unrealizedValue
        portfolio.save()

    def sell(self):
        uID = self.validated_data['UserID']
        code = self.validated_data['code']
        quantity = self.validated_data['quantity']

        user = User.objects.get(UserID=uID)

        try:
            stockDetails = get_stock_by_name(code)
        except AttributeError:
            raise serializers.ValidationError({
                "detail": "Stock api returned null response for the given stock code"
            })

        price = Decimal(stockDetails['averagePrice'])
        balance = user.Usermoney

        if not Stock.objects.filter(ApiRef=code).exists():
            raise serializers.ValidationError({
                "detail": "Stock code does not exist"
            })

        stock = Stock.objects.get(ApiRef=code)

        if not PortfolioStocks.objects.filter(PortfolioID=user.PortfolioID.PortfolioID, StockID=stock.StockID).exists():
            raise serializers.ValidationError({
                "detail": "Your portfolio does not have this stock"
            })

        portfolioItems = PortfolioStocks.objects.filter(
            PortfolioID=user.PortfolioID.PortfolioID, StockID=stock.StockID)

        totalNoOfStocks = 0
        for item in portfolioItems:
            n = item.NumberOfStocks
            totalNoOfStocks += n

        if totalNoOfStocks < quantity:
            raise serializers.ValidationError({
                "detail": "There aren't enough stocks in your portfolio to carry out this request"
            })

        user.Usermoney = balance + (price * quantity)
        user.save()

        transaction = Transactions()
        transaction.UserID = user
        transaction.PortfolioID = user.PortfolioID
        transaction.Price = price
        transaction.Quantity = quantity
        transaction.StockID = stock
        transaction.isSold = True
        transaction.save()

        listLen = portfolioItems.__len__()
        num = quantity
        while num > 0:
            if num >= portfolioItems[listLen - 1].NumberOfStocks:
                num -= portfolioItems[listLen - 1].NumberOfStocks
                portfolioItems[listLen - 1].delete()
                listLen -= 1
            else:
                portfolioItems[listLen - 1].NumberOfStocks -= num
                portfolioItems[listLen - 1].save()
                num = 0

        portfolio = Portfolios.objects.get(
            PortfolioID=user.PortfolioID.PortfolioID)

        unrealizedValue = 0
        transactAggregate = PortfolioStocks.objects.filter(
            PortfolioID=user.PortfolioID.PortfolioID)

        for entry in transactAggregate:
            p = entry.TransactionID.Price
            q = entry.NumberOfStocks
            unrealizedValue += (p * q)
        portfolio.UnrealizedValue = unrealizedValue
        portfolio.save()
