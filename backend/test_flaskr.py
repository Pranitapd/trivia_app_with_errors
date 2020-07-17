import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):  #runs before each test, so if you need anu data before every test you can post it here
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Pranita123','localhost:5432',self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.new_question = {
            'question':'Who is current Prime Minister',
            'answer':'Narendra Modi',
            'category':'4',
            'difficulty': 1
        }
    
    def tearDown(self): # runs after each test
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    # def test_404_if_question_not_found(self): not working
    #     res = self.client().get('/questions/400')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code,404)
    #     self.assertEqual(data['success'],False)
    #     self.assertEqual(data['message'],'not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    # def test_delete_question(self):   working keep it
    #     res = self.client().delete('/questions/9')
    #     data = json.loads(res.data)

    #     # questions = Question.query.filter(Question.id == 5).all()

    #     self.assertEqual(res.status_code,200)
    #     self.assertEqual(data['success'],True)
    #     self.assertTrue(data['total_questions'])
    #     self.assertTrue(len(data['questions']))
    #     self.assertTrue(len(data['categories']))

    def test_405_if_question_does_not_exist(self):# not working
        res = self.client().delete('/questions/10000')
        print(res.status_code)
        # print("Here 84")
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'not found')

    # def test_create_new_question(self):  working
    #     res = self.client().post('/questions',json=self.new_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code,200)
    #     self.assertEqual(data['success'],True)

    
    # def test_405_if_question_creation_is_not_allowed(self):
    #     res = self.client().post('/questions/45',json=self.new_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code,405)
    #     self.assertEqual(data['success'],False)
    #     self.assertEqual(data['message'],'method not allowed')

    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()