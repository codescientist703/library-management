from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField, EmailField, IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class BookForm(FlaskForm):
    title = StringField(label="Book title", validators=[DataRequired()])
    authors = StringField(label="Book Authors", validators=[DataRequired()])
    average_rating = IntegerField(label="Average Rating", validators=[DataRequired()])
    language_code = StringField(label="Language Code", validators=[DataRequired()])
    num_pages = IntegerField(label="Number of Pages", validators=[DataRequired()])
    ratings_count = IntegerField(label="Ratings Count", validators=[DataRequired()])
    text_reviews_count = IntegerField(
        label="Reviews count", validators=[DataRequired()]
    )
    publication_date = DateField(
        label="Publication Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    publisher = StringField(label="Publisher", validators=[DataRequired()])
    isbn = StringField(label="ISBN", validators=[DataRequired()])
    isbn13 = StringField(label="ISBN13", validators=[DataRequired()])
    stock = IntegerField(label="Stock", validators=[DataRequired()])
    price = IntegerField(label="Rent price", validators=[DataRequired()])


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
        validators=[
            InputRequired("Please enter some amount!"),
            NumberRange(min=0, message="Extra amount must be positive !"),
        ],
        default=0,
    )
    transaction_id = HiddenField(label=None)


class BookImportForm(FlaskForm):
    number_books = IntegerField(
        label="Number of books to import",
        validators=[DataRequired()],
    )
    title = StringField(label="Book title")
    isbn = StringField(label="ISBN")
    publisher = StringField(label="Book Publisher")
    authors = StringField(label="Book Authors")
