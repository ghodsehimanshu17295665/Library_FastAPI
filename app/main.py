from fastapi import FastAPI

from app.routers import author, category, user

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI + PostgreSQL"}


# include router
app.include_router(user.router)
app.include_router(author.router)
app.include_router(category.router)
