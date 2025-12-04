from datetime import datetime

from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from db.models import User, Order, Ticket, MovieSession


@transaction.atomic
def create_order(
    tickets: list[dict],
    username: str,
    date: str | None = None,
) -> Order:

    user = get_object_or_404(User, username=username)

    # 1) створюємо order (created_at = now() через auto_now_add)
    order = Order.objects.create(user=user)

    # 2) якщо дата передана → перезаписуємо created_at і зберігаємо
    if date is not None:
        order.created_at = datetime.strptime(date, "%Y-%m-%d %H:%M")
        order.save(update_fields=["created_at"])

    # 3) створюємо tickets
    for _ticket in tickets:
        movie_session = get_object_or_404(
            MovieSession, id=_ticket["movie_session"])

        ticket = Ticket(
            movie_session=movie_session,
            order=order,
            row=_ticket["row"],
            seat=_ticket["seat"],
        )
        ticket.full_clean()
        ticket.save()

    return order


def get_orders(username: str = None) -> QuerySet:
    if username:
        user = get_object_or_404(User, username=username)
        return Order.objects.filter(user=user).order_by("-created_at")

    return Order.objects.all().order_by("-created_at")
