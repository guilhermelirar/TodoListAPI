# TodoListAPI
RESTful API built with Python and Flask to allow users to manage their to-do list. 
Inspired by the [Todo List API Project Idea](https://roadmap.sh/projects/todo-list-api) from roadmap.sh. For learning purpose. 

*This project is a work in progress. Currently only part of the authentication and account services are implemented.*

![To-do List API Project Idea by roadmap.sh](https://assets.roadmap.sh/guest/todo-list-api-bsrdd.png)
(Image from from the project idea page at roadmap.sh)

---

## Features

- User creation with `POST /register` route
- User login with `POST /login` route
- Refresh token mechanism for authentication
- Automated tests with pytest

Other features listed on roadmap.sh project idea are still being implemented

--- 

## Tools used and requirements
- Python 3+
- Flask as a web application framework
- SQLAlchemy as Object Relational Mapper
- PyJWT for encoding and decoding JSON Web Tokens
- pytest as test framework

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


