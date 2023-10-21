from django.contrib import admin
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/theatre/", include("theatre.urls", namespace="theatre")),
    path("api/user/", include("user.urls", namespace="user")),
] + (
    [path("__debug__/", include("debug_toolbar.urls"))]
    if settings.DEBUG
    else []
)
