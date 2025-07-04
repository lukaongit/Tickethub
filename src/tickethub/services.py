import asyncio
from typing import Optional, Dict, Any, List
import httpx
from .models import Ticket, TicketDetail, TicketStats


class DummyJSONService:
    BASE_URL = "https://dummyjson.com"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self._users_cache: Dict[int, str] = {}
    
    async def close(self):
        await self.client.aclose()
    
    async def _get_users(self) -> Dict[int, str]:
        if not self._users_cache:
            response = await self.client.get(f"{self.BASE_URL}/users")
            response.raise_for_status()
            users_data = response.json()
            
            for user in users_data.get("users", []):
                self._users_cache[user["id"]] = user["username"]
        
        return self._users_cache
    
    def _calculate_priority(self, ticket_id: int) -> str:
        priority_map = {0: "low", 1: "medium", 2: "high"}
        return priority_map[ticket_id % 3]
    
    async def _transform_ticket(self, todo_data: dict, users: Dict[int, str]) -> Ticket:
        assignee = users.get(todo_data["userId"], f"user_{todo_data['userId']}")
        
        return Ticket(
            id=todo_data["id"],
            title=todo_data["todo"],
            status="closed" if todo_data["completed"] else "open",
            priority=self._calculate_priority(todo_data["id"]),
            assignee=assignee,
            description=todo_data["todo"][:100] if len(todo_data["todo"]) > 100 else todo_data["todo"]
        )
    
    async def get_tickets(
        self, 
        skip: int = 0, 
        limit: int = 30,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Ticket], int]:
        response = await self.client.get(f"{self.BASE_URL}/todos")
        response.raise_for_status()
        todos_data = response.json()
        
        users = await self._get_users()
        
        tickets = []
        for todo in todos_data.get("todos", []):
            ticket = await self._transform_ticket(todo, users)
            
            # Apply filters
            if status and ticket.status != status:
                continue
            if priority and ticket.priority != priority:
                continue
            if search and search.lower() not in ticket.title.lower():
                continue
                
            tickets.append(ticket)
        
        total = len(tickets)
        paginated_tickets = tickets[skip:skip + limit]
        
        return paginated_tickets, total
    
    async def get_ticket_by_id(self, ticket_id: int) -> Optional[TicketDetail]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/todos/{ticket_id}")
            response.raise_for_status()
            todo_data = response.json()
            
            users = await self._get_users()
            ticket = await self._transform_ticket(todo_data, users)
            
            return TicketDetail(
                **ticket.model_dump(),
                raw_data=todo_data
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    async def get_ticket_stats(self) -> TicketStats:
        tickets, _ = await self.get_tickets(limit=1000)  # Get all tickets
        
        total_tickets = len(tickets)
        open_tickets = sum(1 for t in tickets if t.status == "open")
        closed_tickets = total_tickets - open_tickets
        
        priority_counts = {"low": 0, "medium": 0, "high": 0}
        assignee_counts = {}
        
        for ticket in tickets:
            priority_counts[ticket.priority] += 1
            assignee_counts[ticket.assignee] = assignee_counts.get(ticket.assignee, 0) + 1
        
        return TicketStats(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            closed_tickets=closed_tickets,
            priority_counts=priority_counts,
            assignee_counts=assignee_counts
        )


# Global service instance
dummy_service = DummyJSONService()


async def get_service() -> DummyJSONService:
    return dummy_service


async def cleanup_service():
    await dummy_service.close()
