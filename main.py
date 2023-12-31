from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI
import models
from database import engine
from routers import todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(todos.router)