import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from src.tickethub.handlers import TicketHandler
from src.tickethub.models import Ticket, TicketDetail, TicketStats, TicketStatus, TicketPriority


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.fixture
def handler(mock_service):
    return TicketHandler(mock_service)


@pytest.mark.asyncio
async def test_get_tickets_success(handler, mock_service):
    mock_service.get_tickets.return_value = (
        [
            Ticket(id=1, title="Test 1", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1"),
            Ticket(id=2, title="Test 2", status=TicketStatus.CLOSED, priority=TicketPriority.LOW, assignee="user2")
        ],
        2
    )

    result = await handler.get_tickets(page=1, limit=10)

    assert len(result.tickets) == 2
    assert result.total == 2
    assert result.page == 1
    assert result.limit == 10
    assert result.has_next is False

    mock_service.get_tickets.assert_called_once_with(
        skip=0, limit=10, status=None, priority=None
    )


@pytest.mark.asyncio
async def test_get_tickets_with_filters(handler, mock_service):
    mock_service.get_tickets.return_value = (
        [Ticket(id=1, title="Open high", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1")],
        1
    )

    result = await handler.get_tickets(
        page=1, 
        limit=10, 
        status=TicketStatus.OPEN, 
        priority=TicketPriority.HIGH
    )

    assert len(result.tickets) == 1
    assert result.tickets[0].status == TicketStatus.OPEN
    assert result.tickets[0].priority == TicketPriority.HIGH

    mock_service.get_tickets.assert_called_once_with(
        skip=0, limit=10, status=TicketStatus.OPEN, priority=TicketPriority.HIGH
    )


@pytest.mark.asyncio
async def test_get_tickets_with_pagination(handler, mock_service):
    mock_service.get_tickets.return_value = (
        [Ticket(id=11, title="Test 11", status=TicketStatus.OPEN, priority=TicketPriority.MEDIUM, assignee="user1")],
        15  # Total tickets
    )

    result = await handler.get_tickets(page=2, limit=10)

    assert result.page == 2
    assert result.limit == 10
    assert result.total == 15
    assert result.has_next is False  # 10 + 10 = 20 > 15, so no next page

    mock_service.get_tickets.assert_called_once_with(
        skip=10, limit=10, status=None, priority=None
    )


@pytest.mark.asyncio
async def test_get_tickets_error(handler, mock_service):
    mock_service.get_tickets.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await handler.get_tickets()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"


@pytest.mark.asyncio
async def test_search_tickets_success(handler, mock_service):
    mock_service.get_tickets.return_value = (
        [Ticket(id=1, title="Important task", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1")],
        1
    )

    result = await handler.search_tickets("important", page=1, limit=10)

    assert len(result.tickets) == 1
    assert "Important" in result.tickets[0].title

    mock_service.get_tickets.assert_called_once_with(
        skip=0, limit=10, search="important"
    )


@pytest.mark.asyncio
async def test_search_tickets_error(handler, mock_service):
    mock_service.get_tickets.side_effect = Exception("Search error")

    with pytest.raises(HTTPException) as exc_info:
        await handler.search_tickets("test")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"


@pytest.mark.asyncio
async def test_get_ticket_by_id_success(handler, mock_service):
    mock_service.get_ticket_by_id.return_value = TicketDetail(
        id=1,
        title="Test ticket",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assignee="user1",
        raw_data={"id": 1, "todo": "Test", "completed": False, "userId": 1}
    )

    result = await handler.get_ticket_by_id(1)

    assert result.id == 1
    assert result.title == "Test ticket"
    assert "raw_data" in result.__dict__

    mock_service.get_ticket_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_ticket_by_id_not_found(handler, mock_service):
    mock_service.get_ticket_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await handler.get_ticket_by_id(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Ticket not found"


@pytest.mark.asyncio
async def test_get_ticket_by_id_error(handler, mock_service):
    mock_service.get_ticket_by_id.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await handler.get_ticket_by_id(1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"


@pytest.mark.asyncio
async def test_get_ticket_stats_success(handler, mock_service):
    mock_service.get_ticket_stats.return_value = TicketStats(
        total_tickets=10,
        open_tickets=6,
        closed_tickets=4,
        priority_counts={"low": 3, "medium": 4, "high": 3},
        assignee_counts={"user1": 5, "user2": 5}
    )

    result = await handler.get_ticket_stats()

    assert result.total_tickets == 10
    assert result.open_tickets == 6
    assert result.closed_tickets == 4

    mock_service.get_ticket_stats.assert_called_once()


@pytest.mark.asyncio
async def test_get_ticket_stats_error(handler, mock_service):
    mock_service.get_ticket_stats.side_effect = Exception("Stats error")

    with pytest.raises(HTTPException) as exc_info:
        await handler.get_ticket_stats()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
