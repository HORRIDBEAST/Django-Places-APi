from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Place, Review


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password']
        )


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if not phone_number or not password:
            raise serializers.ValidationError("Phone number and password are required.")
        
        try:
            user = User.objects.get(phone_number=phone_number)
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        data['user'] = user
        return data


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'rating', 'text', 'user_name', 'created_at']
        read_only_fields = ['id', 'user_name', 'created_at']


class AddReviewSerializer(serializers.Serializer):
    place_name = serializers.CharField(max_length=255)
    place_address = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField()
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        place_name = validated_data['place_name']
        place_address = validated_data['place_address']
        
        place, created = Place.objects.get_or_create(
            name=place_name,
            address=place_address
        )
        
        review = Review.objects.create(
            user=user,
            place=place,
            rating=validated_data['rating'],
            text=validated_data['text']
        )
        
        return review


class PlaceSearchSerializer(serializers.ModelSerializer):
    # Map to the annotated field 'db_avg_rating' or fall back to 0
    average_rating = serializers.FloatField(source='db_avg_rating', read_only=True)

    class Meta:
        model = Place
        # Use a method to handle None values gracefully if needed, 
        # or rely on DRF handling None as null
        fields = ['id', 'name', 'average_rating']
    
    def to_representation(self, instance):
        # Handle cases where rating is None (no reviews)
        data = super().to_representation(instance)
        if data['average_rating'] is None:
            data['average_rating'] = 0.0
        else:
            data['average_rating'] = round(data['average_rating'], 2)
        return data


class PlaceDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Place
        fields = ['id', 'name', 'address', 'average_rating', 'reviews']
    
    def get_average_rating(self, obj):
        return round(obj.average_rating, 2)
    
    def get_reviews(self, obj):
        request = self.context.get('request')
        reviews = obj.reviews.all()
        
        if request and request.user.is_authenticated:
            user_review = reviews.filter(user=request.user).first()
            other_reviews = reviews.exclude(user=request.user)
            
            if user_review:
                ordered_reviews = [user_review] + list(other_reviews)
            else:
                ordered_reviews = list(reviews)
        else:
            ordered_reviews = list(reviews)
        
        return ReviewSerializer(ordered_reviews, many=True).data