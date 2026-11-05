import asyncio
import json
import logging

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

from app.config import settings
from app.events.base import EventPublisher

logger = logging.getLogger(__name__)

_RETRY_DELAYS_SECONDS = (0.5, 1.0)


class ServiceBusEventPublisher(EventPublisher):
    """Publica a Service Bus con 2-3 reintentos cortos. Nunca propaga la excepción:
    si fallan todos los intentos, el CV ya quedó guardado y solo se loguea."""

    async def publish(self, *, subject: str, message_id: str, body: dict) -> None:
        message = ServiceBusMessage(
            json.dumps(body),
            content_type="application/json",
            subject=subject,
            message_id=message_id,
        )
        attempts = len(_RETRY_DELAYS_SECONDS) + 1
        for attempt in range(1, attempts + 1):
            try:
                async with ServiceBusClient.from_connection_string(
                    settings.service_bus_connection_string
                ) as client, client.get_queue_sender(settings.service_bus_queue) as sender:
                    await sender.send_messages(message)
                return
            except Exception:
                logger.warning(
                    "Fallo al publicar evento %s (intento %s/%s, eventId=%s)",
                    subject,
                    attempt,
                    attempts,
                    message_id,
                    exc_info=True,
                )
                if attempt < attempts:
                    await asyncio.sleep(_RETRY_DELAYS_SECONDS[attempt - 1])
        logger.error("No se pudo publicar el evento %s tras %s intentos, eventId=%s", subject, attempts, message_id)
