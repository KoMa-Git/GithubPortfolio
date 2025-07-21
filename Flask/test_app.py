import pytest
from minihome import app, db, users, get_password_hash
from flask import session

@pytest.fixture
def client():
    # Use in-memory database for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def register_user(client, name="Test User", email="test@example.com", password="test123"):
    return client.post("/register", data={
        "nm": name,
        "email": email,
        "pwd": password
    }, follow_redirects=True)

def login_user(client, email="test@example.com", password="test123"):
    return client.post("/login", data={
        "email": email,
        "pwd": password
    }, follow_redirects=True)

def test_home_and_about_pages(client):
    assert client.get("/").status_code == 400
    assert client.get("/about").status_code == 400

def test_register(client):
    res = register_user(client)
    assert b"Registered successfully" in res.data

def test_register_duplicate_email(client):
    register_user(client)
    res = register_user(client)
    assert b"Already registered with this email address" in res.data

def test_login_success(client):
    register_user(client)
    res = login_user(client)
    assert b"logged in successful" in res.data

def test_login_failure(client):
    res = login_user(client)
    assert b"Incorrect email or password" in res.data

def test_auth_required(client):
    res = client.get("/user", follow_redirects=True)
    assert b"You are not logged in!" in res.data

def test_change_name(client):
    register_user(client)
    login_user(client)
    res = client.post("/user", data={"nm": "New Name"}, follow_redirects=True)
    assert b"New name was saved" in res.data

def test_change_password(client):
    register_user(client)
    login_user(client)
    res = client.post("/user", data={
        "old_pass": "test123",
        "new_pass": "newpassword"
    }, follow_redirects=True)
    assert b"Password has changed" in res.data

def test_change_password_wrong_old(client):
    register_user(client)
    login_user(client)
    res = client.post("/user", data={
        "old_pass": "wrongpass",
        "new_pass": "newpassword"
    }, follow_redirects=True)
    assert b"Your old password is not valid" in res.data

def test_delete_account(client):
    register_user(client)
    login_user(client)
    res = client.post("/user", data={"del": "DELETE"}, follow_redirects=True)
    assert b"You didn't type DELETE correctly" not in res.data
    assert b"You logged out successfully" not in res.data  # because we just go to index.html silently

def test_session_auth_flag(client):
    register_user(client)
    with client.session_transaction() as sess:
        assert "auth" not in sess

    login_user(client)
    with client.session_transaction() as sess:
        assert sess.get("auth") == True
