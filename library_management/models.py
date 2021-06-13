from library_management import db
from datetime import date


class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    authors = db.Column(db.String(300), nullable=False)
    average_rating = db.Column(db.Float(), nullable=False)
    language_code = db.Column(db.String(10), nullable=False)
    num_pages = db.Column(db.Integer(), nullable=False)
    ratings_count = db.Column(db.Integer(), nullable=False)
    text_reviews_count = db.Column(db.Integer(), nullable=False)
    publication_date = db.Column(db.Date(), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(300), nullable=False)
    isbn13 = db.Column(db.String(300), nullable=False)
    stock = db.Column(db.Integer(), default=1)
    total_stock = db.Column(db.Integer())
    price = db.Column(db.Integer(), default=100)
    revenue = db.Column(db.Integer(), default=0, nullable=False)
    transactions = db.relationship("Transaction", backref="book", lazy=True)

    def __repr__(self):
        return f"{self.title}"

    def __init__(self, **kwargs):
        super(Book, self).__init__(**kwargs)
        self.total_stock = self.stock


class Member(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False)
    debt = db.Column(db.Integer(), default=0)
    transactions = db.relationship("Transaction", backref="member", lazy=True)
    amount_paid = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return f"{self.name}"

    def can_issue_book(self):
        return self.debt <= 500


class Transaction(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    member_id = db.Column(db.Integer(), db.ForeignKey("member.id", ondelete="SET NULL"))
    book_id = db.Column(db.Integer(), db.ForeignKey("book.id", ondelete="SET NULL"))
    start_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date())
    deadline = db.Column(db.Date(), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return f"{self.type} - {self.id}"

    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        self.start_date = date.today()
        self.status = "Issued"

    def return_book(self, extra_amount):
        total_amount = self.book.price + extra_amount
        self.amount = total_amount
        self.status = "Returned"
        self.end_date = date.today()
        self.member.debt -= self.book.price
        self.member.amount_paid += total_amount
        self.book.revenue += total_amount
        db.session.commit()
