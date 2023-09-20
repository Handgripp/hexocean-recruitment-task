from django.urls import path
from .views import login, upload_image, show_image

urlpatterns = [
    path('login', login),
    path('images/upload', upload_image),
    path('images/<str:image_id>', show_image),
]
