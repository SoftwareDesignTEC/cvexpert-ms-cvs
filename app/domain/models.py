from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: str
    email: str
    role: str | None = None


class Template(BaseModel):
    id: str
    name: str
    description: str
    previewUrl: str
    category: str
    isPremium: bool
    availableOffline: bool


class PaginatedTemplates(BaseModel):
    items: list[Template]
    page: int
    pageSize: int
    totalRecords: int
