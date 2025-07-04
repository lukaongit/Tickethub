from typing import Optional
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    id: int
    title: str
    status: str = Field(..., description="Ticket status: open or closed")
    priority: str = Field(..., description="Ticket priority: low, medium, or high")
    assignee: str = Field(..., description="Username of assigned user")
    description: Optional[str] = Field(None, max_length=100, description="Truncated description")


class TicketDetail(Ticket):
    raw_data: dict = Field(..., description="Full JSON from external source")


class TicketList(BaseModel):
    tickets: list[Ticket]
    total: int
    page: int
    limit: int
    has_next: bool


class TicketStats(BaseModel):
    total_tickets: int
    open_tickets: int
    closed_tickets: int
    priority_counts: dict[str, int]
    assignee_counts: dict[str, int]
