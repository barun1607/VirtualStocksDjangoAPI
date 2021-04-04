from rest_framework import serializers, status
from .models import User, Watchlists, Portfolios


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
                {'usernameError': 'Username already exists'})

        if password != password2:
            raise serializers.ValidationError(
                {'passwordError': 'Passwords do not match'})

        user.username = unameInp
        user.set_password(password)

        watchlist.save()
        portfolio.save()

        user.PortfolioID = portfolio
        user.WatchlistID = watchlist

        user.save()

        return user
