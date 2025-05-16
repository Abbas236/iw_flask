from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Create Flask app
app = Flask(__name__)

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

# Initialize database
db = SQLAlchemy(app)

# Define models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'description': self.description,
            'category': self.category,
            'quantity': self.quantity,
            'available': self.available,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    
    book = db.relationship('Book', backref=db.backref('borrow_records', lazy=True))
    user = db.relationship('User', backref=db.backref('borrow_records', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'borrow_date': self.borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': self.return_date.strftime('%Y-%m-%d %H:%M:%S') if self.return_date else None,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create a default admin user if no users exist
    if not User.query.first():
        default_admin = User(
            name="Admin User",
            email="admin@example.com",
            is_admin=True
        )
        default_admin.set_password("admin123")
        
        default_user = User(
            name="Regular User",
            email="user@example.com",
            is_admin=False
        )
        default_user.set_password("user123")
        
        db.session.add(default_admin)
        db.session.add(default_user)
        db.session.commit()
        print("Created default users: admin@example.com and user@example.com")

# API Routes for Books
@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books or search by title/author"""
    search = request.args.get('search', '')
    
    if search:
        books = Book.query.filter(
            (Book.title.contains(search)) | 
            (Book.author.contains(search)) |
            (Book.isbn.contains(search))
        ).all()
    else:
        books = Book.query.all()
    
    return jsonify([book.to_dict() for book in books])

@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    """Get a specific book by ID"""
    book = Book.query.get_or_404(id)
    return jsonify(book.to_dict())

@app.route('/api/books', methods=['POST'])
def create_book():
    """Create a new book"""
    data = request.get_json()
    
    # Validate input
    if not data.get('title') or not data.get('author') or not data.get('isbn'):
        return jsonify({'error': 'Title, author and ISBN are required'}), 400
    
    # Check for duplicate ISBN
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({'error': 'A book with this ISBN already exists'}), 400
    
    # Create new book
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        description=data.get('description', ''),
        category=data.get('category', ''),
        quantity=data.get('quantity', 1),
        available=data.get('available', data.get('quantity', 1))
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201

@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    """Update a book"""
    book = Book.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        # Check for duplicate ISBN if changing
        if data['isbn'] != book.isbn:
            existing_book = Book.query.filter_by(isbn=data['isbn']).first()
            if existing_book:
                return jsonify({'error': 'A book with this ISBN already exists'}), 400
        book.isbn = data['isbn']
    if 'description' in data:
        book.description = data['description']
    if 'category' in data:
        book.category = data['category']
    if 'quantity' in data:
        book.quantity = data['quantity']
    if 'available' in data:
        book.available = data['available']
    
    db.session.commit()
    
    return jsonify(book.to_dict())

@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    """Delete a book"""
    book = Book.query.get_or_404(id)
    
    # Check if book is borrowed
    if book.available < book.quantity:
        return jsonify({'error': 'Cannot delete book as it is currently borrowed'}), 400
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'})

# API Routes for Borrowing
@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    """Borrow a book"""
    data = request.get_json()
    
    # Validate input
    if not data.get('book_id') or not data.get('user_id') or not data.get('due_date'):
        return jsonify({'error': 'Book ID, user ID and due date are required'}), 400
    
    # Check book availability
    book = Book.query.get_or_404(data['book_id'])
    if book.available <= 0:
        return jsonify({'error': 'Book is not available for borrowing'}), 400
    
    # Check user exists
    user = User.query.get_or_404(data['user_id'])
    
    # Create borrow record
    try:
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    borrow = BorrowRecord(
        book_id=data['book_id'],
        user_id=data['user_id'],
        due_date=due_date
    )
    
    # Update book availability
    book.available -= 1
    
    db.session.add(borrow)
    db.session.commit()
    
    return jsonify(borrow.to_dict()), 201

@app.route('/api/return/<int:borrow_id>', methods=['PUT'])
def return_book(borrow_id):
    """Return a borrowed book"""
    borrow = BorrowRecord.query.get_or_404(borrow_id)
    
    # Check if already returned
    if borrow.return_date:
        return jsonify({'error': 'This book has already been returned'}), 400
    
    # Update return date
    borrow.return_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(borrow.book_id)
    book.available += 1
    
    db.session.commit()
    
    return jsonify(borrow.to_dict())

@app.route('/api/borrows', methods=['GET'])
def get_borrows():
    """Get all borrow records"""
    borrows = BorrowRecord.query.all()
    return jsonify([borrow.to_dict() for borrow in borrows])

@app.route('/api/borrows/active', methods=['GET'])
def get_active_borrows():
    """Get all active (not returned) borrow records"""
    borrows = BorrowRecord.query.filter(BorrowRecord.return_date == None).all()
    return jsonify([borrow.to_dict() for borrow in borrows])

@app.route('/api/borrows/overdue', methods=['GET'])
def get_overdue_borrows():
    """Get all overdue borrow records"""
    now = datetime.utcnow()
    borrows = BorrowRecord.query.filter(
        BorrowRecord.return_date == None,
        BorrowRecord.due_date < now
    ).all()
    return jsonify([borrow.to_dict() for borrow in borrows])

# API Routes for Users
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Web UI Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/books')
def list_books():
    """List all books"""
    search = request.args.get('search', '')
    
    if search:
        books = Book.query.filter(
            (Book.title.contains(search)) | 
            (Book.author.contains(search)) |
            (Book.isbn.contains(search))
        ).all()
    else:
        books = Book.query.all()
    
    return render_template('books.html', books=books)

@app.route('/borrows')
def list_borrows():
    """List all borrow records"""
    filter_type = request.args.get('filter', '')
    now = datetime.utcnow()
    
    if filter_type == 'active':
        borrows = BorrowRecord.query.filter(BorrowRecord.return_date == None).all()
    elif filter_type == 'overdue':
        borrows = BorrowRecord.query.filter(
            BorrowRecord.return_date == None,
            BorrowRecord.due_date < now
        ).all()
    else:
        borrows = BorrowRecord.query.all()
    
    return render_template('borrows.html', borrows=borrows, now=now)

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)