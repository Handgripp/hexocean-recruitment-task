from .models import Users, Images


class UserRepository:
    @staticmethod
    def get_user_by_email(email):
        user = Users.objects.filter(email=email).first()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        user = Users.objects.filter(id=user_id).first()
        return user


class ImageRepository:
    @staticmethod
    def add_image(user_id, image_path, file_format):
        image = Images(user_id=user_id, path=image_path, format=file_format)
        image.save()

    @staticmethod
    def get_image_by_name(image_path):
        image = Images.objects.filter(path=image_path).first()
        return image

    @staticmethod
    def get_image_by_id(image_id):
        image = Images.objects.filter(id=image_id).first()
        return image
