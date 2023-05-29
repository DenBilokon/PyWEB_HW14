import redis.asyncio as redis

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings
from src.database.db import get_db
from src.routes import contacts, auth, users

app = FastAPI()


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET,POST,PUT,PATCH"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return {'message': 'hello'}


@app.get('/api/healthchecker')
def healthchecker(db: Session = Depends(get_db)):
    try:
        request = db.execute(text('SELECT 1')).fetchone()
        if request is None:
            raise HTTPException(status_code=500, detail='Database is nor configured correctly')
        return {'message': 'Welcome to FastAPI'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='Error connecting to the database')


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

