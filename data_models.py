from flask_sqlalchemy import SQLAlchemy

# Initialize the database object
db = SQLAlchemy()


# Author model
class Author(db.Model):
    """
    Represents an author in the database.

    Attributes:
        id (int): Primary key, unique identifier for the author.
        name (str): Name of the author, required.
        birth_date (date): Author's birth date.
        date_of_death (date, optional): Author's date of death.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)  # Can be NULL if the author is still alive

    # Relationship with Book model
    books = db.relationship('Book', back_populates='author', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Author {self.name} (ID: {self.id})>"

    def __str__(self):
        return self.name


# Book model
class Book(db.Model):
    """
    Represents a book in the database.

    Attributes:
        id (int): Primary key, unique identifier for the book.
        isbn (str): ISBN as a number of the book, unique and required.
        title (str): Title of the book, required.
        publication_year (int): Year the book was published.
        author_id (int): Foreign key linking to an Author.
        rating (int): Rating for the book (optional, between 1-10).
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book {self.title} (ID: {self.id})>"

    def __str__(self):
        return self.title
