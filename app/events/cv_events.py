import time
import uuid


def build_cv_generated_event(*, user_id: str, cv_id: str, title: str, template_id: str | None) -> dict:
    data: dict = {"cvId": cv_id, "title": title}
    if template_id:
        data["templateId"] = template_id
    return {
        "schemaVersion": 1,
        "eventId": str(uuid.uuid4()),
        "type": "cv.generated",
        "userId": user_id,
        "occurredAt": int(time.time() * 1000),
        "source": "cvs",
        "data": data,
    }
