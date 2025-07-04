from typing import Optional
from fastapi import HTTPException, Depends
import logging

from .models import TicketList, TicketDetail, TicketStats, TicketStatus, TicketPriority
from .services import get_service, DummyJSONService

logger = logging.getLogger(__name__)


class TicketHandler:
    def __init__(self, service: DummyJSONService):
        self.service = service

    async def get_tickets(
        self,
        page: int = 1,
        limit: int = 10,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
    ) -> TicketList:
        """Get paginated list of tickets with optional filtering."""
        skip = (page - 1) * limit
        
        try:
            tickets, total = await self.service.get_tickets(
                skip=skip,
                limit=limit,
                status=status,
                priority=priority
            )
            
            has_next = skip + limit < total
            
            return TicketList(
                tickets=tickets,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
        except Exception as e:
            logger.error(f"Error fetching tickets: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def search_tickets(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
    ) -> TicketList:
        """Search tickets by title."""
        skip = (page - 1) * limit
        
        try:
            tickets, total = await self.service.get_tickets(
                skip=skip,
                limit=limit,
                search=query
            )
            
            has_next = skip + limit < total
            
            return TicketList(
                tickets=tickets,
                total=total,
                page=page,
                limit=limit,
                has_next=has_next
            )
        except Exception as e:
            logger.error(f"Error searching tickets: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_ticket_by_id(self, ticket_id: int) -> TicketDetail:
        """Get detailed ticket information by ID."""
        try:
            ticket = await self.service.get_ticket_by_id(ticket_id)
            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")
            return ticket
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching ticket {ticket_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_ticket_stats(self) -> TicketStats:
        """Get aggregated ticket statistics."""
        try:
            return await self.service.get_ticket_stats()
        except Exception as e:
            logger.error(f"Error fetching ticket stats: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")


async def get_ticket_handler(service: DummyJSONService = Depends(get_service)) -> TicketHandler:
    """Dependency injection for ticket handler."""
    return TicketHandler(service)
