from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .stocksapi import *
from .models import User
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
    return Response({"data": data}, safe=False)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def gainers(request):
    data = get_gainers()
    return Response(data, safe=False)


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
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


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
    user.delete()
    return Response('User deleted')


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = get_object_or_404(User, UserID=pk)
    serializer = UserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return Response(data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
