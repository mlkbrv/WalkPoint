from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(write_only=True,required=True,max_length=150)
    password = serializers.CharField(write_only=True,required=True,max_length=150)
    password2 = serializers.CharField(write_only=True,required=True,max_length=150)

    class Meta:
        model = User
        fields = [
            'identifier',
            'password',
            'password2',
            'first_name',
            'last_name',
            'profile_pic',
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'profile_pic': {'required': False}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        identifier = data['identifier']

        if User.objects.filter(Q(email=identifier) | Q(phone_number=identifier)).exists():
            raise serializers.ValidationError({"identifier": "A user with this identifier already exists."})

        return data

    def create(self, validated_data):
        identifier = validated_data.pop('identifier')
        password = validated_data.pop('password')
        validated_data.pop('password2')

        user = User.objects.create_user(
            identifier=identifier,
            password=password,
            **validated_data
        )

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'profile_pic',
            'email',
            'phone_number',
            'coins',
            'overall_steps',
            'is_active',
        ]
        read_only_fields = ['id', 'email', 'phone_number', 'coins', 'overall_steps', 'is_active']