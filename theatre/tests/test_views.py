import random
import string

from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import get_user_model
from rest_framework_simplejwt.views import status

from theatre.models import Genre, Actor, Performance, Play, TheatreHall
from theatre.serializers import (
    PerformanceDetailSerializer,
    PerformanceListSerializer,
    PerformanceSerializer,
    PlayDetailSerializer,
    PlayListSerializer,
    PlaySerializer,
)


PLAY_URL = reverse("theatre:play-list")
PERFORMANCE_URL = reverse("theatre:performance-list")


def play_detail_url(pk: int) -> str:
    return reverse("theatre:play-detail", args=[pk])


def performance_detail_url(pk: int) -> str:
    return reverse("theatre:performance-detail", args=[pk])


def sample_genre(**params):
    defaults = {
        "name": "".join(random.choices(string.ascii_letters, k=5)),
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {
        "first_name": "".join(random.choices(string.ascii_letters, k=5)),
        "last_name": "".join(random.choices(string.ascii_letters, k=5)),
    }
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_play(**params):
    defaults = {
        "title": "".join(random.choices(string.ascii_letters, k=5)),
        "description": "".join(random.choices(string.ascii_letters, k=50)),
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_theatre_hall(**params):
    defaults = {
        "name": "".join(random.choices(string.ascii_letters, k=5)),
        "rows": 10,
        "seats_in_row": 15,
    }
    defaults.update(params)

    return TheatreHall.objects.create(**defaults)


def sample_performance(
    play_id, theatre_hall_id, show_time="2023-01-01T13:00:00Z"
):
    defaults = {
        "play_id": play_id,
        "theatre_hall_id": theatre_hall_id,
        "show_time": show_time,
    }

    return Performance.objects.create(**defaults)


class UnauthenticatedPlayViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_play_list_is_allowed(self) -> None:
        resp = self.client.get(PLAY_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_play_create_is_forbidden(self) -> None:
        resp = self.client.post(PLAY_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@user.com", password="test_password"
        )
        self.client.force_authenticate(user)

    def test_play_list_is_allowed(self) -> None:
        resp = self.client.get(PLAY_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_play_create_is_forbidden(self) -> None:
        resp = self.client.post(PLAY_URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_play_list(self) -> None:
        for _ in range(3):
            sample_play()

        resp = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_play_list_with_genres_and_actors(self) -> None:
        for _ in range(3):
            sample_genre()
            sample_actor()

        for _ in range(3):
            play = sample_play()
            play.genres.set([1, 2, 3])
            play.actors.set([1, 2, 3])

        resp = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_play_list_filter_by_title(self) -> None:
        sample_play(title="test")
        sample_play(title="another_test")
        sample_play(title="play_title")

        resp = self.client.get(PLAY_URL, {"title": "test"})
        plays = Play.objects.filter(title__icontains="test")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_play_list_filter_by_genres(self) -> None:
        for _ in range(3):
            sample_genre()

        sample_play().genres.set([1, 2])
        sample_play().genres.set([1])
        sample_play().genres.set([3])

        resp = self.client.get(PLAY_URL, {"genres": "1,2"})
        plays = Play.objects.filter(genres__id__in=[1, 2]).distinct()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_play_list_filter_by_actors(self) -> None:
        for _ in range(3):
            sample_actor()

        sample_play().actors.set([1, 2])
        sample_play().actors.set([1])
        sample_play().actors.set([3])

        resp = self.client.get(PLAY_URL, {"actors": "1,2"})
        plays = Play.objects.filter(actors__id__in=[1, 2]).distinct()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_play_retrieve_is_allowed(self) -> None:
        for _ in range(3):
            sample_genre()
            sample_actor()

        play = sample_play()
        play.genres.set([1, 2, 3])
        play.actors.set([1, 2, 3])

        url = play_detail_url(play.pk)
        resp = self.client.get(url)
        serializer = PlayDetailSerializer(play)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)


class AdminPlayViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="test_password"
        )
        self.client.force_authenticate(admin)

    def test_play_list_is_allowed(self) -> None:
        resp = self.client.get(PLAY_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_play_retrieve_is_allowed(self) -> None:
        for _ in range(3):
            sample_genre()
            sample_actor()

        play = sample_play()
        play.genres.set([1, 2, 3])
        play.actors.set([1, 2, 3])

        url = play_detail_url(play.pk)
        resp = self.client.get(url)
        serializer = PlayDetailSerializer(play)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_play_create_is_allowed(self) -> None:
        for _ in range(3):
            sample_genre()
            sample_actor()

        data = {
            "title": "test_title",
            "description": "test_description",
            "genres": [1, 2, 3],
            "actors": [1, 2, 3],
        }

        resp = self.client.post(PLAY_URL, data=data)
        play = get_object_or_404(Play, pk=1)
        serializer = PlaySerializer(play)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        for key, value in data.items():
            self.assertCountEqual(value, serializer.data.get(key))

    def test_play_update_is_allowed(self) -> None:
        play = sample_play()

        for _ in range(3):
            sample_genre()
            sample_actor()

        data = {
            "title": "test_title",
            "description": "test_description",
            "genres": [1, 2, 3],
            "actors": [1, 2, 3],
        }

        url = play_detail_url(play.pk)
        resp = self.client.put(url, data=data)
        play.refresh_from_db()
        serializer = PlaySerializer(play)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key, value in data.items():
            self.assertCountEqual(value, serializer.data.get(key))

    def test_play_delete_is_allowed(self) -> None:
        play = sample_play()

        url = play_detail_url(play.pk)
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Play.objects.filter(id=play.pk).exists())


class UnauthenticatedPerformanceViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_performance_list_is_allowed(self) -> None:
        resp = self.client.get(PERFORMANCE_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_performance_create_is_forbidden(self) -> None:
        resp = self.client.post(PERFORMANCE_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPerformanceViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@user.com", password="test_password"
        )
        self.client.force_authenticate(user)

    def test_performance_list_is_allowed(self) -> None:
        resp = self.client.get(PERFORMANCE_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_performance_create_is_forbidden(self) -> None:
        resp = self.client.post(PERFORMANCE_URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_performance_list(self) -> None:
        sample_play()
        sample_theatre_hall()
        for _ in range(3):
            sample_performance(play_id=1, theatre_hall_id=1)

        resp = self.client.get(PERFORMANCE_URL)
        performances = Performance.objects.annotate(
            available_tickets=F("theatre_hall__rows")
            * F("theatre_hall__seats_in_row")
            - Count("tickets")
        )

        serializer = PerformanceListSerializer(performances, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_performance_list_with_filters(self) -> None:
        sample_theatre_hall()
        for _ in range(2):
            sample_play()
        sample_performance(play_id=1, theatre_hall_id=1)
        sample_performance(play_id=2, theatre_hall_id=1)

        resp = self.client.get(
            PERFORMANCE_URL, {"date": "2023-01-01", "play": 1}
        )
        performances = (
            Performance.objects.filter(show_time__date="2023-01-01", play_id=1)
            .annotate(
                available_tickets=F("theatre_hall__rows")
                * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
            .distinct()
        )
        serializer = PerformanceListSerializer(performances, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_performance_retrieve_is_allowed(self) -> None:
        sample_play()
        sample_theatre_hall()
        performance = sample_performance(play_id=1, theatre_hall_id=1)

        url = performance_detail_url(performance.pk)
        resp = self.client.get(url)
        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)


class AdminPerformanceViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="test_password"
        )
        self.client.force_authenticate(admin)

    def test_performance_list_is_allowed(self) -> None:
        resp = self.client.get(PERFORMANCE_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_performance_create_is_allowed(self) -> None:
        sample_theatre_hall()
        sample_play()
        data = {
            "show_time": "2023-01-01T13:00:00Z",
            "play": 1,
            "theatre_hall": 1,
        }

        resp = self.client.post(PERFORMANCE_URL, data=data)
        performance = get_object_or_404(Performance, pk=1)
        serializer = PerformanceSerializer(performance)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        for key, value in data.items():
            self.assertEqual(value, serializer.data.get(key))

    def test_performance_update_is_allowed(self) -> None:
        for _ in range(2):
            sample_play()
            sample_theatre_hall()
        performance = sample_performance(play_id=1, theatre_hall_id=1)
        data = {
            "show_time": "2023-02-02T00:00:00Z",
            "play": 2,
            "theatre_hall": 2,
        }

        url = performance_detail_url(performance.pk)
        resp = self.client.put(url, data=data)
        performance.refresh_from_db()
        serializer = PerformanceSerializer(performance)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key, value in data.items():
            self.assertEqual(value, serializer.data.get(key))

    def test_performance_delete_is_allowed(self) -> None:
        sample_play()
        sample_theatre_hall()
        performance = sample_performance(play_id=1, theatre_hall_id=1)

        url = performance_detail_url(performance.pk)
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Performance.objects.filter(id=performance.pk).exists()
        )
