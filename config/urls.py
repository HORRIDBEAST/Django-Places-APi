from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
def home(request):
    return JsonResponse({
        "message": "Place Review API is running", 
        "docs": "/api/places/search/"
    })
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('reviews.urls')),
    path('', home),  # Add this line for the root URL
]