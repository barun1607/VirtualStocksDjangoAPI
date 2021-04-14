from django.urls import path
from . import views
from .news_analysis import get_news_analysis
from .news_analysis import get_news_links

urlpatterns = [
    path('stock/<str:name>', views.stock, name='stock'),
    path('stocks', views.stocks, name='stocks'),
    path('gainers', views.gainers, name='gainers'),
    path('losers', views.losers, name='losers'),
    path('', views.apiHome, name='home'),
    path('register-user', views.registerUser, name='register-user'),
    path('list-users', views.listUsers, name='list-users'),
    path('delete-user', views.deleteUser, name='delete-user'),
    path('user-details', views.userDetails, name='user-details'),
    path('populate-stocks/<str:op>',
         views.populateStocksTable, name='populate-stocks'),
    path('add-watchlist/<str:code>', views.addToWatchlist, name='add-watchlist'),
    path('delete-watchlist/<str:code>',
         views.deleteFromWatchlist, name='delete-watchlist'),
    path('view-watchlist', views.viewWatchlist, name='view-watchlist'),
    path('buy-stock/<str:code>/<int:quantity>',
         views.buyStock, name='buy-stock'),
    path('sell-stock/<str:code>/<int:quantity>',
         views.sellStock, name='sell-stock'),
    path('view-portfolio', views.viewPortfolio, name='view-portfolio'),
    path('view-transactions', views.viewTransactions, name='view-transactions'),
    path('graph', views.show_user_graph, name='user-graph'),
    path('portfolio-graph', views.show_portfolio_graph, name='portfolio-graph'),
    path('update-leaderboard', views.updateLeaderboard, name='update-leaderboard'),
    path('view-leaderboard', views.viewLeaderboard, name='view-leaderboard'),
    path('news-graph/<str:name>', get_news_analysis, name='view-news-graph'),
    path('news-links/<str:name>', get_news_links, name='view-news-links')
]
