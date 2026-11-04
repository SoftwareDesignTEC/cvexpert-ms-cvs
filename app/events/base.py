from abc import ABC, abstractmethod


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, *, subject: str, message_id: str, body: dict) -> None: ...
