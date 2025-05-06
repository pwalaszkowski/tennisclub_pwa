from django import forms
from django.contrib.auth.hashers import make_password
from .models import TennisClubMember, Court, Reservation


class TennisClubMemberRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = TennisClubMember
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'address', 'membership_type',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if TennisClubMember.objects.filter(username=username).exists():
            raise forms.ValidationError('Username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if TennisClubMember.objects.filter(email=email).exists():
            raise forms.ValidationError('Email is already registered.')
        return email

    def save(self, commit=True):
        # Get the instance without saving yet
        instance = super().save(commit=False)
        # Hash the password
        instance.password = make_password(self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance


class TennisClubMemberLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class TennisClubMemberProfileForm(forms.ModelForm):
    class Meta:
        model = TennisClubMember
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'date_of_birth', 'membership_type'
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}),
            'email': forms.TextInput(
                attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'membership_type': forms.Select(
                attrs={'class': 'form-control'}),
        }

class CourtForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ['name', 'location', 'surface', 'lighting', 'indoor_outdoor']


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['court', 'date', 'timeslot']
        widgets = {
            'court': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'timeslot': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        court = cleaned_data.get('court')
        date = cleaned_data.get('date')
        timeslot = cleaned_data.get('timeslot')

        # Check for existing reservations
        if Reservation.objects.filter(court=court, date=date, timeslot=timeslot).exists():
            raise forms.ValidationError('This timeslot is already reserved.')
        return cleaned_data
