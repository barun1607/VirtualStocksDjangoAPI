from rest_framework import serializers
from .models import *
from .models import Stock as StockModel
from .helpers import *
from .stocksapi import get_stock_by_name
from decimal import Decimal
from pprint import pprint


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

        if not StockModel.objects.filter(ApiRef=apiRef).exists():
            raise serializers.ValidationError({
                "detail": "StockModel code does not exist"
            })

        stock = StockModel.objects.get(ApiRef=apiRef)

        if WatchlistStocks.objects.filter(StockID=stock.StockID, WatchlistID=watchlistID).exists():
            raise serializers.ValidationError({
                "detail": "StockModel is already there in the watchlist"
            })

        watchlistItem = WatchlistStocks()
        watchlistItem.WatchlistID = watchlistID
        watchlistItem.StockID = stock

        watchlistItem.save()

    def delete(self):
        watchlistID = self.validated_data['WatchlistID']
        apiRef = self.validated_data['code']

        if not StockModel.objects.filter(ApiRef=apiRef).exists():
            raise serializers.ValidationError({
                "detail": "StockModel code does not exist"
            })

        stock = StockModel.objects.get(ApiRef=apiRef)

        if WatchlistStocks.objects.filter(StockID=stock.StockID, WatchlistID=watchlistID).exists():
            watchlistItem = WatchlistStocks.objects.get(
                StockID=stock.StockID, WatchlistID=watchlistID)
            watchlistItem.delete()
        else:
            raise serializers.ValidationError({
                "detail": "StockModel does not exist in the watchlist"
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
                "detail": "StockModel api returned null response for the given stock code"
            })

        price = Decimal(stockDetails['averagePrice'])
        balance = user.Usermoney

        if not StockModel.objects.filter(ApiRef=code).exists():
            raise serializers.ValidationError({
                "detail": "StockModel code does not exist"
            })

        stock = StockModel.objects.get(ApiRef=code)

        if (balance < (price * quantity)):
            raise serializers.ValidationError({
                "detail": "There aren't sufficient funds in your account to carry out this transaction."
            })

        user.Usermoney = balance - (price * quantity)
        user.save()

        transaction = saveTransaction(
            user, user.PortfolioID, price, quantity, stock, False)

        portfolioEntry = PortfolioStocks()
        portfolioEntry.TransactionID = transaction
        portfolioEntry.PortfolioID = user.PortfolioID
        portfolioEntry.StockID = stock
        portfolioEntry.NumberOfStocks = quantity
        portfolioEntry.save()

        setPrice(user.PortfolioID.PortfolioID)

        getPriceCurrent(user.PortfolioID.PortfolioID)

    def sell(self):
        uID = self.validated_data['UserID']
        code = self.validated_data['code']
        quantity = self.validated_data['quantity']

        user = User.objects.get(UserID=uID)

        try:
            stockDetails = get_stock_by_name(code)
        except AttributeError:
            raise serializers.ValidationError({
                "detail": "StockModel api returned null response for the given stock code"
            })

        price = Decimal(stockDetails['averagePrice'])
        balance = user.Usermoney

        if not StockModel.objects.filter(ApiRef=code).exists():
            raise serializers.ValidationError({
                "detail": "StockModel code does not exist"
            })

        stock = StockModel.objects.get(ApiRef=code)

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

        saveTransaction(user, user.PortfolioID, price, quantity, stock, True)

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

        setPrice(user.PortfolioID.PortfolioID)

        getPriceCurrent(user.PortfolioID.PortfolioID)


class ViewPortfolioSerializer(serializers.Serializer):
    PortfolioID = serializers.IntegerField()

    class Meta:
        fields = [
            'PortfolioID'
        ]

    def view(self):
        PortfolioID = self.validated_data['PortfolioID']

        [stockList, unrealizedValueCurr] = getPriceCurrent(PortfolioID)

        resp = {
            'UnrealizedValueInitial': Portfolios.objects.get(PortfolioID=PortfolioID).UnrealizedValue,
            'UnrealizedValueCurr': unrealizedValueCurr,
            'stocks': stockList
        }

        return resp


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = '__all__'
