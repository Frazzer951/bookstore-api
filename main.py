from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()
load_dotenv()


# Pydantic Models
class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int


# Initialize MongoDB client
mongo_client = AsyncIOMotorClient(getenv("DB_HOST"))
db = mongo_client[getenv("DB_NAME")]


@app.get("/")
async def root():
    return {"message": "Hello World"}


# GET /books: Retrieves a list of all books in the store
@app.get("/books")
async def books():
    # TODO
    pass


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    # TODO
    book = db.books.find({"_id": book_id})

    return book


# POST /books: Adds a new book to the store
@app.post("/books")
async def add_book(book: Book):
    # TODO
    db.books.insert_one(book.dict())
    pass


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book(book_id: int, book: Book):
    # TODO

    pass


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    # TODO
    pass


# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range
@app.get("/search?title={}&author={}&min_price={}&max_price={}")
async def search_book(title: str, author: str, min_price: float, max_price: float):
    # TODO
    pass
