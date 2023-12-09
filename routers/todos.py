from datetime import datetime
from enum import Enum
from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Todos

router = APIRouter(
    prefix='/todo',
    tags=['ToDos'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class PrioridadEnum(str, Enum):
    Alta = "Alta"
    Media = "Media"
    Baja = "Baja"


class TodoRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1, max_length=4000)
    fecha_finalizacion: datetime
    prioridad: PrioridadEnum
    completada: bool


class TodosResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    fecha_finalizacion: datetime
    prioridad: str
    completada: bool


@router.get("/", response_model=List[TodosResponse], status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency) -> List[TodosResponse]:
    return db.query(Todos).all()


@router.get("/{id}", response_model=TodosResponse, status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency, id: int = Path(gt=0)) -> TodosResponse:
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is not None:
        return TodosResponse(**todo_model.__dict__)
    raise HTTPException(status_code=404, detail='ToDo no encontrado.')


'''
#alta y modif sin validar la fecha
@router.post("/alta_todo",status_code=status.HTTP_201_CREATED)
async def alta(db: db_dependency,  todo_request: TodoRequest):
    todo_model = models.Todos(**todo_request.model_dump())

    db.add(todo_model)
    db.commit()
    

@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def modificacion(db: db_dependency,
                       todo_request: TodoRequest,
                       id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='ToDo no encontrado.')

    todo_model.titulo = todo_request.titulo
    todo_model.descripcion = todo_request.descripcion
    todo_model.fecha_finalizacion = todo_request.fecha_finalizacion
    todo_model.prioridad = todo_request.prioridad
    todo_model.completada = todo_request.completada

    db.commit()

'''


# alta y modif validando la fecha
@router.post("/create", response_model=TodosResponse, status_code=status.HTTP_201_CREATED)
async def create(db: db_dependency, todo_request: TodoRequest) -> TodosResponse:
    fecha_finalizacion = datetime(
        todo_request.fecha_finalizacion.year,
        todo_request.fecha_finalizacion.month,
        todo_request.fecha_finalizacion.day,
    )

    if fecha_finalizacion < datetime.now():
        raise HTTPException(status_code=400, detail='La fecha de finalización no puede ser anterior a la fecha actual.')

    todo_model = Todos(
        titulo=todo_request.titulo,
        descripcion=todo_request.descripcion,
        fecha_finalizacion=fecha_finalizacion,
        prioridad=todo_request.prioridad,
        completada=todo_request.completada,
    )

    db.add(todo_model)
    db.commit()

    todo_response_dict = {
        'id': todo_model.id,
        'titulo': todo_model.titulo,
        'descripcion': todo_model.descripcion,
        'fecha_finalizacion': todo_model.fecha_finalizacion,
        'prioridad': todo_model.prioridad,
        'completada': todo_model.completada,
    }

    return TodosResponse(**todo_response_dict)


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update(db: db_dependency, todo_request: TodoRequest, id: int = Path(gt=0)) -> None:
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='ToDo no encontrado.')

    fecha_finalizacion = datetime(
        todo_request.fecha_finalizacion.year,
        todo_request.fecha_finalizacion.month,
        todo_request.fecha_finalizacion.day,
    )

    if fecha_finalizacion < datetime.now():
        raise HTTPException(status_code=400, detail='La fecha de finalización no puede ser anterior a la fecha actual.')

    todo_model.titulo = todo_request.titulo
    todo_model.descripcion = todo_request.descripcion
    todo_model.fecha_finalizacion = fecha_finalizacion
    todo_model.prioridad = todo_request.prioridad
    todo_model.completada = todo_request.completada

    db.commit()


@router.put("/update_complete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_complete(db: db_dependency,
                          completada: bool,
                          id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='ToDo no encontrado.')
    todo_model.completada = completada
    db.commit()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(db: db_dependency,
                 id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='ToDo no encontrado.')
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
