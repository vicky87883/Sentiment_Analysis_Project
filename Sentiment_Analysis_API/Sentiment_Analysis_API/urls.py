from django.contrib import admin
from django.urls import path, include  # Make sure to import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analysis.urls')),  # Include your app's urls.py at the root
]
