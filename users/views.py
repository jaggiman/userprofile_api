from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
#The below import is for JWT token generation
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
#google auth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
#the below imports are for otp verification purposes
import random
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return{
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
class RegisterView(APIView):
    """ 
    POST /api/users/register/
    Accepts registration data, validates, creates user, 
    and returns tokens.
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'Registration Successful',
                'user': ProfileSerializer(user).data,
                'tokens': tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GoogleSignInView(APIView):
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        token = serializer.validated_data['id_token']
        #verifying the token with google
        try:
            google_data = id_token.verify_oauth2_token(
                token, google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response({'error': 'Invalid Google token'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        #verify user info from verified token
        google_id = google_data['sub']
        email = google_data['email']
        name = google_data.get('name', '')
        #get existing user or create a new one
        user, created = User.objects.get_or_create(
            email = email,
            defaults = {
                'name'          : name,
                'google_id'     : google_id,
                'auth_provider' : 'google',
            }
        )
        #if user exists but signed up manually, block them
        if not created and user.auth_provider != 'google':
            return Response(
                {'error': "This email is registered manually. Please login with password."},
                status=status.HTTP_400_BAD_REQUEST)
        #return the token and profile status
        tokens = get_tokens_for_user(user)
        return Response({
            'message'           : "Google Sign-in Successful",
            'user'              : ProfileSerializer(user).data,
            'tokens'            : tokens,
            'profile_complete'  : user.profile_complete,
        }, status=status.HTTP_200_OK)
    
class ProfileCompleteView(APIView):
    permission_classes = [IsAuthenticated]
    #this endpoint is protected
    #which means user has to send their JWT access token to reach it
    #which means only after login
    def patch(self, request):
        #patch is for partial updates instead of PUT
        #incase user only need one or two fields to update
        serializer = CompleteProfileSerializer(
            instance=request.user,
            data = request.data,
            partial = True,
            context = {'request' : request} #passes to serializer
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message'          : 'Profile Updated Successfully.',
                'user'             : ProfileSerializer(user).data,
                'profile_complete' : user.profile_complete,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    #this endpoint is protected too
    def get(self, request):
        #DRF extracts user object request.user from JWT token
        #request.user is the logged-in user
        serializer = ProfileSerializer(request.user)
        return Response({
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
class SendCollegeEmailOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        college_email = serializer.validated_data['college_email']
        #generating otp
        otp = str(random.randint(100000, 999999))
        #save otp and college_email temmporarily on user
        request.user.otp = otp
        request.user.otp_created_at = timezone.now()
        request.user.college_email = college_email
        request.user.save()

        #sending OTP to email
        send_mail(
            subject='MyFestivo - College Email Verification',
            message=f'Your OTP is {otp}. It is valid for 10 minutes.',
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list=[college_email],
        )
        return Response(
            {'message': 'OTP sent to your College Email Id.'},
            status=status.HTTP_200_OK
        )
class VerifyCollegeEmailOTPView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        otp_input = serializer.validated_data['otp']
        user = request.user

        #checking if OTP exists
        if not user.otp or not user.otp_created_at:
            return Response(
                {'error': 'No OTP found! Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        
        #checking otp expiry - 4 minutes
        time_elapsed = timezone.now() - user.otp_created_at
        if time_elapsed.total_seconds() > 240:
            return Response(
                {'error': 'OTP has expired! Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        #checking if OTP matches.
        if user.otp != otp_input:
            return Response(
                {'error': 'Invalid OTP!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        #verifying
        user.college_email_verified = True
        user.otp = None
        user.otp_created_at = None
        user.save()
        return Response(
            {'message': 'College Email Id verified successfully.'},
            status=status.HTTP_200_OK
        )        
        