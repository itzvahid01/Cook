from rest_framework import serializers
from ..models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id','profile_img','phone','name','family','city','address',
            'code_posti','is_active','password','is_admin'
        ]
        read_only_fields = ['id','is_active','is_admin','phone']

    def get_is_admin(self, obj):
        return getattr(obj,'is_staff',False) or getattr(obj,'is_superuser',False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password: user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password: instance.set_password(password)
        instance.save()
        return instance

class TeacherMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile_img','name','family']

class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ['phone']
