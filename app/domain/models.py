from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


EmploymentType = Literal["full-time", "part-time", "freelance", "internship"]
Modality = Literal["remote", "on-site", "hybrid"]
WorkExperienceType = Literal["formal", "freelance", "volunteer", "school-project", "informal"]
SkillLevel = Literal["beginner", "intermediate", "advanced", "expert"]
LanguageLevel = Literal["basic", "intermediate", "advanced", "native"]


class PersonalInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    fullName: str
    email: str
    phone: str | None = None
    address: str | None = None
    photoUrl: str | None = None
    bio: str | None = None
    birthDate: int | None = None
    types: list[EmploymentType] = Field(default_factory=list)
    modalities: list[Modality] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)


class WorkExperience(BaseModel):
    id: str | None = None
    company: str
    position: str
    startDate: int
    endDate: int | None = None
    current: bool
    description: str
    type: WorkExperienceType


class Education(BaseModel):
    id: str | None = None
    institution: str
    degree: str
    field: str
    startDate: int
    endDate: int | None = None
    current: bool


class Skill(BaseModel):
    id: str | None = None
    name: str
    level: SkillLevel
    category: str


class Language(BaseModel):
    id: str | None = None
    name: str
    level: LanguageLevel


class Certification(BaseModel):
    id: str | None = None
    name: str
    issuer: str
    issuedAt: int | None = None
    expiresAt: int | None = None
    credentialUrl: str | None = None


class Cv(BaseModel):
    id: str
    userId: str
    title: str
    templateId: str
    thumbnailUrl: str | None = None
    createdAt: int
    updatedAt: int
    personalInfo: PersonalInfo
    workExperiences: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)


class PaginatedCvs(BaseModel):
    items: list[Cv]
    page: int
    pageSize: int
    totalRecords: int


class CvInput(BaseModel):
    title: str
    templateId: str
    personalInfo: PersonalInfo
    workExperiences: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)


class Error(BaseModel):
    statusCode: int
    error: str
    message: str
    errors: dict[str, str] | None = None


NonLaborExperienceType = Literal["volunteer", "school-project", "informal"]
ResponseLanguage = Literal["es", "en"]


class ExpandExperienceRequest(BaseModel):
    company: str
    position: str
    description: str
    type: WorkExperienceType
    language: ResponseLanguage


class ExpandExperienceResponse(BaseModel):
    description: str


class TranslateExperienceRequest(BaseModel):
    type: NonLaborExperienceType
    position: str
    organization: str | None = None
    description: str
    language: ResponseLanguage


class TranslateExperienceResponse(BaseModel):
    position: str
    description: str
