from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from . import db, bcrypt
from .models import User, Contact
from . import create_app
from .email_verification.py import send_verification_email, confirm_token
from . import limiter
import cloudinary
import cloudinary.uploader
import os

app = create_app()

cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

@app.route('/register', methods=['POST'])
def register():
    """
    Rejestruje nowego użytkownika.
    
    Przyjmuje dane użytkownika (email, hasło) w formacie JSON, haszuje hasło
    i zapisuje nowego użytkownika w bazie danych. Wysyła email weryfikacyjny.

    Returns:
        json: Komunikat o powodzeniu lub błędzie rejestracji.
    """

    data = request.get_json()
    email = data['email']
    password = data['password']
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    send_verification_email(email)

    return jsonify({"msg": "User created", "user": {"email": new_user.email}}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Loguje użytkownika.
    
    Przyjmuje dane użytkownika (email, hasło) w formacie JSON, sprawdza poprawność danych
    i generuje tokeny JWT w przypadku pomyślnego logowania.

     Returns:
    json: Tokeny JWT lub komunikat o błędzie logowania.
    """
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route('/contacts', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def create_contact():
    """
    Tworzy nowy kontakt dla zalogowanego użytkownika.

    Returns:
        json: Komunikat o powodzeniu lub błędzie utworzenia kontaktu.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_contact = Contact(name=data['name'], phone=data['phone'], user_id=current_user_id)
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"msg": "Contact created", "contact": {"name": new_contact.name, "phone": new_contact.phone}}), 201

@app.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    """
    Pobiera wszystkie kontakty zalogowanego użytkownika.

    Returns:
        json: Lista kontaktów użytkownika.
    """
    current_user_id = get_jwt_identity()
    contacts = Contact.query.filter_by(user_id=current_user_id).all()
    contacts_list = [{"id": contact.id, "name": contact.name, "phone": contact.phone} for contact in contacts]
    return jsonify(contacts=contacts_list), 200

@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    """
    Usuwa kontakt użytkownika.

    Args:
        contact_id (int): Identyfikator kontaktu do usunięcia.

    Returns:
        json: Komunikat o powodzeniu lub błędzie usunięcia kontaktu.
    """
    current_user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user_id).first()
    if not contact:
        return jsonify({"msg": "Contact not found"}), 404

    db.session.delete(contact)
    db.session.commit()
    return jsonify({"msg": "Contact deleted"}), 200

@app.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    """
    Potwierdza adres email użytkownika za pomocą tokena.

    Args:
        token (str): Token weryfikacyjny wysłany na email użytkownika.

    Returns:
        json: Komunikat o stanie weryfikacji.
    """

    try:
        email = confirm_token(token)
    except:
        return jsonify({"msg": "The confirmation link is invalid or has expired."}), 400

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        return jsonify({"msg": "Account already confirmed."}), 200
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "You have confirmed your account. Thanks!"}), 200
    
@app.route('/upload_avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """
    Aktualizuje awatar użytkownika za pomocą pliku przesłanego przez użytkownika.

    Returns:
        json: Komunikat o powodzeniu lub błędzie aktualizacji awatara.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    upload_result = cloudinary.uploader.upload(file)
    user.avatar_url = upload_result['url']
    db.session.commit()
    return jsonify({"msg": "Avatar updated", "avatar_url": user.avatar_url}), 200