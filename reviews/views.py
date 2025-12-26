from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db.models import Q, Avg, Case, When, Value, IntegerField
from .models import User, Place, Review
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    AddReviewSerializer, PlaceSearchSerializer,
    PlaceDetailSerializer, ReviewSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': {
                'id': user.id,
                'name': user.name,
                'phone_number': user.phone_number
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': {
                'id': user.id,
                'name': user.name,
                'phone_number': user.phone_number
            },
            'token': token.key
        })


class AddReviewView(generics.CreateAPIView):
    serializer_class = AddReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        return Response({
            'id': review.id,
            'place': {
                'id': review.place.id,
                'name': review.place.name,
                'address': review.place.address
            },
            'rating': review.rating,
            'text': review.text,
            'created_at': review.created_at
        }, status=status.HTTP_201_CREATED)


class PlaceSearchView(generics.ListAPIView):
    serializer_class = PlaceSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Always annotate average rating first to avoid N+1 queries later
        queryset = Place.objects.annotate(db_avg_rating=Avg('reviews__rating'))
        
        name = self.request.query_params.get('name', None)
        min_rating = self.request.query_params.get('min_rating', None)

        if min_rating:
            try:
                min_rating = float(min_rating)
                # Filter using the annotation
                queryset = queryset.filter(db_avg_rating__gte=min_rating)
            except (ValueError, TypeError):
                return Place.objects.none()

        if name:
            # OPTIMIZATION: Instead of converting to lists (which kills pagination efficiency),
            # use SQL 'Case/When' to order exact matches first.
            queryset = queryset.filter(name__icontains=name).annotate(
                is_exact=Case(
                    When(name__iexact=name, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by('-is_exact', 'name')

        return queryset


class PlaceDetailView(generics.RetrieveAPIView):
    # Optimize by prefetching reviews and selecting related users
    queryset = Place.objects.prefetch_related('reviews__user').annotate(
        db_avg_rating=Avg('reviews__rating')
    )
    serializer_class = PlaceDetailSerializer
    permission_classes = [IsAuthenticated]