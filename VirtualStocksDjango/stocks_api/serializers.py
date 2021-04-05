from rest_framework import serializers
from .models import *


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
                "detail": "Stock code does not exitst"
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
                "detail": "Stock code does not exitst"
            })

        stock = Stock.objects.get(ApiRef=apiRef)

        if WatchlistStocks.objects.filter(StockID=stock.StockID, WatchlistID=watchlistID).exists():
            watchlistItem = WatchlistStocks.objects.get(
                StockID=stock.StockID, WatchlistID=watchlistID)
            watchlistItem.delete()
        else:
            raise serializers.ValidationError({
                "detail": "Stock does not exitst in the watchlist"
            })


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
