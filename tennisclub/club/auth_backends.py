from django.contrib.auth.backends import BaseBackend
from .models import TennisClubMember

class TennisClubMemberBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            member = TennisClubMember.objects.get(username=username)
            if member.is_active and member.check_password(password):
                return member
        except TennisClubMember.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return TennisClubMember.objects.get(pk=user_id)
        except TennisClubMember.DoesNotExist:
            return None
