import os
import pyotp
import face_recognition
from pathlib import Path
from datetime import datetime

from django.conf import settings
from rest_framework import status
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

from .serializers import (
    UserSignupSerializer,
    UserSerializer,
    PasswordSerializer,
    ImageUploadSerializer,
    ImageSerializer,
)
from .models import Password, CustomUser, Image

User = get_user_model()  # Get custom user model


# ✅ Signup API with Face Image Processing & Secure Storage
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data["email"] = validated_data["email"].strip().lower()

            if User.objects.filter(email=validated_data["email"]).exists():
                return Response(
                    {"error": "Email already registered!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Signup successful!",
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "token_expires_in": refresh.access_token.payload["exp"],
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Login API (Authenticates User Securely)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()  # ✅ Convert to lowercase
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and Password are required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(
                email__iexact=email
            )  # Case-insensitive email lookup
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(password, user.password):  # Verify the hashed password
            return Response(
                {"error": "Invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Generate JWT Token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful!",
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "token_expires_in": refresh.access_token.payload["exp"],
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


# ✅ User Profile API (Fetches Logged-in User Details)
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


# ✅ Root API (Provide basic API info)
@api_view(["GET"])
@permission_classes([AllowAny])  # No authentication required for this view
def api_root(request):
    return Response(
        {
            "message": "Welcome to the API!",
            "endpoints": {
                "users": "/api/users/",
                "signup": "/api/signup/",
                "login": "/api/login/",
                "me": "/api/me/",
                "passwords": "/api/passwords/",
            },
        }
    )


# ✅ Add Password API (Allow authenticated users to add a password)
@api_view(["POST"])
@permission_classes(
    [IsAuthenticated]
)  # Ensure only authenticated users can add passwords
def add_password(request):
    """Allow authenticated users to add a password."""
    # Check if 'domain_name' and 'password' are provided in the request
    if "domain_name" not in request.data or "password" not in request.data:
        return Response(
            {"error": "domain_name and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create serializer to validate and save the password data
    serializer = PasswordSerializer(data=request.data)

    # Validate and save the password
    if serializer.is_valid():
        try:
            # Save the password for the authenticated user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle errors during saving the password
            return Response(
                {"error": f"Error saving password: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        # Return validation errors if the serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Fetch Password API (Allow authenticated users to fetch passwords)
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_passwords(request):
#     """Allow authenticated users to get their passwords."""
#     passwords = Password.objects.filter(
#         user=request.user
#     )  # Fetch passwords for authenticated user
#     serializer = PasswordSerializer(passwords, many=True)
#     return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    """Allow authenticated users to view or add passwords."""
    if request.method == "GET":
        otp = request.query_params.get("otp")  # Get OTP from query params

        if not otp:
            return Response(
                {"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # # Generate OTP
        user = request.user
        print("OPT", otp, user.otp_generated)
        totp = pyotp.TOTP(user.otp_secret)  # Use the user's OTP secret

        # Now verify OTP entered by the user
        if str(user.otp_generated) != str(otp):
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch passwords if OTP is valid
        passwords = Password.objects.filter(user=request.user)
        serializer = PasswordSerializer(passwords, many=True)
        return Response(serializer.data)


# totp = pyotp.TOTP(user.otp_secret, interval=30)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def send_otp_email(request):
    try:
        user = request.user  # Get the logged-in user

        # Generate or fetch OTP secret
        otp_secret = (
            user.generate_otp_secret()
        )  # Generate OTP secret if not already done

        # Generate OTP for the user
        totp = pyotp.TOTP(otp_secret)
        generated_otp = totp.now()  # Generate the OTP

        # Store OTP in the user model (or session for simplicity)
        user.otp_generated = generated_otp  # Save OTP for comparison later
        user.save()

        # Send the OTP to the user's email
        send_mail(
            "Your OTP for Password Access",
            f"Your OTP for accessing your passwords is: {generated_otp}",
            settings.DEFAULT_FROM_EMAIL,  # Sender email (from your settings)
            [user.email],  # Recipient's email
            fail_silently=False,
        )

        return Response(
            {
                "message": "OTP sent successfully to your email!",
                "user": {"email": user.email},
            },
            status=200,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def verify_otp(request):
#     """Verify OTP for the logged-in user"""
#     otp = request.query_params.get("otp")  # Get the OTP from query params

#     if not otp:
#         return Response({"error": "OTP is required."}, status=400)

#     user = request.user  # Get the logged-in user

#     # Verify the OTP with the stored OTP
#     if user.otp_generated == otp:
#         # OTP is correct, fetch passwords for the user
#         passwords = Password.objects.filter(
#             user=user
#         )  # Fetch passwords for authenticated user
#         serializer = PasswordSerializer(passwords, many=True)
#         return Response(serializer.data, status=200)
#     else:
#         return Response({"error": "Invalid OTP."}, status=400)


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ensure the request includes the image file
        user = request.user
        print(request.FILES)

        if "image" not in request.FILES:
            return Response(
                {"error": "No image provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES["image"]

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.name}"

        # Create an image instance and save the image file
        image_instance = Image(image=file, user=user)
        image_instance.save()  # This will automatically save the image to the server and populate image_url

        # Return the image URL in the response
        return Response(
            {
                "message": "Image uploaded successfully!",
                "image_url": str(image_instance.image),
            },
            status=status.HTTP_201_CREATED,
        )


class ImageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        image = Image.objects.get(user=user)
        if not image:
            return Response({"status": False, status: 404})
        serializer = ImageSerializer(image)
        return Response(serializer.data)


class VerifyFaceId(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        # Get FaceId from server

        if "image" not in request.FILES:
            return Response(
                {"error": "No image provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_image = request.FILES["image"]

        # Get faceId from DB
        image = Image.objects.get(user=user)

        image1 = face_recognition.load_image_file(uploaded_image)
        face_location1 = face_recognition.face_locations(image1)
        face_encoding1 = face_recognition.face_encodings(image1)[0]

        print(f"Face Location 1: {face_location1}")
        print(f"Face Encoding 1: {face_encoding1}")

        # Process saved faceId image of user
        user_saved_image_path = self.get_image_path(str(image.image))
        image2 = face_recognition.load_image_file(user_saved_image_path)
        face_location2 = face_recognition.face_locations(image2)
        face_encoding2 = face_recognition.face_encodings(image2)[0]

        print(f"Face Location 2: {face_location2}")
        print(f"Face Encoding 2: {face_encoding2}")

        results = face_recognition.compare_faces([face_encoding1], face_encoding2)

        if results[0]:
            return Response({"status": True})

        return Response({"status": False, status: 400})

    def get_image_path(self, image_path):
        # Assuming image_path is the full path to the image, like '/media/images/your_image.jpg'
        BASE_DIR = Path(__file__).resolve().parent.parent
        # If the path is relative (starts with /media/), you need to resolve it to the absolute file path
        media_root = os.path.join(BASE_DIR, "media")

        full_image_path = os.path.join(media_root, image_path)
        return full_image_path
