from django.urls import path
from .views.login_view import login
from .views.image_view import upload_image, show_image, create_image_link_for_enterprise, show_image_admin
from .views.user_view import get_links
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login', login, name='login'),
    path('images/upload', upload_image, name='images/upload'),
    path('images', get_links),
    path('images/<str:image_id>', show_image, name='images/image_id'),
    path('images-admin/<str:image_id>', show_image_admin),
    path('images/<str:image_id>/generate-link', create_image_link_for_enterprise, name='images/image_id/generate-link')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
