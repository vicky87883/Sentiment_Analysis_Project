from django.urls import path
from .views import upload_file, home

urlpatterns = [
    path('', home, name='home'),  # Home page for file upload
    path('upload/', upload_file, name='upload_file'),  # The upload route
]
