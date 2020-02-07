import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = QUESTIONS_PER_PAGE * (page - 1)
    end = start + QUESTIONS_PER_PAGE
    return [question.format() for question in selection[start:end]]


def get_all_categories():
    return {category.id: category.type for category in Category.query.all()}


def get_questions_by_category(category):
    return Question.query.filter_by(category=category).all()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config and test_config.get("SQLALCHEMY_DATABASE_URI"):
        setup_db(app, test_config.get("SQLALCHEMY_DATABASE_URI"))
    else:
        setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route("/categories")
    def home():
        categories = {category.id: category.type
                      for category in Category.query.all()}

        return jsonify({"categories": categories, "status": 200, "success": True})

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route("/questions", methods=["GET", "POST"])
    def questions():
        if request.method == "GET":
            selection = Question.query.all()
            questions = paginate_questions(request, selection)

            return jsonify({"questions": questions, "status": 200, "success": True, "category": None, "categories": get_all_categories(), "total_questions": len(selection)})
        else:
            data = request.json

            searchTerm = data.get("searchTerm")

            if searchTerm is not None:
                questions = paginate_questions(request, Question.query.filter(
                    Question.question.ilike("%{}%".format(searchTerm))).all())
                return jsonify({"questions": questions, "status": 200, "success": True, "category": None, "categories": get_all_categories()})
            try:
                category_id = data.get("category")

                data["category"] = Category.query.get(category_id).type
                question = Question(**data)
                question.insert()

                return jsonify({"questions": Question.query.count(), "total_questions": Question.query.count(), "status": 200, "success": True, "created": question.id})
            except Exception:
                db.session.rollback()
                return abort(400)

    @app.route("/categories/<int:category_id>/questions")
    def questions_by_category(category_id):
        category = Category.query.get(category_id)

        if not category:
            return abort(404)
        questions = paginate_questions(
            request, get_questions_by_category(category.type))
        return jsonify({"questions": questions, "status": 200, "success": True, "category": category.type, "categories": get_all_categories()})

    """
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        question = Question.query.get(question_id)

        if not question:
            return abort(404)

        question.delete()
        return jsonify({"status": 200, "success": True, "deleted": question_id, "questions": Question.query.count(), "total_questions": Question.query.count()})

    """
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    """

    """
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    """

    """
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    """

    """
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    """

    @app.route("/quizzes", methods=["POST"])
    def quizzes():
        data = request.json
        try:
            previous_questions = data["previous_questions"]
            quiz_category = data["quiz_category"]
            quiz_category_type = quiz_category["type"]
            quiz_category_id = quiz_category["id"]
        except:
            return abort(400)

        questions = Question.query.filter(~Question.id.in_(previous_questions))
        if quiz_category_id != 0:
            questions = questions.filter_by(category=quiz_category_type)

        num_questions = len(questions.all())
        random.seed()
        if num_questions:
            random_num = random.randrange(0, num_questions)
            return jsonify({"question": questions.all()[random_num].format(), "status": 200, "success": True}), 200

        return jsonify({"question": None, "status": 200, "success": True}), 200
    """
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": 400,
            "message": 'Bad request',
            "success": False
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": 404,
            "message": 'Resource not found',
            "success": False
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": 405,
            "message": 'Method not allowed',
            "success": False
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "error": 422,
            "message": 'Unprocessable entity',
            "success": False
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "error": 500,
            "message": 'Internal server error',
            "success": False
        }), 500

    return app
