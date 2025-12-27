from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

metadata = MetaData()

# Users table (already exists in your project)
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False)
)

# Posts table — updated for LEGO flips
posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("username", String, nullable=False),  # denormalized for easy display
    Column("set_number", String, nullable=False),  # e.g., "10305"
    Column("buy_price", Float, nullable=False),
    Column("sell_price", Float, nullable=True)   # NULL if not sold yet
)