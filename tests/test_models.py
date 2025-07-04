import pytest
from pydantic import ValidationError
from src.tickethub.models import Ticket, TicketDetail, TicketList, TicketStats


def test_ticket_model():
    ticket = Ticket(
        id=1,
        title="Test ticket",
        status="open",
        priority="high",
        assignee="testuser",
        description="Test description"
    )
    
    assert ticket.id == 1
    assert ticket.title == "Test ticket"
    assert ticket.status == "open"
    assert ticket.priority == "high"
    assert ticket.assignee == "testuser"
    assert ticket.description == "Test description"


def test_ticket_model_validation():
    with pytest.raises(ValidationError):
        Ticket(
            id="invalid",  # Should be int
            title="Test",
            status="open",
            priority="high",
            assignee="user"
        )


def test_ticket_detail_model():
    raw_data = {"id": 1, "todo": "Test", "completed": False, "userId": 1}
    
    ticket_detail = TicketDetail(
        id=1,
        title="Test ticket",
        status="open",
        priority="high",
        assignee="testuser",
        raw_data=raw_data
    )
    
    assert ticket_detail.raw_data == raw_data


def test_ticket_list_model():
    tickets = [
        Ticket(id=1, title="Test 1", status="open", priority="high", assignee="user1"),
        Ticket(id=2, title="Test 2", status="closed", priority="low", assignee="user2")
    ]
    
    ticket_list = TicketList(
        tickets=tickets,
        total=2,
        page=1,
        limit=10,
        has_next=False
    )
    
    assert len(ticket_list.tickets) == 2
    assert ticket_list.total == 2
    assert ticket_list.has_next is False


def test_ticket_stats_model():
    stats = TicketStats(
        total_tickets=10,
        open_tickets=6,
        closed_tickets=4,
        priority_counts={"low": 3, "medium": 4, "high": 3},
        assignee_counts={"user1": 5, "user2": 5}
    )
    
    assert stats.total_tickets == 10
    assert stats.open_tickets == 6
    assert stats.closed_tickets == 4
    assert stats.priority_counts["high"] == 3
