# Bookstore API

CPSC 449 Final Project

## Group Members

Luke Eltiste

William Lim

## HOW TO USE

### Step 0 - VENV

- Create a Virtual Environment to house the dependencies for the project
  - See [here](https://docs.python.org/3/library/venv.html) for a tutorial on how to setup an environment

### Step 1 - DEPENDENCIES

- Install the dependencies from `requierments.txt` using the following
  ```sh
  pip install -r .\requirements.txt
  ```

### Step 2 - SETUP ENVIRONMENT

- Copy `.env.example` to `.env`
- Fill in the details for your own MongoDB server

### Step 3 - START WITH UVICORN

- Run the following command to start the API
  ```sh
  uvicorn main:app
  ```
- Add `--reload` if you are making changes to the source files

### Step 4 - RUN DEV ENDPOINTS

- Run the Dev Helper endpoints either from the `/docs` enpoint or by calling the endpoints to setup the database
  - `/add-books`
    - Adds in fake book data to the database for the enpoints to use
  - `/add-transactions`
    - Adds in fake transaction data on the books
  - `/add-indexes`
    - Adds in the indexes to optomize the querying enpoints

### Step 5 - USE THE API

- Everything is ready to go and you can start using the API
