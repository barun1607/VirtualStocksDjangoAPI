from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from .stocksapi import *
from .models import *
from .serializers import *
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stock(request, name):
    data = get_stock_by_name(name)
    return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stocks(request):
    data = get_stocks_list()
    return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def gainers(request):
    data = get_gainers()
    return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def losers(request):
    data = get_gainers()
    return Response(data)


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
        return Response({"detail": "User registered"})
    else:
        return Response(serializer.errors)


# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def getUser(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    token_val = token.split(' ')[1]
    user_ptr = Token.objects.get(
        key=token_val).user
    user = User.objects.get(user_ptr=user_ptr)
    return user


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteUser(request):
    user = getUser(request)
    user.delete()
    return Response({"detail": "User deleted"})


# @api_view(['PUT'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def updateUser(request, pk):
#     user = get_object_or_404(User, UserID=pk)
#     if request.user != user:
#         return Response({'response': 'You are not authorized to update that'})
#     serializer = UserSerializer(user, data=request.data, partial=True)

#     if serializer.is_valid():
#         serializer.update()
#         data = serializer.data
#         return Response(data)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def populateStocksTable(request, op):
    if op == "add":
        populate_stocks()
        return Response({'detail': "Stocks table populated successfully"})
    elif op == "delete":
        Stock.objects.all().delete()
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
        return Response({"detail": "Stock added to Watchlist"})
    else:
        return Response(wlistSerializer.errors)


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
        return Response({"detail": "Stock removed from watchlist"})
    else:
        return Response(wlistSerializer.errors)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def viewWatchlist(request):
    user = getUser(request)
    userSerializer = UserSerializer(user)
    watchlistID = userSerializer.data.get('WatchlistID')
    watchListSet = WatchlistStocks.objects.filter(WatchlistID=watchlistID)
    stockList = [obj.StockID for obj in watchListSet]
    respList = [get_stock_by_name(obj.ApiRef) for obj in stockList]
    return Response(respList)
