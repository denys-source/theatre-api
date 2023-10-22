from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from user.serializers import UserSerializer


class UserCreateView(CreateAPIView):
    queryset = get_user_model()
    serializer_class = UserSerializer
