import re
from typing import Any
from django.db.models import F, Count, QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
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
from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(params: str) -> list[int]:
        return [
            int(object_id)
            for object_id in params.split(",")
            if object_id.isnumeric()
        ]

    def get_queryset(self) -> QuerySet[Play]:
        queryset = self.queryset

        if title := self.request.query_params.get("title"):
            queryset = queryset.filter(title__icontains=title)

        if actor_params := self.request.query_params.get("actors"):
            actor_ids = self._params_to_ints(actor_params)
            queryset = queryset.filter(actors__id__in=actor_ids)

        if genre_params := self.request.query_params.get("genres"):
            genre_ids = self._params_to_ints(genre_params)
            queryset = queryset.filter(genres__id__in=genre_ids)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("actors", "genres")

        return queryset.distinct()

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                description="Filter plays by title",
                type={"type": "string"},
            ),
            OpenApiParameter(
                "genres",
                description="Filter plays by genres. Example: ?genres=1,2",
                type={"type": "list", "items": {"type": "number"}},
            ),
            OpenApiParameter(
                "actors",
                description="Filter plays by actors. Example: ?actors=1,2",
                type={"type": "list", "items": {"type": "number"}},
            ),
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self) -> QuerySet[Performance]:
        queryset = self.queryset

        if (
            date_str := self.request.query_params.get("date")
        ) and re.fullmatch(
            r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$", date_str
        ):
            queryset = queryset.filter(show_time__date=date_str)

        if (
            play_id := self.request.query_params.get("play")
        ) and play_id.isnumeric():
            queryset = queryset.filter(play_id=play_id)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("play", "theatre_hall")

        if self.action == "list":
            queryset = queryset.annotate(
                available_tickets=F("theatre_hall__rows")
                * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )

        return queryset.distinct()

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                description="Filter performances by date in the format yyyy-mm-dd. Example: ?date=2023-01-01",
                type={"type": "date"},
            ),
            OpenApiParameter(
                "play",
                description="Filter performances by play id",
                type={"type": "number"},
            ),
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)


class ReservationViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

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
