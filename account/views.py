from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import CustomUserLoginSerializer, CustomUserRegisterSerializer, CustomUserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser 
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError




# Create your views here.
class CustomUserRegisterView(GenericAPIView):
    serializer_class = CustomUserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user.is_staff = True
            user.save()
            return Response(
                    {
                        "message": "User created successfully!!!",
                        'data': serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomUserLoginView(GenericAPIView):
    serializer_class = CustomUserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data  = serializer.validated_data
        try:
            user = CustomUser.objects.get(email=data.get("email"))
        except CustomUser.DoesNotExist:
            return Response(
                {
                    "message": "User does not exist",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        password = user.password
        check = check_password(data["password"], password)
        if check and user.is_active:
            try:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
            except TokenError:
                return Response(
                    {
                        "message": "Token generation failed",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(
                {
                    "message": f"Login successful {user.first_name}",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
        elif user.is_active == False:
            return Response(
                {
                    "message": "User is not active",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            return Response(
                {
                    "message": "Invalid credentials",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

class CustomUserProfileView(GenericAPIView):
    serializer_class = CustomUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(
            {
                "message": "User profile retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class UpdateCustomUserProfileView(GenericAPIView):
    serializer_class = CustomUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "message": "User profile updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not current_password or not new_password:
            return Response({"message": "Both current and new passwords are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({"message": "New password and confirm password do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(current_password, user.password):
            return Response({"message": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

class DeleteAccountView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        # Check if user is authenticated
        if not user.is_authenticated:
            return Response({"message": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        # Delete the user account
        try:
            user.delete()
            return Response({"message": f"Account associated with {user.email} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": f"An error occurred while deleting the account: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
