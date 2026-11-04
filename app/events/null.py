import logging

from app.events.base import EventPublisher

logger = logging.getLogger(__name__)


class NullEventPublisher(EventPublisher):
    """Se usa cuando SERVICE_BUS_CONNECTION_STRING no está configurado (local/dev)."""

    async def publish(self, *, subject: str, message_id: str, body: dict) -> None:
        logger.info("Service Bus no configurado, se omite el evento %s (eventId=%s)", subject, message_id)
