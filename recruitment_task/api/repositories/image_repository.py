from ..models.image_model import Images, ImagesAdmin


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

    @staticmethod
    def get_image_by_id_admin(image_id):
        image = ImagesAdmin.objects.filter(id=image_id).first()
        return image

    @staticmethod
    def get_many_by_user_id(user_id):
        images = Images.objects.filter(user_id=user_id).all()

        images_data = []
        for image in images:
            image_data = str(image.id)
            images_data.append(image_data)

        return images_data
