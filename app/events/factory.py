from typing import Annotated

from fastapi import Depends

from app.config import settings
from app.events.base import EventPublisher
from app.events.null import NullEventPublisher
from app.events.service_bus import ServiceBusEventPublisher


def get_event_publisher() -> EventPublisher:
    if settings.service_bus_connection_string:
        return ServiceBusEventPublisher()
    return NullEventPublisher()


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]
