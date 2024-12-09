from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory storage for books and members
books = []
members = []

# Helper function to generate IDs
def generate_id(data):
    return max([item['id'] for item in data], default=0) + 1

# Token-based authentication (Basic Implementation)
TOKEN = "secure_token"

def authenticate():
    token = request.headers.get("Authorization")
    if not token or token != f"Bearer {TOKEN}":
        abort(401, description="Unauthorized")

# CRUD Operations for Books
@app.route('/books', methods=['GET'])
def get_books():
    authenticate()
    # Search functionality
    title = request.args.get('title')
    author = request.args.get('author')
    
    filtered_books = books
    if title:
        filtered_books = [book for book in filtered_books if title.lower() in book['title'].lower()]
    if author:
        filtered_books = [book for book in filtered_books if author.lower() in book['author'].lower()]
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    start = (page - 1) * per_page
    end = start + per_page
    return jsonify(filtered_books[start:end])

@app.route('/books', methods=['POST'])
def create_book():
    authenticate()
    data = request.json
    if not data or 'title' not in data or 'author' not in data:
        abort(400, description="Invalid book data")
    book = {
        'id': generate_id(books),
        'title': data['title'],
        'author': data['author'],
        'published_year': data.get('published_year', None)
    }
    books.append(book)
    return jsonify(book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    authenticate()
    data = request.json
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        abort(404, description="Book not found")
    book.update({
        'title': data.get('title', book['title']),
        'author': data.get('author', book['author']),
        'published_year': data.get('published_year', book.get('published_year'))
    })
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    authenticate()
    global books
    books = [book for book in books if book['id'] != book_id]
    return '', 204

# CRUD Operations for Members
@app.route('/members', methods=['GET'])
def get_members():
    authenticate()
    return jsonify(members)

@app.route('/members', methods=['POST'])
def create_member():
    authenticate()
    data = request.json
    if not data or 'name' not in data:
        abort(400, description="Invalid member data")
    member = {
        'id': generate_id(members),
        'name': data['name'],
        'joined_date': data.get('joined_date', None)
    }
    members.append(member)
    return jsonify(member), 201

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    authenticate()
    data = request.json
    member = next((m for m in members if m['id'] == member_id), None)
    if not member:
        abort(404, description="Member not found")
    member.update({
        'name': data.get('name', member['name']),
        'joined_date': data.get('joined_date', member.get('joined_date'))
    })
    return jsonify(member)

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    authenticate()
    global members
    members = [member for member in members if member['id'] != member_id]
    return '', 204

# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': str(error)}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

if __name__ == '__main__':
    app.run(debug=True)
