from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.shortcuts import get_object_or_404

from db.models import Order, User, MovieSession, Ticket


@transaction.atomic
def create_order(tickets: list[dict]) -> Order:
    if not tickets:
        raise ValueError("tickets list cannot be empty")

    username = tickets[0].get("username")
    user = get_object_or_404(User, username=username)

    provided_date = tickets[0].get("date")

    # створення order всередині atomic
    order = Order.objects.create(
        user=user,
        created_at=provided_date if provided_date else timezone.now()
    )

    # створення квитків всередині atomic
    for ticket_data in tickets:
        movie_session = get_object_or_404(
            MovieSession,
            id=ticket_data["movie_session"]
        )

        ticket = Ticket(
            movie_session=movie_session,
            order=order,
            row=ticket_data["row"],
            seat=ticket_data["seat"]
        )

        ticket.full_clean()   # перевірка row/seat
        ticket.save()

    return order


def get_orders(username: str = None) -> QuerySet:
    if username:
        user = get_object_or_404(User, username=username)
        return Order.objects.filter(user=user).order_by("-created_at")

    return Order.objects.all().order_by("-created_at")
