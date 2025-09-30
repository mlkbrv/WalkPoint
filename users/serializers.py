from rest_framework import serializers
from users.models import User, DailyStep
from .models import validate_password



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'first_name',
            'last_name',
            'bio',
            'instagram',
            'profile_pic',
            'cover',
            'total_steps',
            'available_steps'
        ]



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'}, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'first_name',
            'last_name',
            'password',
            'password2'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords must match')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class DailyStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStep
        fields = [
            'date',
            'steps'
        ]