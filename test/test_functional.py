import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_register_user(client):
    response = client.post('/register', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    assert response.status_code == 201
    assert b"User created. Please verify your email" in response.data

def test_confirm_email(client):
    user = User(email='test@example.com', password='password', confirmed=False)
    db.session.add(user)
    db.session.commit()
    token = generate_confirmation_token(user.email)

    response = client.get(f'/confirm/{token}')
    assert response.status_code == 200
    assert b"You have confirmed your account. Thanks!" in response.data

    user = User.query.filter_by(email='test@example.com').first()
    assert user.confirmed

if __name__ == '__main__':
    pytest.main()
