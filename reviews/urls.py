from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView,
    AddReviewView, PlaceSearchView, PlaceDetailView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('reviews/', AddReviewView.as_view(), name='add-review'),
    path('places/search/', PlaceSearchView.as_view(), name='search-places'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
]