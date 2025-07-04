import pytest
import httpx
from unittest.mock import AsyncMock, patch
from src.tickethub.services import DummyJSONService
from src.tickethub.models import TicketStatus, TicketPriority


@pytest.fixture
async def service():
    service = DummyJSONService()
    yield service
    await service.close()


@pytest.mark.asyncio
async def test_calculate_priority():
    service = DummyJSONService()
    
    assert service._calculate_priority(1) == TicketPriority.MEDIUM  # 1 % 3 = 1
    assert service._calculate_priority(2) == TicketPriority.HIGH    # 2 % 3 = 2  
    assert service._calculate_priority(3) == TicketPriority.LOW     # 3 % 3 = 0


@pytest.mark.asyncio
async def test_get_users_caching(service):
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "users": [
            {"id": 1, "username": "atuny0"},
            {"id": 2, "username": "hbingley1"}
        ]
    }
    mock_response.raise_for_status = AsyncMock()
    
    with patch.object(service.client, 'get', return_value=mock_response):
        # First call should make HTTP request
        users = await service._get_users()
        assert users[1] == "atuny0"
        assert users[2] == "hbingley1"
        
        # Second call should use cache
        users2 = await service._get_users()
        assert users2 == users
        
        # Should only have made one HTTP call
        service.client.get.assert_called_once()


@pytest.mark.asyncio
async def test_transform_ticket():
    service = DummyJSONService()
    
    todo_data = {
        "id": 1,
        "todo": "Do something important",
        "completed": False,
        "userId": 1
    }
    users = {1: "testuser"}
    
    ticket = await service._transform_ticket(todo_data, users)
    
    assert ticket.id == 1
    assert ticket.title == "Do something important"
    assert ticket.status == TicketStatus.OPEN
    assert ticket.priority == TicketPriority.MEDIUM  # 1 % 3 = 1
    assert ticket.assignee == "testuser"


@pytest.mark.asyncio
async def test_transform_ticket_completed():
    service = DummyJSONService()
    
    todo_data = {
        "id": 2,
        "todo": "Completed task",
        "completed": True,
        "userId": 1
    }
    users = {1: "testuser"}
    
    ticket = await service._transform_ticket(todo_data, users)
    
    assert ticket.status == TicketStatus.CLOSED
    assert ticket.priority == TicketPriority.HIGH  # 2 % 3 = 2


@pytest.mark.asyncio
async def test_get_ticket_by_id_not_found(service):
    mock_response = AsyncMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not found", 
        request=httpx.Request("GET", "http://test.com"),
        response=httpx.Response(404)
    )
    
    with patch.object(service.client, 'get', return_value=mock_response):
        ticket = await service.get_ticket_by_id(999)
        assert ticket is None


@pytest.mark.asyncio
async def test_get_tickets_filtering(service):
    mock_todos_response = AsyncMock()
    mock_todos_response.json.return_value = {
        "todos": [
            {"id": 1, "todo": "Open task", "completed": False, "userId": 1},
            {"id": 2, "todo": "Closed task", "completed": True, "userId": 1},
            {"id": 3, "todo": "Another open", "completed": False, "userId": 1}
        ]
    }
    mock_todos_response.raise_for_status = AsyncMock()
    
    mock_users_response = AsyncMock()
    mock_users_response.json.return_value = {
        "users": [{"id": 1, "username": "testuser"}]
    }
    mock_users_response.raise_for_status = AsyncMock()
    
    with patch.object(service.client, 'get') as mock_get:
        mock_get.side_effect = [mock_todos_response, mock_users_response]
        
        # Test status filtering
        tickets, total = await service.get_tickets(status=TicketStatus.OPEN)
        assert len(tickets) == 2
        assert all(t.status == TicketStatus.OPEN for t in tickets)
        
        # Reset mock
        mock_get.side_effect = [mock_todos_response, mock_users_response]
        
        # Test search filtering
        tickets, total = await service.get_tickets(search="Open")
        assert len(tickets) == 2
        assert all("open" in t.title.lower() for t in tickets)
