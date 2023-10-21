from django.urls import include, path
from rest_framework.routers import DefaultRouter

from theatre.views import (
    ActorViewSet,
    GenreViewSet,
    PerformanceViewSet,
    PlayViewSet,
    ReservationViewSet,
    TheatreHallViewSet,
)


router = DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)
router.register("theatre_halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "theatre"
