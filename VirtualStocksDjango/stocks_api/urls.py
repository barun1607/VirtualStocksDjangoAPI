from django.urls import path
from . import views

urlpatterns = [
    path('stock/<str:name>', views.stock, name='stock'),
    path('stocks', views.stocks, name='stocks'),
    path('gainers', views.gainers, name='gainers'),
    path('losers', views.losers, name='losers'),
    path('', views.apiHome, name='home'),
    path('register-user/', views.registerUser, name='register-user'),
    path('list-users/', views.listUsers, name='list-users'),
    path('delete-user/<str:pk>/', views.deleteUser, name='delete-user'),
    path('update-user/<str:pk>/', views.updateUser, name='update-user'),
]
