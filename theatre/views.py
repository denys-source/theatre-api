from django.db.models import F, Count, QuerySet
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from theatre.models import (
    Actor,
    Genre,
    Performance,
    Play,
    Reservation,
    TheatreHall,
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    PerformanceDetailSerializer,
    PerformanceListSerializer,
    PerformanceSerializer,
    PlayDetailSerializer,
    PlayListSerializer,
    PlaySerializer,
    ReservationListSerializer,
    ReservationSerializer,
    TheatreHallSerializer,
)


class ActorViewSet(ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_queryset(self) -> QuerySet[Play]:
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("actors", "genres")

        return queryset

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayDetailSerializer
        return self.serializer_class


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_queryset(self) -> QuerySet[Performance]:
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("play", "theatre_hall")

        if self.action == "list":
            queryset = queryset.annotate(
                available_tickets=F("theatre_hall__rows")
                * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )

        return queryset

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceDetailSerializer
        return self.serializer_class


class ReservationViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self) -> QuerySet[Reservation]:
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__performance__play",
                "tickets__performance__theatre_hall",
            )

        return queryset

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "list":
            return ReservationListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
