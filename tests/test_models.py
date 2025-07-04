import pytest
from pydantic import ValidationError
from src.tickethub.models import Ticket, TicketDetail, TicketList, TicketStats, TicketStatus, TicketPriority


def test_ticket_model():
    ticket = Ticket(
        id=1,
        title="Test ticket",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assignee="testuser",
        description="Test description"
    )
    
    assert ticket.id == 1
    assert ticket.title == "Test ticket"
    assert ticket.status == TicketStatus.OPEN
    assert ticket.priority == TicketPriority.HIGH
    assert ticket.assignee == "testuser"
    assert ticket.description == "Test description"


def test_ticket_model_validation():
    with pytest.raises(ValidationError):
        Ticket(
            id="invalid",  # Should be int
            title="Test",
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH,
            assignee="user"
        )


def test_ticket_detail_model():
    raw_data = {"id": 1, "todo": "Test", "completed": False, "userId": 1}
    
    ticket_detail = TicketDetail(
        id=1,
        title="Test ticket",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assignee="testuser",
        raw_data=raw_data
    )
    
    assert ticket_detail.raw_data == raw_data


def test_ticket_list_model():
    tickets = [
        Ticket(id=1, title="Test 1", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1"),
        Ticket(id=2, title="Test 2", status=TicketStatus.CLOSED, priority=TicketPriority.LOW, assignee="user2")
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


def test_ticket_enum_validation():
    """Test that ticket status and priority enums validate correctly."""
    # Test valid enum values
    ticket = Ticket(
        id=1,
        title="Test",
        status="open",  # String that matches enum
        priority="medium",  # String that matches enum
        assignee="user1"
    )
    assert ticket.status == TicketStatus.OPEN
    assert ticket.priority == TicketPriority.MEDIUM
    
    # Test invalid enum values
    with pytest.raises(ValidationError):
        Ticket(
            id=1,
            title="Test",
            status="invalid_status",  # Invalid status
            priority=TicketPriority.HIGH,
            assignee="user1"
        )
    
    with pytest.raises(ValidationError):
        Ticket(
            id=1,
            title="Test",
            status=TicketStatus.OPEN,
            priority="invalid_priority",  # Invalid priority
            assignee="user1"
        )


def test_ticket_status_enum():
    """Test TicketStatus enum values."""
    assert TicketStatus.OPEN.value == "open"
    assert TicketStatus.CLOSED.value == "closed"
    assert list(TicketStatus) == [TicketStatus.OPEN, TicketStatus.CLOSED]


def test_ticket_priority_enum():
    """Test TicketPriority enum values."""
    assert TicketPriority.LOW.value == "low"
    assert TicketPriority.MEDIUM.value == "medium"
    assert TicketPriority.HIGH.value == "high"
    assert list(TicketPriority) == [TicketPriority.LOW, TicketPriority.MEDIUM, TicketPriority.HIGH]
