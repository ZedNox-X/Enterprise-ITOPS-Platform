from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import DeviceStatus, IncidentStatus, Severity


class DeviceCreate(BaseModel):
    hostname: str = Field(min_length=1, max_length=255)
    platform: str = Field(min_length=1, max_length=50)
    status: DeviceStatus = DeviceStatus.UNKNOWN


class DeviceResponse(DeviceCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class IncidentCreate(BaseModel):
    device_id: UUID
    title: str = Field(min_length=3, max_length=255)
    severity: Severity


class IncidentResponse(IncidentCreate):
    id: UUID
    status: IncidentStatus
    model_config = ConfigDict(from_attributes=True)


class AutomationResponse(BaseModel):
    job_id: UUID
    status: str
    idempotent_replay: bool = False
