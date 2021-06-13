from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField, EmailField, IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, InputRequired


class BookForm(FlaskForm):
    title = StringField(label="Book title")
    authors = StringField(label="Book Authors")
    average_rating = IntegerField(label="Average Rating")
    language_code = StringField(label="Language Code")
    num_pages = IntegerField(label="Number of Pages")
    ratings_count = IntegerField(label="Ratings Count")
    text_reviews_count = IntegerField(label="Reviews count")
    publication_date = DateField(label="Publication Date", format="%Y-%m-%d")
    publisher = StringField(label="Publisher")
    isbn = StringField(label="ISBN")
    isbn13 = StringField(label="ISBN13")
    stock = IntegerField(label="Stock")
    price = IntegerField(label="Rent price")


class MemberForm(FlaskForm):
    name = StringField(label="Member name", validators=[DataRequired()])
    username = StringField(label="Member username", validators=[DataRequired()])
    email = EmailField(label="Member email", validators=[DataRequired()])


class IssueForm(FlaskForm):
    username = StringField(label="Member name", validators=[DataRequired()])
    deadline = DateField(
        label="Deadline", format="%Y-%m-%d", validators=[DataRequired()]
    )


class ReturnForm(FlaskForm):
    extra_amount = IntegerField(
        label="Extra Amount Charged",
        validators=[InputRequired("Please enter some amount!")],
        default=0,
    )
    transaction_id = HiddenField(label=None)


class BookImportForm(FlaskForm):
    number_books = IntegerField(
        label="Number of books to import", validators=[DataRequired()]
    )
    title = StringField(label="Book title")
    isbn = StringField(label="ISBN")
    publisher = StringField(label="Book Publisher")
    authors = StringField(label="Book Authors")
