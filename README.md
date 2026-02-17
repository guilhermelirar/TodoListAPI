# TodoListAPI
RESTful API built with Python and Flask to allow users to manage their to-do list. 
Inspired by the [Todo List API Project Idea](https://roadmap.sh/projects/todo-list-api) from roadmap.sh. 

![To-do List API Project Idea by roadmap.sh](https://assets.roadmap.sh/guest/todo-list-api-bsrdd.png)
(Image from from the project idea page at roadmap.sh)

---

## Features

### Authentication & Users
- Register a new user (`POST /register`)
- Login and receive access & refresh tokens (`POST /login`)
- Delete existing user (`DELETE /user`)
- Refresh token mechanism for authentication
- Rate limiting for security

### Tasks
- Create a to-do item (`POST /todos`)
- Update a to-do item (`PUT /todos/<int:id>`)
- Delete a to-do item (`DELETE /todos/<int:id>`)
- Get to-do items with pagination (`GET /todos/?page=1&limit=10`)

### Documentation & Testing
- Interactive Swagger documentation (`GET /apidocs`)
- Automated tests covering authentication, user management, and tasks functionality (`pytest`)
- pytest-cov for coverage

### Deployment
- Run locally or inside a Docker container

---

## Tools & Requirements
- Python 3+
- Flask (web framework)
- SQLAlchemy (ORM)
- PyJWT (JSON Web Tokens)
- pytest (testing framework)
- Flask-Limiter (rate limiting)
- Flasgger (Swagger API docs)
- Flask-Migrate (database migrations)
- Docker & Docker Compose

---

## Getting Started

First, Clone this repository

```bash
git clone https://github.com/guilhermelirar/TodoListAPI.git
cd TodoListAPI
```

### Without Docker

#### 1. Create and activate a python virtual environment
Create it
```shell
python -m venv venv
```
Activate it:
- Windows:  
  ```shell
  venv\Scripts\activate
  ```

- Linux/Mac:
  ```shell
   source venv/bin/activate
   ```

#### 2. Install dependencies

Install all dependencies listed in `requirements.txt`.
```shell
pip install -r requirements.txt
```

#### 3. Run application 

```shell
python run.py
```

---

### Using Docker
Make sure Docker and Docker Compose are installed.

```bash
docker compose up --build
```
This will build the containers, install dependencies, and run PostgreSQL as the database automatically.


---


## API Documentation

Interactive API documentation is available via Swagger at:

```/apidocs```

You can explore endpoints, see request/response examples, and test the API directly from your browser..

---

## Running Tests
This project uses `pytest` for testing. 

To run tests, simply use the following command in the terminal:
```shell
pytest
```

For coverage, run
```shell
pytest --cov=app
```

Tests are located in the `/tests` directory and cover authentication, user management, and task operations.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
