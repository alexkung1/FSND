import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        # self.app = create_app({"SQLALCHEMY_DATABASE_URI": self.database_path})
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'postgres:password@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy(self.app)

        self.seed_db()

    def seed_db(self):
        if not Question.query.all() or not Category.query.all():
            q = Question(question="What is 4+2", category="Math",
                         answer="6", difficulty=1)
            c = Category(type="Math")
            self.db.session.add(q)
            self.db.session.add(c)
            self.db.session.commit()

        self.test_category = Category.query.first()
        self.test_question = Question.query.first()
        self.test_category_id = self.test_category.id
        self.test_question_id = self.test_question.id
        self.total_questions = len(Question.query.all())
        self.total_categories = len(Category.query.all())

    def tearDown(self):
        """Executed after reach test"""
        self.db.session.query(Question).delete()
        self.db.session.query(Category).delete()
        self.db.session.commit()
        self.db.session.remove()
        self.db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = res.json
        self.assertEqual(len(data.get('questions')), 1)
        self.assertEqual(data.get('category'), None)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)

    def test_post_question(self):
        res = self.client().post('/questions',
                                 json={'category': self.test_category_id, "question": "What is 10+4", "answer": "14", "difficulty": 5})
        data = res.json
        self.assertEqual(data.get('total_questions'), 2)
        self.assertTrue(data.get('created'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)

    def test_search_questions(self):
        res = self.client().post(
            '/questions', json={"searchTerm": "What is 4+2"})
        data = res.json
        self.assertEqual(len(data.get("questions")), 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)

    def test_questions_by_category(self):
        res = self.client().get(
            '/categories/{}/questions'.format(self.test_category_id))
        data = res.json
        self.assertEqual(len(data.get("questions")), 1)
        self.assertEqual(data.get("category"), "Math")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)

    def test_delete_question(self):
        res = self.client().delete(
            '/questions/{}'.format(self.test_question_id))
        data = res.json

        self.assertEqual(data.get("questions"), 0)
        self.assertEqual(data.get("deleted"), self.test_question_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)

    def test_quizzes(self):
        res = self.client().post(
            '/quizzes', json={"previous_questions": [], "quiz_category": self.test_category.format()})
        data = res.json
        self.assertTrue(data.get("question"))
        self.assertEqual(data.get("success"), True)
        self.assertEqual(res.status_code, 200)

    # Test Error Handling

    def test_method_not_allowed(self):
        res = self.client().get(
            '/questions/30')
        data = res.json
        self.assertEqual(data.get("success"), False)
        self.assertEqual(data.get("error"), "Method not allowed")
        self.assertEqual(res.status_code, 405)

    def test_not_found(self):
        res = self.client().delete(
            '/questions/30')
        data = res.json
        self.assertEqual(data.get("success"), False)
        self.assertEqual(data.get("error"), "Resource not found")
        self.assertEqual(res.status_code, 404)

    def test_bad_request(self):
        res = self.client().post(
            '/questions', json={"badjson": "fakedata"})
        data = res.json
        self.assertEqual(data.get("success"), False)
        self.assertEqual(data.get("error"), "Bad request")
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
