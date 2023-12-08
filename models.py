from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descripcion = Column(String)
    fecha_finalizacion = Column(DateTime)  # Corregir aquí
    prioridad = Column(String)
    completada = Column(Boolean, default=False)
