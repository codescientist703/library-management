from library_management import app
from library_management.models import db
from datetime import date
import unittest

TEST_DB = "test.db"


class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + TEST_DB
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        self.assertEqual(app.debug, False)

        self.book_data = dict(
            title="test",
            authors="sdfsfd",
            average_rating=1,
            language_code="eng",
            num_pages=1,
            ratings_count=1,
            text_reviews_count=1,
            publication_date=date.today(),
            publisher="Nihal",
            isbn="1",
            isbn13="11",
            stock=5,
            price=501,
        )

    def tearDown(self):
        pass

    def test_dashboard_view(self):
        # Test if dashboard returns 200 status code
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_book_list_view(self):
        # Test if Book list returns 200 status code
        response = self.app.get("/books", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_book_add_view(self):
        # Test for adding book
        response = self.add_book()
        self.assertIn(b"Book successfully added", response.data)

    def test_book_delete_view(self):
        # Test for deleting book
        response = self.add_book()
        response = self.app.get(
            "/book/delete/1",
            follow_redirects=True,
        )
        self.assertIn(b"Book successfully deleted", response.data)

    def test_book_update_view(self):
        response = self.add_book()

        # Test for updating book information
        response = self.app.post(
            "/book/update/1",
            data=self.book_data,
            follow_redirects=True,
        )
        self.assertIn(b"Book successfully updated", response.data)

        # Test for book update form returning 200 status code
        response = self.app.get(
            "/book/update/1",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        # Test for book update form not found
        response = self.app.get(
            "/book/update/3",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 404)

    def test_book_detail_view(self):
        response = self.add_book()

        # Test book detail view for returning 200 status code
        response = self.app.get(
            "/book/detail/1",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        # Test for book not found
        response = self.app.get(
            "/book/detail/3",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 404)

        # Test if book issue is successful
        response = self.add_member("john")
        response = self.issue_book("john")
        self.assertIn(b"Book successfully issued", response.data)

        # Test if username does not exist
        response = self.issue_book("speedwagon")
        self.assertIn(b"Member with username speedwagon does not exist", response.data)

        # Test for member's debt
        response = self.issue_book("john")
        self.assertIn(b"has a debt", response.data)

    def test_book_import_view(self):
        # Test for book import form returning 200 status code
        response = self.app.get("/book/import", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Test for importing book
        response = self.app.post(
            "/book/import", data=dict(number_books=2), follow_redirects=True
        )
        self.assertIn(b"2 books successfully imported", response.data)

    def test_member_list_view(self):
        # Test for member list page returning 200 status code
        response = self.app.get("/members")
        self.assertEqual(response.status_code, 200)

    def test_member_add_view(self):
        # Test for member add form returning 200 status code
        response = self.app.get("/member/add")
        self.assertEqual(response.status_code, 200)

        # Test for adding member
        response = self.add_member("dio")
        self.assertIn(b"Member successfully added", response.data)

        # Test for checking username already existing
        response = self.add_member("dio")
        self.assertIn(b"This username is already taken", response.data)

    def test_member_delete_view(self):
        # Test for deleting member
        response = self.add_member("william")
        response = self.app.get("/member/delete/william", follow_redirects=True)
        self.assertIn(b"Member successfully deleted", response.data)

    def test_member_update_view(self):
        # Test for member update form return 200 status
        response = self.add_member("jonathan")
        response = self.app.get("/member/update/jonathan", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Test for member update form not found
        response = self.app.get(
            "/member/update/haha",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 404)

        # Test for updating member information
        response = self.app.post(
            "/member/update/jonathan",
            data=dict(
                username="jonathan",
                name="Jonathan Joestar",
                email="jonathan@joestar.com",
            ),
            follow_redirects=True,
        )
        self.assertIn(b"Member successfully updated", response.data)

    def test_member_detail_view(self):
        # Test for member detail page returning 200 status
        response = self.add_member("jonathan")
        response = self.app.get("/member/detail/jonathan")
        self.assertEqual(response.status_code, 200)

        # Test for member not found
        response = self.app.get(
            "/member/detail/haha",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 404)

    def test_member_search_api(self):
        # Test for member detail page returning 200 status
        response = self.add_member("skipper")
        response = self.app.get("/member/search?term=skipper")
        self.assertEqual(response.status_code, 200)

    def test_transaction_list_view(self):
        # Test for transaction list page returning 200 status
        response = self.app.get("/transactions")
        self.assertEqual(response.status_code, 200)

        # Test for issuing book return
        response = self.add_member("mob")
        response = self.add_book()
        response = self.issue_book("mob")
        response = self.app.post(
            "/transactions",
            data=dict(transaction_id=1, extra_amount=1),
            follow_redirects=True,
        )
        self.assertIn(b"Book successfully returned by mob", response.data)

    # Helper Methods

    def add_book(self):
        return self.app.post(
            "/book/add",
            data=self.book_data,
            follow_redirects=True,
        )

    def add_member(self, username):
        return self.app.post(
            "/member/add",
            data=dict(name="John Doe", username=username, email="john@doe.com"),
            follow_redirects=True,
        )

    def issue_book(self, username):
        return self.app.post(
            "/book/detail/1",
            data=dict(username=username, deadline=date.today()),
            follow_redirects=True,
        )


if __name__ == "__main__":
    unittest.main()
