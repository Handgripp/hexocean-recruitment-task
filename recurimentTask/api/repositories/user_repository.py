from ..models.user_model import Users


class UserRepository:
    @staticmethod
    def get_user_by_email(email):
        user = Users.objects.filter(email=email).first()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        user = Users.objects.filter(id=user_id).first()
        return user

