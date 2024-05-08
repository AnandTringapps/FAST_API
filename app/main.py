from fastapi import FastAPI, HTTPException, status, Depends, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from .db.config import CLIENT_ID, CLIENT_SECRET
from fastapi.staticfiles import StaticFiles
from routes.user import user

app = FastAPI()
app.include_router(user)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
app.mount("/static", StaticFiles(directory="static"), name="static")

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth'
    }
)
templates = Jinja2Templates(directory="templates")
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({"loc": err["loc"], "msg": err["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": errors},
    )
@app.exception_handler(OAuthError)
async def handle_oauth_error(request: Request, exc: OAuthError):
    if exc.error == 'access_denied':
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': 'User denied access'}
        )
    else:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': 'Authentication Error'}
        )
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')

    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )
@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )
@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        if e.error == 'access_denied':
            return templates.TemplateResponse(
                name='error.html',
                context={'request': request, 'error': 'User denied access'}
            )
        else:
            return templates.TemplateResponse(
                name='error.html',
                context={'request': request, 'error': 'Authentication Error'}
            )
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse('welcome')


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
