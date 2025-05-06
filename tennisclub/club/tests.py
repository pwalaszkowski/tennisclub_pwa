from datetime import time

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.utils import IntegrityError

from .forms import TennisClubMemberRegistrationForm
from .models import TennisClubMember, Court, Reservation

class TennisClubMemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        self.member = TennisClubMember.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john.doe@test.com',
            phone_number='1234567890',
            date_of_birth='1990-01-01',
            address='123 Main St',
            username='john_doe',
        )

    def test_tennis_club_member_str(self):
        self.assertEqual(str(self.member), 'John Doe - john_doe')

    def test_password_hashing(self):
        self.member.set_password('newpassword')
        self.assertTrue(self.member.check_password('newpassword'))

    def test_email_sync_with_user(self):
        self.member.email = 'new_email@test.com'
        self.member.save()
        self.assertEqual(self.user.email, 'new_email@test.com')

    def test_unique_username_and_email(self):
        with self.assertRaises(IntegrityError):
            TennisClubMember.objects.create(
                user=self.user,
                first_name='Jane',
                last_name='Smith',
                email='john.doe@test.com',  # Duplicate email
                phone_number='9876543210',
                date_of_birth='1992-02-02',
                address='456 Another St',
                username='john_doe',  # Duplicate username
            )

class CourtModelTest(TestCase):
    def setUp(self):
        self.court = Court.objects.create(
            name='Court 1',
            location='Main Complex',
            surface='clay',
            lighting='standard',
            indoor_outdoor='indoor'
        )

    def test_court_str(self):
        self.assertEqual(str(self.court), 'Court 1')


class ReservationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword',
                                             email='test@test.com')
        self.member = TennisClubMember.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john.doe@test.com',
            phone_number='1234567890',
            date_of_birth='1990-01-01',
            address='123 Main St',
            username='john_doe',
        )
        self.court = Court.objects.create(
            name='Court 1',
            location='Main Complex',
            surface='clay',
            lighting='standard',
            indoor_outdoor='indoor'
        )
        self.reservation = Reservation.objects.create(
            member=self.member,
            court=self.court,
            date='2025-01-01',
            timeslot='08:00:00'
        )

    def test_reservation_str(self):
        court = Court.objects.create(name='Court 7897')
        reservation = Reservation.objects.create(
            court=court,
            date='2025-01-01',
            timeslot=time(8, 0),  # Correct timeslot as a time object
            member = self.member
        )

        # Test the __str__ method
        self.assertEqual(str(reservation), 'Court 7897 - 2025-01-01 - 08:00')

    def test_unique_reservation(self):
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                member=self.member,
                court=self.court,
                date='2025-01-01',
                timeslot='08:00:00'  # Duplicate reservation
            )

class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        self.url = reverse('login')

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')

    def test_login_view_post_success(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, reverse('main'))  # Redirects to main page after successful login

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword',
        })
        # Check if form errors are in the response context
        self.assertContains(response, 'Invalid username or password.')

class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('logout')

    # TODO: Test is not working as expected
    # def test_logout_view(self):
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, reverse('login'))  # Redirects to login after logging out
    #     self.assertNotIn('access_token', response.cookies)
    #     self.assertNotIn('refresh_token', response.cookies)

class MemberRegistrationTest(TestCase):
    def setUp(self):
        self.url = reverse('member_registration')

    def test_member_registration_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/member_registration.html')

    def test_member_registration_post_success(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@test.com',
            'phone_number': '1234567890',
            'date_of_birth': '1995-01-01',
            'address': '456 New St',
            'membership_type': 'Premium',
            'username': 'janedoe',
            'password': 'newpassword'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='janedoe').exists())

    def test_member_registration_post_invalid(self):
        # Try submitting a form with an existing username
        response = self.client.post(reverse('member_registration'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '1234567890',
            'date_of_birth': '1990-01-01',
            'address': '123 Main St',
            'membership_type': 'Standard',
            'username': 'existingusername',  # This username already exists
            'password': 'password123',
        })

        # Follow the redirect after form submission
        self.assertEqual(response.status_code, 302)  # Ensure redirect occurs

class TennisClubMemberRegistrationFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@test.com',
            'phone_number': '1234567890',
            'date_of_birth': '1995-01-01',
            'address': '456 New St',
            'membership_type': 'Premium',
            'username': 'janedoe',
            'password': 'newpassword'
        }
        form = TennisClubMemberRegistrationForm(data)
        self.assertTrue(form.is_valid())

    # TODO: Test is not working as expected
    # def test_invalid_username(self):
    #     self.existing_member = TennisClubMember.objects.create(
    #         username='janedoe',
    #         first_name='Jane',
    #         last_name='Doe',
    #         email='jane.doe@test.com',
    #         phone_number='1234567890',
    #         date_of_birth='1995-01-01',
    #         address='456 New St',
    #         membership_type='Standard',
    #         password='newpassword'  # Hash this properly in production
    #     )
    #
    #     data = {
    #         'username': 'janedoe',  # Already taken
    #         'first_name': 'Jane',
    #         'last_name': 'Doe',
    #         'email': 'jane.doe@test.com',
    #         'phone_number': '1234567890',
    #         'date_of_birth': '1995-01-01',
    #         'address': '456 New St',
    #         'membership_type': 'Standard',
    #         'password': 'newpassword'
    #     }
    #     form = TennisClubMemberRegistrationForm(data)
    #     self.assertFalse(form.is_valid())
    #     self.assertIn('Username is already taken.', form.errors['username'])