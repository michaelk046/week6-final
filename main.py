from dotenv import load_dotenv
load_dotenv()

import crud
import models
import schemas
import auth
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from config import settings

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler # pyright: ignore[reportMissingImports]
from slowapi.util import get_remote_address # pyright: ignore[reportMissingImports]
from slowapi.errors import RateLimitExceeded # pyright: ignore[reportMissingImports]

app = FastAPI(title="Week 5 – Production Ready")

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your domain in real prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- AUTH -------------------
@app.post("/register", response_model=schemas.UserOut)
@limiter.limit("5/minute")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(400, "Username already taken")
    return crud.create_user(db, user)

@app.post("/login")
@limiter.limit("10/minute")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form.username)
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# ------------------- POSTS -------------------
@app.post("/posts", response_model=schemas.PostOut)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_post(db, post, current_user.id)

@app.get("/posts", response_model=list[schemas.PostOut])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip, limit)

@app.get("/my-posts", response_model=list[schemas.PostOut])
def my_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_posts(db, current_user.id)

@app.get("/")
def home():
    return {"message": "Week 5 Complete → /docs"}

# Test rate limiting
@app.get("/rate-test")
@limiter.limit("3/minute")
async def rate_test():
    return {"message": "Rate limited to 3/minute"}

# ----------------- Mock -----------------------
@app.get("/price/{asin}")
async def mock_price(asin: str):
    # Mock data — replace with real PAAPI later
    mock_prices = {
        "B0BBYRH7P8": 419.99,  # Razor Crest example
        "B09B8Z5Q5V": 239.99,  # X-Wing example
    }
    return {"asin": asin, "price": mock_prices.get(asin, 0.0), "source": "mock (real PAAPI coming soon)"}