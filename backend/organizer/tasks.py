from celery import shared_task
from django.db import transaction
import logging

from .models import Hackathon
from .services.seating import get_teams_for_allocation, allocate

logger = logging.getLogger(__name__)

@shared_task
def allocate_seats_task(hackathon_id: int):
    """
    Background task to compute and save seating allocation.
    This can be a heavy operation (O(N*M)) that would otherwise block
    the main thread and cause API timeouts for large events.
    """
    logger.info(f"Starting seating allocation for hackathon {hackathon_id}")
    
    try:
        # We don't want the task to crash if the hackathon is deleted right as it starts,
        # but we also need a fresh read of the DB.
        hackathon = Hackathon.objects.get(id=hackathon_id)
        
        rooms_config = hackathon.room_configuration
        if not rooms_config:
            logger.warning(f"Hackathon {hackathon_id} has no room configuration. Aborting allocation.")
            return {"error": "Missing room configuration"}
            
        teams = get_teams_for_allocation(hackathon_id)
        if not teams:
            logger.warning(f"Hackathon {hackathon_id} has no teams. Aborting allocation.")
            return {"error": "No teams found"}

        allocation_result = allocate(teams, rooms_config)
        
        # Save atomically
        with transaction.atomic():
            # Refresh from db and lock row to avoid race conditions
            locked_hackathon = Hackathon.objects.select_for_update().get(id=hackathon_id)
            locked_hackathon.seating_allocation = allocation_result
            locked_hackathon.save(update_fields=['seating_allocation'])
            
        logger.info(f"Successfully allocated seating for hackathon {hackathon_id}")
        return {"status": "success", "allocated_teams": len(teams)}
        
    except Hackathon.DoesNotExist:
        logger.error(f"Hackathon {hackathon_id} not found during seating allocation.")
        return {"error": "Hackathon not found"}
    except Exception as e:
        logger.exception(f"Error during seating allocation for hackathon {hackathon_id}: {str(e)}")
        # In a real system, you might want to save the error state to the Hackathon model
        # so the user knows it failed.
        return {"error": str(e)}
