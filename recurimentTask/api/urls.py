from django.urls import path
from .views.login_view import login
from .views.image_view import upload_image, show_image

urlpatterns = [
    path('login', login),
    path('images/upload', upload_image),
    path('images/<str:image_id>', show_image),
]
