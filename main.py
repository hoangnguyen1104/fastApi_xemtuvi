from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import crud,models, schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import SessionLocal, engine
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


#Dependency
def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/users/",response_model=schemas.User)
def post_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db,user=user)


@app.get("/users/", response_model=list[schemas.User])
def get_users(skip:int=0, limit:int=0, db:Session=Depends(get_db)):
    users = crud.get_users(db,skip=skip,limit=limit)
    return users


@app.get("/users/{user_id}/",response_model=schemas.User)
def get_user(user_id:int, db:Session=Depends(get_db)):
    db_user = crud.get_user(db,user_id =user_id )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/todos/",response_model=schemas.Todo)
def post_todo_for_user(user_id:int, todo:schemas.TodoCreate, db:Session=Depends(get_db)):
    return crud.create_user_todo(db=db,user_id=user_id, todo=todo)


@app.get("/todos/", response_model=list[schemas.Todo])
def get_todos(skip:int=0,limit:int=100,db:Session=Depends(get_db)):
    todos = crud.get_todos(db,skip=skip,limit=limit)
    return todos