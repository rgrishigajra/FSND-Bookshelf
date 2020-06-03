import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_book = {
            'title': 'Anansi Boys',
            'author': 'Neil Gaiman',
            'rating': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_create_book(self):
        res = self.client().post('/books', data=json.dumps(self.new_book),
                                 headers={'Content-Type': 'application/json'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsInstance(data["created"], int)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_422_sent_when_creating_book(self):
        res = self.client().post('/books', data=json.dumps({"error": "not a proper book"}),
                                 headers={'Content-Type': 'application/json'})
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 422)
        self.assertEqual(data['message'], "request cant be processed")

    def test_delete_book(self):
        book_id = Book.query.with_entities(Book.id).all()
        res = self.client().delete('/books/'+str(book_id[0][0]))
        data = json.loads(res.data)
        book = Book.query.get(book_id[0][0])
        self.assertEqual(book,None)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], book_id[0][0])
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_update_book_rating(self):
        book_id = Book.query.with_entities(Book.id).all()
        res = self.client().patch(
            '/books/'+str(book_id[0][0]), json={"rating": 3})
        data = json.loads(res.data)
        book = Book.query.get(book_id[0][0])
        self.assertEqual(book.rating, 3)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], book_id[0][0])

    def test_fail_404_update_book_rating(self):
        res = self.client().patch('/books/'+str(1000), json={"rating": 3})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_get_books(self):
        res = self.client().get('/books')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000', json={'rating': 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

# @TODONE: Write at least two tests for each endpoint - one each for success and error behavior.
#        You can feel free to write additional tests for nuanced functionality,
#        Such as adding a book without a rating, etc.
#        Since there are four routes currently, you should have at least eight tests.
# Optional: Update the book information in setUp to make the test database your own!


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
