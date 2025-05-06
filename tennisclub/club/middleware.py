from django.shortcuts import redirect

from rest_framework_simplejwt.authentication import JWTAuthentication, InvalidToken

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        jwt_auth = JWTAuthentication()
        header = request.COOKIES.get('access_token')
        if header:
            raw_token = header
            try:
                validated_token = jwt_auth.get_validated_token(raw_token)
                request.user = jwt_auth.get_user(validated_token)
            except InvalidToken:  # This handles both ExpiredSignatureError and InvalidToken
                response = redirect('login')  # Redirect to login or refresh token page
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                return response
        return self.get_response(request)