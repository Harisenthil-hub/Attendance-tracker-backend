from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import AppUser

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self,validated_token):
        user_id = validated_token.get('user_id')

        try:
            return AppUser.objects.get(user_id=user_id)
        except AppUser.DoesNotExist:
            return None