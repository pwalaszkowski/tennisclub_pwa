from rest_framework import serializers
from .models import TennisClubMember, Court, Reservation

class TennisClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TennisClubMember
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name',
                 'phone_number', 'date_of_birth', 'address', 'membership_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = TennisClubMember.objects.create_user(**validated_data)
        return user

class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'