from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from database import database
import tables
from schemas import UserCreate, UserOut, PostCreate, PostInDB
from auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash
)
app = FastAPI(title="LEGO Flip Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lego-flip-frontend-clean.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

    async with database.transaction():
        await database.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            )
        """)
        await database.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) NOT NULL,
                username TEXT NOT NULL,
                set_number TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL
            )
        """)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    try:
        query = tables.users.select().where(tables.users.c.username == user.username)
        existing = await database.fetch_one(query)
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = get_password_hash(user.password)
        query = tables.users.insert().values(
            username=user.username,
            hashed_password=hashed_password
        )
        record_id = await database.execute(query)
        return UserOut(id=record_id, username=user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/posts", response_model=PostInDB)
async def create_post(post: PostCreate, current_user: UserOut = Depends(get_current_user)):
    query = tables.posts.insert().values(
        user_id=current_user.id,
        username=current_user.username,
        set_number=post.set_number,
        buy_price=post.buy_price,
        sell_price=post.sell_price
    )
    record_id = await database.execute(query)

    return PostInDB(
        id=record_id,
        user_id=current_user.id,
        username=current_user.username,
        set_number=post.set_number,
        buy_price=post.buy_price,
        sell_price=post.sell_price
    )

@app.get("/posts", response_model=List[PostInDB])
async def get_all_posts():
    query = tables.posts.select().order_by(tables.posts.c.id.desc())
    results = await database.fetch_all(query)
    return [PostInDB.from_orm(r) for r in results]  # or PostInDB(**dict(r))

@app.get("/my-posts", response_model=List[PostInDB])
async def get_my_posts(current_user: UserOut = Depends(get_current_user)):
    query = (
        tables.posts.select()
        .where(tables.posts.c.user_id == current_user.id)
        .order_by(tables.posts.c.id.desc())
    )
    results = await database.fetch_all(query)
    return [PostInDB.from_orm(r) for r in results]

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: UserOut = Depends(get_current_user)):
    query = tables.posts.select().where(tables.posts.c.id == post_id)
    post = await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    delete_query = tables.posts.delete().where(tables.posts.c.id == post_id)
    await database.execute(delete_query)

    return {"detail": "Flip deleted successfully"}

@app.get("/")
async def root():
    return {"message": "LEGO Flip Tracker API is running! 🧱🚀"}