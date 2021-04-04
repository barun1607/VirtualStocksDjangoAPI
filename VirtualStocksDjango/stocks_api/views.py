from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .stocksapi import *
from .models import User, Stock
from .serializers import UserSerializer, RegistrationSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


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
@permission_classes([IsAuthenticated])
def listUsers(request):
    if request.user.is_superuser:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    else:
        return Response({'response': 'You are not authorized to view that'})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def registerUser(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        response = serializer.save()
        data = serializer.data
    else:
        data = serializer.errors
    return Response(data)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteUser(request, pk):
    user = get_object_or_404(User, UserID=pk)
    if request.user != user:
        return Response({'response': 'You are not authorized to delete that'})
    user.delete()
    return Response('User deleted')


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = get_object_or_404(User, UserID=pk)
    if request.user != user:
        return Response({'response': 'You are not authorized to update that'})
    serializer = UserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return Response(data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def populateStocksTable(request, op):
    if request.user.is_superuser:
        if op == "add":
            populate_stocks()
            return Response("Stocks table populated successfully ")
        elif op == "delete":
            Stock.objects.all().delete()
            return Response("Stocks table records deleted successfully ")
    else:
        return Response({'response': 'You are not authorized to view that'})
