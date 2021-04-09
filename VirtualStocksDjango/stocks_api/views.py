from rest_framework.response import Response
from rest_framework.decorators import api_view
from .stocksapi import *
from .models import *
from .models import Stock as StockModel
from .serializers import *
from .helpers import *
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework import status


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stock(request, name):
    data = get_stock_by_name(name)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stocks(request):
    data = get_stocks_list()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def gainers(request):
    data = get_gainers()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def losers(request):
    data = get_losers()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def apiHome(request):
    api_urls = {
        "Register a user": "register-user/",
        "Display all users": "list-users/",
        "Update a user's details": "update-user/<str:pk>",
        "Delete a user": "delete-user/<str:pk>"
    }
    return Response(api_urls)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def listUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def registerUser(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "User registered"}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteUser(request):
    user = getUser(request)
    user.delete()
    return Response({"detail": "User deleted"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def populateStocksTable(request, op):
    if op == "add":
        populate_stocks()
        return Response({'detail': "Stocks table populated successfully"})
    elif op == "delete":
        StockModel.objects.all().delete()
        return Response({"detail": "Stocks table records deleted successfully"})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addToWatchlist(request, code):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    watchlistID = userSerializer.data.get('WatchlistID')
    data = {
        "WatchlistID": watchlistID,
        "code": code
    }
    wlistSerializer = WatchlistSerializer(data=data)

    if wlistSerializer.is_valid():
        wlistSerializer.save()
        return Response({"detail": "StockModel added to Watchlist"}, status=status.HTTP_200_OK)
    else:
        return Response(wlistSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteFromWatchlist(request, code):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    watchlistID = userSerializer.data.get('WatchlistID')
    data = {
        "WatchlistID": watchlistID,
        "code": code
    }
    wlistSerializer = WatchlistSerializer(data=data)

    if wlistSerializer.is_valid():
        wlistSerializer.delete()
        return Response({"detail": "StockModel removed from watchlist"}, status=status.HTTP_200_OK)
    else:
        return Response(wlistSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def viewWatchlist(request):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    watchlistID = userSerializer.data.get('WatchlistID')

    if not WatchlistStocks.objects.filter(WatchlistID=watchlistID).exists():
        return Response({"detail": "Watchlist is empty"}, status=status.HTTP_200_OK)

    watchListSet = WatchlistStocks.objects.filter(WatchlistID=watchlistID)
    stockList = [obj.StockID for obj in watchListSet]
    respList = [get_stock_by_name(obj.ApiRef) for obj in stockList]
    return Response(respList, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def buyStock(request, code, quantity):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    userID = userSerializer.data.get('UserID')
    data = {
        'UserID': userID,
        'code': code,
        'quantity': quantity
    }
    buySerializer = TransactStockSerializer(data=data)
    if buySerializer.is_valid():
        buySerializer.buy()
        return Response({
            "detail": "The stocks have been added to your portfolio",
        }, status=status.HTTP_200_OK)
    else:
        return buySerializer.errors


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sellStock(request, code, quantity):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    userID = userSerializer.data.get('UserID')
    data = {
        'UserID': userID,
        'code': code,
        'quantity': quantity
    }
    sellSerializer = TransactStockSerializer(data=data)
    if sellSerializer.is_valid():
        sellSerializer.sell()
        return Response({
            "detail": "The stocks have been sold"
        }, status=status.HTTP_200_OK)
    else:
        return sellSerializer.errors


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def viewPortfolio(request):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    portfolioID = userSerializer.data.get('PortfolioID')
    data = {
        "PortfolioID": portfolioID
    }
    serializer = ViewPortfolioSerializer(data=data)
    if serializer.is_valid():
        resp = serializer.view()
        return Response(resp, status=status.HTTP_200_OK)
    else:
        return serializer.errors


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def viewTransactions(request):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    portfolioID = userSerializer.data.get('PortfolioID')
    transactions = Transactions.objects.filter(PortfolioID=portfolioID)
    serializer = TransactionsSerializer(transactions, many=True)
    data = [{
            "StockModel": StockModel.objects.get(StockID=item['StockID']).ApiRef,
            "Price": item['Price'],
            "Quantity": item['Quantity'],
            "Timestamp": item['Timestamp'],
            "Type": 'Sell' if item['isSold'] else 'Buy',
            } for item in serializer.data]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateLeaderboard(request):
    Leaderboard.objects.all().delete()
    leaderboardItemList = []
    for user in User.objects.all():
        leaderboardItem = Leaderboard()
        leaderboardItem.UserID = user
        leaderboardItem.Unrealizedvalue = user.PortfolioID.UnrealizedValue
        leaderboardItem.Realizedvalue = user.Usermoney
        leaderboardItem.UnrealizedvalueCurrent = getPriceCurrent(
            user.PortfolioID.PortfolioID)[1]
        leaderboardItem.save()
        leaderboardItemList.append(leaderboardItem)
    return Response({
        "detail": "Leaderboard updated"
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def viewLeaderboard(request):
    serializer = LeaderboardSerializer(Leaderboard.objects.all(), many=True)
    data = [{
        "username": User.objects.get(UserID=item['UserID']).username,
        "UnrealizedValueInitial": item['Unrealizedvalue'],
        "UnrealizedValueCurrent": item['UnrealizedvalueCurrent'],
        "RealizedValue": item['Realizedvalue']
    } for item in serializer.data]
    return Response(data)
