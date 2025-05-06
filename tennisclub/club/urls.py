from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import TennisClubMemberViewSet, CourtViewSet, ReservationViewSet

from . import views

router = DefaultRouter()
router.register(r'members', TennisClubMemberViewSet)
router.register(r'courts', CourtViewSet)
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', views.login_view, name='login'),         # Login Page
    path('main/', views.main, name='main'),           # Main page
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('members/members/', views.members, name='members'),  # Members page
    path('members/member_registration/', views.member_registration, name='member_registration'),
    path('members/member_edit/', views.member_edit, name='member_edit'), # Member profile edit
    path('courts/courts/', views.courts, name='courts'),    # Courts page
    path('courts/court_add/', views.court_add, name='court_add'),
    path('courts/court_reservation/', views.court_reservation, name='court_reservation'),
    path('courts/court_reservations_edit/<int:pk>', views.court_reservation_edit,
         name='court_reservation_edit'), # Edit a reservation
    path('about/', views.about, name='about'),      # About page
    path('contact/', views.contact, name='contact'),  # Contact page
    path('logout/', views.logout_view, name='logout'),    # Logout
]
