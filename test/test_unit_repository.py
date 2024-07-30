import unittest
from app.models import User
from app import db, create_app

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        """
        Ustawienia wstępne przed każdym testem.
        """
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """
        Sprzątanie po każdym teście.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """
        Test tworzenia nowego użytkownika.
        """
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().email, "test@example.com")

if __name__ == '__main__':
    unittest.main()
