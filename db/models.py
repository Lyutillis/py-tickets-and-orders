from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(to=Actor, related_name="movies")
    genres = models.ManyToManyField(to=Genre, related_name="movies")

    def __str__(self) -> str:
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["title"])
        ]


class CinemaHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class MovieSession(models.Model):
    show_time = models.DateTimeField()
    cinema_hall = models.ForeignKey(
        to=CinemaHall, on_delete=models.CASCADE, related_name="movie_sessions"
    )
    movie = models.ForeignKey(
        to=Movie, on_delete=models.CASCADE, related_name="movie_sessions"
    )

    def __str__(self) -> str:
        return f"{self.movie.title} {str(self.show_time)}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("db.User", on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")


class Ticket(models.Model):
    movie_session = models.ForeignKey(MovieSession, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    row = models.IntegerField()
    seat = models.IntegerField()

    def __str__(self) -> str:
        return (
            f"{self.movie_session.movie.title} "
            f"{self.movie_session.show_time.strftime('%Y-%m-%d %H:%M:%S')} "
            f"(row: {self.row}, seat: {self.seat})"
        )

    def clean(self, *args, **kwargs) -> None:
        super().clean(*args, **kwargs)
        duplicates = Ticket.objects.filter(
            movie_session=self.movie_session,
            order=self.order,
            row=self.row,
            seat=self.seat,
        )
        if duplicates.exists():
            raise ValidationError("Unique constraint failed")
        if self.row > self.movie_session.cinema_hall.rows:
            raise ValidationError({"row": [
                f"row number must be in available range:"
                f" (1, rows): (1, {self.movie_session.cinema_hall.rows})"
            ]})
        if self.seat > self.movie_session.cinema_hall.seats_in_row:
            raise ValidationError({"seat": [
                f"seat number must be in available range: (1, seats_in_row):"
                f" (1, {self.movie_session.cinema_hall.seats_in_row})"
            ]})

    def save(self, *args, **kwargs) -> None:
        self.clean()
        super(Ticket, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "movie_session",
                    "row",
                    "seat"
                ],
                name="TicketUniqueConstraint"
            )
        ]


class User(AbstractUser):
    ...
