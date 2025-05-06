from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .forms import TennisClubMemberRegistrationForm, TennisClubMemberLoginForm, \
    TennisClubMemberProfileForm, CourtForm, ReservationForm
from .models import TennisClubMember, Court, Reservation
from .serializers import TennisClubMemberSerializer, CourtSerializer, ReservationSerializer


class TennisClubMemberViewSet(viewsets.ModelViewSet):
    queryset = TennisClubMember.objects.all()
    serializer_class = TennisClubMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(member=self.request.user.tennisclubmember)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user.tennisclubmember)


def login_view(request):
    if request.method == 'POST':
        form = TennisClubMemberLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                response = redirect('main')
                response.set_cookie('access_token', str(refresh.access_token), httponly=True)
                response.set_cookie('refresh_token', str(refresh), httponly=True)
                return response
            messages.error(request, 'Invalid username or password.')
    else:
        form = TennisClubMemberLoginForm()
    return render(request, 'login/login.html', {'form': form})

def logout_view(request):
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

# Main view
@login_required
def main(request):
    return render(request, 'main.html')

# Members view
@login_required
def members(request):
    members = TennisClubMember.objects.all()  # Fetch all members
    return render(request, 'members/members.html', {'members': members})

# Member Registration view
def member_registration(request):
    if request.method == 'POST':
        form = TennisClubMemberRegistrationForm(request.POST)
        if form.is_valid():
            # Extract cleaned data
            data = form.cleaned_data
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            try:
                # Create the User object
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                )

                # Create the TennisClubMember object
                TennisClubMember.objects.create(
                    user=user,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    phone_number=data.get('phone_number'),
                    date_of_birth=data.get('date_of_birth'),
                    address=data.get('address'),
                    membership_type=data.get('membership_type'),
                )

                messages.success(request, 'Registration successful!')
                return redirect('login')  # Redirect to login or success page
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {e}')
                return redirect('member_registration')
        else:
            messages.error(request, 'There were errors in the form. Please correct them.')
    else:
        form = TennisClubMemberRegistrationForm()

    return render(request, 'members/member_registration.html', {'form': form})

@login_required
def member_edit(request):
    user = request.user.tennisclubmember  # Assuming `TennisClubMember` is tied to `User`
    if request.method == 'POST':
        form = TennisClubMemberProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('member_edit')
    else:
        form = TennisClubMemberProfileForm(instance=user)

    return render(request, 'members/member_edit.html', {'form': form})

# Courts view
@login_required
def courts(request):
    courts_list = Court.objects.all()  # Fetch all courts
    reservations = Reservation.objects.all()  # Fetch all reservations

    if request.method == 'POST':
        # Handle selection and actions (edit or delete)
        selected_reservations = request.POST.getlist('selected_reservations')

        if 'edit_selected' in request.POST:
            # Handle edit action for selected reservations
            for reservation_id in selected_reservations:
                # Redirect to edit page with reservation ID
                return redirect('reservation_edit', pk=reservation_id)

        elif 'delete_selected' in request.POST:
            # Handle delete action for selected reservations
            Reservation.objects.filter(id__in=selected_reservations).delete()
            messages.success(request, 'Selected reservations deleted successfully.')
            return redirect('courts')

    return render(request, 'courts/courts.html',
                  {'courts': courts_list, 'reservations': reservations})

@login_required
def court_add(request):
    if request.method == 'POST':
        form = CourtForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Court added successfully!')
            return redirect('courts')  # Redirect to court list after adding
        else:
            messages.error(request, 'Failed to add court. Please check the form.')
    else:
        form = CourtForm()
    return render(request, 'courts/court_add.html', {'form': form})

@login_required
def court_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.member = request.user.tennisclubmember  # Link to logged-in member
            reservation.save()
            messages.success(request, 'Reservation successful!')
            return redirect('courts')
        else:
            messages.error(request, 'Failed to make reservation. Please check the form.')
    else:
        form = ReservationForm()
    return render(request, 'courts/court_reservation.html', {'form': form})

@login_required
def court_reservation_edit(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation updated successfully!')
            return redirect('courts')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'courts/court_reservation_edit.html', {'form': form})

# About view
@login_required
def about(request):
    return render(request, 'about.html')

# Contact view
@login_required
def contact(request):
    return render(request, 'contact.html')
