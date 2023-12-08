from datetime import datetime
from enum import Enum
from typing import Annotated
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


@router.get("/", status_code=status.HTTP_200_OK)
async def listado(db: db_dependency):
    return db.query(Todos).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency,
                    todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='ToDo no encontrado.')


'''
#alta y modif sin validar la fecha
@router.post("/alta_todo",status_code=status.HTTP_201_CREATED)
async def alta(db: db_dependency,  todo_request: TodoRequest):
    todo_model = models.Todos(**todo_request.model_dump())

    db.add(todo_model)
    db.commit()
    

@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def modificacion(db: db_dependency,
                       todo_request: TodoRequest,
                       todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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
@router.post("/alta", status_code=status.HTTP_201_CREATED)
async def alta(db: db_dependency, todo_request: TodoRequest):
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

    return todo_model


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def modificacion(db: db_dependency,
                       todo_request: TodoRequest,
                       todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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


@router.put("/completada/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def modificacion_completada(db: db_dependency,
                                  completada: bool,
                                  todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='ToDo no encontrado.')
    todo_model.completada = completada
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def baja(db: db_dependency,
               todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='ToDo no encontrado.')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
