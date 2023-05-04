from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson.objectid import ObjectId
import json

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


# GET /books: Retrieves a list of all books in the store
@app.get("/books", tags=["Find Books"])
async def books():  # TODO
    result = await db.books.find().to_list(None)
    books = [
        {
            "id": str(book["_id"]),
            "book": Book(
                title=book["title"],
                author=book["author"],
                description=book["description"],
                price=book["price"],
                stock=book["stock"],
            ),
        }
        for book in result
    ]
    return books


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}", tags=["Find Books"])
async def get_book(book_id: str):
    book = await db.books.find_one({"_id": ObjectId(book_id)})
    book = {
        "id": str(book["_id"]),
        "book": Book(
            title=book["title"],
            author=book["author"],
            description=book["description"],
            price=book["price"],
            stock=book["stock"],
        ),
    }
    return book


# POST /books: Adds a new book to the store
@app.post("/books", tags=["Modify Books"])
async def add_book(book: Book):
    result = await db.books.insert_one(book.dict())
    id = result.inserted_id
    return {"id": str(id)}


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}", tags=["Modify Books"])
async def update_book(book_id: int, book: Book):  # TODO
    pass


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}", tags=["Modify Books"])
async def delete_book(book_id: int):  # TODO
    pass


# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range
@app.get("/search", tags=["Find Books"])
async def search_book(title: str = None, author: str = None, min_price: float = None, max_price: float = None):  # TODO
    pass


# POST /add-books: Adds a bunch of books from books.json into the store
@app.post("/add-books", tags=["Dev Helpers"])
async def add_books():
    # load books.json
    with open("books.json", "r") as f:
        books = json.load(f)

    # insert books into db using insert_many
    result = await db.books.insert_many(books)

    # return the number of books added
    return {"books_added": len(result.inserted_ids)}
