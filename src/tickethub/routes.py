from typing import Optional
from fastapi import APIRouter, Query, Depends, Path

from .models import TicketList, TicketDetail, TicketStats, TicketStatus, TicketPriority
from .handlers import TicketHandler, get_ticket_handler

router = APIRouter()


@router.get("/tickets", response_model=TicketList)
async def get_tickets(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TicketStatus] = Query(None, description="Filter by status"),
    priority: Optional[TicketPriority] = Query(None, description="Filter by priority"),
    handler: TicketHandler = Depends(get_ticket_handler)
):
    """Get paginated list of tickets with optional filtering."""
    return await handler.get_tickets(
        page=page,
        limit=limit,
        status=status,
        priority=priority
    )


@router.get("/tickets/search", response_model=TicketList)
async def search_tickets(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    handler: TicketHandler = Depends(get_ticket_handler)
):
    """Search tickets by title."""
    return await handler.search_tickets(
        query=q,
        page=page,
        limit=limit
    )


@router.get("/tickets/{ticket_id}", response_model=TicketDetail)
async def get_ticket(
    ticket_id: int = Path(..., description="Ticket ID"),
    handler: TicketHandler = Depends(get_ticket_handler)
):
    """Get detailed ticket information by ID."""
    return await handler.get_ticket_by_id(ticket_id)


@router.get("/stats", response_model=TicketStats)
async def get_ticket_stats(
    handler: TicketHandler = Depends(get_ticket_handler)
):
    """Get aggregated ticket statistics."""
    return await handler.get_ticket_stats()
