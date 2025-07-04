import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.tickethub.main import app
from src.tickethub.models import Ticket, TicketDetail, TicketStats, TicketStatus, TicketPriority


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.mark.asyncio
async def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "TicketHub"}


def test_root_redirect(client):
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


@patch('src.tickethub.handlers.get_service')
def test_get_tickets(mock_get_service, client):
    mock_service = AsyncMock()
    mock_service.get_tickets.return_value = (
        [
            Ticket(id=1, title="Test 1", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1"),
            Ticket(id=2, title="Test 2", status=TicketStatus.CLOSED, priority=TicketPriority.LOW, assignee="user2")
        ],
        2
    )
    mock_get_service.return_value = mock_service
    
    response = client.get("/tickets?page=1&limit=10")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["tickets"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["has_next"] is False


@patch('src.tickethub.handlers.get_service')
def test_get_tickets_with_filters(mock_get_service, client):
    mock_service = AsyncMock()
    mock_service.get_tickets.return_value = (
        [Ticket(id=1, title="Open ticket", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1")],
        1
    )
    mock_get_service.return_value = mock_service
    
    response = client.get("/tickets?status=open&priority=high")
    assert response.status_code == 200
    
    mock_service.get_tickets.assert_called_once_with(
        skip=0, limit=10, status=TicketStatus.OPEN, priority=TicketPriority.HIGH
    )


@patch('src.tickethub.handlers.get_service')
def test_search_tickets(mock_get_service, client):
    mock_service = AsyncMock()
    mock_service.get_tickets.return_value = (
        [Ticket(id=1, title="Important task", status=TicketStatus.OPEN, priority=TicketPriority.HIGH, assignee="user1")],
        1
    )
    mock_get_service.return_value = mock_service
    
    response = client.get("/tickets/search?q=important")
    assert response.status_code == 200
    
    mock_service.get_tickets.assert_called_once_with(
        skip=0, limit=10, search="important"
    )


@patch('src.tickethub.handlers.get_service')
def test_get_ticket_by_id(mock_get_service, client):
    mock_service = AsyncMock()
    mock_service.get_ticket_by_id.return_value = TicketDetail(
        id=1,
        title="Test ticket",
        status=TicketStatus.OPEN, 
        priority=TicketPriority.HIGH,
        assignee="user1",
        raw_data={"id": 1, "todo": "Test", "completed": False, "userId": 1}
    )
    mock_get_service.return_value = mock_service
    
    response = client.get("/tickets/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test ticket"
    assert "raw_data" in data


@patch('src.tickethub.handlers.get_service')
def test_get_ticket_not_found(mock_get_service, client):
    mock_service = AsyncMock()
    mock_service.get_ticket_by_id.return_value = None
    mock_get_service.return_value = mock_service
    
    response = client.get("/tickets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


@patch('src.tickethub.handlers.get_service')
def test_get_stats(mock_get_service, client):
    mock_service = AsyncMock()
    mock_service.get_ticket_stats.return_value = TicketStats(
        total_tickets=10,
        open_tickets=6,
        closed_tickets=4,
        priority_counts={"low": 3, "medium": 4, "high": 3},
        assignee_counts={"user1": 5, "user2": 5}
    )
    mock_get_service.return_value = mock_service
    
    response = client.get("/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_tickets"] == 10
    assert data["open_tickets"] == 6
    assert data["closed_tickets"] == 4


def test_invalid_status_filter(client):
    response = client.get("/tickets?status=invalid")
    assert response.status_code == 422


def test_invalid_priority_filter(client):
    response = client.get("/tickets?priority=invalid")
    assert response.status_code == 422


def test_invalid_page_number(client):
    response = client.get("/tickets?page=0")
    assert response.status_code == 422


def test_search_without_query(client):
    response = client.get("/tickets/search")
    assert response.status_code == 422
