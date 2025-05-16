# Library Management System

A Flask-based backend system for managing library books and borrowing records. This project was developed as an individual backend project to demonstrate CRUD operations and database interactions.

## Features

- **Books Management**
  - Add, view, update, and delete books
  - Search books by title, author, or ISBN
  - Track book quantities and availability

- **Borrowing System**
  - Borrow books with due dates
  - Return borrowed books
  - View all borrowing records
  - Filter for active borrows and overdue books

- **RESTful API**
  - Complete API for all operations
  - JSON responses for easy integration
  - Well-documented endpoints

- **Simple Web UI**
  - Bootstrap-based interface for managing books and borrowings
  - Responsive design
  - Modal dialogs for forms

## Technology Stack

- **Backend:** Python with Flask
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **API:** RESTful architecture

## Project Structure

```
library-management-system/
├── app.py               # Main Flask application
├── library.db           # SQLite database file (created on first run)
├── templates/           # HTML templates
│   ├── layout.html      # Base template with navigation
│   ├── index.html       # Home page with API docs
│   ├── books.html       # Books management page
│   └── borrows.html     # Borrowing records page
└── README.md            # Project documentation
```

## API Documentation

### Books API

- `GET /api/books` - Get all books (with optional search parameter)
- `GET /api/books/<id>` - Get book details by ID
- `POST /api/books` - Create a new book
- `PUT /api/books/<id>` - Update a book
- `DELETE /api/books/<id>` - Delete a book

### Borrowing API

- `GET /api/borrows` - Get all borrowing records
- `GET /api/borrows/active` - Get all active (not returned) borrowing records
- `GET /api/borrows/overdue` - Get all overdue borrowing records
- `POST /api/borrow` - Create a new borrowing record
- `PUT /api/return/<id>` - Return a borrowed book

### Users API

- `GET /api/users` - Get all users

## Setup Instructions

1. Clone the repository or download the source code

2. Set up a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install flask flask-sqlalchemy
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application:
   - Web interface: http://localhost:5000
   - API: http://localhost:5000/api/books

## Default Users

On first run, the system creates two default users:
- Admin: admin@example.com (password: admin123)
- Regular User: user@example.com (password: user123)

## Future Enhancements

- User authentication and authorization
- Book categories and tagging
- Advanced search functionality
- Email notifications for due dates
- Book reservations
- Statistics and reporting