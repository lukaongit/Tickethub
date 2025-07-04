from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
import logging
from contextlib import asynccontextmanager

from .models import Ticket, TicketDetail, TicketList, TicketStats
from .services import get_service, cleanup_service, DummyJSONService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TicketHub service")
    yield
    logger.info("Shutting down TicketHub service")
    await cleanup_service()


app = FastAPI(
    title="TicketHub",
    description="Middleware REST service for support ticket management",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TicketHub"}


@app.get("/tickets", response_model=TicketList)
async def get_tickets(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, regex="^(open|closed)$", description="Filter by status"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$", description="Filter by priority"),
    service: DummyJSONService = Depends(get_service)
):
    skip = (page - 1) * limit
    
    try:
        tickets, total = await service.get_tickets(
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


@app.get("/tickets/search", response_model=TicketList)
async def search_tickets(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: DummyJSONService = Depends(get_service)
):
    skip = (page - 1) * limit
    
    try:
        tickets, total = await service.get_tickets(
            skip=skip,
            limit=limit,
            search=q
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


@app.get("/tickets/{ticket_id}", response_model=TicketDetail)
async def get_ticket(
    ticket_id: int,
    service: DummyJSONService = Depends(get_service)
):
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/stats", response_model=TicketStats)
async def get_ticket_stats(
    service: DummyJSONService = Depends(get_service)
):
    try:
        return await service.get_ticket_stats()
    except Exception as e:
        logger.error(f"Error fetching ticket stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
