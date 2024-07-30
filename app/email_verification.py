import os
import smtplib
from email.mime.text import MIMEText
from flask import url_for
from itsdangerous import URLSafeTimedSerializer

def send_verification_email(user_email):
    """
    Wysyła email weryfikacyjny do nowo zarejestrowanego użytkownika.

    Args:
        user_email (str): Adres email użytkownika, do którego zostanie wysłany email weryfikacyjny.

    Returns:
        None
    """
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = f'<p>Proszę kliknąć na poniższy link, aby potwierdzić adres email:</p><p><a href="{confirm_url}">{confirm_url}</a></p>'
    subject = "Potwierdzenie adresu email"
    
    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = os.getenv('MAIL_USERNAME')
    msg['To'] = user_email
    
    with smtplib.SMTP(os.getenv('MAIL_SERVER'), os.getenv('MAIL_PORT')) as server:
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.send_message(msg)

def generate_confirmation_token(email):
    """
    Generuje token weryfikacyjny dla podanego adresu email.

    Args:
        email (str): Adres email, dla którego zostanie wygenerowany token weryfikacyjny.

    Returns:
        str: Token weryfikacyjny.
    """
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    return serializer.dumps(email, salt=os.getenv('SECURITY_PASSWORD_SALT'))

def confirm_token(token, expiration=3600):
    """
    Weryfikuje token weryfikacyjny i zwraca adres email, jeśli token jest ważny.

    Args:
        token (str): Token weryfikacyjny do sprawdzenia.
        expiration (int, optional): Czas ważności tokena w sekundach. Domyślnie 3600 sekund (1 godzina).

    Returns:
        str: Adres email, jeśli token jest ważny.
        bool: False, jeśli token jest nieważny lub wygasł.
    """
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    try:
        email = serializer.loads(token, salt=os.getenv('SECURITY_PASSWORD_SALT'), max_age=expiration)
    except:
        return False
    return email
