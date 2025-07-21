import pytest
import allure
from minihome import app, db, users, get_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register_user(client, name="Test User", email="test@example.com", password="test123"):
    return client.post("/register", data={"nm": name, "email": email, "pwd": password}, follow_redirects=True)

def login_user(client, email="test@example.com", password="test123"):
    return client.post("/login", data={"email": email, "pwd": password}, follow_redirects=True)

@allure.title("Full user journey: register → login → change name → change password → delete account")
@allure.feature("Full User Flow")
@allure.severity(allure.severity_level.CRITICAL)
def test_full_user_flow(client):
    with allure.step("Register user"):
        res = register_user(client)
        assert b"Registered successfully" in res.data

    with allure.step("Login user"):
        res = login_user(client)
        assert b"logged in successful" in res.data

    with allure.step("Change name"):
        res = client.post("/user", data={"nm": "Updated Name"}, follow_redirects=True)
        assert b"New name was saved" in res.data

    with allure.step("Change password"):
        res = client.post("/user", data={"old_pass": "test123", "new_pass": "newpass456"}, follow_redirects=True)
        assert b"Password has changed" in res.data

    with allure.step("Logout"):
        res = client.get("/logout", follow_redirects=True)
        assert b"You logged out successfully" in res.data

    with allure.step("Login with new password"):
        res = login_user(client, password="newpass456")
        assert b"logged in successful" in res.data

    with allure.step("Delete account"):
        res = client.post("/user", data={"del": "DELETE"}, follow_redirects=True)
        assert b"You didn't type DELETE correctly" not in res.data

    with allure.step("Ensure user is logged out"):
        res = client.get("/user", follow_redirects=True)
        assert b"You are not logged in!" in res.data
