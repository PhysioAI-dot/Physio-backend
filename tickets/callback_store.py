from typing import List
from schemas import CallbackTicket

_CALLBACKS: list[CallbackTicket] = []


def save_callback(ticket: CallbackTicket) -> None:
    _CALLBACKS.append(ticket)


def list_callbacks() -> List[CallbackTicket]:
    return list(_CALLBACKS)
