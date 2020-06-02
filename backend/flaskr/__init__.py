import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random
import sys
from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginate(books, request):
    page = request.args.get('page', 1, type=int)
    start = (page-1)*BOOKS_PER_SHELF
    end = start+BOOKS_PER_SHELF
    selection = [book.format() for book in books[start:end]]
    return selection
# @TODONE: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODONE' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # @TODONE: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    @app.route('/books', methods=['GET'])
    def get_books():
        books = Book.query.order_by(Book.id).all()
        selection = paginate(books, request)
        if len(selection) is None:
            abort(404)
        return jsonify({
            "success": True,
            "books": selection,
            "total_books": len(books)
        })

    # @TODONE: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def modify_book(book_id):
        try:
            book = Book.query.get(book_id)
            if book is None:
                abort(404)
            if 'rating' in request.get_json():
                book.rating = int(request.get_json()['rating'])
            print(book.format())
            book.update()
        except:
            print(sys.exc_info())
            abort(400)
        return jsonify({
            "success": True,
            "id": book_id
        })
    # @TODONE: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            print("oi")
            book = Book.query.get(book_id)
            if book is None:
                abort(404)
            book.delete()
            books = Book.query.order_by(Book.id).all()
            selection = paginate(books, request)
            if len(selection) is None:
                abort(404)
            return jsonify({
                "success": True,
                "deleted": book_id,
                "books": selection,
                "total_books": len(books)
            })
        except:
            print(sys.exc_info())
            abort(422)

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # @TODONE: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    @app.route('/books', methods=['POST'])
    def create_book():
        try:
            print(request.get_json())
            book=Book(title=request.get_json()['title'],author=request.get_json()['author'],rating=request.get_json()['rating'])
            book.insert()
            books = Book.query.order_by(Book.id).all()
            selection = paginate(books, request)
            return jsonify({
                "success": True,
                "created": book.id,
                "books": selection,
                "total_books": len(books)
            })
        except:
            print(sys.exc_info())
            abort(4)

    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.

    return app
