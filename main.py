from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import (
    RequestValidationError,  # handling validation errors like hello in params instead of an integer
)
from fastapi.responses import (
    JSONResponse,  # manually return json responses from our exception handler
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,  # fastapi is built on top of starlette, and when user goes to a route that doesn't exist, it is starlette that raises the 404 error, so we need to import the HTTPException from starlette to handle that error
)

from schemas import PostCreate, PostResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]



# By default they return json, if we want to return hmtl, we can use the HTMLResponse class from the fastapi.responses module.
# This route returns html, something we want for the users in the browser, the docs and redoc only want to show APIs that returns json
# So to ignore them in the docs, we can set the include_in_schema parameter to False in the route decorator.
@app.get("/", include_in_schema=False, name='home')
@app.get("/posts", include_in_schema=False, name='posts')
def home(request: Request):
    return templates.TemplateResponse(request, 'home.html', {'posts': posts, 'title': 'home'})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post['title']
            return templates.TemplateResponse(
                request,
                'post.html',
                {'post': post, 'title': title}
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id = max(post['id'] for post in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 22, 2025",
    }
    posts.append(new_post)
    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail if exception.detail
        else "An error occurred, Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            'status_code': exception.status_code,
            'title': exception.status_code,
            'message': message
        },
        status_code=exception.status_code,
    )

"""
validation errors don't have a simple detail string, they have a list of detailed error information
"""
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            'status_code': status.HTTP_422_UNPROCESSABLE_ENTITY,
            'title': "Validation Error",
            'message': "There was an error with your request, Please check the data you sent and try again."
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
