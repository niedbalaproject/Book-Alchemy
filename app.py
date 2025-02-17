from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book
from datetime import datetime
import secrets  # Import for generating a secret key

app = Flask(__name__)

# Set a secret key for session management (fixes RuntimeError)
app.secret_key = secrets.token_hex(16)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/niedb/PycharmProjects/Book_Alchemy_project/data/library.sqlite'

db.init_app(app)

# with app.app_context():
#     db.create_all()


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Handles adding a new author to the database.

    GET: Renders the add_author.html template.
    POST: Retrieves form data, creates a new Author object,
          saves it to the database, and returns a success message.
    """
    if request.method == "POST":
        name = request.form["name"]
        birth_date_str = request.form["birthdate"]
        date_of_death_str = request.form["date_of_death"]

        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d").date() if date_of_death_str else None

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        return "Author added successfully!"

    return render_template("add_author.html")


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Handles adding a new book to the database.

    GET: Renders the add_book.html template with a list of authors.
    POST: Retrieves form data, creates a new Book object,
          assigns an existing or new author, and saves it to the database.
    """
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']
        new_author_name = request.form.get('new_author_name')
        rating = request.form.get('rating')  # Get rating from the form

        # If "Add New" is selected, create a new author
        if author_id == "new" and new_author_name:
            new_author = Author(name=new_author_name)
            db.session.add(new_author)
            db.session.commit()
            author_id = new_author.id  # Use the new author's ID

        # Create and add the book
        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id,
            rating=int(rating) if rating else None  # Convert rating to integer
        )
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Deletes a book from the database.
    If the author has no other books, delete the author as well.

    :param book_id: ID of the book to be deleted.
    :return: Redirects to the home page after deletion.
    """
    book = Book.query.get_or_404(book_id)  # get the book or return 404 if not found
    author = book.author  # get the author before deleting the book

    db.session.delete(book)
    db.session.commit()

    # Checking if the author has any other books left
    if not author.books:
        db.session.delete(author)
        db.session.commit()

    flash("Book deleted successfully!", "success")
    return redirect(url_for("home"))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """
    Displays the details of a specific book.
    :param book_id: ID of the book to be displayed.
    :return: Renders the book_detail.html template.
    """
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


@app.route('/book/<int:book_id>/rate', methods=['POST'])
def rate_book(book_id):
    """
    Handles rating submission for a book.

    :param book_id: ID of the book being rated.
    :return: Redirects to home page with a success or error message.
    """
    book = Book.query.get_or_404(book_id)
    rating = request.form.get('rating')

    if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 10:
        flash("Invalid rating. Please select a number between 1 and 10.", 'danger')
        return redirect(url_for('home'))

    book.rating = int(rating)
    db.session.commit()

    flash("Rating updated successfully!", 'success')
    return redirect(url_for('home'))


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    """
    Displays the details of a specific author.

    :param author_id: ID of the author to be displayed.
    :return: Renders the author_detail.html template.
    """
    author = Author.query.get_or_404(author_id)
    books = Book.query.filter_by(author_id=author.id).all()
    return render_template('author_detail.html', author=author, books=books)


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """
    Deletes an author and all books associated with them.
    :param author_id: ID of the author to be deleted.
    :return: Redirects to the homepage after deletion.
    """
    author = Author.query.get_or_404(author_id)

    db.session.delete(author)
    db.session.commit()

    flash('Author and all their books deleted successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/')
def home():
    """
    Displays the homepage with books sorted by title or author name.
    Includes search features for books and authors.

    :return: Renders the home.html template with sorted and filtered book data.
    """
    sort_by = request.args.get('sort_by', 'title')  # Default sorting
    search_query = request.args.get('search', '').strip()  # Get book search query
    search_author_query = request.args.get('search_author', '').strip()  # Get author search query

    # Start query joining Book and Author
    books_query = Book.query.join(Author)

    # Filter by book title if a book search query exists
    if search_query:
        books_query = books_query.filter(Book.title.contains(search_query))

    # Filter by author name if an author search query exists
    if search_author_query:
        books_query = books_query.filter(Author.name.contains(search_author_query))

    # Apply sorting
    if sort_by == "author":
        books_query = books_query.order_by(Author.name)
    else:
        books_query = books_query.order_by(Book.title)

    books = books_query.all()

    return render_template('home.html', books=books)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
