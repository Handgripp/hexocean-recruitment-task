from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..validate_token import validate_jwt_token
from ..repositories.image_repository import ImageRepository
from ..repositories.user_repository import UserRepository
from decouple import config


@api_view(['GET'])
def get_links(request):
    api_base_url = config('API_BASE_URL')
    token = request.headers.get('Authorization')
    decoded_token = validate_jwt_token(token)

    if not token or not decoded_token:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

    user_id = decoded_token["user_id"]

    user = UserRepository.get_user_by_id(user_id)
    if not user:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    images_id = ImageRepository.get_many_by_user_id(user_id)

    if not images_id:
        return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

    image_links = []

    for image_id in images_id:
        image_links.append({"link": f"{api_base_url}images/{image_id}"})

    return Response({"image_links": image_links}, status=status.HTTP_201_CREATED)



