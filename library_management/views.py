from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify
from library_management import app
from .forms import BookForm, MemberForm, IssueForm, ReturnForm, BookImportForm
from .models import Book, Member, Transaction
from . import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc
import requests
import math


# Book Routes
@app.route("/", methods=["GET"])
@app.route("/dashboard", methods=["GET"])
def dashboard_view():
    # Getting total revenue generated
    total_revenue = (
        Transaction.query.filter_by(status="Returned")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
    )
    if total_revenue is None:
        total_revenue = 0

    total_issues = Transaction.query.filter_by().count()  # Total book issues

    pending_issues = Transaction.query.filter_by(
        status="Issued"
    ).count()  # Total pending issues

    top_books = Book.query.order_by(desc(Book.revenue)).all()[
        :5
    ]  # Top 5 best selling books

    top_members = Member.query.order_by(desc(Member.amount_paid)).all()[
        :5
    ]  # Top 5 most paying customers

    report = {
        "total_revenue": total_revenue,
        "total_issues": total_issues,
        "pending_issues": pending_issues,
        "top_books": top_books,
        "top_members": top_members,
    }
    return render_template("dashboard.html", report=report)


@app.route("/books", methods=["GET"])
def book_list_view():
    # Getting list of all books
    books = Book.query.all()
    return render_template("book/books.html", books=books)


@app.route("/book/add", methods=["GET", "POST"])
def book_add_view():
    # Form for adding book
    form = BookForm()
    context = {"heading": "Add Book"}

    if form.validate_on_submit() and request.method == "POST":
        # Adding book in database
        book = Book(
            title=form.title.data,
            authors=form.authors.data,
            average_rating=form.average_rating.data,
            language_code=form.language_code.data,
            num_pages=form.num_pages.data,
            ratings_count=form.ratings_count.data,
            text_reviews_count=form.text_reviews_count.data,
            publication_date=form.publication_date.data,
            publisher=form.publisher.data,
            isbn=form.isbn.data,
            isbn13=form.isbn13.data,
            stock=form.stock.data,
            price=form.price.data,
        )
        db.session.add(book)
        db.session.commit()
        flash(f"Book successfully added !", category="success")
        return render_template("book/book_form.html", form=form, context=context)

    if form.errors:
        form_display_errors(form.errors)

    return render_template("book/book_form.html", form=form, context=context)


@app.route("/book/delete/<id>", methods=["GET"])
def book_delete_view(id):
    book_to_delete = Book.query.get(id)  # Getting book to delete

    # Deleting the book
    db.session.delete(book_to_delete)
    db.session.commit()

    flash("Book successfully deleted !", category="success")
    return redirect(url_for("book_list_view"))


@app.route("/book/update/<id>", methods=["GET", "POST"])
def book_update_view(id):
    # Fetching book to be updated and passing it to form
    book_to_update = Book.query.get_or_404(id)
    form = BookForm(request.form, obj=book_to_update)
    context = {"heading": "Update Book"}

    if request.method == "POST" and form.validate_on_submit():
        # Updating the book
        book_to_update.title = form.title.data
        book_to_update.authors = form.authors.data
        book_to_update.average_rating = form.average_rating.data
        book_to_update.language_code = form.language_code.data
        book_to_update.num_pages = form.num_pages.data
        book_to_update.ratings_count = form.ratings_count.data
        book_to_update.text_reviews_count = form.text_reviews_count.data
        book_to_update.publication_date = form.publication_date.data
        book_to_update.publisher = form.publisher.data
        book_to_update.isbn = form.isbn.data
        book_to_update.isbn13 = form.isbn13.data
        book_to_update.stock = form.stock.data
        book_to_update.price = form.price.data
        db.session.commit()
        flash("Book successfully updated !", category="success")
        return redirect(url_for("book_list_view"))

    if form.errors:
        form_display_errors(form.errors)

    return render_template("book/book_form.html", form=form, context=context)


@app.route("/book/detail/<id>", methods=["GET", "POST"])
def book_detail_view(id):
    # Fetching a book's all details
    book = Book.query.filter_by(id=id).first_or_404()

    # Book issue form
    form = IssueForm()
    if form.validate_on_submit() and request.method == "POST":
        # Checking if member exists in database
        member = Member.query.filter_by(username=form.username.data).first()
        if member is None:
            flash(
                f"Member with username {form.username.data} does not exist !",
                category="info",
            )
        elif member.can_issue_book() is False:
            # Member has a debt
            flash(
                f"{member.name} has a debt of Rs. {member.debt}, so cannot issue this book",
                category="danger",
            )
        else:
            # Issuing the book
            book.stock -= 1
            member.debt += book.price
            transaction = Transaction(
                book=book, member=member, deadline=form.deadline.data
            )
            db.session.add(transaction)
            db.session.commit()
            flash(f"Book successfully issued to {member.name} !", category="success")

    return render_template("book/book_detail.html", book=book, form=form)


@app.route("/book/import", methods=["GET", "POST"])
def book_import_view():
    # Book import Form
    form = BookImportForm()

    if request.method == "POST":
        # Number of api calls to make
        num_pages = math.ceil(form.number_books.data / 20)
        current_count = 0

        for i in range(num_pages):
            # Making API call to Frappe API
            url = f"https://frappe.io/api/method/frappe-library/?page={i+1}"
            payload = {"page": i + 1}
            if form.title.data:
                payload["title"] = form.title.data
            if form.authors.data:
                payload["authors"] = form.authors.data
            if form.publisher.data:
                payload["publisher"] = form.publisher.data
            if form.isbn.data:
                payload["isbn"] = form.isbn.data

            response = requests.get(url, params=payload)

            # Checking for status code
            if response.status_code != 200:
                break

            # Getting the json data
            response = response.json()
            if not response["message"] or current_count == form.number_books.data:
                break
            for book in response["message"]:
                if current_count == form.number_books.data:
                    break

                # Adding book to database
                new_book = Book(
                    title=book["title"],
                    authors=book["authors"],
                    average_rating=float(book["average_rating"]),
                    language_code=book["language_code"],
                    num_pages=2,
                    ratings_count=int(book["ratings_count"]),
                    text_reviews_count=int(book["text_reviews_count"]),
                    publication_date=datetime.strptime(
                        book["publication_date"], "%m/%d/%Y"
                    ),
                    publisher=book["publisher"],
                    isbn=book["isbn"],
                    isbn13=book["isbn13"],
                    stock=10,
                    price=200,
                )
                db.session.add(new_book)
                current_count += 1

        flash(f"{current_count} books successfully imported!", category="success")
        db.session.commit()

    return render_template("book/book_import.html", form=form)


@app.route("/members", methods=["GET"])
def member_list_view():
    # Getting all member list
    members = Member.query.all()
    return render_template("member/members.html", members=members)


@app.route("/member/add", methods=["GET", "POST"])
def member_add_view():
    # Form for adding new member
    form = MemberForm()
    context = {"heading": "Add Member"}
    if form.validate_on_submit() and request.method == "POST":
        # Adding the member into the database
        try:
            # Member added to the database
            member = Member(
                username=form.username.data, email=form.email.data, name=form.name.data
            )
            db.session.add(member)
            db.session.commit()
            flash(f"Member successfully added !", category="success")
            return redirect(url_for("member_add_view"))
        except IntegrityError:
            # Username already exists
            flash(f"This username is already taken !", category="warning")

    if form.errors:
        form_display_errors(form.errors)

    return render_template("member/member_form.html", form=form, context=context)


@app.route("/member/delete/<username>", methods=["GET"])
def member_delete_view(username):
    # Getting the member to be deleted
    member_to_delete = Member.query.filter_by(username=username).first()

    # Deleting the member
    db.session.delete(member_to_delete)
    db.session.commit()

    flash("Member successfully deleted !", category="success")
    return redirect(url_for("member_list_view"))


@app.route("/member/update/<username>", methods=["POST", "GET"])
def member_update_view(username):
    # Getting the member to be updated and passing it to member update form
    member_to_update = Member.query.filter_by(username=username).first_or_404()
    form = MemberForm(request.form, obj=member_to_update)
    context = {"heading": "Update Member"}

    if request.method == "POST" and form.validate_on_submit():
        # Updating the member's data
        member_to_update.username = form.username.data
        member_to_update.name = form.name.data
        member_to_update.email = form.email.data
        db.session.commit()
        flash("Member successfully updated !", category="success")
        return redirect(url_for("member_list_view"))

    if form.errors:
        form_display_errors(form.errors)

    return render_template("member/member_form.html", form=form, context=context)


@app.route("/member/detail/<username>", methods=["GET"])
def member_detail_view(username):
    # Getting detailed information of a member
    member = Member.query.filter_by(username=username).first_or_404()
    return render_template("member/member_detail.html", member=member)


@app.route("/member/search", methods=["GET"])
def member_search_api():
    # API to get list of member username from query
    term = request.args.get("term")
    members = Member.query.filter(Member.username.contains(term.lower()))
    data = [item.username for item in members]
    return jsonify(data)


@app.route("/transactions", methods=["GET", "POST"])
def transaction_list_view():
    # Getting all transactions list
    transactions = Transaction.query.all()

    # Book return form
    form = ReturnForm()

    if form.validate_on_submit() and request.method == "POST":
        # Returning the book which was issued
        transaction_processed = Transaction.query.get(form.transaction_id.data)
        transaction_processed.return_book(form.extra_amount.data)
        flash(
            f"Book successfully returned by {transaction_processed.member.username} !",
            category="success",
        )

    if form.errors:
        form_display_errors(form.errors)

    return render_template(
        "transaction/transactions.html", transactions=transactions, form=form
    )


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("404.html"), 404


# Utility Methods
def form_display_errors(errors):
    for fieldName, errorMessage in errors.items():
        flash(f"{fieldName} - {''.join(errorMessage)}", category="danger")
