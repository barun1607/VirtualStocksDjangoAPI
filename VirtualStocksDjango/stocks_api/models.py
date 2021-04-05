from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib import auth

# Create your models here.


class Stock(models.Model):
    ApiRef = models.CharField(max_length=50)
    StockID = models.AutoField(primary_key=True)

    def __str__(self):
        return self.ApiRef


class Watchlists(models.Model):
    WatchlistID = models.AutoField(primary_key=True)

    def __str__(self):
        return f"{self.WatchlistID}"


class WatchlistStocks(models.Model):
    WatchlistID = models.ForeignKey(Watchlists, on_delete=models.CASCADE)
    StockID = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self):
        return f"Watchlist ID: {self.WatchlistID}, Stock ID: {self.StockID}"


class Portfolios(models.Model):
    PortfolioID = models.AutoField(primary_key=True)
    UnrealizedValue = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=10, default=0)


class PortfolioStocks(models.Model):
    PortfolioID = models.ForeignKey(Portfolios, on_delete=models.CASCADE)
    StockID = models.ForeignKey(Stock, on_delete=models.CASCADE)
    NumberOfStocks = models.IntegerField()


class User(auth.models.User):
    UserID = models.AutoField(primary_key=True)
    Usermoney = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=10, default=500000)
    PortfolioID = models.ForeignKey(Portfolios, on_delete=models.CASCADE)
    WatchlistID = models.ForeignKey(Watchlists, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Transactions(models.Model):
    TransactionID = models.AutoField(primary_key=True)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    Timestamp = models.DateTimeField(auto_now_add=True)
    Price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=10)
    Quantity = models.IntegerField(null=False)
    isSold = models.BooleanField(default=False)
    StockID = models.ForeignKey(Stock, on_delete=models.CASCADE)


class Leaderboard(models.Model):
    LeaderboardID = models.AutoField(primary_key=True)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    Timestamp = models.DateTimeField(auto_now_add=True)
    Unrealizedvalue = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=10)
    Realizedvalue = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=10)
