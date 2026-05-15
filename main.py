from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import (
    http_exception_handler,  # this is the default exception handler for HTTPException, we can
    request_validation_exception_handler,  # this is the default exception handler for RequestValidationError, we can use it to handle validation errors in our custom way
)
from fastapi.exceptions import (
    RequestValidationError,  # handling validation errors like hello in params instead of an integer
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,  # fastapi is built on top of starlette, and when user goes to a route that doesn't exist, it is starlette that raises the 404 error, so we need to import the HTTPException from starlette to handle that error
)

import models
from database import Base, engine, get_db
from routers import posts, users


# a modern way to handle startup and shutdown events in FastAPI is to use the lifespan function, which is an async generator that yields
# control back to FastAPI after doing the startup tasks, and then continues to do the shutdown tasks when the application is shutting down.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


# biggest difference between async and sync in sqlalchemy:
# in sync lazy loading is the default, which means that related objects are not loaded until you access them, and this can lead to
# the N+1 problem if you are not careful, but in async eager loading is the default, which means that related objects are loaded immediately,
# and this can lead to more efficient queries and better performance in many cases.

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])


# By default they return json, if we want to return hmtl, we can use the HTMLResponse class from the fastapi.responses module.
# This route returns html, something we want for the users in the browser, the docs and redoc only want to show APIs that returns json
# So to ignore them in the docs, we can set the include_in_schema parameter to False in the route decorator.
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "home"}
    )


@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(
    request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request, "post.html", {"post": post, "title": title}
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"title": "register"})


@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(request, "account.html", {"title": "Account"})


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred, Please check your request and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


"""
validation errors don't have a simple detail string, they have a list of detailed error information
"""


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exception: RequestValidationError
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "There was an error with your request, Please check the data you sent and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


"""200 OK - Successful GET, PUT, or PATCH
201 Created - Successful POST for users and posts
204 No Content - Successful DELETE
400 Bad Request - Duplicate username/email when creating user
404 Not Found - Resource doesn't exist (user or post)
422 Unprocessable Entity - Validation error (automatic from Pydantic)*"""
