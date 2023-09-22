import pathlib
import shutil
from datetime import datetime, timedelta
import PIL
import jwt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..repositories.user_repository import UserRepository
from ..repositories.image_repository import ImageRepository
from PIL import Image
from decouple import config
from django.http import FileResponse
from ..validate_token import validate_jwt_token

ALLOWED_PLANS_TO_CREATE_EXPIRES_LINKS = ["Enterprise"]
ALLOWED_FILES_FORMAT = [".png", ".jpg"]


class ImageProcessor:
    def __init__(self, user):
        self.user = user
        self.image_links = []

    def copy_and_resize_image(self, image_path, size):
        image_path_resized = image_path.replace(".", f"_{size}px.")
        shutil.copy(image_path, image_path_resized)
        file_format_without_dot = pathlib.Path(image_path).suffix.replace(".", "")
        try:
            img = Image.open(image_path_resized)
            img_resized = img.resize((img.width, size))
            img_resized.save(image_path_resized, file_format_without_dot)
            ImageRepository.add_image(self.user, image_path_resized, file_format_without_dot)
            return ImageRepository.get_image_by_name(image_path_resized)
        except PIL.UnidentifiedImageError:
            return Response({"error": "Unidentified image"}, status=status.HTTP_400_BAD_REQUEST)

    def process_image(self, image_path, api_base_url):

        self.resize_image(200, api_base_url, image_path)

        if self.user.plan in ("Premium", "Enterprise"):
            self.resize_image(400, api_base_url, image_path)

        if self.user.plan == "Enterprise":
            image_original_from_db = ImageRepository.get_image_by_name(image_path)
            self.add_image_link("original", image_original_from_db.id, api_base_url)

    def resize_image(self, image_size, api_base_url, image_path):
        image = self.copy_and_resize_image(image_path, image_size)
        self.add_image_link(image_size, image.id, api_base_url)

    def add_image_link(self, size, image_id, api_base_url):
        self.image_links.append({"size": size, "link": f"{api_base_url}images/{image_id}"})


@api_view(['POST'])
def upload_image(request):
    api_base_url = config('API_BASE_URL')
    token = request.headers.get('Authorization')
    decoded_token = validate_jwt_token(token)

    if not token or not decoded_token:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

    user_id = decoded_token["user_id"]

    if 'image' not in request.FILES:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

    image = request.FILES['image']

    uploaded_image = image.name
    user = UserRepository.get_user_by_id(user_id)
    if not user:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    file_format = pathlib.Path(uploaded_image).suffix

    if file_format not in ALLOWED_FILES_FORMAT:
        return Response({"error": "Incorrect file format"}, status=status.HTTP_400_BAD_REQUEST)

    image_path_deleted_spaces = uploaded_image.replace(" ", "_")
    image_path = 'media/' + image_path_deleted_spaces
    image_from_db = ImageRepository.get_image_by_name(image_path)

    if image_from_db:
        return Response({"error": "This image already exists"}, status=status.HTTP_409_CONFLICT)

    ImageRepository.add_image(user, image_path, file_format.replace(".", ""))

    with open(image_path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)

    image_processor = ImageProcessor(user)
    image_processor.process_image(image_path, api_base_url)

    return Response({"message": "Image uploaded successfully",
                     "image_links": image_processor.image_links}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def show_image(request, image_id):
    image = ImageRepository.get_image_by_id(image_id)
    if not image:
        return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)
    image_path = image.path
    expires_token = request.GET.get('expires_token')
    if expires_token:
        try:
            jwt.decode(expires_token, config('SIGNING_KEY'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)

    img_file = open(str(image_path), 'rb')
    response = FileResponse(img_file)
    return response


@api_view(['GET'])
def show_image_admin(request, image_id):
    image = ImageRepository.get_image_by_id_admin(image_id)
    if not image:
        return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

    image_path = image.path
    image_path = str(image_path)
    expires_token = request.GET.get('expires_token')
    if expires_token:
        try:
            jwt.decode(expires_token, config('SIGNING_KEY'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
    if not image_path.startswith("media/"):
        image_path = f'media/{image_path}'
    img_file = open(image_path, 'rb')
    response = FileResponse(img_file, status=status.HTTP_200_OK)
    return response


@api_view(['POST'])
def create_image_link_for_enterprise(request, image_id):
    api_base_url = config('API_BASE_URL')
    token_from_headers = request.headers.get('Authorization')
    decoded_token = validate_jwt_token(token_from_headers)

    if not token_from_headers or not decoded_token:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

    user_id = decoded_token["user_id"]
    user = UserRepository.get_user_by_id(user_id)

    if not user:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    if user.plan not in ALLOWED_PLANS_TO_CREATE_EXPIRES_LINKS:
        return Response({"error": "You haven't enterprise plan"}, status=status.HTTP_401_UNAUTHORIZED)

    image = ImageRepository.get_image_by_id(image_id)

    expiration_time = request.data.get('expiration_time')

    if expiration_time is None or not isinstance(expiration_time, int):
        return Response({"error": "Expiration time is required and must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST)

    expiration_datetime = datetime.utcnow() + timedelta(seconds=expiration_time)
    expiration_timestamp = expiration_datetime.timestamp()

    token = jwt.encode({"id": str(image.id), "exp": expiration_timestamp}, config('SIGNING_KEY'), algorithm="HS256")

    image_link = f"{api_base_url}images/{image.id}?expires_token={token}"

    return Response({"image_link": image_link}, status=status.HTTP_201_CREATED)






