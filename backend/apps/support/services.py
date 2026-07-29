from django.utils import timezone

from apps.support.models import SupportTicket


class SupportTicketTransitionError(Exception):
    """Raised when a requested ticket status transition isn't allowed."""


def close_ticket(ticket: SupportTicket, user) -> SupportTicket:
    if ticket.status == SupportTicket.Status.CLOSED:
        raise SupportTicketTransitionError("Ticket is already closed.")

    ticket.status = SupportTicket.Status.CLOSED
    ticket.closed_at = timezone.now()
    ticket.updated_by = user
    ticket.save(update_fields=["status", "closed_at", "updated_by", "updated_at"])
    return ticket


def reopen_ticket(ticket: SupportTicket, user) -> SupportTicket:
    if ticket.status != SupportTicket.Status.CLOSED:
        raise SupportTicketTransitionError("Only a closed ticket can be reopened.")

    ticket.status = SupportTicket.Status.OPEN
    ticket.closed_at = None
    ticket.updated_by = user
    ticket.save(update_fields=["status", "closed_at", "updated_by", "updated_at"])
    return ticket
