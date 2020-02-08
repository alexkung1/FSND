# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

## Database Setup

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

## Endpoints

#### GET /categories

Returns a dictionary of categories which map a category id to the corresponding string of the category

**Example Response**

```
{
    "categories":
        {
            12: "Math",
            4: "Biology",
            8: "English",
            3: "Physics"
        },
    "status": 200,
    "success": true
}
```

#### GET /questions

Returns a paginated list of questions with a limit of 10 questions per page.
Include a page number as a request argument e.g., `/questions?page=2`

**Example Response**

```
{
    "categories": {
        "1": "Science",
        "2": "Math"
    },
    "category": null,
    "questions": [
        {
            "answer": "6",
            "category": "Math",
            "difficulty": 1,
            "id": 1,
            "question": "What is 4+2?"
        },
        {
            "answer": "Mitochondria",
            "category": "Science",
            "difficulty": 1,
            "id": 2,
            "question": "What is the powerhouse of the cell?"
        }
    ],
    "status": 200,
    "success": true,
    "total_questions": 2
}
```

#### POST /questions

_Creating a new question_

To create a new question, provide a request in the following format:

**Example Request**

```
{
	"question": "What is 12x4?",
	"answer": "48",
	"difficulty": 3,
	"category": 1
}
```

**Example Response**

```
{
    "created": 9,
    "questions": 9,
    "status": 200,
    "success": true,
    "total_questions": 9
}
```

_Searching questions_

To filter questions based on a search term, provide a search term in the request as follows:

```
{
	"searchTerm": "powerhouse"
}
```

**Example Response**

```
{
    "categories": {
        "1": "Science",
        "2": "Math"
    },
    "category": null,
    "questions": [
        {
            "answer": "Mitochondria",
            "category": "Science",
            "difficulty": 1,
            "id": 2,
            "question": "What is the powerhouse of the cell?"
        }
    ],
    "status": 200,
    "success": true
}
```

#### GET /categories/<category_id>/questions

Retrieve a questions based on category id

**Example Request**

```
curl 127.0.0.1:5000/categories/1/questions
```

**Example Response**

```
{
    "categories": {
        "1": "Science",
        "2": "Math"
    },
    "category": "Science",
    "questions": [
        {
            "answer": "Mitochondria",
            "category": "Science",
            "difficulty": 1,
            "id": 2,
            "question": "What is the powerhouse of the cell?"
        },
    ],
    "status": 200,
    "success": true
}
```

#### DELETE /questions/<question_id>

Delete a question based on the provided question id

**Example Request**

```
curl -X DELETE 127.0.0.1:5000/questions/7
```

**Example Response**

```
{
    "deleted": 7,
    "questions": 10,
    "status": 200,
    "success": true,
    "total_questions": 10
}
```

#### POST /quizzes

Retrieve a random question from the specified category. Previous questions are specified by id as follows

**Example Request**

```
{
	"previous_questions": [4, 3],
	"quiz_category": {
		"id": 2,
		"type": "Math"
	}

}
```

**Example Response**

```
{
    "question": {
        "answer": "14",
        "category": "Math",
        "difficulty": 1,
        "id": 3,
        "question": "What is 12+2?"
    },
    "status": 200,
    "success": true
}
```

## Errors

Errors are returned as JSON in the following format:

```
{
    "error": 404,
    "message": "Resource not found",
    "success": False
}
```

The API will return any of the following errors following a failed request:

- 400: Bad request
- 404: Resource not found
- 405: Method not allowed
- 422: Unprocessable entity
- 500: Internal server error

## Testing

To run the tests, run

```
dropdb trivia_test
createdb trivia_test
python3 test_flaskr.py
```
