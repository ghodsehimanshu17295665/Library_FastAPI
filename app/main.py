from fastapi import FastAPI

from app.routers import author, book, category, course, issued_book, user

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI + PostgreSQL"}


# include router
app.include_router(user.router)
app.include_router(author.router)
app.include_router(category.router)
app.include_router(course.router)
app.include_router(book.router)
app.include_router(issued_book.router)
