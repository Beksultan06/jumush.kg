from rest_framework import serializers
from .models import User, UserType
import re
from apps.users.utils import set_reset_code, send_reset_code


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'title'] 

class UserSerializer(serializers.ModelSerializer):
    role = UserTypeSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'role',
            'is_verified', 'replies_balance',
            'date_joined', 'is_active'
        ]
        read_only_fields = ['is_verified', 'replies_balance', 'date_joined', 'is_active']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.exclude(title__iexact="admin")
    )

    class Meta:
        model = User
        fields = ["username", 'email', 'password', 'phone', 'role']

    def validate_phone(self, value):
        pattern = r'^\+996\d{9}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Формат номера должен быть: +996XXXXXXXXX")
        return value

    def create(self, validated_data):
        if "username" not in validated_data:
            validated_data["username"] = str(uuid.uuid4())
        return User.objects.create_user(**validated_data)



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Новый пароль должен содержать минимум 8 символов.")
        return value

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        code = generate_code()
        set_reset_code(email, code)
        send_reset_code(email, code)
        return {"detail": "Код отправлен на почту"}


class ConfirmResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        saved_code = get_reset_code(email)
        if saved_code is None:
            raise serializers.ValidationError('Код истёк или не существует.')
        if saved_code != code:
            raise serializers.ValidationError('Неверный код.')
        return data

    def save(self, **kwargs):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        delete_reset_code(email)
        return user
