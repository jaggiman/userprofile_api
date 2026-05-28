from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/', GoogleSignInView.as_view(), name='google-signin'),
    path('profile/complete/', ProfileCompleteView.as_view(), name='complete-profile'),
    path('profile/', GetProfileView.as_view(), name='profile'),
    path('profile/send-otp/', SendCollegeEmailOTPView.as_view(), name='send-otp'),
    path('profile/verify-otp/', VerifyCollegeEmailOTPView.as_view(), name='verify-otp')
]