import json
from os import getenv

from bson.objectid import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from fastapi import FastAPI, Response, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI()
load_dotenv()


# Pydantic Models
class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int


class Transaction(BaseModel):
    book_id: str
    name: str
    amount: int


# Initialize MongoDB client
mongo_client = AsyncIOMotorClient(getenv("DB_HOST"))
db = mongo_client[getenv("DB_NAME")]


# GET /books: Retrieves a list of all books in the store
@app.get("/books", tags=["Find Books"])
async def books():
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
async def get_book(book_id: str, response: Response):
    try:
        book_id = ObjectId(book_id)
    except InvalidId:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Invalid Book ID"}

    book = await db.books.find_one({"_id": book_id})

    if book is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Book not found"}

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
async def update_book(book_id: str, book: Book, response: Response):
    try:
        book_id = ObjectId(book_id)
    except InvalidId:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Invalid Book ID"}

    result = await db.books.update_one({"_id": ObjectId(book_id)}, {"$set": book.dict()})
    return {"id": book_id}


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}", tags=["Modify Books"])
async def delete_book(book_id: str, response: Response):
    try:
        book_id = ObjectId(book_id)
    except InvalidId:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Invalid Book ID"}

    result = await db.books.delete_one({"_id": ObjectId(book_id)})
    return {"id": book_id}


# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range
@app.get("/search", tags=["Find Books"])
async def search_book(title: str = None, author: str = None, min_price: float = None, max_price: float = None):
    # build the query
    parameters = {}
    if title:
        parameters["title"] = title
    if author:
        parameters["author"] = author
    if min_price or max_price:
        parameters["price"] = {}
    if min_price:
        parameters["price"]["$gte"] = min_price
    if max_price:
        parameters["price"]["$lte"] = max_price

    # get the result
    result = []
    async for book in db.books.find(parameters):
        result.append(
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
        )

    return result


# GET /top-5-authors: Gets a list of top 5 authors
@app.get("/top-5-authors", tags=["Aggregation"])
async def top_5_authors():
    # query for authors
    query = [
        {"$group": {"_id": {"author": "$author"}, "count": {"$count": {}}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "author": "$_id.author", "count": 1}},
        {"$limit": 5},
    ]

    result = []
    # build result value
    async for author in db.books.aggregate(query):
        result.append({"author": author["author"], "count": author["count"]})

    return result


# GET /total-stock: Gets the total stock of books in the store
@app.get("/total-stock", tags=["Aggregation"])
async def total_stock():
    # get stock
    stock = await db.books.aggregate(
        [{"$group": {"_id": "", "stock": {"$sum": "$stock"}}}, {"$project": {"_id": 0, "stock": 1}}]
    ).to_list(None)

    return {"stock": stock[0]["stock"]}


# GET /bestselling: Lists the top 5 books with the most transactions
@app.get("/bestselling", tags=["Aggregation"])
async def bestselling():
    # query for bestsellers
    query = [
        {"$group": {"_id": {"book_id": "$book_id"}, "count": {"$sum": "$amount"}}},
        {"$sort": {"count": -1}},
        {"$project": {"book_id": {"$toObjectId": "$_id.book_id"}, "count": 1}},
        {"$lookup": {"from": "books", "localField": "book_id", "foreignField": "_id", "as": "book"}},
        {"$unwind": {"path": "$book"}},
        {
            "$project": {
                "_id": "$book._id",
                "title": "$book.title",
                "author": "$book.author",
                "description": "$book.description",
                "price": "$book.description",
                "stock": "$book.stock",
                "ammount_sold": "$count",
            }
        },
        {"$limit": 5},
    ]

    result = []
    # build result value
    async for bestseller in db.transactions.aggregate(query):
        result.append(
            {
                "_id": str(bestseller["_id"]),
                "title": bestseller["title"],
                "author": bestseller["author"],
                "description": bestseller["description"],
                "price": bestseller["price"],
                "stock": bestseller["stock"],
                "ammount_sold": bestseller["ammount_sold"],
            }
        )

    return result


# PUT /purchase: Purchases an existing book by ID
@app.put("/purchase", tags=["Purchase"])
async def purchase_book(transaction: Transaction, response: Response):
    # Creates a new transaction using json data from the body of the request.

    trans_dict = transaction.dict()
    # check if book in stock
    stock = await db.books.find_one({"_id": ObjectId(trans_dict["book_id"])})

    if stock["stock"] > trans_dict["amount"]:
        await db.books.update_one(
            {"_id": ObjectId(trans_dict["book_id"])}, {"$set": {"stock": stock["stock"] - trans_dict["amount"]}}
        )
        await db.transactions.insert_one(trans_dict)
        return {"id": trans_dict["book_id"]}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "There are not enough books in stock to buy that ammount", "stock": stock["stock"]}


# POST /add-books: Adds a bunch of books from books.json into the store
@app.post("/add-books", tags=["Dev Helpers"])
async def add_books():
    # load books.json
    with open("books.json", "r") as f:
        books = json.load(f)

    for book in books:
        book["_id"] = ObjectId(book["_id"])

    # insert books into db using insert_many
    result = await db.books.insert_many(books)

    # return the number of books added
    return {"books_added": len(result.inserted_ids)}


# POST /add-transactions: Adds a bunch of transactions from transactions.json into the store
@app.post("/add-transactions", tags=["Dev Helpers"])
async def add_transactions():
    # load transactions.json
    with open("transactions.json", "r") as f:
        transactions = json.load(f)

    # insert books into db using insert_many
    result = await db.transactions.insert_many(transactions)

    # return the number of books added
    return {"transactions_added": len(result.inserted_ids)}


# POST /add-indexes: Adds indexes to the database for more efficient queries
@app.post("/add-indexes", tags=["Dev Helpers"])
async def add_indexes():
    # add indexes to books
    await db.books.create_index("title")
    await db.books.create_index("author")
    await db.books.create_index("price")
    await db.books.create_index("stock")

    # add indexes to transactions
    await db.transactions.create_index("book_id")
    await db.transactions.create_index("amount")

    return {"message": "Indexes added"}
