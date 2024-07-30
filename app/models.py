from . import db

class User(db.Model):
    """
    Model reprezentujący użytkownika w aplikacji.

    Attributes:
        id (int): Unikalny identyfikator użytkownika.
        email (str): Adres email użytkownika.
        password (str): Zahaszowane hasło użytkownika.
        contacts (list): Lista kontaktów powiązanych z użytkownikiem.
        confirmed (bool): Flaga oznaczająca czy użytkownik potwierdził swój adres email.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    contacts = db.relationship('Contact', backref='owner', lazy=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """
        Zwraca reprezentację użytkownika w postaci stringa.
        
        Returns:
            str: Reprezentacja użytkownika.
        """
        return f"User('{self.email}', '{self.confirmed}')"

class Contact(db.Model):
    """
    Model reprezentujący kontakt w aplikacji.

    Attributes:
        id (int): Unikalny identyfikator kontaktu.
        name (str): Imię kontaktu.
        phone (str): Numer telefonu kontaktu.
        user_id (int): Identyfikator użytkownika, do którego należy kontakt.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        """
        Zwraca reprezentację kontaktu w postaci stringa.
        
        Returns:
            str: Reprezentacja kontaktu.
        """
        return f"Contact('{self.name}', '{self.phone}')"
