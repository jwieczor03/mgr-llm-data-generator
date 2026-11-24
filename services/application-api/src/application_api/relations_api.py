"""Project-scoped relation review endpoints."""
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    model_validator,
)

from application_api.ddl_api import access
from application_api.projects import ProjectRoute
from application_api.relations import (
    decide,
    discover,
    discovery,
    lock_project,
    readiness,
    relations,
)


class DiscoveryRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: UUID4


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: StrictInt = Field(ge=1)
    decision: Literal['APPROVE', 'REJECT']
    reference_required: StrictBool | None = None

    @model_validator(mode='after')
    def valid_choice(self):
        if (self.decision == 'APPROVE' and self.reference_required is None
                or self.decision == 'REJECT' and 'reference_required' in self.model_fields_set):
            raise ValueError('invalid choice')
        return self


router = APIRouter(prefix='/api/v1/projects/{project_id}/schema-versions/{version_id}', route_class=ProjectRoute)


@router.post('/relation-discoveries', status_code=202)
def create_discovery(project_id: UUID, version_id: UUID4, data: DiscoveryRequest, request: Request):
    _, repo = access(request, project_id)
    return {'discovery_id': discover(repo.database, project_id, version_id, data.request_id)}


@router.get('/relation-discoveries/{discovery_id}')
def get_discovery(project_id: UUID, version_id: UUID4, discovery_id: UUID4, request: Request):
    _, repo = access(request, project_id)
    return discovery(repo.database, project_id, version_id, discovery_id)


@router.get('/relations')
def get_relations(project_id: UUID, version_id: UUID4, request: Request):
    _, repo = access(request, project_id)
    with repo.database.session() as session:
        lock_project(session, project_id)
        return {'items': relations(session, project_id, version_id)}


@router.post('/relation-proposals/{proposal_id}/decision')
def decision(project_id: UUID, version_id: UUID4, proposal_id: UUID4, data: DecisionRequest, request: Request):
    actor, repo = access(request, project_id)
    return decide(repo.database, project_id, version_id, proposal_id, actor.subject,
                  data.expected_revision, data.decision, data.reference_required)


@router.get('/readiness')
def get_readiness(project_id: UUID, version_id: UUID4, request: Request):
    _, repo = access(request, project_id)
    with repo.database.session() as session:
        lock_project(session, project_id)
        return readiness(session, project_id, version_id)
