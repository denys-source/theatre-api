from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings


class TheatreHall(models.Model):
    name = models.CharField(max_length=63, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} (rows: {self.rows}, seats: {self.seats_in_row})"


class Actor(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        ordering = ("first_name",)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reservations",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.created_at


class Play(models.Model):
    title = models.CharField(max_length=63)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")

    class Meta:
        ordering = ("title",)

    def __str__(self) -> str:
        return self.title


class Performance(models.Model):
    play = models.ForeignKey(
        Play, related_name="performances", on_delete=models.CASCADE
    )
    theatre_hall = models.ForeignKey(
        TheatreHall, related_name="performances", on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ("-show_time",)

    def __str__(self) -> str:
        return f"{self.play.title} ({self.show_time})"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        Performance, related_name="tickets", on_delete=models.CASCADE
    )
    reservation = models.ForeignKey(
        Reservation, related_name="tickets", on_delete=models.CASCADE
    )

    @staticmethod
    def validate_ticket(
        row: int,
        seat: int,
        performance: Performance,
        exc_to_raise: type[Exception],
    ) -> None:
        for attr_name, attr_value, performance_attr_name in (
            ("row", row, "rows"),
            ("seat", seat, "seats_in_row"),
        ):
            max_value = getattr(performance, performance_attr_name)
            if not attr_value <= max_value:
                raise exc_to_raise(
                    f"{attr_name} must be in range [1, {max_value}]"
                )

    def clean(self) -> None:
        self.validate_ticket(
            self.row, self.seat, self.performance, ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("performance", "row", "seat")
        ordering = ("row", "seat")

    def __str__(self) -> str:
        return f"{self.performance} (row: {self.row}, seat: {self.seat})"
