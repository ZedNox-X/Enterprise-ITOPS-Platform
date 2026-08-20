import json
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_operator
from app.api.schemas import (
    AutomationResponse,
    DeviceCreate,
    DeviceResponse,
    IncidentCreate,
    IncidentResponse,
)
from app.db.session import get_session
from app.domain.models import AutomationJob, Device, Incident, IncidentStatus, OutboxEvent

router = APIRouter(prefix="/api/v1", tags=["itops"])


@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_session)):
    device = Device(**payload.model_dump())
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: UUID, db: AsyncSession = Depends(get_session)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_session),
):
    if not await db.get(Device, payload.device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    incident = Incident(**payload.model_dump())
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.post(
    "/incidents/{incident_id}/diagnose",
    response_model=AutomationResponse,
)
async def diagnose_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_session),
    role: str = Depends(require_operator),
):
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = IncidentStatus.DIAGNOSING
    event = OutboxEvent(
        event_type="DiagnosticRequested",
        aggregate_id=incident.id,
        payload=json.dumps(
            {"incident_id": str(incident.id), "requested_by_role": role}
        ),
    )
    db.add(event)
    await db.commit()
    return AutomationResponse(job_id=event.id, status="queued")


@router.post(
    "/incidents/{incident_id}/remediate",
    response_model=AutomationResponse,
)
async def remediate_incident(
    incident_id: UUID,
    x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_session),
    role: str = Depends(require_operator),
):
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    existing = await db.scalar(
        select(AutomationJob).where(AutomationJob.idempotency_key == x_idempotency_key)
    )
    if existing:
        return AutomationResponse(
            job_id=existing.id,
            status=existing.status,
            idempotent_replay=True,
        )

    job = AutomationJob(
        incident_id=incident.id,
        action="restart_service",
        idempotency_key=x_idempotency_key,
    )
    incident.status = IncidentStatus.REMEDIATING
    event = OutboxEvent(
        event_type="RemediationRequested",
        aggregate_id=incident.id,
        payload=json.dumps(
            {"job_id": str(job.id), "incident_id": str(incident.id), "role": role}
        ),
    )
    db.add(job)
    db.add(event)
    await db.commit()
    return AutomationResponse(job_id=job.id, status=job.status)
