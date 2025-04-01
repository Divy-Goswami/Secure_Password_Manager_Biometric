from rest_framework import serializers
from .models import CustomUser, Password


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "phone",
            "email",
            "password",
        ]

    def validate_email(self, value):
        """Ensure email is always stored in lowercase."""
        return value.strip().lower()

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        # Ensure email is lowercase
        validated_data["email"] = validated_data["email"].strip().lower()

        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password before saving
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
        ]  # Include only the fields needed for user details


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Password
        fields = [
            "domain_name",
            "password",
            "link",
        ]  # Fields for storing passwords and associated info


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "face_image",
        ]


from .models import Image


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ["id", "image", "user"]
