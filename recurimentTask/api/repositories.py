from .models import User


class UserRepository:
    @staticmethod
    def get_user_by_email(email):
        user = User.objects.filter(email=email).first()
        return user
