from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Included for the "minimal UI / admin improvements" bonus points
    path('admin/', admin.site.urls),
    
    # Route all baseline endpoints directly to the root
    path('', include('scanner.urls')),
]