# TodoListAPI
RESTful API built with Python and Flask to allow users to manage their to-do list. 
Inspired by the [Todo List API Project Idea](https://roadmap.sh/projects/todo-list-api) from roadmap.sh. For learning purpose. 

![To-do List API Project Idea by roadmap.sh](https://assets.roadmap.sh/guest/todo-list-api-bsrdd.png)
(Image from from the project idea page at roadmap.sh)

---

## Features

- Create user with `POST /register` endpoint
- Login with `POST /login` endpoint
- Create to-do item with `POST /todos` endpoint
- Update to-do item with `PUT /todos/<int:id>` endpoint
- Delete to-do item with `DELETE /todos/<int:id>` endpoint
- Get to-do items in paginated response with `GET /todos/?page=1&limit=10`
- Refresh token mechanism for authentication
- Rate limiting
- Automated tests with pytest

--- 

## Tools used and requirements
- Python 3+
- Flask as a web application framework
- SQLAlchemy as Object Relational Mapper
- PyJWT for encoding and decoding JSON Web Tokens
- pytest as test framework
- Flask-Limiter for rate limiting
- Flasgger for API documentation with Swagger

---

## How to run

### 1. Clone this repository

```shell
git clone https://github.com/guilhermelirar/TodoListAPI.git
cd TodoListAPI
```

### 2. Create and activate a python virtual environment
Create it
```shell
python -m venv .venv
```
Activate it:
- On Windows:  
  ```shell
  .venv\Scripts\activate
  ```

- On Linux or Mac:
  ```shell
   source .venv/bin/activate
   ```

### 3. Install dependencies

Install all dependencies listed in `requirements.txt`.
```shell
pip install -r requirements.txt
```

### 4. Run application

The application can be run using the `flask run` command or through the `run.py` file as follows:
```shell
python run.py
```
The `/hello` route will only work if `run.py` is used.

---

## Documentation
This project is documented with Swagger through Flasgger, as listed in the
requirements. The generated documentation can be accessed via browser through
`/api docs`.

---

## Tests
This project uses `pytest` as test framework. 

To run tests, simply use the following command in the terminal:
```shell
pytest
```
Tests are located in the `/tests` directory.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
