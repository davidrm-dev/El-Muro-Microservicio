from fastapi import APIRouter, Depends, Header, Query

from app.core.security import require_admin, require_authenticated
from app.repositories.tema_repository import MongoTemaRepository, TemaRepository
from app.schemas.tema import TemaCreate, TemaPostsResponse, TemaResponse, TemaUpdate
from app.services.external_clients import MateriasClient, PostsClient
from app.services.tema_service import TemaService


router = APIRouter(prefix="/api/temas", tags=["temas"])


def get_tema_repository() -> TemaRepository:
    return MongoTemaRepository()


def get_materias_client() -> MateriasClient:
    return MateriasClient()


def get_posts_client() -> PostsClient:
    return PostsClient()


def get_tema_service(
    repository: TemaRepository = Depends(get_tema_repository),
    materias_client: MateriasClient = Depends(get_materias_client),
    posts_client: PostsClient = Depends(get_posts_client),
) -> TemaService:
    return TemaService(repository, materias_client, posts_client)


@router.post("", response_model=TemaResponse, status_code=201)
def create_tema(
    payload: TemaCreate,
    authorization: str | None = Header(default=None),
    _: str = Depends(require_admin),
    service: TemaService = Depends(get_tema_service),
):
    return service.create_tema(payload, authorization)


@router.get("", response_model=list[TemaResponse])
def list_temas(
    materia_id: int | None = Query(default=None, gt=0),
    include_inactive: bool = Query(default=False),
    _: str = Depends(require_authenticated),
    service: TemaService = Depends(get_tema_service),
):
    return service.list_temas(materia_id, include_inactive)


@router.get("/{tema_id}", response_model=TemaResponse)
def get_tema(
    tema_id: str,
    _: str = Depends(require_authenticated),
    service: TemaService = Depends(get_tema_service),
):
    return service.get_tema(tema_id)


@router.put("/{tema_id}", response_model=TemaResponse)
def update_tema(
    tema_id: str,
    payload: TemaUpdate,
    authorization: str | None = Header(default=None),
    _: str = Depends(require_admin),
    service: TemaService = Depends(get_tema_service),
):
    return service.update_tema(tema_id, payload, authorization)


@router.patch("/{tema_id}/disable", response_model=TemaResponse)
def disable_tema(
    tema_id: str,
    _: str = Depends(require_admin),
    service: TemaService = Depends(get_tema_service),
):
    return service.disable_tema(tema_id)


@router.get("/{tema_id}/posts", response_model=TemaPostsResponse)
def get_posts_by_tema(
    tema_id: str,
    authorization: str | None = Header(default=None),
    _: str = Depends(require_authenticated),
    service: TemaService = Depends(get_tema_service),
):
    return service.get_posts_for_tema(tema_id, authorization)
