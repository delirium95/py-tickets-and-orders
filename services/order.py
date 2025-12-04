from datetime import datetime

from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from db.models import User, Order, Ticket, MovieSession


@transaction.atomic
def create_order(
    tickets: list[dict],
    username: str,
    date: str | None = None,
) -> Order:

    user = get_object_or_404(User, username=username)

    if date is not None:
        created_at = datetime.strptime(date, "%Y-%m-%d %H:%M")
    else:
        created_at = timezone.now()

    order = Order.objects.create(
        user=user,
        created_at=created_at
    )

    for t in tickets:
        movie_session = get_object_or_404(MovieSession, id=t["movie_session"])

        ticket = Ticket(
            movie_session=movie_session,
            order=order,
            row=t["row"],
            seat=t["seat"],
        )

        ticket.full_clean()
        ticket.save()

    return order


def get_orders(username: str = None) -> QuerySet:
    if username:
        user = get_object_or_404(User, username=username)
        return Order.objects.filter(user=user).order_by("-created_at")

    return Order.objects.all().order_by("-created_at")
