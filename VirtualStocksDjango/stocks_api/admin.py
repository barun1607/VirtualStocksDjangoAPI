from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Watchlists)
admin.site.register(WatchlistStocks)
admin.site.register(Portfolios)
admin.site.register(PortfolioStocks)
admin.site.register(Stock)
admin.site.register(Transactions)
admin.site.register(Leaderboard)
